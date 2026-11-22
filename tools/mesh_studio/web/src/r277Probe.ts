/** Browser capability snapshot; no claim of GPU scanout, RSS, or scientific geometry. */
export interface R277BrowserEnvironment {
  schema: 'apmesh.meshstudio.r277.browser_capabilities.v1';
  browserUserAgent: string;
  browserPlatform: string;
  hardwareConcurrency: number | null;
  deviceMemoryGiBBucket: number | null;
  devicePixelRatio: number;
  viewportCSS: {width:number;height:number};
  documentVisibility: string;
  documentHasFocus: boolean;
  webgl: {
    available: boolean;
    version: string | null;
    vendor: string | null;
    renderer: string | null;
    unmaskedRenderer: string | null;
    unmaskedVendor: string | null;
    softwareSuspected: boolean | null;
    debugRendererExtension: boolean;
  };
  jsHeapEstimateBytes: number | null;
  userAgentSpecificMemoryBytes: null;
  totalProcessRssBytes: null;
  workerRssBytes: null;
  gpuVramBytes: null;
  scope: 'BROWSER_REPORTED_GL_AND_JS_ESTIMATES_NOT_CERTIFIED_PHYSICAL_GPU_OR_RSS';
}

/** Detect obvious software renderers, but never certify a physical GPU from a name alone. */
export function r277SoftwareRendererSuspected(renderer:string | null): boolean | null {
  if(renderer === null)return null;
  return /swiftshader|llvmpipe|softpipe|software rasterizer|microsoft basic render|lavapipe/i
    .test(renderer);
}

/** This snapshot is diagnostic; the operator must independently attest the GPU. */
export function captureR277BrowserEnvironment(): R277BrowserEnvironment {
  const canvas=document.createElement('canvas');
  const gl=(canvas.getContext('webgl2') as WebGL2RenderingContext | null) ||
    (canvas.getContext('webgl') as WebGLRenderingContext | null);
  const debug=gl?.getExtension('WEBGL_debug_renderer_info');
  const get=(name:number):string|null=>{
    if(!gl)return null;
    try {const raw=gl.getParameter(name);return raw==null?null:String(raw);}
    catch{return null;}
  };
  const unmaskedRenderer=debug ? get(debug.UNMASKED_RENDERER_WEBGL):null;
  const unmaskedVendor=debug ? get(debug.UNMASKED_VENDOR_WEBGL):null;
  const memory=(performance as Performance & {memory?:{usedJSHeapSize?:number}}).memory;
  const estimated=memory?.usedJSHeapSize;
  const browserMemory=(navigator as Navigator & {deviceMemory?:number}).deviceMemory;
  const environment:R277BrowserEnvironment={
    schema:'apmesh.meshstudio.r277.browser_capabilities.v1',
    browserUserAgent:navigator.userAgent,
    browserPlatform:navigator.platform,
    hardwareConcurrency:Number.isSafeInteger(navigator.hardwareConcurrency)&&
      navigator.hardwareConcurrency>0?navigator.hardwareConcurrency:null,
    deviceMemoryGiBBucket:typeof browserMemory==='number'&&Number.isFinite(browserMemory)&&
      browserMemory>0?browserMemory:null,
    devicePixelRatio:window.devicePixelRatio,
    viewportCSS:{width:innerWidth,height:innerHeight},
    documentVisibility:document.visibilityState,
    documentHasFocus:document.hasFocus(),
    webgl:{
      available:gl!==null,version:gl?get(gl.VERSION):null,
      vendor:gl?get(gl.VENDOR):null,
      renderer:gl?get(gl.RENDERER):null,
      unmaskedRenderer,unmaskedVendor,
      softwareSuspected:r277SoftwareRendererSuspected(unmaskedRenderer|| (gl?get(gl.RENDERER):null)),
      debugRendererExtension:Boolean(debug),
    },
    jsHeapEstimateBytes:typeof estimated==='number'&&
      Number.isFinite(estimated)&&estimated>=0?estimated:null,
    // These fields are deliberately null even if a coarse Chromium estimate exists.
    userAgentSpecificMemoryBytes:null,
    totalProcessRssBytes:null,workerRssBytes:null,gpuVramBytes:null,
    scope:'BROWSER_REPORTED_GL_AND_JS_ESTIMATES_NOT_CERTIFIED_PHYSICAL_GPU_OR_RSS',
  };
  const lose=gl?.getExtension('WEBGL_lose_context');
  lose?.loseContext();
  return environment;
}

/** Validate empirical timings without discarding slow samples. */
export function r277Distribution(values:readonly number[]){
  if(values.length<2||values.some(x=>!Number.isFinite(x)||x<0)){
    throw new Error('R277_invalid_distribution');
  }
  const sorted=[...values].sort((a,b)=>a-b);
  const nearest=(p:number)=>Math.round(sorted[Math.ceil(sorted.length*p)-1]*1000)/1000;
  return {n:sorted.length,p50_ms:nearest(.5),p95_ms:nearest(.95),
    min_ms:Math.round(sorted[0]*1000)/1000,
    max_ms:Math.round(sorted[sorted.length-1]*1000)/1000};
}
