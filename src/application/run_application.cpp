#include "application/run_application.h"
#include "application/runtime_config.h"
#include <algorithm>
#include "adapter/domain_generation_error.h"
#include <atomic>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/definitions.h"
#include "data/model.h"
#include "data/patch/patch_bezier.h"
#include "data/patch/patch_hermite.h"
#include "data/vector_adaptive.h"
#include "data/vertex_adaptive.h"
#include "generator/generator_adaptive.h"
#include "input_output/models_3d.h"
#include "input_output/input_validation.h"
#include "input_output/patch_reader.h"
#include "timer/timer.h"

namespace apmesh::application {
int RunApplication(int argc, char** argv) {
#if USE_MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &SIZE_MPI);
  MPI_Comm_rank(MPI_COMM_WORLD, &RANK_MPI);
  MPI_Status status;

#endif

  const bool config_mode = (argc == 3 && std::string(argv[1]) == "--config");
  if (config_mode) {
    try {
      const RuntimeConfig config = LoadRuntimeConfig(argv[2]);
      ApplyRuntimeConfig(config);

#if USE_MPI
      if (config.num_processes < SIZE_MPI) {
        SIZE_MPI = config.num_processes;
      }
#endif

      Timer timer(config.num_processes, config.num_threads, 12);
      std::vector<std::string> synthetic_args_storage = {argv[0],
                                                         std::to_string(config.num_processes),
                                                         std::to_string(config.num_threads),
                                                         config.input_model,
                                                         config.write_mode,
                                                         config.output_prefix,
                                                         config.use_template};
      std::vector<char*> synthetic_args;
      synthetic_args.reserve(synthetic_args_storage.size() + 1);
      for (std::string& arg : synthetic_args_storage) {
        synthetic_args.push_back(arg.data());
      }
      synthetic_args.push_back(nullptr);

      if (RANK_MPI == 0) {
        cout << "Metodo por config: mode=" << ADAPTIVE_MODE << ", input=" << config.input_model
             << ", output=" << config.output_prefix << ", threads=" << config.num_threads << endl;
      }

      GeneratorAdaptive generator(MakeGenerationContext(config, NUMBER_PROCESS));
      int run_rc = 0;
#if USE_MPI
      run_rc = generator.Execute(synthetic_args.data(), &timer, status);
#else
      run_rc = generator.Execute(synthetic_args.data(), &timer);
#endif
      if (RANK_MPI == 0) {
        const unsigned long long fc = FINDUV_TOTAL_CALLS.load();
        const unsigned long long ix = FINDUV_IMAX_EXITS.load();
        if (fc > 0ULL) {
          const double pct = 100.0 * static_cast<double>(ix) / static_cast<double>(fc);
          std::cout << "[FindUV] chamadas=" << fc << " saidas_por_I_MAX=" << ix << " ("
                    << std::fixed << std::setprecision(2) << pct << "%)" << std::endl;
        }
      }
      return run_rc;
#if !USE_MPI && !USE_OPENMP
    } catch (const apmesh::adaptation::DomainGenerationError& error) {
      std::cerr << "Error: " << error.what() << " (step=" << error.Step()
                << ", patch=" << error.PatchIndex() << ", retry=" << error.RetryIndex()
                << ", status=" << error.Status() << ")\n";
      return EXIT_FAILURE;
#endif
    } catch (const std::exception& ex) {
      std::cerr << "Error: input or configuration failure: " << ex.what() << std::endl;
      return -1;
    }
  }

  std::cerr << "Error: expected ap_mesh --config <configuration.conf>" << std::endl;
#if USE_MPI
  MPI_Finalize();
#endif
  return -1;
}

} // namespace apmesh::application
