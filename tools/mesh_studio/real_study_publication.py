"""Vector journal figures from verified real, staged-only APMesh candidates."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from .import_obj import import_obj
from .publication import _scan_pdf, _scan_svg
from .real_candidate_study import ORDER, STAGED, qualify_real_study

WIDTH_MM = 190
HEIGHT_MM = 132


def _sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()


def _json(path:Path,record:dict)->None:
    path.write_text(json.dumps(record,sort_keys=True,indent=2,
                               ensure_ascii=True,allow_nan=False)+"\n",encoding="utf-8")


def _render_figures(study:dict,source_dir:Path,output:Path)->None:
    import matplotlib
    matplotlib.use("Agg",force=True)
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    stable_date=datetime(2026,11,14,tzinfo=timezone.utc)
    with matplotlib.rc_context({"font.family":"DejaVu Sans", "font.size":7.0,
                                 "axes.unicode_minus":False,
                                 "pdf.fonttype":42,
                                 "svg.fonttype":"path",
                                 "svg.hashsalt":"APMeshMeshStudioS5D",
                                 "savefig.facecolor":"white"}):
        fig=plt.figure(figsize=(WIDTH_MM/25.4,HEIGHT_MM/25.4),facecolor="white")
        fig.suptitle("APMesh  |  Original Bezier patch: real physical QUAD/TRI candidates",
                     fontsize=11.0,fontweight="bold",x=.055,ha="left",y=.978)
        fig.text(.055,.923,"ORIGINAL CI ARTIFACTS  |  one controlled run  |  same UV chart  |  no accepted adapted epochs",
                 fontsize=7,color="#3D5366")
        positions=[(.075,.565),(.385,.565),(.695,.565),(.075,.145),(.385,.145)]
        labels={"control":"(a) Initial controlled output", "band":"(b) First staged band",
                "west":"(c) Second band / west", "north":"(d) Second band / north",
                "both":"(e) Second band / both"}
        for name,(left,bottom) in zip(ORDER,positions):
            ax=fig.add_axes([left,bottom,.225,.255])
            ax.set_aspect("equal")
            ax.set_xlim(-.012,1.012);ax.set_ylim(-.012,1.012)
            ax.set_xticks([0,.5,1]);ax.set_yticks([0,.5,1])
            ax.tick_params(labelsize=6,length=2,pad=1)
            ax.set_title(labels[name],fontsize=7.5,fontweight="bold",loc="left",pad=7)
            doc=import_obj(source_dir/(name+".obj"),auto_sidecar=False)
            for face in doc.faces:
                ax.add_patch(Polygon(face.uv,closed=True,
                                     facecolor="#C1DDE8" if face.element_type=="quad" else "#E3E6EB",
                                     edgecolor="#273C4A",linewidth=.22,antialiased=True))
            details=study["physical_candidates"][name]
            g=details["geometry"]
            ax.text(.01,-.20,f"Q {g['quads']}  /  T {g['triangles']}  /  N {g['nodes']}",
                    transform=ax.transAxes,fontsize=6.3)
        ax=fig.add_axes([.688,.15,.27,.27]);ax.axis("off")
        ax.text(0,.98,"Legend and evidence",fontweight="bold",fontsize=8,va="top")
        ax.text(0,.76,"Blue: original QUAD faces\nGray: original AFT TRI faces\n\n"
                "Control: fixed16, nonadaptive\nBand / west / north / both:\nSTAGED, not accepted epochs",
                fontsize=7,va="top",linespacing=1.55)
        fig.text(.06,.045,"Same physical chart coordinates; source CURVE/PATCH identities are not inferred from OBJ grouping.",
                 color="#445B6C",fontsize=6.6)
        for extension in ("svg","pdf"):
            meta={"Creator":"APMesh Mesh Studio S5d",
                  "CreationDate":stable_date} if extension=="pdf" else {
                  "Creator":"APMesh Mesh Studio S5d","Date":"2026-11-14"}
            fig.savefig(output/("real_candidate_gallery."+extension),
                        metadata=meta,facecolor="white")
        plt.close(fig)

        fig=plt.figure(figsize=(WIDTH_MM/25.4,HEIGHT_MM/25.4),facecolor="white")
        fig.suptitle("Source approximation vs mesh complexity: two non-equivalent Pareto profiles",
                     fontsize=10.2,fontweight="bold",x=.055,ha="left",y=.978)
        fig.text(.055,.920,
                 "Source: 4,096 identical UV midpoints  |  discrete Bernstein XYZ residual  |  staged alternatives only",
                 fontsize=7,color="#3D5366")
        prof=study["pareto_evidence"]["profiles"]
        for i,(key,title) in enumerate((("uv_area_profile","(a) QUAD UV area profile: 7 objectives"),
                                        ("quad_count_profile","(b) QUAD count profile: 8 objectives"))):
            ax=fig.add_axes([.085+i*.475,.34,.392,.47])
            ax.set_title(title,loc="left",fontsize=8,fontweight="bold",pad=9)
            ax.set_xlabel("Total physical faces",fontsize=7)
            if i==0:ax.set_ylabel("Source-area weighted RMS XYZ",fontsize=7)
            else: ax.set_ylabel("Source-area weighted RMS XYZ",fontsize=7)
            ax.tick_params(labelsize=7)
            ax.grid(color="#E2E7ED",linewidth=.5)
            ax.set_xlim(100,140);ax.set_ylim(.0084,.0127)
            for name in STAGED:
                case=study["physical_candidates"][name]
                x=case["geometry"]["elements"]
                y=case["same_site_error"]["rms_source_area"]
                nondominated=name in prof[key]["nondominated"]
                ax.scatter([x],[y],s=55 if nondominated else 80,
                           marker="o" if nondominated else "x",linewidths=1.2,
                           c="#256B87" if nondominated else "#B24A40",zorder=3)
                offset={"band":(3,8),"west":(4,12),"north":(3,-12),"both":(-29,9)}[name]
                ax.annotate(name,(x,y),xytext=offset,textcoords="offset points",fontsize=7)
        fig.text(.073,.240,
                 "Area profile: north dominates west.   QUAD-count profile: all four candidates are non-dominated.",
                 fontsize=8,fontweight="bold",color="#233A50")
        fig.text(.073,.181,
                 "A 2D projection does NOT prove high-dimensional dominance; statuses use all 7/8 audited objectives.",
                 fontsize=7,color="#48596A")
        fig.text(.073,.119,
                 "No selected winner / no adopted adaptive owner / no all-QUAD or anisotropic performance claim.",
                 fontsize=7,color="#48596A")
        for extension in ("svg","pdf"):
            meta={"Creator":"APMesh Mesh Studio S5d",
                  "CreationDate":stable_date} if extension=="pdf" else {
                  "Creator":"APMesh Mesh Studio S5d","Date":"2026-11-14"}
            fig.savefig(output/("real_candidate_pareto."+extension),
                        metadata=meta,facecolor="white")
        plt.close(fig)


def export_real_candidate_bundle(source_dir:Path|str,output_dir:Path|str)->dict:
    """Export source-qualified CSV, report, true-vector 2-panel figures and LaTeX."""
    source_dir=Path(source_dir)
    destination=Path(output_dir)
    destination.mkdir(parents=True,exist_ok=True)
    report=qualify_real_study(source_dir)
    _json(destination/"qualified_study.json",report)
    with (destination/"candidate_metrics.csv").open("w",newline="",encoding="utf-8") as output:
        fields=["candidate","source_mesh_sha256","candidate_status","nodes","quads","triangles",
                "elements","quad_uv_area","max_xyz_4096","rms_uv_4096","rms_source_area_4096",
                "minimum_quad_scaled_jacobian","minimum_quad_warpage_cosine",
                "accepted_adaptive_epochs"]
        writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader()
        for name in ORDER:
            item=report["physical_candidates"][name]
            geom,errors=item["geometry"],item["same_site_error"]
            writer.writerow({"candidate":name,"source_mesh_sha256":item["source_mesh_sha256"],
                             "candidate_status":item["state"],"nodes":geom["nodes"],
                             "quads":geom["quads"],"triangles":geom["triangles"],
                             "elements":geom["elements"],"quad_uv_area":geom["quad_uv_area"],
                             "max_xyz_4096":errors["max_xyz"],"rms_uv_4096":errors["rms_uv"],
                             "rms_source_area_4096":errors["rms_source_area"],
                             "minimum_quad_scaled_jacobian":geom["min_scaled_jacobian"],
                             "minimum_quad_warpage_cosine":geom["min_warpage_cosine"],
                             "accepted_adaptive_epochs":0})
    _render_figures(report,source_dir,destination)
    tex=r"""% Real single-run source geometry: control + four staged candidate meshes.
