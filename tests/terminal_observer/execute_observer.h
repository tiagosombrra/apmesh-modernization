#ifndef APMESH_TESTS_TERMINAL_EXECUTE_OBSERVER_H
#define APMESH_TESTS_TERMINAL_EXECUTE_OBSERVER_H

#include "crab_mesh/aft/advancing_front.h"

namespace terminal_observer {
bool Execute(AdvancingFront& front, const FaceList& previous);
}

#endif
