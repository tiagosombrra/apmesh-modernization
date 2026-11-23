/**
 * Capture actual Rolldown output-module provenance and Vite 8 license metadata.
 *
 * This runs a separate diagnostic production build, never modifies the seven
 * server-distributed V5.11 assets and never declares license clearance.
 */
import { build } from 'vite';
import { createHash } from 'node:crypto';
import {
  copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync,
  writeFileSync,
} from 'node:fs';
import { join, relative, resolve, sep } from 'node:path';

const WEB = process.cwd();
const ROOT = resolve(WEB, '../../..');
const DIST = join(WEB, 'dist');
const DIAGNOSTIC = join(ROOT, 'build/v511-bundle-diagnostic');
const EVIDENCE = join(ROOT, 'build/v511-bundle-evidence');
const SOURCE_LOCK = join(WEB, 'package-lock.json');
const BUILT_IN_LICENSE = join(DIAGNOSTIC, '.vite/license.json');
const ORIGINAL_INVENTORY = join(DIST, '.apmesh-local-review-inventory.json');
const STATIC_INVENTORY_SHA256 =
  'ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5';
const GRAPH_SCHEMA = 'apmesh.meshstudio.v511.rolldown_rendered_source_graph.v1';
const PARITY_SCHEMA = 'apmesh.meshstudio.v511.diagnostic_bundle_parity.v1';

function requireCondition(condition, reason) {
  if (!condition) throw new Error('v511_bundle_attribution_' + reason);
}

function digest(data) {
  return createHash('sha256').update(data).digest('hex');
}

function normalizeId(input) {
  return input.replaceAll('\\', '/').replaceAll(WEB.replaceAll('\\', '/'), '<web>');
}

function lockPackageId(moduleId, entries) {
  // Prefer the longest matching nested node_modules package path.
  const path = moduleId.replaceAll('\\', '/');
  const index = path.indexOf('/node_modules/');
  if (index < 0) return null;
  const suffix = path.slice(index + 1).split('?')[0];
  const packagePath = entries.find((candidate) =>
    suffix === candidate || suffix.startsWith(candidate + '/'));
  return { path: packagePath ?? null, source_path: normalizeId(suffix) };
}

function moduleSource(id, entries) {
  const normalized = normalizeId(id);
  const owner = lockPackageId(id, entries);
  if (id.includes('\0')) {
    return { kind: 'virtual_or_generated', module: normalized,
      source_package: owner?.path ?? null };
  }
  if (owner) {
    return { kind: owner.path ? 'npm_source' : 'unmatched_npm_source',
      module: normalized, source_package: owner.path };
  }
  if (normalized.startsWith('<web>/') || normalized === '<web>') {
    return { kind: 'application_source', module: normalized, source_package: null };
  }
  return { kind: 'unclassified_module', module: normalized, source_package: null };
}

function walk(root) {
  if (!existsSync(root)) return [];
  const found = [];
  const descend = (folder) => {
    for (const dirent of readdirSync(folder, { withFileTypes: true })) {
      const path = join(folder, dirent.name);
      requireCondition(!dirent.isSymbolicLink(), 'diagnostic_symlink');
      if (dirent.isDirectory()) descend(path);
      else if (dirent.isFile()) found.push(relative(root, path).split(sep).join('/'));
      else throw new Error('v511_bundle_attribution_unknown_diagnostic_entry');
    }
  };
  descend(root);
  return found.sort();
}

