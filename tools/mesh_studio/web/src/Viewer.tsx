import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkCellPicker from '@kitware/vtk.js/Rendering/Core/CellPicker';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import vtkCoordinate from '@kitware/vtk.js/Rendering/Core/Coordinate';
import type { MeshGeometry, Space } from './contracts';
import type { CameraPose } from './camera';
import type { PickObservation, ScriptedOrbitObservation } from './performanceProbe';
import { summarizeScriptedOrbit } from './performanceProbe';
import { isCameraPose } from './camera';
import { asVtkCells, vtkPointBuffer } from './geometry';
import { buildUvSpatialIndex } from './uvSpatialIndex';
import { buildSyntheticXyzRayPicker } from './xyzSyntheticRayPicker';
import { meshCellKind, meshFaceCorners, meshFaceIds, meshPointAt } from './meshAccess';

interface ViewerProps {
  space: Space;
  modelId: string;
  geometry: MeshGeometry;
  showTri: boolean;
  showQuad: boolean;
  edges: boolean;
  selectedId: number | null;
  onSelect: (faceId: number | null) => void;
  onRendered?: () => void;
  onPickMeasured?: (observation: PickObservation) => void;
  pickingMode?: 'auto' | 'native';
}

export interface ViewerHandle {
  snapshotCamera(): CameraPose | null;
  restoreCamera(pose: CameraPose): boolean;
  resetCamera(): void;
  probeOrbit(frames: number): Promise<ScriptedOrbitObservation | null>;
}

type GRW = ReturnType<typeof vtkGenericRenderWindow.newInstance>;
type Actor = ReturnType<typeof vtkActor.newInstance>;