% The five physical candidate files are NOT independent statistical repetitions.
\begin{figure*}[tb]
  \centering
  \includegraphics[width=\textwidth]{real_candidate_gallery.pdf}
  \caption{Original Bezier physical QUAD/TRI meshes: controlled initial output and four staged/unaccepted alternatives. No adaptive epoch was accepted.}
  \label{fig:apmesh-real-candidates}
\end{figure*}
\begin{figure*}[tb]
  \centering
  \includegraphics[width=\textwidth]{real_candidate_pareto.pdf}
  \caption{Discrete common-site geometric residual against total face count. Nondominance is determined by different seven- and eight-objective profiles, not by the two-dimensional projection alone. No mesh is scientifically adopted.}
  \label{fig:apmesh-real-pareto}
\end{figure*}
"""
    (destination/"include.tex").write_text(tex,encoding="utf-8")
    recipes={"schema":"apmesh.meshstudio.real_candidate_figure_recipe.v1",
             "width_mm":WIDTH_MM,"height_mm":HEIGHT_MM,
             "same_uv_camera":[0,1,0,1],"sampling":"4096 identical UV midpoint sites",
             "source_sha256":{name:report["physical_candidates"][name]["source_mesh_sha256"] for name in ORDER},
             "graphic_semantics":"REAL_SOURCE_GEOMETRY_STAGED_NOT_ADAPTIVE_ACCEPTED",
             "pareto_profiles":list(report["pareto_evidence"]["profiles"])}
    _json(destination/"figure.recipe.json",recipes)
    audits={}
    for prefix in ("real_candidate_gallery","real_candidate_pareto"):
        audits[prefix]={"svg":_scan_svg(destination/(prefix+".svg")),
                        "pdf":_scan_pdf(destination/(prefix+".pdf"),WIDTH_MM,HEIGHT_MM,
                                        min_drawings=35)}
    files={p.name:_sha(p) for p in sorted(destination.iterdir()) if p.is_file()}
    audit={"schema":"apmesh.meshstudio.real_candidate_publication_audit.v1",
           "same_source_revalidated":True,"source_report_sha256":report["provenance"]["original_source_report_sha256"],
           "observed_adaptive_epochs":0,"candidate_count":len(STAGED),
           "source_run_not_independent_replicates":True,
           "vector_audits":audits,"file_sha256":files,
           "qt_gui_qualified":False,"source_CI_does_not_qualify_studio":True}
    _json(destination/"publication.audit.json",audit)
    return audit
