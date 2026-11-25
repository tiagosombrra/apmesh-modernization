import { useEffect, useMemo, useRef, useState } from 'react';
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import { evaluateCurve, evaluatePatch } from './bezierSource';
import type { BezierSource, BezierCurve, Point3 } from './bezierSource';

export const PATCH_COLORS = ['#64c8d4', '#e5af72', '#a1c884', '#b79cdd', '#e58f9c', '#89a8e0'];

interface Props {
  source: BezierSource;
  curve: BezierCurve;
  parameter: number;
  visible: boolean[];
  selectedPatch: number;
  active: boolean;
}

type RenderWindow = ReturnType<typeof vtkGenericRenderWindow.newInstance>;
type Actor = ReturnType<typeof vtkActor.newInstance>;
type Resource = { delete(): void };

function rgb(hex: string): [number, number, number] {
  return [1, 3, 5].map(offset => parseInt(hex.slice(offset, offset + 2), 16) / 255) as [number, number, number];
}

/** Normalize only a display copy, before any interpolation or Float32 conversion. */
export function prepareBezierDisplaySource(source: BezierSource): BezierSource {
  const used = new Set(source.patches.flat());
  let maxAbs = 0;
  for (const id of used) {
    for (const coordinate of source.controls[id]) maxAbs = Math.max(maxAbs, Math.abs(coordinate));
  }
  const divisor = maxAbs || 1;
  const controls: Point3[] = source.controls.map((point, id) => used.has(id)
    ? point.map((coordinate) => coordinate / divisor) as Point3 : [0, 0, 0]);
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (const id of used) {
    controls[id].forEach((coordinate, axis) => {
      min[axis] = Math.min(min[axis], coordinate);
      max[axis] = Math.max(max[axis], coordinate);
    });
  }
  // Bounds are now in [-1, 1], so neither subtraction nor interpolation overflows.
  const extent = Math.max(...max.map((coordinate, axis) => coordinate - min[axis])) || 1;
  const center = min.map((coordinate, axis) => coordinate / 2 + max[axis] / 2);
  for (const id of used) {
    controls[id] = controls[id].map((coordinate, axis) => (coordinate - center[axis]) / extent) as Point3;
  }
  // Unused controls do not affect the camera or collapse a small referenced model.
  return { ...source, controls };
}