async function main() {
  requireCondition(existsSync(ORIGINAL_INVENTORY), 'missing_certified_build');
  const originalBytes = readFileSync(ORIGINAL_INVENTORY);
  requireCondition(digest(originalBytes) === STATIC_INVENTORY_SHA256,
    'original_build_inventory_not_source_certified');
  const original = JSON.parse(originalBytes.toString('utf8'));
  requireCondition(original.static_asset_count === 7 &&
    original.npm_source_lock_sha256 === digest(readFileSync(SOURCE_LOCK)),
    'original_build_asset_count_or_npm_lock_drift');
  const lock = JSON.parse(readFileSync(SOURCE_LOCK, 'utf8'));
  const paths = Object.keys(lock.packages).filter(Boolean)
    .sort((a, b) => b.length - a.length || a.localeCompare(b));
  requireCondition(paths.length === 141, 'npm_lock_source_count_changed');
  rmSync(DIAGNOSTIC, { recursive: true, force: true });
  mkdirSync(EVIDENCE, { recursive: true });

  const chunks = [];
  const sourcePlugin = {
    name: 'mesh-studio-source-only-rolldown-attribution',
    apply: 'build',
    enforce: 'post',
    generateBundle(_options, bundle) {
      for (const item of Object.values(bundle)) {
        if (item.type !== 'chunk') continue;
        const sourceModules = Object.entries(item.modules ?? {}).map(([id, data]) => ({
          ...moduleSource(id, paths),
          rendered_length: typeof data.renderedLength === 'number'
            ? data.renderedLength : null,
          original_length: typeof data.originalLength === 'number'
            ? data.originalLength : null,
        }));
        sourceModules.sort((a, b) => a.module.localeCompare(b.module));
        chunks.push({
          file: item.fileName,
          entrypoint: Boolean(item.isEntry),
          imports: [...item.imports].sort(),
          dynamic_imports: [...item.dynamicImports].sort(),
          css_assets: [...(item.viteMetadata?.importedCss ?? [])].sort(),
          other_assets: [...(item.viteMetadata?.importedAssets ?? [])].sort(),
          modules: sourceModules,
        });
      }
    },
  };

  // Vite 8 owns both the output module graph and the 'build.license' inventory.
  // The outDir is deliberately isolated so no diagnostic NOTICE enters the
  // seven-file read-only static server's allowlist.
  await build({
    root: WEB,
    configFile: join(WEB, 'vite.config.ts'),
    plugins: [sourcePlugin],
    build: {
      outDir: DIAGNOSTIC,
      emptyOutDir: true,
      license: { fileName: '.vite/license.json' },
    },
  });
  requireCondition(existsSync(BUILT_IN_LICENSE), 'vite_license_json_not_emitted');
  const licenseBytes = readFileSync(BUILT_IN_LICENSE);
  const licenseRows = JSON.parse(licenseBytes.toString('utf8'));
  requireCondition(Array.isArray(licenseRows), 'vite_license_json_not_array');
  requireCondition(chunks.length > 0, 'rolldown_chunk_graph_missing');
  chunks.sort((a, b) => a.file.localeCompare(b.file));

  const generated = walk(DIAGNOSTIC);
  const extra = generated.filter((p) => p !== '.vite/license.json');
  const originals = Object.keys(original.static_assets).sort();
  requireCondition(JSON.stringify(extra) === JSON.stringify(originals),
    'diagnostic_added_or_missing_built_asset');
  const parity = {};
  for (const name of originals) {
    const path = join(DIAGNOSTIC, ...name.split('/'));
    const raw = readFileSync(path);
    // This only normalizes Vite-emitted HTML, mirroring the V5.11
    // production inventory procedure. JS/CSS/source bytes are untouched.
    const data = name.endsWith('.html')
      ? Buffer.from(raw.toString('utf8').replaceAll('\r\r\n', '\n')
        .replaceAll('\r\n', '\n'), 'utf8') : raw;
    const exact = original.static_assets[name];
    requireCondition(data.length === exact.size && digest(data) === exact.sha256,
      'diagnostic_build_asset_not_byte_identical:' + name);
    parity[name] = { size: data.length, sha256: digest(data) };
  }
  const chunkFiles = chunks.map((c) => c.file);
  requireCondition(chunkFiles.every((p) => p.endsWith('.js') && originals.includes(p)),
    'chunk_missing_from_certified_static_files');
  const referencedCss = [...new Set(chunks.flatMap((c) => c.css_assets))].sort();
  requireCondition(referencedCss.every((p) => originals.includes(p)),
    'chunk_css_missing_from_certified_static_files');

  const sourcePackages = [...new Set(chunks.flatMap((c) => c.modules
    .filter((m) => m.source_package !== null).map((m) => m.source_package)))].sort();
  const unresolvedModules = chunks.flatMap((c) => c.modules.filter((m) =>
    m.kind === 'unclassified_module' || m.kind === 'unmatched_npm_source')
    .map((m) => ({ chunk: c.file, ...m })));
  const originalGraph = {
    schema: GRAPH_SCHEMA,
    classification: 'BUNDLER_OBSERVED_MODULE_GRAPH_NOT_BINARY_LICENSE_APPROVAL',
    npm_source_lock_sha256: original.npm_source_lock_sha256,
    original_static_inventory_sha256: STATIC_INVENTORY_SHA256,
    vite_license_sha256: digest(licenseBytes),
    diagnostic_cpp_recompiled: false,
    bundled_packages_claimed_independent_of_vite: false,
    css_transitive_license_closure_qualified: false,
    excluded_development_dependencies_not_assumed_shipped: true,
    detected_npm_source_paths: sourcePackages,
    unresolved_module_ids: unresolvedModules,
    chunks,
  };
  const buildParity = {
    schema: PARITY_SCHEMA,
    original_static_inventory_sha256: STATIC_INVENTORY_SHA256,
    npm_source_lock_sha256: original.npm_source_lock_sha256,
    compiled_assets_byte_identical: true,
    exact_static_files: parity,
    chunk_js_files: chunkFiles,
    chunk_referenced_css: referencedCss,
    vite_license_sha256: digest(licenseBytes),
    vite_license_rows: licenseRows.length,
    diagnostic_license_generated_outside_served_static_tree: true,
    physical_review_approved: false,
    legal_distribution_approved: false,
    original_cpp_source_changed: false,
    scientific_lod_qualified: false,
  };
  copyFileSync(BUILT_IN_LICENSE, join(EVIDENCE, 'vite-bundled-licenses.json'));
  writeFileSync(join(EVIDENCE, 'rolldown-source-graph.json'),
    JSON.stringify(originalGraph, null, 2) + '\n');
  writeFileSync(join(EVIDENCE, 'diagnostic-parity.json'),
    JSON.stringify(buildParity, null, 2) + '\n');
  console.log('V511_DIAGNOSTIC_BUNDLE_SOURCE=' + JSON.stringify({
    exact_static_sha: STATIC_INVENTORY_SHA256,
    rendered_chunks: chunks.length,
    source_package_paths: sourcePackages.length,
    unresolved_modules: unresolvedModules.length,
    vite_bundled_license_rows: licenseRows.length,
    exact_original_static_assets: originals.length,
    legal_distribution_approved: false,
  }));
}

await main();
