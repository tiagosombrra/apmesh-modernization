#include "../../../include/crab_mesh/aft/boundary.h"
#include "pending_template.h"

Boundary::Boundary() : Shape() {
  lastVertexId = lastEdgeId = 0;

  first = nullptr;
}

Boundary::~Boundary() {
  while (!edges.empty()) {
    Edge *e = edges.front();
    edges.pop_front();

    e->DetachVertices();

    delete e;
  }

  while (!boundary.empty()) {
    Vertex *v = boundary.front();
    boundary.pop_front();

    delete v;
  }
}

Edge *Boundary::makeEdge(Vertex *v) {
  apmesh::memory::PendingEdge e(new Edge(boundary.back(), v, lastEdgeId + 1));

  boundary.back()->addAdjacentEdge(e.get());
  v->addAdjacentEdge(e.get());

  return e.release();
}

void Boundary::setBoundary(VertexList boundary) { this->boundary = boundary; }

VertexList Boundary::getBoundary() { return boundary; }

void Boundary::setEdges(EdgeList edges) {
  for (EdgeList::iterator iter = edges.begin(); iter != edges.end(); iter++) {
    (*iter)->setInBoundary(false);
  }

  this->edges = edges;

  for (EdgeList::iterator iter = edges.begin(); iter != edges.end(); iter++) {
    (*iter)->setInBoundary(true);
  }
}

EdgeList Boundary::getEdges() { return edges; }

long int Boundary::getLastVertexId() { return lastVertexId; }

long int Boundary::getLastEdgeId() { return lastEdgeId; }

Vertex* Boundary::addVertex(double x, double y, CurveAdaptiveParametric* c, bool reversed) {
  auto pending_vertex = std::make_unique<Vertex>(x, y, lastVertexId + 1);
  Vertex* v = pending_vertex.get();
  apmesh::memory::PendingEdge pending_edge;

  // #if USE_OPENGL
  //     //figura
  //     //v->setSize(3.0);
  //     //v->setSize(1.0);
  //     v->setColor(0.0, 0.0, 0.0);
  //     //endfigura
  // #endif //#if USE_OPENGL

  if (first && !boundary.empty()) {
    pending_edge.reset(makeEdge(v));
    Edge* e = pending_edge.get();

    // The completed edge belongs to the previous vertex's outgoing side.
    e->setCurva(outgoing_curve_, outgoing_reversed_);

    e->makeParamMid();

    ////figura
    // #if USE_OPENGL
    //  e->setColor(0.0, 0.0, 0.0);
    // #endif //#if USE_OPENGL
    ////endfigura

    edges.push_back(e);

    e->setInBoundary(true);

    // figura
    // e->setWidth(2.0);
    // endfigura
  }

  try {
    boundary.push_back(v);
  } catch (...) {
    // Undo the completed edge registration before its local owner unwinds.
    if (pending_edge)
      edges.pop_back();
    throw;
  }
  if (!first)
    first = v;
  ++lastVertexId;
  if (pending_edge)
    ++lastEdgeId;
  outgoing_curve_ = c;
  outgoing_reversed_ = reversed;
  pending_edge.release();
  pending_vertex.release();

  return v;
}

Vertex *Boundary::addVertex(long int id, double x, double y) {
  Vertex* v = addVertex(x, y, nullptr);

  if (v) {
    v->setId(id);

    if (id > lastVertexId) {
      lastVertexId = id;
    }
  }

  return v;
}

bool Boundary::close(CurveAdaptiveParametric* c, bool reversed) {
  apmesh::memory::PendingEdge pending_edge(new Edge(boundary.back(), first, lastEdgeId + 1));
  Edge* e = pending_edge.get();

  e->setCurva(c, reversed);

  e->makeParamMid();

  boundary.back()->addAdjacentEdge(e);
  first->addAdjacentEdge(e);

  ////figura
  // #if USE_OPENGL
  //  e->setColor(0.0, 0.0, 0.0);
  // #endif //#if USE_OPENGL
  ////endfigura

  e->setInBoundary(true);

  edges.push_back(e);

  // Closing commits only after both adjacencies and the owner-list node exist.
  first = nullptr;
  ++lastEdgeId;
  pending_edge.release();

  return true;
}

Edge *Boundary::getEdge(long int id) {
  for (EdgeList::iterator iter = edges.begin(); iter != edges.end(); iter++) {
    if ((*iter)->getId() == id) {
      return (*iter);
    }
  }

  return nullptr;
}

Vertex *Boundary::getVertex(long int id) {
  for (VertexList::iterator iter = boundary.begin(); iter != boundary.end();
       iter++) {
    if ((*iter)->getId() == id) {
      return (*iter);
    }
  }

  return nullptr;
}

void Boundary::getBox(double *minX, double *minY, double *maxX, double *maxY) {
  *minX = boundary.front()->getX();
  *maxX = boundary.front()->getX();

  *minY = boundary.front()->getY();
  *maxY = boundary.front()->getY();

  for (VertexList::iterator iter = ++boundary.begin(); iter != boundary.end();
       iter++) {
    if ((*iter)->getX() < *minX) {
      *minX = (*iter)->getX();
    }

    if ((*iter)->getY() < *minY) {
      *minY = (*iter)->getY();
    }

    if ((*iter)->getX() > *maxX) {
      *maxX = (*iter)->getX();
    }

    if ((*iter)->getY() > *maxY) {
      *maxY = (*iter)->getY();
    }
  }
}

bool Boundary::belongs(Edge *e) {
  for (EdgeList::iterator iter = edges.begin(); iter != edges.end(); iter++) {
    if ((*iter) == e) {
      return true;
    }
  }

  return false;
}

bool Boundary::belongs(Vertex *v1, Vertex *v2) {
  for (EdgeList::iterator iter = edges.begin(); iter != edges.end(); iter++) {
    if ((*iter)->equals(v1, v2)) {
      return true;
    }
  }

  return false;
}

string Boundary::getText() {
  string s;

  return s;
}

// #if USE_OPENGL
//  void Boundary::highlight()
//{

//}

// void Boundary::unhighlight()
//{

//}

// void Boundary::draw()
//{
//    for (EdgeList::iterator iter = edges.begin();
//         iter != edges.end(); iter++)
//    {
//        (*iter)->draw();
//    }

//    for (VertexList::iterator iter = boundary.begin();
//         iter != boundary.end(); iter++)
//    {
//        (*iter)->draw();
//    }
//}

// void Boundary::drawNormals()
//{
//    for (EdgeList::iterator iter = edges.begin();
//         iter != edges.end(); iter++)
//    {
//        (*iter)->drawNormal();
//    }
//}
// #endif //#if USE_OPENGL
