import {expect,test} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';

const P1_SHA='cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0';

test('R2.7.7 CI capability instrumentation is explicitly not a physical GPU qualification',
  async({page},info)=>{
    await page.goto('/');
    const host=page.getByTestId('viewport-xyz');
    await expect(host.locator('canvas').first()).toBeVisible();
    await expect(page.locator('.model-foot code')).toHaveAttribute('title',P1_SHA);
    // No experimental selector is activated by default.
    expect(await host.getAttribute('data-main-bvh-ready')).toBe('false');
    expect(await host.getAttribute('data-bvh-ready')).toBeNull();
    const probe=await page.evaluate(async ()=>{
      const {captureR277BrowserEnvironment,r277Distribution,
        r277SoftwareRendererSuspected}=await import('/src/r277Probe.ts');
      const env=captureR277BrowserEnvironment();
      return{
        env,
        fixedNearestRank:r277Distribution([.2,.1,2,.3,.4]),
        softwareKnown:r277SoftwareRendererSuspected('ANGLE (SwiftShader Device)'),
        softwareUnknown:r277SoftwareRendererSuspected(null),
      };
    });
    expect(probe.env).toMatchObject({
      schema:'apmesh.meshstudio.r277.browser_capabilities.v1',
      scope:'BROWSER_REPORTED_GL_AND_JS_ESTIMATES_NOT_CERTIFIED_PHYSICAL_GPU_OR_RSS',
      totalProcessRssBytes:null,workerRssBytes:null,gpuVramBytes:null,
      userAgentSpecificMemoryBytes:null,
    });
    expect(probe.env.browserUserAgent.length).toBeGreaterThan(0);
    expect(probe.env.devicePixelRatio).toBeGreaterThan(0);
    expect(probe.env.viewportCSS.width).toBeGreaterThan(0);
    expect(probe.fixedNearestRank).toMatchObject({n:5,p50_ms:.3,p95_ms:2});
    expect(probe.softwareKnown).toBe(true);
    expect(probe.softwareUnknown).toBeNull();
    // A reported GPU name does not verify that a physical display is attached.
    const receipt={
      schema:'apmesh.meshstudio.r277.ci_environment_preflight.v1',
      source_sha256:P1_SHA,
      testClassification:'CI_CAPABILITY_PROBE_NOT_HARDWARE_GPU_QUALIFICATION',
      physicalDesktopCertified:false,
      gpuPresentedFrameMeasured:false,
      independentGPUVramMeasured:false,
      browserProbe:probe.env,
    };
    await mkdir('test-results',{recursive:true});
    const json=JSON.stringify(receipt,null,2)+'\n';
    await writeFile('test-results/r277-ci-capability-preflight.json',json,'utf8');
    await info.attach('r277-ci-capability-preflight.json',{
      body:Buffer.from(json),contentType:'application/json',
    });
    console.log('R277_CI_CAPABILITIES='+JSON.stringify({
      webgl:probe.env.webgl.available,
      renderer:probe.env.webgl.unmaskedRenderer||probe.env.webgl.renderer,
      softwareSuspected:probe.env.webgl.softwareSuspected,
      machineQualified:false,
      gpuPresentQualified:false,
    }));
  });

test('R2.7.7 local runner refuses unattended CI and missing physical attestation',()=>{
  const script=resolve('scripts/run-r277-desktop.mjs');
  const blockedCI=spawnSync(process.execPath,[script],{
    encoding:'utf8',timeout:10_000,
    env:{...process.env,CI:'true',APMESH_R277_PHYSICAL_DESKTOP:'I_CONFIRM_PHYSICAL_WORKSTATION',
      APMESH_R277_GPU_MODEL:'test',APMESH_R277_GPU_DRIVER:'test',
      APMESH_R277_DISPLAY_REFRESH_HZ:'60'},
  });
  expect(blockedCI.status).toBe(2);
  expect(blockedCI.stderr).toContain('hosted CI cannot qualify');
  const blockedNoAttestation=spawnSync(process.execPath,[script],{
    encoding:'utf8',timeout:10_000,
    env:{...process.env,CI:'',APMESH_R277_PHYSICAL_DESKTOP:''},
  });
  expect(blockedNoAttestation.status).toBe(2);
  expect(blockedNoAttestation.stderr).toContain('confirm a local physical workstation');
});