/** Display buffers are sampled previews, never native TRI or geometric evidence. */
export function BezierSourceViewer({ source, curve, parameter, visible, selectedPatch, active }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const windowRef = useRef<RenderWindow | null>(null);
  const actorsRef = useRef<Actor[]>([]);
  const [error, setError] = useState('');
  const stateRef = useRef({ visible, selectedPatch });
  stateRef.current = { visible, selectedPatch };
  const activeRef = useRef(active);
  activeRef.current = active;
  const displaySource = useMemo(() => prepareBezierDisplaySource(source), [source]);

  const resetCamera = () => {
    const grw = windowRef.current;
    if (!grw) return;
    const camera = grw.getRenderer().getActiveCamera();
    camera.setPosition(3, -5, 3);
    camera.setFocalPoint(0, 0, 0);
    camera.setViewUp(0, 0, 1);
    grw.getRenderer().resetCamera();
    if (activeRef.current && hostRef.current?.clientWidth && hostRef.current?.clientHeight) {
      grw.getRenderWindow().render();
    }
  };

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    setError('');
    const resources: Resource[] = [];
    let grw: RenderWindow | null = null;
    let resize: ResizeObserver | null = null;
    const dispose = () => {
      resize?.disconnect();
      resize = null;
      delete host.dataset.sourcePatches;
      actorsRef.current = [];
      if (windowRef.current === grw) windowRef.current = null;
      if (grw) {
        const interactor = grw.getInteractor();
        const style = interactor.getInteractorStyle();
        const renderer = grw.getRenderer();
        const renderWindow = grw.getRenderWindow();
        interactor.setEnableRender(false);
        interactor.setEnabled(false);
        renderer.getActors().forEach(actor => renderer.removeActor(actor));
        // GenericRenderWindow releases its canvas and GL view, but not these owners.
        grw.delete();
        interactor.setInteractorStyle(null);
        interactor.delete();
        style?.delete();
        renderer.getActiveCamera().delete();
        renderer.getLights().forEach(light => light.delete());
        renderer.delete();
        renderWindow.delete();
        grw = null;
      }
      resources.reverse().forEach(resource => resource.delete());
      resources.length = 0;
    };
    try {
      grw = vtkGenericRenderWindow.newInstance({ background: [0.047, 0.085, 0.126], listenWindowResize: false });
      grw.setContainer(host);
      grw.getInteractor().setEnabled(activeRef.current);
      grw.getInteractor().setEnableRender(activeRef.current);
      if (activeRef.current && host.clientWidth && host.clientHeight) grw.resize();
      windowRef.current = grw;
      const renderer = grw.getRenderer();
      const divisions = 16;
      source.patches.forEach((_patch, patchId) => {
        const points: number[] = [];
        const triangles: number[] = [];
        for (let j = 0; j <= divisions; j++) for (let i = 0; i <= divisions; i++) {
          points.push(...evaluatePatch(displaySource, patchId, i / divisions, j / divisions));
          if (i < divisions && j < divisions) {
            const a = j * (divisions + 1) + i;
            triangles.push(3, a, a + 1, a + divisions + 2,
              3, a, a + divisions + 2, a + divisions + 1);
          }
        }
        const poly = vtkPolyData.newInstance();
        resources.push(poly);
        poly.getPoints().setData(new Float32Array(points), 3);
        poly.getPolys().setData(new Uint32Array(triangles));
        const mapper = vtkMapper.newInstance();
        resources.push(mapper);
        mapper.setInputData(poly);
        mapper.setScalarVisibility(false);
        const actor = vtkActor.newInstance();
        resources.push(actor);
        actor.setMapper(mapper);
        actor.getProperty().setColor(...rgb(PATCH_COLORS[patchId % PATCH_COLORS.length]));
        actor.getProperty().setAmbient(0.45);
        actor.getProperty().setDiffuse(0.55);
        actor.getProperty().setEdgeVisibility(false);
        actor.setVisibility(stateRef.current.visible[patchId]);
        actor.getProperty().setOpacity(patchId === stateRef.current.selectedPatch ? 1 : 0.55);
        renderer.addActor(actor);
        actorsRef.current.push(actor);
      });
      resetCamera();
      host.dataset.sourcePatches = String(source.patches.length);
      resize = new ResizeObserver(() => {
        if (activeRef.current && host.clientWidth && host.clientHeight) grw?.resize();
      });
      resize.observe(host);
    } catch (reason) {
      dispose();
      setError(`3D preview unavailable: ${reason instanceof Error ? reason.message : String(reason)}`);
    }
    return dispose;
  }, [source, displaySource]);

  useEffect(() => {
    actorsRef.current.forEach((actor, patchId) => {
      actor.setVisibility(visible[patchId]);
      actor.getProperty().setOpacity(patchId === selectedPatch ? 1 : 0.55);
    });
    if (activeRef.current) windowRef.current?.getRenderWindow().render();
  }, [visible, selectedPatch]);

  useEffect(() => {
    const grw = windowRef.current;
    if (!grw) return;
    const renderer = grw.getRenderer();
    const resources: Resource[] = [];
    const actors: Actor[] = [];
    const makeActor = (points: number[], cells: number[], marker: boolean) => {
      const poly = vtkPolyData.newInstance();
      const mapper = vtkMapper.newInstance();
      const actor = vtkActor.newInstance();
      resources.push(poly, mapper, actor);
      poly.getPoints().setData(new Float32Array(points), 3);
      (marker ? poly.getVerts() : poly.getLines()).setData(new Uint32Array(cells));
      mapper.setInputData(poly);
      mapper.setScalarVisibility(false);
      actor.setMapper(mapper);
      actor.getProperty().setColor(...(marker ? [1, 0.47, 0.37] : [1, 0.86, 0.48]) as [number, number, number]);
      actor.getProperty().setLighting(false);
      actor.getProperty().setLineWidth(4);
      actor.getProperty().setPointSize(13);
      renderer.addActor(actor);
      actors.push(actor);
    };
    const dispose = () => {
      // Source replacement may have already disposed the old render window.
      if (!renderer.isDeleted()) actors.forEach(actor => renderer.removeActor(actor));
      resources.reverse().forEach(resource => resource.delete());
      resources.length = 0;
      actors.length = 0;
    };
    try {
      const points: number[] = [];
      for (let i = 0; i <= 64; i++) points.push(...evaluateCurve(displaySource, curve, i / 64));
      makeActor(points, [65, ...Array.from({ length: 65 }, (_, i) => i)], false);
      makeActor(evaluateCurve(displaySource, curve, parameter), [1, 0], true);
      if (activeRef.current) grw.getRenderWindow().render();
    } catch (reason) {
      dispose();
      setError(`Curve preview unavailable: ${reason instanceof Error ? reason.message : String(reason)}`);
    }
    return dispose;
  }, [displaySource, curve, parameter]);

  useEffect(() => {
    const grw = windowRef.current;
    const host = hostRef.current;
    if (!grw || !host) return;
    const interactor = grw.getInteractor();
    interactor.setEnableRender(active);
    interactor.setEnabled(active);
    if (active && host.clientWidth && host.clientHeight) {
      // Returning to the workspace preserves the existing camera.
      grw.resize();
    } else if (!active) {
      const style = interactor.getInteractorStyle();
      style?.endRotate(); style?.endPan(); style?.endDolly(); style?.endSpin();
      if (style) interactor.cancelAnimation(style, true);
    }
  }, [active]);

  return <div className="bezier-preview">
    <div className="bezier-preview-heading"><span>XYZ <strong>Surface preview</strong></span>
      <button type="button" onClick={resetCamera} data-testid="bezier-reset-camera">Reset view</button></div>
    {error && <p role="alert" className="error">{error}</p>}
    <div ref={hostRef} className="bezier-vtk" data-testid="bezier-viewport"
      aria-label="Interactive sampled Bézier surface preview" />
    <div className="bezier-preview-footer"><span>Drag to orbit · scroll to zoom</span>
      <span>Yellow: selected curve · coral: C(t)</span></div>
  </div>;
}
