#include "estimate/charge_estimate_process.h"
#include "generator/generator_adaptive.h"
bool ChargeEstimateProcess::CalculateErroEstimative(MeshAdaptive* mesh,
                                                    Timer* timer, int degree) {
  GeneratorAdaptive* ger = new GeneratorAdaptive();
#if USE_OPENMP
  double erro = ger->CalculateErrorGlobalOmp(mesh, timer);
#else
  double erro = ger->ErrorGlobal(mesh, timer);
#endif
  // delete ger;

  // cout << "erro: " << erro << " tolerancia: " << ESTIMATIVE_TOLERANCE <<
  // endl;

  if (erro < minor_error_) {
    minor_degree_ = degree;
  }

  if (erro <= ESTIMATIVE_TOLERANCE) {
    //  cout<<"return: false" <<endl;
    return false;
  }
  // cout<<"return: true" <<endl;

  return true;
}
