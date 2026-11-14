"""Headless journal-size source-verified UV figures with SVG/PDF vector checks.

Only face polygons, path patches, bars and text are rendered. No rasterized
3D scene is presented as a true-vector PDF. The mesh source and the quality
metric definitions are retained in a replayable recipe and provenance record.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import csv
import json
import math
import xml.etree.ElementTree as ET

from .comparison import controlled_p1_registry
from .import_obj import import_obj
from .p1_source_oracle import qualify_p1, bezier, _cross
from .quality_analysis import analyze_mesh

FIGURE_SCHEMA = "apmesh.meshstudio.paper_figure.v1"
WIDTH_MM = 178
HEIGHT_MM = 108


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _save_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=True, sort_keys=True,
                               indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _scan_svg(svg: Path) -> dict:
    root = ET.parse(svg).getroot()
    tags = [tag.tag.rsplit('}', 1)[-1] for tag in root.iter()]
    if any(tag in ('image', 'foreignObject', 'script') for tag in tags):
        raise ValueError("svg_contains_raster_or_executable_content")
    hrefs = []
    for element in root.iter():
        for key, value in element.attrib.items():
            if key.rsplit('}', 1)[-1] == 'href':
                hrefs.append(value)
            if key.startswith('on') or 'url(http' in value or 'data:' in value:
                raise ValueError("svg_external_or_active_content")
    if any(not val.startswith('#') for val in hrefs):
        raise ValueError("svg_external_reference")
    if not any(t in ('path', 'polygon', 'rect') for t in tags):
        raise ValueError("svg_no_vector_geometry")
    return {"vector_only": True, "image_elements": 0,
            "path_elements": tags.count("path"), "local_glyph_references": len(hrefs)}


def _scan_pdf(pdf: Path, width_mm: int, height_mm: int, *, min_drawings: int = 70) -> dict:
    from pypdf import PdfReader
    import fitz
    reader = PdfReader(str(pdf), strict=True)
    if len(reader.pages) != 1:
        raise ValueError("pdf_page_inventory")
    page = reader.pages[0]
    scale = 72/25.4
    box = page.mediabox
    if (abs(float(box.width)-width_mm*scale) > .1 or
        abs(float(box.height)-height_mm*scale) > .1):
        raise ValueError("pdf_wrong_physical_dimensions")
    with fitz.open(pdf) as f:
        if f[0].get_images(full=True):
            raise ValueError("pdf_contains_raster_image_xobject")
        if min_drawings < 20 or len(f[0].get_drawings()) < min_drawings:
            raise ValueError("pdf_insufficient_vector_geometry")
        embedded = f[0].get_fonts(full=True)
        if not embedded or not all(f.extract_font(row[0]) and f.extract_font(row[0])[3]
                                   for row in embedded):
            raise ValueError("pdf_fonts_not_embedded")
    # A PDF can also contain inline images, which are not Image XObjects.
    from pypdf.generic import ContentStream
    stream = ContentStream(page.get_contents(), reader)
    if any(operator in (b'INLINE IMAGE', b'BI') for _, operator in stream.operations):
        raise ValueError("pdf_inline_raster_image")
    return {"vector_only_no_image_xobjects": True,
            "page_count": 1, "width_mm": width_mm, "height_mm": height_mm,
            "font_inventory": len(embedded), "vector_drawings_at_least": min_drawings}


def _quality_histogram(scores: list[float]) -> list[int]:
    bins = [0]*8
    for q in scores:
        if not math.isfinite(q) or not 0 < q <= 1:
            raise ValueError("invalid_tri_quality")
        bins[min(7, int(8*q))] += 1
    return bins


def _make_plot(document, scores: list[float], path: Path, pdf: Path) -> None:
    import matplotlib
    matplotlib.use('Agg', force=True)
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import FigureCanvasPdf
    from matplotlib.backends.backend_svg import FigureCanvasSVG
    from matplotlib.patches import Polygon, Rectangle
    import matplotlib as mpl

    with mpl.rc_context({"font.family": "DejaVu Sans", "font.size": 7,
                         "svg.fonttype": "path", "svg.hashsalt": "APMeshMeshStudioS5", "pdf.fonttype": 42,
                         "axes.edgecolor": "#455C70", "savefig.facecolor": "white",
                         "axes.unicode_minus": False}):
        fig = Figure(figsize=(WIDTH_MM/25.4, HEIGHT_MM/25.4), dpi=150,
                     facecolor="white")
        fig.suptitle("APMesh  |  Controlled curved-patch hybrid construction",
                     fontsize=11, fontweight='bold', x=.045, ha='left', y=.977,
                     color='#142A3C')
        fig.text(.045,.921,
                 "REAL SOURCE  /  PR #217  /  fixed16 vertex-mean  /  not adaptive history",
                 fontsize=6.8, color='#3C566B')
        ax=fig.add_axes([.055,.23,.47,.62])
        ax.set_aspect('equal')
        ax.set_xlim(-.02,1.02); ax.set_ylim(-.02,1.02)
        ax.set_xlabel('u (source chart)',labelpad=1); ax.set_ylabel('v',labelpad=1)
        ax.tick_params(labelsize=6, length=2)
        ax.grid(False)
        for face in document.faces:
            if face.uv is None:
                raise ValueError("source_missing_uv")
            fill = '#B8D9E5' if face.element_type == 'quad' else '#E0E5EA'
            ax.add_patch(Polygon(face.uv, closed=True, facecolor=fill,
                                 edgecolor='#283B49', linewidth=.46,
                                 joinstyle='round'))
        ax.text(.02,.99,'(a) Source UV: QUAD interior + AFT TRI exterior',
                transform=ax.transAxes,va='bottom',ha='left',fontsize=7,
                fontweight='bold',color='#152D3F')
        hist=fig.add_axes([.607,.48,.347,.365])
        centers=[(i+.5)/8 for i in range(8)]
        counts=_quality_histogram(scores)
        hist.bar(centers,counts,width=.103, color='#486A8D',edgecolor='#253A50',linewidth=.4)
        hist.set_xlim(0,1);hist.set_ylim(0,max(counts)+2)
        hist.set_xlabel('TRI mean-ratio quality (Studio)',fontsize=6.5,labelpad=2)
        hist.set_ylabel('Elements',fontsize=6.5,labelpad=2)
        hist.tick_params(labelsize=6,length=2)
        hist.set_title('(b) TRI shape-quality distribution  (n = 36)',
                       fontsize=7.2,loc='left',fontweight='bold',color='#152D3F',pad=8)
        hist.spines['top'].set_visible(False);hist.spines['right'].set_visible(False)
        sub=fig.add_axes([.607,.17,.347,.235]); sub.axis('off')
        sub.add_patch(Rectangle((0,0),1,1,transform=sub.transAxes,
                                facecolor='#F4F7FA',edgecolor='#D0D8E0',linewidth=.7))
        sub.text(.045,.83,'(c) Verified source inventory',fontsize=7.1,fontweight='bold',
                 color='#152D3F',transform=sub.transAxes)
        facts=[('QUAD', '42'), ('AFT TRI', '36'), ('XYZ nodes', '69'),
               ('Boundary / seam edges','16 / 20'),('Accepted adaptive epochs','0')]
        for i,(label,val) in enumerate(facts):
            y=.67-i*.125
            sub.text(.05,y,label,fontsize=6.45,color='#3C5368',transform=sub.transAxes)
            sub.text(.95,y,val,fontsize=6.65,color='#132D3F',fontweight='bold',
                     ha='right',transform=sub.transAxes)
        fig.text(.055,.145,
                 "QUAD cell quality not scored by planar Jacobian: all 42 mapped cells are nonplanar.",
                 fontsize=6.5,color='#8A401D')
        fig.text(.055,.090,
                 "Original mesh SHA-256: " + document.source_sha256,
                 fontsize=5.7,color='#334E61')
        fig.text(.055,.048,
                 "Facet-wise orientation verified; no continuous Jacobian, global welding or anisotropic claim.",
                 fontsize=6,color='#425B6D')
        FigureCanvasSVG(fig).print_svg(str(path),metadata={'Date':None,'Creator':'APMesh Mesh Studio S5'})
        FigureCanvasPdf(fig).print_pdf(str(pdf),metadata={'CreationDate':None,
                                                            'ModDate':None,
                                                            'Creator':'APMesh Mesh Studio S5'})
        fig.clear()


def export_p1_paper_figure(obj:Path, generator_report:Path, output_dir:Path) -> dict:
    """Emit a scientifically bounded, true-vector journal figure package."""
    output_dir=Path(output_dir)
    if output_dir.exists():
        raise FileExistsError("output_directory_already_exists")
    document=import_obj(obj,auto_sidecar=False)
    record=json.loads(generator_report.read_text(encoding='utf-8'))
    proof=qualify_p1(document,record)
    quality=analyze_mesh(document,source_normal=lambda u,v: _cross(bezier(u,v)[1],bezier(u,v)[2]))
    tri=[float(c['triangle_mean_ratio']) for c in quality['cells'] if c['element_type']=='triangle']
    if len(tri)!=36 or any(c['planar_quad_min_scaled_jacobian'] is not None
                           for c in quality['cells'] if c['element_type']=='quad'):
        raise ValueError("unexpected_physical_quality_scope")
    out=output_dir
    out.mkdir(parents=True)
    svg=out/'figure.svg';pdf=out/'figure.pdf'
    _make_plot(document,tri,svg,pdf)
    svg_gate=_scan_svg(svg)
    pdf_gate=_scan_pdf(pdf,WIDTH_MM,HEIGHT_MM)
    sourcehash=document.source_sha256
    recipe={"schema":FIGURE_SCHEMA,"version":1,
            "source_obj_sha256":sourcehash,
            "generator_report_sha256":_digest(generator_report),
            "model":"Models3d::ModelCurvaBezier",
            "algorithm":"QUAD interior + original AFT exterior",
            "sampling":"fixed16_vertex_mean_v1",
            "comparison_policy":"NOT_A_3x2_ISOTROPIC_VS_ANISOTROPIC_ADAPTIVE_RUN",
            "accepted_adaptive_epochs":0,
            "figure_width_mm":WIDTH_MM,"figure_height_mm":HEIGHT_MM,
            "panels":["source_uv_indexed_mesh","triangle_mean_ratio_distribution","original_face_inventory"],
            "metrics":["triangle_mean_ratio_3d_v1"],
            "quad_planar_quality":"NOT_EVALUABLE_NONPLANAR",
            "evidence_kind":"REAL_SOURCE_CI_ARTIFACT_NOT_SYNTHETIC",
            "svg_raster_image_count":0,"pdf_raster_image_count":0,
            "publication_figures_are_not_continuous_surface_certification":True}
    _save_json(out/'figure.recipe.json',recipe)
    with (out/'triangle_quality.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.writer(f,lineterminator='\n')
        writer.writerow(['source_face_id','element_type','triangle_mean_ratio_3d_v1'])
        for row in quality['cells']:
            if row['element_type']=='triangle':
                writer.writerow([row['index'],'triangle',format(row['triangle_mean_ratio'],'.17g')])
    _save_json(out/'comparison_matrix.json',controlled_p1_registry(sourcehash))
    (out/'include.tex').write_text(
        r'\begin{figure*}[tb]'+'\n'+
        r'  \centering'+'\n'+
        r'  \includegraphics[width=\textwidth]{figure.pdf}'+'\n'+
        r'  \caption{Controlled real-source QUAD/AFT TRI construction in the UV chart, '
        r'with independent TRI quality measurements. This one-shot fixed16 experiment '
        r'does not establish adaptive epochs, all-QUAD, or anisotropic performance.}'+'\n'+
        r'  \label{fig:apmesh-controlled-p1}'+'\n'+
        r'\end{figure*}'+'\n',encoding='utf-8')
    _save_json(out/'source_oracle.json',proof)
    receipt={"schema":"apmesh.meshstudio.publication_receipt.v1",
             "source_obj_sha256":sourcehash,
             "source_real":True,"synthetic":False,"cell_inventory":{"quad":42,"triangle":36},
             "svg_vector_audit":svg_gate,"pdf_vector_audit":pdf_gate,
             "pdf_size_mm":[WIDTH_MM,HEIGHT_MM],"adaptive_epochs":0,
             "files_sha256":{p.name:_digest(p) for p in sorted(out.iterdir()) if p.is_file()}}
    _save_json(out/'publication.audit.json',receipt)
    return receipt
