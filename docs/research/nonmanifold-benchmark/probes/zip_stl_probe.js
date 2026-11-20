/* Inspect small byte-pinned ZIP archives containing ASCII/binary STL data.
 * No silent geometric healing, coordinate rounding, or external libraries.
 * This probe is intentionally scoped to bounded single-entry ZIP sources.
 */
'use strict';
function read16(a,p){return a[p] | (a[p+1]<<8)}
function read32(a,p){return (a[p] | (a[p+1]<<8) | (a[p+2]<<16) | (a[p+3]<<24))>>>0}
function decodeBase64(s){
  const abc='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',out=[];
  let val=0,bits=0;
  for(let i=0;i<s.length;i++){
    let c=s[i];if(c==='=' )break;
    if(c==='\r'||c==='\n'||c===' '||c==='\t')continue;
    const d=abc.indexOf(c);if(d<0)throw Error('Invalid base64 character');
    val=(val<<6)|d; bits+=6;
    if(bits>=8){bits-=8;out.push((val>>>bits)&255)}
  }
  return new Uint8Array(out)
}
function crc32(bytes){let c=0xffffffff; for(const b of bytes){c^=b;for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xedb88320:0)}return (c^0xffffffff)>>>0}
function inflateRaw(input, expectedLength=20_000_000){
  let bit=0,out=[];
  function take(n){if(n<0||n>24||bit+n>input.length*8)throw Error('Truncated or invalid deflate');let v=0;for(let i=0;i<n;i++)v|=((input[bit>>3]>>(bit&7))&1)<<i,bit++;return v}
  function codes(lengths){
    const counts=Array(16).fill(0),first=Array(16).fill(0),map=new Map();let max=0;
    for(const n of lengths){if(n<0||n>15)throw Error('Bad Huffman code length');if(n){counts[n]++;max=Math.max(max,n)}}
    let curr=0;for(let n=1;n<=15;n++){curr=(curr+counts[n-1])*2;first[n]=curr;if(curr+counts[n]>Math.pow(2,n))throw Error('Oversubscribed Huffman tree')}
    for(let s=0;s<lengths.length;s++){const len=lengths[s];if(len)map.set(len+':'+first[len]++,s)}
    return function(){let code=0;for(let n=1;n<=max;n++){code=(code<<1)|take(1);const val=map.get(n+':'+code);if(val!==undefined)return val}throw Error('Invalid Huffman symbol')}
  }
  const lnbase=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258],lnex=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];
  const db=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577],de=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
  let done=false;
  while(!done){done=!!take(1);const typ=take(2);if(typ===3)throw Error('Reserved deflate block');
    if(typ===0){bit=(bit+7)&~7;const len=take(16),check=take(16);if(((len^65535)&65535)!==check)throw Error('Uncompressed DEFLATE LEN mismatch');for(let i=0;i<len;i++){out.push(take(8));if(out.length>expectedLength)throw Error('Deflate output limit')}}
    else{
      let lit,dist;
      if(typ===1){const lengths=Array.from({length:288},(_,i)=>i<=143?8:i<=255?9:i<=279?7:8);lit=codes(lengths);dist=codes(Array(32).fill(5));}
      else{
        const hlit=257+take(5),hdist=1+take(5),hclen=4+take(4),order=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];
        const cl=Array(19).fill(0);for(let i=0;i<hclen;i++)cl[order[i]]=take(3);const decodeLength=codes(cl);const length=[];
        while(length.length<hlit+hdist){const sym=decodeLength();if(sym<=15)length.push(sym);else{let n,value;if(sym===16){if(!length.length)throw Error('Repeat without previous code');n=3+take(2);value=length[length.length-1];}else if(sym===17){n=3+take(3);value=0;}else if(sym===18){n=11+take(7);value=0;}else throw Error('Unknown code length');for(let i=0;i<n;i++)length.push(value)}}
        if(length.length!==hlit+hdist)throw Error('Huffman code length overflow');lit=codes(length.slice(0,hlit));dist=codes(length.slice(hlit));
      }
      while(true){const s=lit();if(s<256){out.push(s);if(out.length>expectedLength)throw Error('Deflate output limit')}else if(s===256)break;else{if(s>285)throw Error('Illegal length code');const l=lnbase[s-257]+take(lnex[s-257]);const d=dist();if(d>29)throw Error('Illegal distance code');const offset=db[d]+take(de[d]);if(offset>out.length||offset===0)throw Error('Backref before stream');for(let k=0;k<l;k++){out.push(out[out.length-offset]);if(out.length>expectedLength)throw Error('Deflate output limit')}}}
    }
  }
  return new Uint8Array(out)
}
function extractSingleZip(zip,limit=20_000_000){
 if(zip.length<98||zip.length>25_000_000||read32(zip,0)!==0x04034b50)throw Error('Missing or oversized local ZIP header');
 let end=-1;
 for(let p=zip.length-22;p>=Math.max(0,zip.length-65557);p--){
   if(read32(zip,p)===0x06054b50&&p+22+read16(zip,p+20)===zip.length){end=p;break}
 }
 if(end<0||read16(zip,end+8)!==1||read16(zip,end+10)!==1||read16(zip,end+4)!==0||read16(zip,end+6)!==0)throw Error('ZIP must contain one non-spanned entry');
 const directorySize=read32(zip,end+12),directoryOffset=read32(zip,end+16);
 if(directoryOffset+directorySize!==end||read32(zip,directoryOffset)!==0x02014b50)throw Error('ZIP central directory invalid');
 const flags=read16(zip,6),method=read16(zip,8),comp=read32(zip,18),length=read32(zip,22),n=read16(zip,26),e=read16(zip,28),begin=30+n+e;
 if(flags&0x0009)throw Error('Encrypted or descriptor-style ZIP not supported');
 if(![0,8].includes(method)||length>limit||begin+comp!==directoryOffset)throw Error('ZIP compression/input size unsupported');
 if(read32(zip,directoryOffset+42)!==0||read16(zip,directoryOffset+8)!==flags||read16(zip,directoryOffset+10)!==method||read32(zip,directoryOffset+20)!==comp||read32(zip,directoryOffset+24)!==length||read32(zip,directoryOffset+16)!==read32(zip,14))throw Error('ZIP central/local header conflict');
 if(read16(zip,directoryOffset+28)!==n)throw Error('ZIP archive filename length conflict');
 for(let i=0;i<n;i++)if(zip[30+i]!==zip[directoryOffset+46+i])throw Error('ZIP archive filename conflict');
 const directoryEnd=directoryOffset+46+read16(zip,directoryOffset+28)+read16(zip,directoryOffset+30)+read16(zip,directoryOffset+32);
 if(directoryEnd!==end)throw Error('ZIP central directory has surplus data');
 const body=zip.subarray(begin,begin+comp);const result=method===0?body:inflateRaw(body,limit);
 if(result.length!==length)throw Error('ZIP output size mismatch');
 const c=read32(zip,14);if(crc32(result)!==c)throw Error('ZIP CRC mismatch');
 const name=String.fromCharCode(...zip.subarray(30,30+n));
 if(!/^[0-9]+\.stl$/i.test(name)||n>100)throw Error('Archive does not contain one numeric STL');
 return {name,bytes:result,crc32:c>>>0,zip_bytes:zip.length,compressed_bytes:comp,uncompressed_bytes:length};
}
function parseBinaryStl(src,faceLimit=1_000_000){
 if(src.length<84)throw Error('Truncated binary STL'); const view=new DataView(src.buffer,src.byteOffset,src.byteLength),f=view.getUint32(80,true);
 if(f>faceLimit||84+f*50!==src.length)throw Error('Binary STL length/triangle count mismatch');
 const pointIds=new Map(),vertices=[],faces=[];
 function idAt(pos){const words=[];for(let j=0;j<3;j++)words.push(view.getUint32(pos+j*4,true));const coords=words.map((_,j)=>view.getFloat32(pos+j*4,true));if(coords.some(x=>!Number.isFinite(x)))throw Error('Nonfinite coordinate');const key=coords.map(x=>Object.is(x,-0)?'0':x.toString()).join('/');let id=pointIds.get(key);if(id===undefined){id=vertices.length;vertices.push(coords);pointIds.set(key,id)}return id;}
 let zeroAreas=0,duplicates=0;const triangles=new Set();const edges=new Map(),perVertex=Array();
 for(let i=0;i<f;i++){
   const pos=84+50*i,vs=[idAt(pos+12),idAt(pos+24),idAt(pos+36)];faces.push(vs);
   if(new Set(vs).size!==3)zeroAreas++;
   else{const a=vertices[vs[0]],b=vertices[vs[1]],c=vertices[vs[2]],u=a.map((v,j)=>b[j]-v),v=a.map((w,j)=>c[j]-w),cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],m=cross.reduce((s,x)=>s+x*x,0);if(m===0)zeroAreas++}
   const canonical=vs.slice().sort((a,b)=>a-b).join(',');if(triangles.has(canonical))duplicates++;triangles.add(canonical);
   for(let j=0;j<3;j++){const a=vs[j],b=vs[(j+1)%3],key=a<b?a+','+b:b+','+a;let ed=edges.get(key);if(!ed){ed={a:Math.min(a,b),b:Math.max(a,b),uses:0,directions:0};edges.set(key,ed)}ed.uses++;ed.directions+=(a<b)?1:-1;}
 }
 const hist={};let oppositeWindingViolations=0;for(const ed of edges.values()){hist[ed.uses]=(hist[ed.uses]||0)+1;if(ed.uses===2&&ed.directions!==0)oppositeWindingViolations++;}
 const parent=Array.from({length:vertices.length},(_,i)=>i);function find(i){while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i]}return i}function union(a,b){a=find(a);b=find(b);if(a!==b)parent[b]=a}
 for(const ed of edges.values())union(ed.a,ed.b);
 const groups=new Set();for(let i=0;i<vertices.length;i++)groups.add(find(i));
 return {source_triangles:f,source_unique_exact_vertices:vertices.length,source_unique_exact_edges:edges.size,edge_incidence_histogram:hist,boundary_edges:hist['1']||0,two_face_edges:hist['2']||0,three_plus_edges:[...edges.values()].filter(x=>x.uses>=3).length,raw_duplicate_triangles:duplicates,zero_area_triangles:zeroAreas,edge_winding_conflicts:oppositeWindingViolations,vertex_connected_components:groups.size,exact_coordinate_welding:true,triangle_coordinates:vertices,triangles:faces};
}
if(typeof module!=='undefined'&&module.exports)module.exports={read16,read32,decodeBase64,crc32,inflateRaw,extractSingleZip,parseBinaryStl};

