#!/usr/bin/env python3
"""Independent analytic/structural audit for the fixed curved R3 research control.

This uses its own power-basis analytic curve, not the producer's cubic poles.
It does not certify an arbitrary STEP or a general non-manifold converter.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from audit_analytic_bp import read_bp, surface

RAYS = ((0.,5.),(-5.,0.),(5.,0.),(0.,-5.))
PAIRS = (('A','B'),('A','C'),('B','VOID'),('C','VOID'))
SIDES=((0,1,2,3),(3,7,11,15),(12,13,14,15),(0,4,8,12))


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def analytic(u,v,dx,dy):
    """Use power basis instead of the producer's Bernstein control representation."""
    return (0.4*v*(1-v)+u*dx,
            0.3*v*(1-v)*(2*v-1)+u*dy,
            -2.5+5*v)


def audit(bp, metadata, native_shape=None):
    require(metadata.get('schema')=='apmesh-r3-curved-bicubic-v1','Wrong schema')
    require(hashlib.sha256(bp.encode()).hexdigest()==metadata.get('bp_sha256'),'BP hash mismatch')
    require(metadata.get('classification')=='CONSTRUCTED_CURVED_ANALYTIC_CONTROL','Source scope misclassified')
    require(metadata.get('external_model_admission')=='NOT_GRANTED','False model approval')
    require(metadata.get('source_cad_conversion')=='NOT_PERFORMED','False CAD converter claim')
    require(metadata.get('apmesh_tri_generation')=='NOT_RUN','False TRI run claim')
    vertices, patches=read_bp(bp)
    require(len(vertices)==52 and len(patches)==4,'Wrong model size')
    require(metadata.get('unique_vertex_count')==52 and metadata.get('patch_count')==4,'Wrong declared size')
    require(metadata.get('canonical_control_indices')==[0,1,2,3],'Wrong canonical curve indices')
    require(metadata.get('canonical_curve')=='C0' and metadata.get('common_curve_incidence')==4,'Wrong common curve identity')
    require(metadata.get('reversed_shared_side_patch')==1,'Missing reversed orientation control')
    require(len(metadata.get('patches',[]))==4,'Missing patch records')
    require(len({v for p in patches for v in p})==52,'Unexpected vertex sharing')
    shared_edges=Counter()
    maxerror=0.
    for k,(ids,item) in enumerate(zip(patches,metadata['patches'])):
        dx,dy=RAYS[k]
        reverse=k==1
        require(item['index']==k and item['control_indices']==list(ids),'Source index map mismatch')
        require(item['region_pair']==list(PAIRS[k]),'Wrong sheet region pair')
        require(item['radial_xy']==[dx,dy] and item['reverse_v'] is reverse,'Wrong sheet direction')
        require(len(ids)==len(set(ids))==16,'Duplicate local control')
        expected=[3,2,1,0] if reverse else [0,1,2,3]
        require([ids[x] for x in SIDES[3]]==expected,'Shared edge control mismatch')
        require(len(item['sides'])==4,'Missing curve-side map')
        for slot,positions in enumerate(SIDES):
            side=item['sides'][slot]
            require(side['slot']==slot and side['control_indices']==[ids[i] for i in positions],'Side index drift')
            name='C0' if slot==3 else f'P{k}:S{slot}'
            require(side['curve_id']==name,'Wrong curve key')
            require(side['orientation']==(('reversed' if reverse else 'forward') if slot==3 else 'local'),'Side orientation mismatch')
            shared_edges[name]+=1
        net=[vertices[i] for i in ids]
        for iu in range(9):
            u=iu/8
            for iv in range(9):
                lv=iv/8
                global_t=1-lv if reverse else lv
                expected_xyz=analytic(u,global_t,dx,dy)
                xyz=surface(net,u,lv)
                error=max(abs(a-b) for a,b in zip(xyz,expected_xyz))
                maxerror=max(maxerror,error)
                require(error<=2e-12,'Curved polynomial mismatch')
    require(len(shared_edges)==13 and shared_edges['C0']==4 and all(n==1 for key,n in shared_edges.items() if key!='C0'),'Invalid curve incidences')
    require(metadata.get('unique_curve_count')==13,'Incorrect curve count')
    native_error=None
    native_hist=None
    if native_shape is not None:
        require(native_shape.isValid() and len(native_shape.Faces())==4,'Invalid native shape')
        faces=native_shape.Faces()
        groups=[]
        for i,face in enumerate(faces):
            for edge in face.Edges():
                g=next((x for x in groups if x[0].wrapped.IsSame(edge.wrapped)),None)
                if g is None:
                    g=[edge,set()];groups.append(g)
                g[1].add(i)
        native_hist=dict(Counter(len(group[1]) for group in groups))
        require(native_hist=={1:12,4:1},'Native source does not have four-way topology')
        # Orientation-independent geometric comparison: each source patch is
        # compared to a face at 64 interior analytic points, by minimum shape
        # distance, not by assuming Open CASCADE face enumeration order.
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
        from OCP.BRepExtrema import BRepExtrema_DistShapeShape
        from OCP.gp import gp_Pnt
        native_error=0.
        for k,(dx,dy) in enumerate(RAYS):
            for i in range(1,9):
                for j in range(1,9):
                    p=analytic(i/9,j/9,dx,dy)
                    point=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex()
                    distances=[]
                    for f in faces:
                        d=BRepExtrema_DistShapeShape(point,f.wrapped)
                        d.Perform()
                        require(d.IsDone(),'Native distance operation failed')
                        distances.append(d.Value())
                    error=min(distances)
                    native_error=max(native_error,error)
                    require(error<=1e-8,'Native curved surface mismatch')
    return {
        'schema':'apmesh-r3-curved-independent-audit-v1',
        'classification':'LOCAL_ANALYTIC_CONTROL_NOT_GENERAL_CAD_CONVERSION',
        'patches':4,
        'unique_control_vertices':52,
        'unique_curve_groups':13,
        'canonical_curve_incidence':4,
        'reversed_v_orientation_patches':[1],
        'max_power_basis_difference':maxerror,
        'evaluated_bp_points':324,
        'max_native_brep_distance':native_error,
        'native_edge_face_incidence':native_hist,
        'g2_external_admission':'NOT_GRANTED',
        'apmesh_generation':'NOT_RUN',
    }


def sine_nonpolynomial_exact_case():
    """Exhibit a nonzero fourth derivative to reject exact cubic representation."""
    v=0.25
    fourth_derivative=0.05*(2*math.pi)**4*math.sin(2*math.pi*v)
    require(abs(fourth_derivative)>1.,'Bad adversarial source definition')
    return {'source':'cubic_centerline_plus_sine_perturbation',
            'fourth_derivative_at_v_quarter':fourth_derivative,
            'exact_nonrational_cubic_representation':'IMPOSSIBLE_FOR_THIS_SOURCE',
            'approximation_or_trim_decomposition':'NOT_EVALUATED'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bp',type=Path,required=True)
    p.add_argument('--sidecar',type=Path,required=True)
    p.add_argument('--brep',type=Path)
    args=p.parse_args()
    shape=None
    if args.brep is not None:
        import cadquery as cq
        shape=cq.Shape.importBrep(str(args.brep))
    print(json.dumps(audit(args.bp.read_text(),json.loads(args.sidecar.read_text()),shape),sort_keys=True,indent=2))


if __name__=='__main__':
    main()
