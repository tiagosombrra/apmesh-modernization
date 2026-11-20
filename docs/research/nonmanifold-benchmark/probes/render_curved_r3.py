#!/usr/bin/env python3
"""Render the exact R3 curved synthetic BP surfaces and common control curve."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from curved_bicubic_pilot import CURVE, RAYS


def center(t):
    """Evaluate the independent analytic cubic spine in power basis."""
    return (0.4*t*(1-t), 0.3*t*(1-t)*(2*t-1), -2.5+5*t)


def render(output):
    u=np.linspace(0,1,21)
    v=np.linspace(0,1,85)
    U,V=np.meshgrid(u,v,indexing='ij')
    x,y,z=center(V)
    fig=plt.figure(figsize=(11.5,8),dpi=150)
    ax=fig.add_subplot(111,projection='3d')
    colors=plt.rcParams['axes.prop_cycle'].by_key()['color']
    names=('A/B','A/C','B/VOID','C/VOID')
    for k,((dx,dy),name) in enumerate(zip(RAYS,names)):
        ax.plot_surface(x+dx*U,y+dy*U,z,color=colors[k],alpha=0.49,linewidth=0.18,edgecolor=colors[k],rstride=3,cstride=7)
    t=np.linspace(0,1,300)
    cx,cy,cz=center(t)
    ax.plot(cx,cy,cz,color='black',linewidth=4,label='Curva canonica C0')
    poles=np.asarray(CURVE)
    ax.plot(*poles.T,linestyle='--',color='black',linewidth=1,alpha=0.6)
    ax.scatter(*poles.T,color='black',s=38,zorder=10)
    ax.set_xlabel('X (unidades sinteticas)')
    ax.set_ylabel('Y (unidades sinteticas)')
    ax.set_zlabel('Z (unidades sinteticas)')
    ax.set_xlim(-5.5,5.5);ax.set_ylim(-5.5,5.5);ax.set_zlim(-3.0,3.0)
    ax.set_box_aspect((11,11,7))
    ax.view_init(elev=27,azim=36)
    ax.set_title('R3: quatro superficies Bezier curvas e uma curva C0 compartilhada\nControle analitico sintetico — NAO e malha gerada pelo APMesh',fontsize=13,pad=20)
    handles=[Line2D([0],[0],color=colors[i],lw=5,label=names[i]) for i in range(4)]
    handles.append(Line2D([0],[0],color='black',lw=3,label='C0: curva cubica compartilhada'))
    ax.legend(handles=handles,loc='upper left',frameon=True,fontsize=9)
    fig.text(.5,.035,'Quatro patches bicubicos; 52 vertices de controle distintos; P1 utiliza orientacao parametrica inversa.',ha='center',fontsize=9)
    output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,bbox_inches='tight',dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    render(args.output)