function sha256Hex(data){
  const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const total=Math.ceil((data.length+9)/64)*64;const msg=new Uint8Array(total);msg.set(data);msg[data.length]=128;
  const bits=data.length*8;
  if(!Number.isSafeInteger(bits))throw Error('SHA-256 size overflow');
  for(let i=0;i<8;i++)msg[total-1-i]=Math.floor(bits/Math.pow(2,8*i))&255;
  const rr=(v,n)=>(v>>>n)|(v<<(32-n)),w=new Uint32Array(64);
  for(let start=0;start<total;start+=64){
    for(let j=0;j<16;j++){const p=start+j*4;w[j]=((msg[p]<<24)|(msg[p+1]<<16)|(msg[p+2]<<8)|msg[p+3])>>>0;}
    for(let j=16;j<64;j++){const x=w[j-15],y=w[j-2];const sx=rr(x,7)^rr(x,18)^(x>>>3);const sy=rr(y,17)^rr(y,19)^(y>>>10);w[j]=(w[j-16]+sx+w[j-7]+sy)>>>0;}
    let [a,b,c,d,e,f,g,v]=h;
    for(let j=0;j<64;j++){
      const t1=(v+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^(~e&g))+k[j]+w[j])>>>0;
      const t2=((rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;
      v=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
    }
    for(let j=0;j<8;j++)h[j]=(h[j]+[a,b,c,d,e,f,g,v][j])>>>0;
  }
  return h.map(x=>x.toString(16).padStart(8,'0')).join('');
}

function auditMeshVertices(vertices,faces){
  const edgeMap=new Map(),triMap=new Set();let duplicates=0,zero=0;
  const links=Array.from({length:vertices.length},()=>new Map());
  for(const tri of faces){
    if(tri.length!==3||tri.some(x=>!Number.isInteger(x)||x<0||x>=vertices.length))throw Error('Invalid triangle index');
    const canonical=tri.slice().sort((a,b)=>a-b).join(',');if(triMap.has(canonical))duplicates++;triMap.add(canonical);
    const [a,b,c]=tri.map(x=>vertices[x]);if(new Set(tri).size<3)zero++;else{
      const u=a.map((x,i)=>b[i]-x),v=a.map((x,i)=>c[i]-x);
      const cr=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      if(cr.reduce((s,x)=>s+x*x,0)===0)zero++;
    }
    for(let j=0;j<3;j++){
      const x=tri[j],y=tri[(j+1)%3],z=tri[(j+2)%3];
      const key=x<y?x+','+y:y+','+x;let entry=edgeMap.get(key);
      if(!entry){entry={x:Math.min(x,y),y:Math.max(x,y),uses:0,winding:0};edgeMap.set(key,entry)}
      entry.uses++;entry.winding+=(x<y)?1:-1;
      const link=links[x],l=link.get(y)||[];l.push(z);link.set(y,l);
    }
  }
  const hist={};let windingConflicts=0;for(const e of edgeMap.values()){hist[e.uses]=(hist[e.uses]||0)+1;if(e.uses===2&&e.winding!==0)windingConflicts++}
  const root=Array.from({length:vertices.length},(_,i)=>i);const find=i=>{while(root[i]!==i){root[i]=root[root[i]];i=root[i]}return i};
  for(const e of edgeMap.values()){const a=find(e.x),b=find(e.y);if(a!==b)root[a]=b}
  const components=new Set(root.map((_,i)=>find(i))).size;
  let singularLinkVertices=0,boundaryLinkVertices=0,interiorLinkVertices=0;
  for(let x=0;x<vertices.length;x++){
    const edges=new Map();const neighbors=new Set();let nFaces=0;
    for(const [y,arr] of links[x])for(const z of arr){nFaces++;neighbors.add(y);neighbors.add(z);const a=Math.min(y,z),b=Math.max(y,z),key=a+','+b;edges.set(key,(edges.get(key)||0)+1)}
    if(nFaces===0){singularLinkVertices++;continue}
    const degree=new Map(),adj=new Map();for(const y of neighbors){degree.set(y,0);adj.set(y,new Set())}
    for(const [pair,count] of edges){const [a,b]=pair.split(',').map(Number);degree.set(a,degree.get(a)+count);degree.set(b,degree.get(b)+count);adj.get(a).add(b);adj.get(b).add(a)}
    const visited=new Set(),stack=[neighbors.values().next().value];while(stack.length){const n=stack.pop();if(visited.has(n))continue;visited.add(n);for(const v of adj.get(n))stack.push(v)}
    const values=[...degree.values()],ends=values.filter(d=>d===1).length;
    if(visited.size===neighbors.size&&values.every(d=>d===2)&&edges.size===nFaces){interiorLinkVertices++;}
    else if(visited.size===neighbors.size&&ends===2&&values.every(d=>d===1||d===2)&&edges.size===nFaces){boundaryLinkVertices++;}
    else singularLinkVertices++;
  }
  return {source_triangles:faces.length,source_unique_exact_vertices:vertices.length,source_unique_exact_edges:edgeMap.size,edge_incidence_histogram:hist,boundary_edges:hist['1']||0,two_face_edges:hist['2']||0,three_plus_edges:[...edgeMap.values()].filter(x=>x.uses>=3).length,raw_duplicate_triangles:duplicates,zero_area_triangles:zero,edge_winding_conflicts:windingConflicts,vertex_connected_components:components,vertex_link_interior:interiorLinkVertices,vertex_link_boundary:boundaryLinkVertices,vertex_link_singular:singularLinkVertices};
}
function parseAsciiStl(src,faceLimit=300000){
 if(src.length>50000000)throw Error('ASCII STL exceeds size limit');let text='';
 for(let p=0;p<src.length;p+=8192)text+=String.fromCharCode(...src.subarray(p,Math.min(src.length,p+8192)));
 if(!/^\s*solid\b/i.test(text)||!/\bendsolid\s+/i.test(text.slice(-200)))throw Error('ASCII STL headers missing');
 const facets=(text.match(/\bfacet\s+normal\b/g)||[]).length, ends=(text.match(/\bendfacet\b/g)||[]).length;
 const regex=/^\s*vertex\s+([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)/gm;
 const vertices=[],idMap=new Map(),tri=[],faces=[];let match;
 while((match=regex.exec(text))!==null){const v=match.slice(1,4).map(Number);if(v.some(n=>!Number.isFinite(n)))throw Error('Nonfinite ASCII STL position');const k=v.map(x=>Object.is(x,-0)?'0':x.toString()).join('/');let i=idMap.get(k);if(i===undefined){i=vertices.length;idMap.set(k,i);vertices.push(v)}tri.push(i);if(tri.length===3){faces.push(tri.splice(0,3));if(faces.length>faceLimit)throw Error('Too many ASCII STL faces')}}
 if(tri.length||faces.length!==facets||faces.length!==ends||!faces.length)throw Error('Incomplete or malformed ASCII STL facet count');
 return auditMeshVertices(vertices,faces);
}
if(typeof module!=='undefined'&&module.exports){module.exports.sha256Hex=sha256Hex;module.exports.parseAsciiStl=parseAsciiStl;module.exports.auditMeshVertices=auditMeshVertices;}
