#ifndef APMESH_APPLICATION_RUN_APPLICATION_H
#define APMESH_APPLICATION_RUN_APPLICATION_H

namespace apmesh::application {
// Execute the existing CLI contract. Calls mutate legacy process-wide state and must be serialized.
int RunApplication(int argc, char** argv);
} // namespace apmesh::application

#endif
