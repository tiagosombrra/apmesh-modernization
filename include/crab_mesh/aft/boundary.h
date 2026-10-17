#ifndef _BOUNDARY_H_
#define _BOUNDARY_H_

#include "../../data/curve/curve_adaptive_parametric.h"
#include "../../data/definitions.h"
#include "edge.h"
#include "quadtree.h"
#include "quadtree_cell.h"
#include "shape.h"
#include "vertex.h"

using namespace Par2DJMesh;
using namespace Par2DJMesh::AFT;
using namespace Par2DJMesh::Basics;

namespace Par2DJMesh {
namespace AFT {
class Boundary : public Shape {
 private:
  VertexList boundary;
  EdgeList edges;

  long int lastVertexId;
  long int lastEdgeId;

  Vertex *first;
  CurveAdaptiveParametric* outgoing_curve_ = nullptr;
  bool outgoing_reversed_ = false;

private:
  Edge *makeEdge(Vertex *v);

 public:
  Boundary();
  ~Boundary() override;

  void setBoundary(VertexList boundary);
  VertexList getBoundary();

  void setEdges(EdgeList edges);
  EdgeList getEdges();

  long int getLastVertexId();
  long int getLastEdgeId();

  // Failed registration preserves existing owners, adjacency, IDs and contour start.
  Vertex* addVertex(double x, double y, CurveAdaptiveParametric* c, bool reversed = false);
  Vertex *addVertex(long int id, double x, double y);
  bool close(CurveAdaptiveParametric* c, bool reversed = false);

  Edge *getEdge(long int id);
  Vertex *getVertex(long int id);

  void getBox(double *minX, double *minY, double *maxX, double *maxY);

  bool belongs(Edge *e);
  bool belongs(Vertex *v1, Vertex *v2);

  string getText() override;

  // #if USE_OPENGL
  //     void highlight();
  //     void unhighlight();

  //    void draw();
  //    void drawNormals();
  // #endif //#if USE_OPENGL
};
}  // namespace AFT
}  // namespace Par2DJMesh

#endif  // #ifndef _BOUNDARY_H_
