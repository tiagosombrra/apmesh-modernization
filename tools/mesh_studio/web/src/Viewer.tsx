import { useEffect, useRef } from 'react';
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkCellPicker from '@kitware/vtk.js/Rendering/Core/CellPicker';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import type { MeshGeometry, Space } from './contracts';
import { asVtkCells } from './geometry';

interface ViewerProps {
  space: Space;
  modelId: string;
  geometry: MeshGeometry;
  showTri: boolean;
  showQuad: boolean;
  edges: boolean;
  selectedId: number | null;
  onSelect: (faceId: number | null) => void;
}

export function Viewer({ space, modelId, geometry, showTri, showQuad, edges,
                         selectedId, onSelect }: ViewerProps) {
  const container = useRef<HTMLDivElement>(null);
  const sourceFaceIds = useRef<number[]>([]);
  const rendererRef = useRef<ReturnType<typeof vtkGenericRenderWindow.newInstance> | null>(null);
  const onSelectRef = useRef(onSelect);
  const overlayRef = useRef<ReturnType<typeof vtkActor.newInstance> | null>(null);
  const geometryRef = useRef<MeshGeometry | null>(null);
  const rebuildOverlay = useRef<(id: number | null) => void>(() => {});
  useEffect(() => { onSelectRef.current = onSelect; }, [onSelect]);

  useEffect(() => {
    if (!container.current) return;
    const grw = vtkGenericRenderWindow.newInstance({ background: [0.047, 0.085, 0.126] });
    grw.setContainer(container.current);
    grw.resize();
    rendererRef.current = grw;
    const renderer = grw.getRenderer();
    const renderWindow = grw.getRenderWindow();
    const vtk = asVtkCells(geometry, showTri, showQuad);
    sourceFaceIds.current = vtk.sourceIds;
    geometryRef.current = geometry;
    const data = vtkPolyData.newInstance();
    data.getPoints().setData(vtk.points, 3);
    data.getPolys().setData(vtk.polys);
    data.getCellData().setScalars(vtkDataArray.newInstance({
      name: 'elementTypeColor', values: vtk.colorBytes, numberOfComponents: 4,
    }));
    const mapper = vtkMapper.newInstance();
    mapper.setInputData(data);
    mapper.setScalarVisibility(true);
    mapper.setScalarModeToUseCellData();
    mapper.setColorModeToDirectScalars();
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setEdgeVisibility(edges);
    actor.getProperty().setEdgeColor(0.08, 0.16, 0.22);
    actor.getProperty().setLineWidth(1);
    renderer.addActor(actor);

    rebuildOverlay.current = (id) => {
      if (overlayRef.current) renderer.removeActor(overlayRef.current);
      overlayRef.current = null;
      const g = geometryRef.current;
      const i = g?.source_face_ids.indexOf(id ?? -1) ?? -1;
      if (id === null || i < 0 || !g) { renderWindow.render(); return; }
      if ((!showTri && g.cell_types[i] === 'triangle') ||
          (!showQuad && g.cell_types[i] === 'quad')) return;
      const highlight = vtkPolyData.newInstance();
      highlight.getPoints().setData(new Float32Array(g.points.flat()), 3);
      highlight.getPolys().setData(new Uint32Array([g.cells[i].length, ...g.cells[i]]));
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
      renderWindow.render();
    };

    const camera = renderer.getActiveCamera();
    if (space === 'uv') {
      camera.setParallelProjection(true);
      camera.setPosition(0.5, 0.5, 4);
      camera.setFocalPoint(0.5, 0.5, 0);
      camera.setViewUp(0, 1, 0);
    }
    renderer.resetCamera();
    grw.resize();
    renderWindow.render();
    rebuildOverlay.current(selectedId);
    const picker = vtkCellPicker.newInstance();
    picker.setPickFromList(true);
    picker.addPickList(actor);
    const click = (event: MouseEvent) => {
      const host = container.current;
      if (!host) return;
      const rect = host.getBoundingClientRect();
      picker.pick([event.clientX - rect.left, rect.height - (event.clientY - rect.top), 0], renderer);
      const picked = picker.getCellId();
      onSelectRef.current(picked >= 0 ? sourceFaceIds.current[picked] ?? null : null);
    };
    container.current.addEventListener('click', click);
    const observer = new ResizeObserver(() => grw.resize());
    observer.observe(container.current);
    return () => {
      observer.disconnect();
      container.current?.removeEventListener('click', click);
      rendererRef.current = null;
      rebuildOverlay.current = () => {};
      grw.delete();
    };
    // Rebuild data on model/layer changes; selection update does not reset camera.
  }, [geometry, modelId, space, showTri, showQuad, edges]);

  useEffect(() => { rebuildOverlay.current(selectedId); }, [selectedId]);
  return (
    <section className="view-pane" aria-label={`Vista ${space.toUpperCase()}`}>
      <div className="view-heading">
        <div><span className="view-space">{space === 'uv' ? '02' : '01'}</span>
          <strong>{space === 'xyz' ? 'Espaço físico' : 'Domínio paramétrico'}</strong></div>
        <span className="view-tag">{space.toUpperCase()}</span>
      </div>
      <div ref={container} className="vtk-canvas" data-testid={`viewport-${space}`} />
      <div className="view-footer">{space === 'xyz' ? 'Arraste para orbitar · role para ampliar' : 'A mesma face, na parametrização UV'}</div>
    </section>
  );
}
