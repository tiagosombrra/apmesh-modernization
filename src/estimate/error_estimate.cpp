#include "estimate/charge_estimate_process.h"

#include <memory>

#include "generator/generator_adaptive.h"

bool ChargeEstimateProcess::CalculateErroEstimative(MeshAdaptive* mesh, Timer* timer, int degree) {
  auto generator = std::make_unique<GeneratorAdaptive>();
#if USE_OPENMP
  const double error = generator->CalculateErrorGlobalOmp(mesh, timer);
#else
  const double error = generator->ErrorGlobal(mesh, timer);
#endif

  if (error < minor_error_) {
    minor_degree_ = degree;
  }

  if (error <= ESTIMATIVE_TOLERANCE) {
    return false;
  }

  return true;
}
