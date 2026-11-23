import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';

const expectedBase = 'http://127.0.0.1:8765';

test('V5.11 real P1 uses compiled immutable same-origin files without Vite HMR/WebSockets',
  async ({ page }) => {
    test.setTimeout(120_000);
    expect(process.env.APMESH_V511_STATIC_BASE_URL).toBe(expectedBase);
    const websockets: string[] = [];
    const outside: string[] = [];
    const loadedAssets: string[] = [];
    page.on('websocket', socket => websockets.push(socket.url()));
    page.on('request', request => {
      const url = new URL(request.url());
      if (!['127.0.0.1'].includes(url.hostname)) outside.push(request.url());
    });
    page.on('response', response => {
      if (response.url().includes('/assets/')) loadedAssets.push(response.url());
    });
    const index = await page.request.get('/');
    expect(index.status()).toBe(200);
    expect(index.headers()['x-content-type-options']).toBe('nosniff');
    expect(index.headers()['x-frame-options']).toBe('DENY');
    expect(index.headers()['cross-origin-resource-policy']).toBe('same-origin');
    expect(index.headers()['cache-control']).toBe('no-store');
    const source = await index.text();
    expect(source).toContain('/assets/');
    expect(source).not.toContain('/@vite/client');
    expect(source).not.toContain('http://127.0.0.1:5173');
    await page.goto('/');
    await expect(page.locator('.main-status')).toHaveText('Dados verificados');
    await expect(page.getByTestId('viewport-xyz').locator('canvas').first())
      .toBeVisible();
    await expect(page.getByTestId('viewport-uv').locator('canvas').first())
      .toBeVisible();
    expect(loadedAssets.length).toBeGreaterThan(0);
    expect(websockets).toEqual([]);
    expect(outside).toEqual([]);
    const vector = await page.request.get('/api/v1/models/p1/publication.svg');
    expect(vector.status()).toBe(200);
    const bytes = await vector.body();
    const digest = createHash('sha256').update(bytes).digest('hex');
    expect(digest).toBe(
      'c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe');
    expect(vector.headers()['x-vector-figure-sha256']).toBe(digest);
    const health = await page.request.get('/api/v1/health',
      { headers: { Origin: expectedBase } });
    expect(health.status()).toBe(200);
    expect(health.headers()['access-control-allow-origin']).toBe(expectedBase);
    console.log('V511_NO_VITE_HMR_REAL_SOURCE=' + JSON.stringify({
      base: expectedBase, assets_loaded: loadedAssets.length,
      websockets: websockets.length, external_requests: outside.length,
      original_source_p1_svg_sha256: digest,
      research_only: true,
    }));
  });

test('V5.11 built source uses only inventoried static files and rejects dev/HMR, foreign origin and writes',
  async ({ page }) => {
    test.setTimeout(120_000);
    expect(process.env.APMESH_V511_STATIC_BASE_URL).toBe(expectedBase);
    for (const request of ['/src/main.tsx', '/@vite/client',
                           '/node_modules/vite/dist/client/client.mjs',
                           '/.apmesh-local-review-inventory.json']) {
      const response = await page.request.get(request);
      expect(response.status(), request).toBe(404);
      expect(response.headers()['cache-control']).toBe('no-store');
    }
    const invalidOrigin = await page.request.get('/api/v1/health',
      { headers: { Origin: 'http://127.0.0.1:5173' } });
    expect(invalidOrigin.status()).toBe(403);
    const invalidSite = await page.request.get('/',
      { headers: { 'Sec-Fetch-Site': 'cross-site' } });
    expect(invalidSite.status()).toBe(403);
    const invalidPost = await page.request.post('/api/v1/health');
    expect(invalidPost.status()).toBe(405);
    const staticPost = await page.request.post('/');
    expect(staticPost.status()).toBe(405);

    const head = await page.request.head('/');
    expect(head.status()).toBe(200);
    expect(head.headers()['content-type']).toContain('text/html');
    expect((await head.body()).length).toBe(0);
    await page.goto('/bench.html');
    await expect(page.getByTestId('benchmark-cells')).toBeVisible();
    console.log('V511_STATIC_SOURCE_EXCLUSION_GATES=PASS');
  });
