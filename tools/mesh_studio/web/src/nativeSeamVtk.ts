/** VTK-only view of verified accepted patch-local source-curve TRI edges. */
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import type { NativeSeamTrace, NativeSeamSegment } from './nativeSeamTrace';

type Space = 'xyz' | 'uv';

function polylineData(edges: NativeSeamSegment[],space:Space) {
  const poly=vtkPolyData.newInstance();
  const positions=new Float32Array(edges.length*6);
  const lines=new Uint32Array(edges.length*3);
  edges.forEach((segment,i) => {
    const before=space==='xyz' ? segment.xyzStart :
      [segment.uvStart[0],segment.uvStart[1],0];
    const after=space==='xyz' ? segment.xyzEnd :
      [segment.uvEnd[0],segment.uvEnd[1],0];
    positions.set(before,i*6);
    positions.set(after,i*6+3);
    lines.set([2,i*2,i*2+1],i*3);
  });
  poly.getPoints().setData(positions,3);
  poly.getLines().setData(lines);
  return poly;
}

function lineActor(edges:NativeSeamSegment[],space:Space,
  color:[number,number,number],width:number): ReturnType<typeof vtkActor.newInstance>|null {
  if(!edges.length) return null;
  const poly=polylineData(edges,space);
  const mapper=vtkMapper.newInstance();
  mapper.setInputData(poly);
  const actor=vtkActor.newInstance();
  actor.setMapper(mapper);
  actor.setPickable(false);
  actor.getProperty().setColor(...color);
  actor.getProperty().setLineWidth(width);
  return actor;
}

function markerActor(xyz:[number,number,number],color:[number,number,number],
  width:number): ReturnType<typeof vtkActor.newInstance> {
  const poly=vtkPolyData.newInstance();
  poly.getPoints().setData(new Float32Array(xyz),3);
  poly.getVerts().setData(new Uint32Array([1,0]));
  const mapper=vtkMapper.newInstance();
  mapper.setInputData(poly);
  const actor=vtkActor.newInstance();
  actor.setMapper(mapper);
  actor.setPickable(false);
  actor.getProperty().setRepresentationToPoints();
  actor.getProperty().setPointSize(width);
  actor.getProperty().setColor(...color);
  return actor;
}

/**
 * Never call global native node welding. Each original source patch keeps
 * its own segment cells even when its physical XYZ overlaps other patches.
 */
export function nativeSeamActors(trace:NativeSeamTrace,space:Space,
  selectedPatch:number,selectedOrdinal:number) {
  const eligible=space==='uv'
    ? trace.segments.filter(s=>s.patchSlot===selectedPatch)
    : trace.segments;
  const background=space==='xyz'
    ? eligible.filter(s=>s.patchSlot!==selectedPatch):[];
  const active=eligible.filter(s=>s.patchSlot===selectedPatch);
  const actors:ReturnType<typeof vtkActor.newInstance>[]=[];
  const neutral=lineActor(background,space,[0.18,0.75,0.76],3);
  if(neutral)actors.push(neutral);
  const focus=lineActor(active,space,[1.0,0.82,0.22],5);
  if(focus)actors.push(focus);
  const sample=trace.samples.find(s=>
    s.patchSlot===selectedPatch && s.ordinal===selectedOrdinal);
  if(sample)actors.push(markerActor(
    space==='xyz' ? sample.xyz : [sample.uv[0],sample.uv[1],0],
    [1,0.27,0.16],12));
  return actors;
}
