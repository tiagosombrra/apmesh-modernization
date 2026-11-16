/** Fail-closed operator entry for the physical-desktop-only R2.7.7 probe. */
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

if(process.env.CI) {
  process.stderr.write('R277_REFUSED: hosted CI cannot qualify a physical desktop GPU.\n');
  process.exit(2);
}
if(process.env.APMESH_R277_PHYSICAL_DESKTOP!=='I_CONFIRM_PHYSICAL_WORKSTATION') {
  process.stderr.write('R277_REFUSED: confirm a local physical workstation explicitly.\n');
  process.exit(2);
}
for(const key of ['APMESH_R277_GPU_MODEL','APMESH_R277_GPU_DRIVER','APMESH_R277_DISPLAY_REFRESH_HZ']){
  if(!(process.env[key]||'').trim()) {
    process.stderr.write('R277_REFUSED: missing '+key+' operator evidence.\n');
    process.exit(2);
  }
}
const hz=Number(process.env.APMESH_R277_DISPLAY_REFRESH_HZ);
if(!Number.isFinite(hz)||hz<30||hz>500){
  process.stderr.write('R277_REFUSED: invalid display refresh frequency.\n');
  process.exit(2);
}
const cli=resolve('node_modules','@playwright','test','cli.js');
if(!existsSync(cli)){
  process.stderr.write('R277_REFUSED: run npm install in tools/mesh_studio/web.\n');
  process.exit(2);
}
const extra=process.argv.slice(2);
if(extra.some(x=>x==='--headless'||x==='--project=headless')){
  process.stderr.write('R277_REFUSED: this protocol requires headed Chromium.\n');
  process.exit(2);
}
const command=[
  cli,'test','--config=playwright.r277.config.ts','--headed',...extra,
];
const result=spawnSync(process.execPath,command,{
  stdio:'inherit',
  env:process.env,
  cwd:process.cwd(),
});
if(result.error)throw result.error;
process.exit(result.status??1);
