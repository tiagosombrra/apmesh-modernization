import { useEffect, useMemo, useRef } from 'react';
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkCellPicker from '@kitware/vtk.js/Rendering/Core/CellPicker';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import type { NativeAcceptedScene } from './nativeAcceptedSceneContract';
import type { NativeSeamTrace } from './nativeSeamTrace';
import { nativeSeamActors } from './nativeSeamVtk';

type Space = 'xyz' | 'uv';

interface Props {
  scene: NativeAcceptedScene;
  space: Space;
  patchSlot: number;
  selectedFaceIndex: number | null;
  seamTrace: NativeSeamTrace | null;
  selectedSampleOrdinal: number;
  onSelectFace(index: number | null): void;
}

interface NativeDisplayBuffers {
  positions: Float32Array;
  polys: Uint32Array;
  colors: Uint8Array;
  originalFaceIndices: number[];
}

function patchColor(slot: number): [number,number,number,number] {
  // Deterministic patch presentation colors are not source ownership labels.
  const palette = [
    [92,173,194],[207,155,98],[144,176,112],[172,139,197],
    [191,114,126],[105,169,161],[209,180,92],[123,144,199],
  ];
  const p = palette[slot % palette.length];
  const scale = 0.78 + 0.06 * (Math.floor(slot / palette.length) % 4);
  return [Math.round(p[0] * scale), Math.round(p[1] * scale),
    Math.round(p[2] * scale), 255];
}

function prepareNativeDisplay(
  scene: NativeAcceptedScene, space: Space, patchSlot: number,
): NativeDisplayBuffers {
  const indices: number[] = [];
  for (let i = 0; i < scene.native_faces.length; i += 1) {
    if (space === 'xyz' || scene.native_faces[i][0] === patchSlot) indices.push(i);
  }
  const positions = new Float32Array(indices.length * 9);
  const polys = new Uint32Array(indices.length * 4);
  const colors = new Uint8Array(indices.length * 4);
  indices.forEach((index, localIndex) => {
    const face = scene.native_faces[index];
    const rgb = patchColor(face[0]);
    colors.set(rgb, localIndex * 4);
    polys.set([3, localIndex * 3, localIndex * 3 + 1,
      localIndex * 3 + 2], localIndex * 4);
    face[4].forEach((corner, cornerIndex) => {
      const base = localIndex * 9 + cornerIndex * 3;
      if (space === 'xyz') {
        positions.set([corner[1],corner[2],corner[3]],base);
      } else {
        // UV is patch-local. Never superimpose different patch UV charts.
        positions.set([corner[4],corner[5],0],base);
      }
    });
  });
  return { positions, polys, colors, originalFaceIndices: indices };
}

/**
 * One accepted TRI mesh visualized with nonwelded, per-face display corners.
 * The viewer's cell index maps to (patch_slot, element_slot, native_element_id).
 * Float32 buffers are never fed back to scientific source data.
 */
