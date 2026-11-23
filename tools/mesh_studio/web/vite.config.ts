import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';

// Dev-only same-host filter; do not treat this as production authentication.
const localResearchGuard = (): Plugin => ({
  name: 'mesh-studio-local-research-loopback-guard',
  apply: 'serve',
  configureServer(server) {
    server.middlewares.use((request, response, next) => {
      const host = request.headers.host;
      const origin = request.headers.origin;
      const site = request.headers['sec-fetch-site'];
      const isOriginAllowed = origin === undefined ||
        origin === 'http://127.0.0.1:5173';
      const isFetchSiteAllowed = site === undefined ||
        site === 'same-origin' || site === 'same-site' || site === 'none';
      const isReadOnly = request.method === 'GET' ||
        request.method === 'HEAD' || request.method === 'OPTIONS';
      if (host !== '127.0.0.1:5173' || !isOriginAllowed ||
          !isFetchSiteAllowed || !isReadOnly) {
        response.statusCode = host !== '127.0.0.1:5173' ? 400 :
          !isReadOnly ? 405 : 403;
        response.setHeader('Content-Type', 'text/plain; charset=utf-8');
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('X-Content-Type-Options', 'nosniff');
        response.end('local_research_request_rejected');
        return;
      }
      response.setHeader('X-Content-Type-Options', 'nosniff');
      response.setHeader('X-Frame-Options', 'DENY');
      response.setHeader('Referrer-Policy', 'no-referrer');
      next();
    });
  },
});

export default defineConfig({
  plugins: [localResearchGuard(), react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    // A default Vite hostname list is wider than this launcher requires.
    allowedHosts: ['127.0.0.1'],
    cors: { origin: 'http://127.0.0.1:5173' },
    proxy: {
      // The backend independently permits only Host 127.0.0.1:8765.
      '/api': { target: 'http://127.0.0.1:8765', changeOrigin: true },
    },
  },
  build: { target: 'es2022', rollupOptions: { input: { main: 'index.html', bench: 'bench.html' } } },
});