export const Viewer = forwardRef<ViewerHandle, ViewerProps>(function Viewer({
  space, geometry, showTri, showQuad, edges, selectedId, onSelect, onRendered, onPickMeasured, pickingMode = 'auto',
}, ref) {
  const container = useRef<HTMLDivElement>(null);
  const renderRef = useRef<GRW | null>(null);
  const actorRef = useRef<Actor | null>(null);
  const dataRef = useRef<ReturnType<typeof vtkPolyData.newInstance> | null>(null);
  const overlayRef = useRef<Actor | null>(null);
  const sourceIds = useRef<number[] | Uint32Array>([]);
  const onSelectRef = useRef(onSelect);
  const visibleRef = useRef({ showTri, showQuad, edges });
  const selectedRef = useRef(selectedId);
  const initializedRef = useRef(false);
  const firstFrameReported = useRef(false);
  const onRenderedRef = useRef(onRendered);
  onRenderedRef.current = onRendered;
  const onPickMeasuredRef = useRef(onPickMeasured);
  onPickMeasuredRef.current = onPickMeasured;
  const pickingModeRef = useRef(pickingMode);
  pickingModeRef.current = pickingMode;
  const updateOverlay = useRef<() => void>(() => {});
  onSelectRef.current = onSelect;
  visibleRef.current = { showTri, showQuad, edges };
  selectedRef.current = selectedId;

  function resetCamera() {
    const grw = renderRef.current;
    if (!grw) return;
    const renderer = grw.getRenderer();
    const camera = renderer.getActiveCamera();
    if (space === 'uv') {
      camera.setParallelProjection(true);
      camera.setPosition(0.5, 0.5, 4);
      camera.setFocalPoint(0.5, 0.5, 0);
      camera.setViewUp(0, 1, 0);
    } else {
      const positions = vtkPointBuffer(geometry);
      const minima = [Infinity, Infinity, Infinity];
      const maxima = [-Infinity, -Infinity, -Infinity];
      for (let offset = 0; offset < positions.length; offset += 3) {
        for (let i = 0; i < 3; i += 1) {
          minima[i] = Math.min(minima[i], positions[offset + i]);
          maxima[i] = Math.max(maxima[i], positions[offset + i]);
        }
      }
      const center = minima.map((v, i) => (v + maxima[i]) / 2);
      const diag = Math.max(Math.hypot(...maxima.map((v, i) => v - minima[i])), 1e-3);
      camera.setParallelProjection(false);
      camera.setFocalPoint(center[0], center[1], center[2]);
      camera.setPosition(center[0] + diag, center[1] - 1.3 * diag, center[2] + diag);
      camera.setViewUp(0, 0, 1);
    }
    renderer.resetCamera();
    grw.getRenderWindow().render();
  }

  useImperativeHandle(ref, () => ({
    snapshotCamera() {
      if (!renderRef.current) return null;
      const camera = renderRef.current.getRenderer().getActiveCamera();
      return {
        position: [...camera.getPosition()] as [number, number, number],
        focal_point: [...camera.getFocalPoint()] as [number, number, number],
        view_up: [...camera.getViewUp()] as [number, number, number],
        parallel_scale: camera.getParallelScale(),
        parallel: camera.getParallelProjection(),
      };
    },
    restoreCamera(pose: CameraPose) {
      if (!isCameraPose(pose) || !renderRef.current) return false;
      const camera = renderRef.current.getRenderer().getActiveCamera();
      camera.setPosition(...pose.position);
      camera.setFocalPoint(...pose.focal_point);
      camera.setViewUp(...pose.view_up);
      camera.setParallelScale(pose.parallel_scale);
      camera.setParallelProjection(pose.parallel);
      renderRef.current.getRenderWindow().render();
      return true;
    },
    resetCamera,
    async probeOrbit(frames: number): Promise<ScriptedOrbitObservation | null> {
      const grw = renderRef.current;
      if (!grw || !initializedRef.current || !Number.isSafeInteger(frames) ||
          frames < 8 || frames > 120) return null;
      const camera = grw.getRenderer().getActiveCamera();
      const saved = {
        position: [...camera.getPosition()] as [number, number, number],
        focal_point: [...camera.getFocalPoint()] as [number, number, number],
        view_up: [...camera.getViewUp()] as [number, number, number],
        scale: camera.getParallelScale(),
        parallel: camera.getParallelProjection(),
      };
      const intervals: number[] = [];
      const started = performance.now();
      try {
        for (let i = 0; i < frames; i += 1) {
          const frameStarted = performance.now();
          await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
          if (renderRef.current !== grw) return null;
          // This is scripted camera motion; measure RAF scheduling and VTK render dispatch.
          camera.azimuth(2.5);
          camera.orthogonalizeViewUp();
          grw.getRenderWindow().render();
          intervals.push(performance.now() - frameStarted);
        }
        return summarizeScriptedOrbit(intervals, performance.now() - started);
      } finally {
        // Do not alter the user's persisted camera as a side effect of measurement.
        if (renderRef.current === grw) {
          camera.setPosition(...saved.position);
          camera.setFocalPoint(...saved.focal_point);
          camera.setViewUp(...saved.view_up);
          camera.setParallelScale(saved.scale);
          camera.setParallelProjection(saved.parallel);
          grw.getRenderWindow().render();
        }
      }
    },
  }));

  useEffect(() => {
    const host = container.current;
    if (!host) return;
    const grw = vtkGenericRenderWindow.newInstance({ background: [0.047, 0.085, 0.126] });
    grw.setContainer(host);
    grw.resize();
    renderRef.current = grw;
    const renderer = grw.getRenderer();
    const data = vtkPolyData.newInstance();
    data.getPoints().setData(vtkPointBuffer(geometry), 3);
    const faceIndexBySource = new Map(Array.from(meshFaceIds(geometry), (id, i) => [id, i] as [number, number]));
    const uvIndex = space === 'uv' ? buildUvSpatialIndex(geometry) : null;
    // Only benchmark-owned exact structured synthetic cells qualify for this fast path.
    const syntheticXyzEligible = space === 'xyz' && geometry.quads === 500_000 &&
      geometry.source_sha256 === '0'.repeat(64) &&
      geometry.source_patch_ownership === 'NOT_APMESH_SOURCE';
    let xyzPicker: ReturnType<typeof buildSyntheticXyzRayPicker> | undefined;
    const displayCoordinate = (uvIndex || syntheticXyzEligible) ? vtkCoordinate.newInstance() : null;
    displayCoordinate?.setCoordinateSystemToDisplay();
    dataRef.current = data;
    const mapper = vtkMapper.newInstance();
    mapper.setInputData(data);
    mapper.setScalarVisibility(true);
    mapper.setScalarModeToUseCellData();
    mapper.setColorModeToDirectScalars();
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setEdgeColor(0.08, 0.16, 0.22);
    actor.getProperty().setLineWidth(1);
    actorRef.current = actor;
    renderer.addActor(actor);

    // Overlay uses only the selected cell corners, not a duplicate entire mesh.
    updateOverlay.current = () => {
      if (overlayRef.current) {
        renderer.removeActor(overlayRef.current);
        overlayRef.current.delete();
      }
      overlayRef.current = null;
      const sourceId = selectedRef.current;
      const index = faceIndexBySource.get(sourceId ?? -1) ?? -1;
      if (sourceId === null || index < 0 ||
          (meshCellKind(geometry, index) === 'triangle' && !visibleRef.current.showTri) ||
          (meshCellKind(geometry, index) === 'quad' && !visibleRef.current.showQuad)) {
        grw.getRenderWindow().render();
        return;
      }
      const face = meshFaceCorners(geometry, index);
      const highlight = vtkPolyData.newInstance();
      const coords = new Float32Array(face.flatMap((vertex) => meshPointAt(geometry, vertex)));
      highlight.getPoints().setData(coords, 3);
      highlight.getPolys().setData(new Uint32Array([face.length, ...face.map((_, i) => i)]));
      const highlightMapper = vtkMapper.newInstance();
      highlightMapper.setInputData(highlight);
      const highlightActor = vtkActor.newInstance();
      highlightActor.setMapper(highlightMapper);
      highlightActor.setPickable(false);
      highlightActor.getProperty().setRepresentationToWireframe();
      highlightActor.getProperty().setLineWidth(4);
      highlightActor.getProperty().setColor(1.0, 0.31, 0.20);
      overlayRef.current = highlightActor;
      renderer.addActor(highlightActor);
      grw.getRenderWindow().render();
    };

    const picker = vtkCellPicker.newInstance();
    picker.setPickFromList(true);
    picker.addPickList(actor);
    let pointerDown: [number, number] | null = null;
    const down = (e: PointerEvent) => { pointerDown = [e.clientX, e.clientY]; };
    const click = (event: MouseEvent) => {
      if (pointerDown && Math.hypot(event.clientX - pointerDown[0], event.clientY - pointerDown[1]) > 5) {
        pointerDown = null;
        return;
      }
      pointerDown = null;
      const rect = host.getBoundingClientRect();
      const pixelX = event.clientX - rect.left;
      const pixelY = rect.height - (event.clientY - rect.top);
      const started = performance.now();
      let sourceId: number | null = null;
      let method: 'UV_SPATIAL_INDEX' | 'VTK_CELL_PICKER' | 'SYNTHETIC_XYZ_GRID_RAY' = 'VTK_CELL_PICKER';
      let spatialCandidates: number | null = null;
      let resolved = false;
      if (space === 'uv' && uvIndex && displayCoordinate && pickingModeRef.current !== 'native') {
        try {
          // Transform a display ray onto the flat UV z=0 plane. Never guess a
          // UV chart from group color or Euclidean XYZ vertex coincidence.
          displayCoordinate.setValue([pixelX, pixelY, 0]);
          const near = [...displayCoordinate.getComputedWorldValue(renderer)];
          displayCoordinate.setValue([pixelX, pixelY, 1]);
          const far = [...displayCoordinate.getComputedWorldValue(renderer)];
          const dz = far[2] - near[2];
          const fraction = -near[2] / dz;
          if (near.every(Number.isFinite) && far.every(Number.isFinite) &&
              Math.abs(dz) > 1e-12 && fraction >= 0 && fraction <= 1) {
            const u = near[0] + fraction * (far[0] - near[0]);
            const v = near[1] + fraction * (far[1] - near[1]);
            const hit = uvIndex.pick(u, v, visibleRef.current.showTri,
              visibleRef.current.showQuad);
            if (hit.kind !== 'ambiguous') {
              sourceId = hit.kind === 'hit' ? hit.sourceFaceId : null;
              spatialCandidates = hit.testedFaces;
              method = 'UV_SPATIAL_INDEX';
              resolved = true;
            }
          }
        } catch {
          // Any unsupported projection or overlapping UV patch uses the native picker.
        }
      }
      if (!resolved && syntheticXyzEligible && displayCoordinate &&
          pickingModeRef.current !== 'native') {
        try {
          // Qualified benchmark geometry only: no real source patch/curve inference.
          if (xyzPicker === undefined) xyzPicker = buildSyntheticXyzRayPicker(geometry);
          if (xyzPicker) {
            displayCoordinate.setValue([pixelX, pixelY, 0]);
            const near = [...displayCoordinate.getComputedWorldValue(renderer)];
            displayCoordinate.setValue([pixelX, pixelY, 1]);
            const far = [...displayCoordinate.getComputedWorldValue(renderer)];
            const hit = xyzPicker.pick(near, far, visibleRef.current.showQuad);
            if (hit.kind === 'hit') {
              sourceId = hit.sourceFaceId;
              spatialCandidates = hit.testedFaces;
              method = 'SYNTHETIC_XYZ_GRID_RAY';
              resolved = true;
            }
            // Ambiguous edges, unknown geometry and misses use VTK fallback.
          }
        } catch {
          // The general VTK picker remains authoritative on unsupported conditions.
        }
      }
      if (!resolved) {
        picker.pick([pixelX, pixelY, 0], renderer);
        const picked = picker.getCellId();
        sourceId = picked >= 0 ? sourceIds.current[picked] ?? null : null;
      }
      const pickerMs = performance.now() - started;
      onSelectRef.current(sourceId);
      onPickMeasuredRef.current?.({
        space, source_face_id: sourceId, hit: sourceId !== null,
        picker_wall_ms: Math.round(pickerMs * 1000) / 1000,
        method, spatial_candidates_tested: spatialCandidates,
        scope: method === 'UV_SPATIAL_INDEX'
          ? 'UV_PLANE_SPATIAL_QUERY_NOT_END_TO_END_UI_LATENCY'
          : method === 'SYNTHETIC_XYZ_GRID_RAY'
          ? 'SYNTHETIC_XYZ_GRID_RAY_QUERY_NOT_END_TO_END_UI_LATENCY'
          : 'VTK_CELL_PICKER_SYNCHRONOUS_CALL_NOT_END_TO_END_UI_LATENCY',
      });
    };
    host.addEventListener('pointerdown', down);
    host.addEventListener('click', click);
    const observer = new ResizeObserver(() => grw.resize());
    observer.observe(host);
    initializedRef.current = false;
    firstFrameReported.current = false;
    return () => {
      observer.disconnect();
      host.removeEventListener('pointerdown', down);
      host.removeEventListener('click', click);
      if (overlayRef.current) {
        renderer.removeActor(overlayRef.current);
        overlayRef.current.delete();
      }
      overlayRef.current = null;
      updateOverlay.current = () => {};
      renderRef.current = null;
      actorRef.current = null;
      dataRef.current = null;
      sourceIds.current = [];
      picker.delete();
      displayCoordinate?.delete();
      grw.delete();
    };
    // Recreate the GL context only if the actual source mesh or space changes.
  }, [geometry, space]);

  useEffect(() => {
    const grw = renderRef.current;
    const data = dataRef.current;
    const actor = actorRef.current;
    if (!grw || !data || !actor) return;
    const mesh = asVtkCells(geometry, showTri, showQuad);
    sourceIds.current = mesh.sourceIds;
    data.getPolys().setData(mesh.polys);
    data.getCellData().setScalars(vtkDataArray.newInstance({
      name: 'elementTypeColor', values: mesh.colorBytes, numberOfComponents: 4,
    }));
    data.modified();
    actor.getProperty().setEdgeVisibility(edges);
    if (!initializedRef.current) {
      resetCamera();
      initializedRef.current = true;
    }
    updateOverlay.current();
    if (!firstFrameReported.current) {
      firstFrameReported.current = true;
      onRenderedRef.current?.();
    }
    // Replacing cell data never resets the active camera or renderer context.
  }, [geometry, showTri, showQuad, edges]);

  useEffect(() => { updateOverlay.current(); }, [selectedId]);

  return (
    <section className="view-pane" aria-label={`Vista ${space.toUpperCase()}`}>
      <div className="view-heading">
        <div><span className="view-space">{space === 'uv' ? '02' : '01'}</span>
          <strong>{space === 'xyz' ? 'Espaço físico' : 'Domínio paramétrico'}</strong></div>
        <span className="view-tag">{space.toUpperCase()}</span>
      </div>
      <div ref={container} className="vtk-canvas" data-testid={`viewport-${space}`}
        data-selected-source-face={selectedId ?? ''} />
      <div className="view-footer">
        {space === 'xyz' ? 'Arraste para orbitar · role para ampliar' : 'A mesma face, na parametrização UV'}
        {selectedId !== null && <span className="selected-face-label" data-testid={`selected-${space}`}>Face #{selectedId}</span>}
      </div>
    </section>
  );
});
