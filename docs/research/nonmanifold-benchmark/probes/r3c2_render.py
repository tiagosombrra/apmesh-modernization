#!/usr/bin/env python3
"""Render exact native split-faces and their 3-way shared edge identities."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from r3c2_native import extract, _topology


def _corners(face):
    vertices=[v.toTuple() for v in face.Vertices()]
    zlo=min(v[2] for v in vertices)
    zhi=max(v[2] for v in vertices)
    low=sorted((v for v in vertices if abs(v[2]-zlo)<1e-8),key=lambda v:(v[0],v[1]))
    high=sorted((v for v in vertices if abs(v[2]-zhi)<1e-8),key=lambda v:(v[0],v[1]))
    return [low[0],low[1],high[1],high[0]]


def render(path:Path):
    fig=plt.figure(figsize=(14,7),dpi=160)
    cases=[('t_junction','T-Junction'),('cross_junction','Cross-Junction')]
    roles=['interface','host_exterior','arm_exterior']
    colors=['#eead61','#79add8','#91bfa4']
    for i,(case,name) in enumerate(cases):
        shape,report=extract(case)
        ax=fig.add_subplot(1,2,i+1,projection='3d')
        for sheet in report['source_face_to_subface']:
            face=shape.Faces()[sheet['sewn_face_index']]
            role=sheet['role']
            role_idx=0 if role=='interface' else 1 if role.startswith('host_') else 2
            poly=Poly3DCollection([_corners(face)],facecolors=colors[role_idx],edgecolors='#405364',linewidth=0.95,alpha=0.68)
            ax.add_collection3d(poly)
        entries,hist,triples=_topology(shape)
        for entry in entries:
            if len(entry['face_ids'])!=3:continue
            v=entry['edge'].Vertices()
            ax.plot([v[0].X,v[1].X],[v[0].Y,v[1].Y],[v[0].Z,v[1].Z],color='#15283e',linewidth=5)
            p=v[0]
            ax.scatter([p.X],[p.Y],[p.Z],c='#15283e',s=30)
        ax.set_xlabel('X');ax.set_ylabel('Y');ax.set_zlabel('Z')
        ax.set_title(f'{name}: {len(shape.Faces())} patches / {hist.get(3,0)} arestas de incidencia 3',pad=14,fontsize=11)
        ax.view_init(elev=25,azim=-55)
        if case=='t_junction':ax.set(xlim=(-11,11),ylim=(0,13),zlim=(-3,3))
        else:ax.set(xlim=(-11,11),ylim=(-11,11),zlim=(-3,3))
        ax.set_box_aspect((2,1.8,0.9))
    fig.suptitle('APMesh R3.C2 — decomposicao CAD com interfaces parciais',fontsize=15,fontweight='bold')
    fig.text(0.5,0.04,'Laranja: interface material | Azul: superficie externa do corpo principal | Verde: lateral do braco | Preto: aresta compartilhada por 3 faces',ha='center',fontsize=9)
    fig.text(0.5,0.01,'Fonte: geometrias locais que reproduzem as receitas CAD publicadas; nao sao malhas triangulares/quadrangulares do APMesh.',ha='center',fontsize=8)
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,bbox_inches='tight',dpi=175)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    render(args.output)