export function NativeAcceptedTriViewer({
  scene, space, patchSlot, selectedFaceIndex, seamTrace,
  selectedSampleOrdinal, onSelectFace,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const renderRef = useRef<ReturnType<typeof vtkGenericRenderWindow.newInstance> | null>(null);
  const actorRef = useRef<ReturnType<typeof vtkActor.newInstance> | null>(null);
  const overlayRef = useRef<ReturnType<typeof vtkActor.newInstance> | null>(null);
  const seamActorsRef = useRef<ReturnType<typeof vtkActor.newInstance>[]>([]);
  const onSelectRef = useRef(onSelectFace);
  onSelectRef.current = onSelectFace;
  // A patch selection changes only the XYZ seam overlay and the local UV
  // chart. Do not rebuild a 4,256-face XYZ buffer or reset the user's
  // camera whenever a different original source patch is selected.
  const displayPatch = space === 'uv' ? patchSlot : -1;
  const prepared = useMemo(() => prepareNativeDisplay(scene, space, displayPatch),
    [scene, space, displayPatch]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const setupStart = performance.now();
    const grw = vtkGenericRenderWindow.newInstance({background:[0.047,0.085,0.126]});
    grw.setContainer(host);
    grw.resize();
    renderRef.current = grw;
    const renderer = grw.getRenderer();
    const poly = vtkPolyData.newInstance();
    poly.getPoints().setData(prepared.positions, 3);
    poly.getPolys().setData(prepared.polys);
    poly.getCellData().setScalars(vtkDataArray.newInstance({
      name: 'sourcePatchDisplayColor', values: prepared.colors,
      numberOfComponents: 4,
    }));
    const mapper = vtkMapper.newInstance();
    mapper.setInputData(poly);
    mapper.setScalarVisibility(true);
    mapper.setScalarModeToUseCellData();
    mapper.setColorModeToDirectScalars();
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setEdgeVisibility(true);
    actor.getProperty().setEdgeColor(0.07,0.13,0.19);
    actor.getProperty().setLineWidth(1);
    actorRef.current = actor;
    renderer.addActor(actor);
    if (space === 'uv') {
      const camera = renderer.getActiveCamera();
      camera.setParallelProjection(true);
      camera.setPosition(0.5,0.5,3);
      camera.setFocalPoint(0.5,0.5,0);
      camera.setViewUp(0,1,0);
      camera.setParallelScale(0.7);
      renderer.resetCameraClippingRange();
    } else {
      renderer.resetCamera();
      const camera = renderer.getActiveCamera();
      camera.setViewUp(0,0,1);
      camera.azimuth(18);
      camera.elevation(12);
      camera.orthogonalizeViewUp();
      renderer.resetCameraClippingRange();
    }
    const renderStart = performance.now();
    grw.getRenderWindow().render();
    if (new URLSearchParams(window.location.search).get('nativePerf') === '1') {
      host.dataset.nativePerfVtkSetupCpuMs =
        (performance.now() - setupStart).toFixed(3);
      host.dataset.nativePerfVtkRenderCallCpuMs =
        (performance.now() - renderStart).toFixed(3);
      host.dataset.nativePerfVtkExplicitCpuTypedBytes = String(
        prepared.positions.byteLength + prepared.polys.byteLength +
        prepared.colors.byteLength);
    }
    host.dataset.nativeAcceptedFaces = String(prepared.originalFaceIndices.length);
    host.dataset.originalSourceModel = scene.model;
    host.dataset.nativeDisplayedPatchSlot = String(space === 'uv' ? patchSlot : -1);
    host.dataset.nativeAcceptedStep = String(scene.accepted_native_step);
    const picker = vtkCellPicker.newInstance();
    picker.setPickFromList(true);
    picker.addPickList(actor);
    let down: [number,number] | null = null;
    const pointerDown = (event: PointerEvent) => {
      down = [event.clientX, event.clientY];
    };
    const click = (event: MouseEvent) => {
      if (down && Math.hypot(event.clientX-down[0],event.clientY-down[1]) > 5) {
        down = null;
        return;
      }
      down = null;
      const box = host.getBoundingClientRect();
      picker.pick([event.clientX-box.left,box.height-(event.clientY-box.top),0],
        renderer);
      const localCell = picker.getCellId();
      const originalIndex = localCell >= 0
        ? prepared.originalFaceIndices[localCell] ?? null : null;
      host.dataset.lastNativeFaceIndex = originalIndex === null
        ? '' : String(originalIndex);
      onSelectRef.current(originalIndex);
    };
    host.addEventListener('pointerdown',pointerDown);
    host.addEventListener('click',click);
    const resize = new ResizeObserver(() => grw.resize());
    resize.observe(host);
    return () => {
      resize.disconnect();
      host.removeEventListener('pointerdown',pointerDown);
      host.removeEventListener('click',click);
      if (overlayRef.current) {
        renderer.removeActor(overlayRef.current);
        overlayRef.current.delete();
        overlayRef.current=null;
      }
      for (const seam of seamActorsRef.current) {
        renderer.removeActor(seam);
        seam.delete();
      }
      seamActorsRef.current=[];
      renderer.removeActor(actor);
      picker.delete();
      renderRef.current=null;
      actorRef.current=null;
      grw.delete();
    };
  }, [prepared, scene.model, scene.accepted_native_step, space]);

  useEffect(() => {
    const grw = renderRef.current;
    const host = hostRef.current;
    if (!grw || !host) return;
    const renderer = grw.getRenderer();
    const overlayStart = performance.now();
    for(const actor of seamActorsRef.current) {
      renderer.removeActor(actor);
      actor.delete();
    }
    seamActorsRef.current=[];
    delete host.dataset.nativeSeamSegments;
    delete host.dataset.nativeSeamPatchIncidences;
    if (seamTrace) {
      const actors=nativeSeamActors(
        seamTrace,space,patchSlot,selectedSampleOrdinal);
      seamActorsRef.current=actors;
      actors.forEach(actor=>renderer.addActor(actor));
      host.dataset.nativeSeamSegments=String(
        space==='xyz' ? seamTrace.segments.length :
        seamTrace.segments.filter(s=>s.patchSlot===patchSlot).length);
      host.dataset.nativeSeamPatchIncidences=String(seamTrace.patchSlots.length);
      host.dataset.nativeSelectedSample=String(selectedSampleOrdinal);
    }
    grw.getRenderWindow().render();
    if (new URLSearchParams(window.location.search).get('nativePerf') === '1')
      host.dataset.nativePerfSeamOverlayCpuMs =
        (performance.now() - overlayStart).toFixed(3);
    return () => {
      if(renderRef.current===grw) {
        for(const actor of seamActorsRef.current){
          renderer.removeActor(actor);actor.delete();
        }
        seamActorsRef.current=[];
      }
    };
  }, [prepared,seamTrace,space,patchSlot,selectedSampleOrdinal]);

  useEffect(() => {
    const grw = renderRef.current;
    if (!grw) return;
    const renderer = grw.getRenderer();
    if (overlayRef.current) {
      renderer.removeActor(overlayRef.current);
      overlayRef.current.delete();
      overlayRef.current=null;
    }
    if (selectedFaceIndex === null ||
        !prepared.originalFaceIndices.includes(selectedFaceIndex)) {
      grw.getRenderWindow().render();
      return;
    }
    const face = scene.native_faces[selectedFaceIndex];
    const vertices = new Float32Array(9);
    face[4].forEach((node,i) => {
      vertices.set(space === 'xyz'
        ? [node[1],node[2],node[3]] : [node[4],node[5],0],i*3);
    });
    const poly = vtkPolyData.newInstance();
    poly.getPoints().setData(vertices,3);
    poly.getPolys().setData(new Uint32Array([3,0,1,2]));
    const mapper = vtkMapper.newInstance();
    mapper.setInputData(poly);
    const selected = vtkActor.newInstance();
    selected.setMapper(mapper);
    selected.setPickable(false);
    selected.getProperty().setRepresentationToWireframe();
    selected.getProperty().setLineWidth(4);
    selected.getProperty().setColor(1,0.38,0.23);
    overlayRef.current=selected;
    renderer.addActor(selected);
    grw.getRenderWindow().render();
    return () => {
      if (overlayRef.current === selected) {
        renderer.removeActor(selected);
        selected.delete();
        overlayRef.current=null;
      }
    };
  }, [prepared,scene,space,selectedFaceIndex]);

  return <div className="view-pane native-accepted-view">
    <div className="view-heading"><strong>
      {space === 'xyz' ? 'TRI nativa aceita · XYZ' : 'UV local do patch ' + patchSlot}
    </strong><span className="view-tag">R2.7.20 / SOURCE</span></div>
    <div className="vtk-canvas" ref={hostRef}
      data-testid={'r2720-viewport-' + space}
      aria-label={'Geometria TRI nativa aceita ' + space}/>
    <div className="view-footer">
      {space === 'xyz'
        ? 'TRI nativa original por patch · sem soldagem de nós'
        : 'UV é local ao patch selecionado · sem atlas global inferido'}
    </div>
  </div>;
}
