#include <algorithm>
#include <atomic>
#include <cctype>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "../include/data/curve/curve_adaptive_parametric_bezier.h"
#include "../include/data/curve/curve_adaptive_parametric_hermite.h"
#include "../include/data/definitions.h"
#include "../include/data/model.h"
#include "../include/data/patch/patch_bezier.h"
#include "../include/data/patch/patch_hermite.h"
#include "../include/data/vector_adaptive.h"
#include "../include/data/vertex_adaptive.h"
#include "../include/generator/generator_adaptive.h"
#include "../include/input_output/models_3d.h"
#include "../include/input_output/patch_reader.h"
#include "../include/timer/timer.h"

int RANK_MPI = 0;
int SIZE_MPI = 1;
int STEPS = 3;
double TRIANGLE_MEDIO = 0.0;
double ESTIMATIVE_TOLERANCE = 1.0;
// distância entre um parâmetro e outro
double DELTA = 0.0001;
// distância máxima entre dois pontos
double TOLERANCE = 0.0001;
double TOLERANCE_CURVATURE = 0.0001;
double TOLERANCE_AFT = 0.0001;
// proporção usada no avanço de fronteira (antes era 0.5)
double RATIO_AFT = 1.0;
// número de vezes que se dará a suavização laplaciana
double SMOOTHING_LAPLACIAN_NUMBER = 7;
// fator usado na suavização laplaciana
double SMOOTHING_LAPLACIAN_FACTOR = 0.5;
double EPSYLON = 0.0000001;  // trashrold
double MIN_IMPROVEMENT = 0.01;  // 1% de ganho mínimo por iteração
int PATIENCE = 2;               // iterações consecutivas sem ganho mínimo
double TOL_LOCAL = 0.0000001;   // limiar local para refinamento por submalha
double ADAPTATION_RELAXATION = 1.0;  // 1.0 = sem amortecimento
double ADAPTATION_MAX_DELTA = 0.20;  // variacao maxima do fator por passo
int ADAPTIVE_RETRY_COUNT = 0;  // retry desabilitado
double ADAPTIVE_RETRY_SHRINK = 1.0;  // sem efeito com retry desabilitado
double MAX_RETRY_ELEMENT_GROWTH_FACTOR = 0.0;  // 0 desabilita
double MAX_RETRY_ELEMENT_GROWTH_ABS = 0.0;  // 0 desabilita
double ERROR_FLOOR = 0.0;  // piso assintotico opcional do erro global
double MIN_ERROR_DROP_ABS = 0.0;  // queda absoluta minima aceitavel
double MIN_ERROR_DROP_PER_ELEMENT = 0.0;  // eficiencia minima de queda por elemento
int PATCH_ADAPTATION_MODE = 0;
double PATCH_FACTOR_MIN = 0.80;
double PATCH_FACTOR_MAX = 1.12;
double PATCH_REFINEMENT_STRENGTH = 0.22;
double PATCH_COARSENING_STRENGTH = 0.10;
double PATCH_ERROR_EXPONENT = 1.35;
double PATCH_QUALITY_WEIGHT = 0.35;
double PATCH_QUALITY_TARGET = 0.78;
double PATCH_QUALITY_MIN_TARGET = 0.45;
double PATCH_TOP_ERROR_FRACTION = 1.0;
int CURVE_ADAPTATION_POLICY = 0;
double CURVE_ADAPTATION_BLEND = 0.75;
double CURVE_FACTOR_SENSITIVITY = 1.0;
int ACCEPTANCE_MODE = 0;
double ACCEPTANCE_WEIGHT_ERROR = 1.0;
double ACCEPTANCE_WEIGHT_QUALITY_MIN = 0.20;
double ACCEPTANCE_WEIGHT_POOR_RATIO = 0.20;
double ACCEPTANCE_WEIGHT_GROWTH = 0.10;
double ACCEPTANCE_STEP1_GROWTH_WEIGHT = 0.02;
double ACCEPTANCE_STEPN_GROWTH_WEIGHT = 0.18;
double ACCEPTANCE_STEP1_MAX_GROWTH_SOFT = 40.0;
double ACCEPTANCE_STEPN_MAX_GROWTH_SOFT = 6.0;
int ACCEPTANCE_GROWTH_PENALTY_MODE = 0;
double ACCEPTANCE_STEP1_MIN_ERROR_DROP_ABS = 0.0;
double ACCEPTANCE_STEP1_MIN_ERROR_DROP_PCT = 0.0;
double ACCEPTANCE_MIN_SCORE = 0.0;
double ACCEPTANCE_MAX_ERROR_INCREASE_PCT = 0.0;
double ACCEPTANCE_POOR_RATIO_TARGET = 0.15;
int WRITE_ADAPTATION_DEBUG = 1;
double PATCH_EFFICIENCY_WEIGHT = 0.0;
double PATCH_EFFICIENCY_TARGET = 0.003;
double PATCH_HISTORY_BLEND = 0.5;
double PATCH_STEP2_REFINEMENT_SCALE = 0.75;
double PATCH_INEFFICIENT_CAP = 0.98;
int PATCH_STEPWISE_MODE = 0;
double STEP2_REFINEMENT_ATTENUATION = 0.8;
double STEP2_TOP_ERROR_FRACTION_SCALE = 0.7;
double STEP2_FACTOR_RANGE_SHRINK = 0.8;
double STEP2_CURVE_SENSITIVITY_SCALE = 0.8;
double CURVE_EFFICIENCY_WEIGHT = 0.5;
int STEP2_HARD_SPATIAL_FILTER_MODE = 0;
int STEP2_TOP_PATCH_COUNT_MIN = 2;
int STEP2_TOP_PATCH_COUNT_MAX = 6;
double STEP2_NONELIGIBLE_FACTOR_MIN = 1.0;
int STEP2_NONELIGIBLE_FORCE_COARSEN = 1;
double STEP2_SMOOTHING_NEIGHBOR_WEIGHT = 0.02;
double STEP2_ELIGIBLE_REFINEMENT_DAMP = 0.65;
double STEP2_ELIGIBLE_REFINEMENT_DAMP_ON_RETRY = 0.50;
double STEP2_ELIGIBLE_ELEMENTS_THRESHOLD = 600.0;
double STEP2_ELIGIBLE_H_SCALE = 1.12;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0.0;
double QUADTREE_LOW_QUALITY_H_FACTOR = 1.0;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0.0;
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0.35;
double AFT_LOCAL_POSTPROCESS_BLEND = 0.35;
int QUADTREE_SATURATION_MODE = 0;
double QUADTREE_SATURATION_ELEMENTS_THRESHOLD = 500.0;
double QUADTREE_SATURATION_EFFICIENCY_THRESHOLD = 0.001;
double QUADTREE_SATURATION_H_SCALE = 1.1;
int QUADTREE_HARD_SATURATION_MODE = 0;
int QUADTREE_HARD_SATURATION_STEPS = 1;
double QUADTREE_HARD_SATURATION_FACTOR_MIN = 1.02;
int QUADTREE_SKIP_LOW_QUALITY_SUBDIVIDE_ON_SATURATED = 1;
int QUADTREE_POSTPROCESS_DAMP_ON_SATURATED = 1;
int STEP_ELEMENT_BUDGET_MODE = 0;
double STEP_ELEMENT_BUDGET_ABS = 12000.0;
double STEP_ELEMENT_BUDGET_GROWTH_FACTOR = 3.0;
double STEP_ELEMENT_BUDGET_SOFT_RATIO = 1.05;
double STEP_ELEMENT_BUDGET_RETRY_SHRINK_TOPK = 0.65;
double STEP_ELEMENT_BUDGET_RETRY_H_SCALE = 1.08;
double STEP_ELEMENT_BUDGET_RETRY_FACTOR_RANGE_SCALE = 0.75;
int STEP_ELEMENT_BUDGET_PRESSURE_MODE = 0;
double STEP_ELEMENT_BUDGET_PRESSURE_START = 0.70;
double STEP_ELEMENT_BUDGET_PRESSURE_H_SCALE = 1.06;
double STEP_ELEMENT_BUDGET_PRESSURE_FACTOR_SHRINK = 0.85;
int STEP2_MICRO_REFINEMENT_MODE = 0;
double STEP2_MICRO_RELAXATION_SCALE = 0.75;
double STEP2_MICRO_MAX_DELTA_SCALE = 0.70;
double STEP2_MICRO_PATCH_REFINEMENT_SCALE = 0.60;
double STEP2_MICRO_FACTOR_RANGE_SCALE = 0.70;
int STEP2_ACCEPT_SMALL_GAINS_MODE = 0;
double STEP2_MIN_ERROR_DROP_ABS = 0.005;
double STEP2_MIN_ERROR_DROP_PER_ELEMENT = 0.0;
double STEP2_ACCEPTANCE_GROWTH_WEIGHT = 0.10;
int PATCH_LOCAL_ELEMENT_BUDGET_MODE = 1;
double PATCH_LOCAL_ELEMENT_BUDGET_BASE = 1800.0;
double PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_RANK = 0.75;
double PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_EFFICIENCY = 1.25;
double PATCH_LOCAL_BUDGET_H_SCALE = 1.10;
double PATCH_LOCAL_BUDGET_HARD_CAP = 2600.0;
int PATCH_GENERATION_CONTROL_MODE = 1;
double PATCH_GENERATION_BUDGET_PRESSURE_START = 0.70;
double PATCH_GENERATION_MICRO_H_SCALE = 1.10;
double PATCH_GENERATION_CONSTRAINED_H_SCALE = 1.18;
int PATCH_GENERATION_TOP_RANK_ONLY_MODE = 1;
int STEP_TARGET_ELEMENT_GROWTH_MODE = 1;
double STEP2_TARGET_ELEMENT_GROWTH = 1.8;
double STEP3PLUS_TARGET_ELEMENT_GROWTH = 1.5;
double STEP_TARGET_GROWTH_H_SCALE = 1.10;
int STEP_ACCEPT_EFFICIENCY_MODE = 1;
double STEP_ACCEPT_MIN_EFFICIENCY = 1.0e-6;
double STEP_ACCEPT_MAX_ELEMENT_GROWTH_SOFT = 2.0;
double STEP_ACCEPT_QUALITY_DROP_TOLERANCE = 0.02;
int BUDGET_DRIVEN_ADAPTATION = 0;
int STEP_ELEMENT_TARGET_MODE = 0;
double STEP1_TARGET_ELEMENT_GROWTH = 8.0;
double STEP_ELEMENT_TARGET_MIN = 0.0;
double STEP_ELEMENT_TARGET_MAX = 0.0;
int PATCH_BUDGET_ALLOCATION_MODE = 0;
double PATCH_BUDGET_ERROR_WEIGHT = 1.0;
double PATCH_BUDGET_EFFICIENCY_WEIGHT = 0.5;
double PATCH_BUDGET_QUALITY_WEIGHT = 0.3;
double PATCH_BUDGET_MIN_SHARE = 0.01;
int PATCH_BUDGET_TOPK_ONLY_MODE = 0;
int CURVE_POINT_BUDGET_MODE = 0;
double CURVE_POINT_GROWTH_STEP1 = 2.5;
double CURVE_POINT_GROWTH_STEPN = 2.4;
double CURVE_POINT_BUDGET_BLEND = 0.7;
int CURVE_POINT_MIN = 2;
int CURVE_POINT_MAX = 128;
int PATCH_QUADTREE_CAP_MODE = 0;
int PATCH_QUADTREE_DEPTH_STEP1 = 5;
int PATCH_QUADTREE_DEPTH_STEPN = 4;
// Se 1, profundidade < 0 vinda do gerador vira PATCH_QUADTREE_DEPTH_STEP1/STPN no
// adapter (malha de domínio); se 0, mantém -1 (quadtree sem teto explícito).
int ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH = 1;
double PATCH_QUADTREE_MIN_H_SCALE = 1.0;
double PATCH_QUADTREE_NEIGHBOR_RELAX = 1.0;
int PATCH_QUADTREE_TEMPLATE_LIMIT_MODE = 0;
double STEP_ACCEPT_TARGET_GROWTH_TOLERANCE = 0.35;
double STEP_ACCEPT_ERROR_DROP_MIN = 0.0;
double STEP_ACCEPT_BUDGET_MISS_PENALTY = 0.1;
int PATCH_CONSISTENCY_MODE = 0;
double PATCH_CONSISTENCY_AREA_TOL = 0.20;
double PATCH_CONSISTENCY_ERROR_TOL = 0.25;
double PATCH_CONSISTENCY_CURVATURE_TOL = 0.25;
double PATCH_CONSISTENCY_QUALITY_TOL = 0.20;
int PATCH_CONSISTENCY_NEIGHBOR_ONLY = 1;
double PATCH_CONSISTENCY_MAX_BUDGET_RATIO_STEP2 = 1.5;
double PATCH_CONSISTENCY_MAX_BUDGET_RATIO_STEPN = 2.0;
double PATCH_CONSISTENCY_MIN_GROUP_SHARE = 0.75;
double PATCH_CONSISTENCY_H_CLAMP_RATIO = 1.25;
int PATCH_CONSISTENCY_DEPTH_CLAMP = 1;
int CURVE_CONSISTENCY_MODE = 0;
double CURVE_CONSISTENCY_MAX_POINT_RATIO_STEP2 = 1.5;
int CURVE_CONSISTENCY_PRIORITY_BONUS = 1;
double CURVE_CONSISTENCY_GROUP_BLEND = 0.65;
double STEP2_CONSISTENCY_WEIGHT = 0.55;
int STEP2_GROUP_MIN_PATCHES = 2;
int STEP2_GROUP_NEIGHBOR_PROTECTION = 1;
int STEP2_DISABLE_GROUP_COARSEN_IF_UNBALANCED = 1;
int STEP_ACCEPT_CONSISTENCY_MODE = 0;
double STEP_ACCEPT_CONSISTENCY_PENALTY_WEIGHT = 0.35;
double STEP_ACCEPT_MAX_GROUP_DISPERSION_STEP2 = 0.45;
std::string ADAPTIVE_MODE = "adaptive_stable";
double ADAPTIVE_INTENSITY = 0.45;
double ADAPTIVE_QUALITY_PRIORITY = 0.75;
int ADAPTIVE_MAX_STEPS = 6;
double ADAPTIVE_TARGET_GROWTH = 1.6;
int ADAPTIVE_CURRENT_STEP = -1;
int ADAPTIVE_CURRENT_RETRY = 0;
int ENABLE_SHARED_CURVE_SYNC = 1;
int ENABLE_HYBRID_RECONSTRUCTION = 1;
int WRITE_RUNTIME_SUMMARY = 1;
double DISCRETIZATION_CURVE_FACTOR = 1.414213562;
double DISCRETIZATION_CURVE_FACTOR_INTERNAL = sqrt(DISCRETIZATION_CURVE_FACTOR);
double TIME_READ_FILE = 0.0;
// Limite de seguranca por chamada FindUV (Newton amortecido + parada 3D).
unsigned int I_MAX = 2048;

// Estatisticas globais FindUV (Bezier + Hermite); diagnostico fim de corrida.
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0};
std::atomic<unsigned long long> FINDUV_IMAX_EXITS{0};
double MAX_TIME = 999999999;
int MAX_THREADS = 1;
std::set<PointAdaptive *> LIST_ALL_POINTS_MODEL;
std::set<SubMesh *> LIST_ALL_SUB_MESH_MODEL;
std::string NAME_MODEL;
std::string INPUT_MODEL;
std::string NUMBER_PROCESS;
std::string WRITE_MESH;
std::string USE_TEMPLATE;

namespace {
struct RuntimeConfig {
  int num_processes = 1;
  int num_threads = 1;
  std::string input_model;
  std::string write_mode = "h";
  std::string output_prefix;
  std::string use_template = "n";
  std::string adaptive_mode = "adaptive_stable";
  double adaptive_intensity = 0.45;
  double adaptive_quality_priority = 0.75;
  int adaptive_max_iterations = 6;
  double adaptive_target_growth = 1.6;
  double epsylon = EPSYLON;
  double min_improvement = MIN_IMPROVEMENT;
  int patience = PATIENCE;
  double tol_local = TOL_LOCAL;
  double smoothing_laplacian_number = SMOOTHING_LAPLACIAN_NUMBER;
  double smoothing_laplacian_factor = SMOOTHING_LAPLACIAN_FACTOR;
  double adaptation_relaxation = ADAPTATION_RELAXATION;
  double adaptation_max_delta = ADAPTATION_MAX_DELTA;
  int adaptive_retry_count = 0;
  double adaptive_retry_shrink = 1.0;
  double patch_factor_min = PATCH_FACTOR_MIN;
  double patch_factor_max = PATCH_FACTOR_MAX;
  double patch_refinement_strength = 0.22;
  double patch_coarsening_strength = PATCH_COARSENING_STRENGTH;
  int curve_adaptation_policy = CURVE_ADAPTATION_POLICY;
  double curve_adaptation_blend = CURVE_ADAPTATION_BLEND;
  double curve_factor_sensitivity = CURVE_FACTOR_SENSITIVITY;
  int curve_point_budget_mode = CURVE_POINT_BUDGET_MODE;
  double curve_point_growth_step1 = CURVE_POINT_GROWTH_STEP1;
  double curve_point_growth_stepn = CURVE_POINT_GROWTH_STEPN;
  double curve_point_budget_blend = CURVE_POINT_BUDGET_BLEND;
  int curve_point_min = CURVE_POINT_MIN;
  int curve_point_max = CURVE_POINT_MAX;
  double quadtree_face_quality_threshold = QUADTREE_FACE_QUALITY_THRESHOLD;
  double quadtree_low_quality_h_factor = QUADTREE_LOW_QUALITY_H_FACTOR;
  int aft_local_postprocess_passes = AFT_LOCAL_POSTPROCESS_PASSES;
  double aft_local_postprocess_quality_threshold =
      AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD;
  double aft_local_postprocess_blend = AFT_LOCAL_POSTPROCESS_BLEND;
  double step2_eligible_refinement_damp = 0.65;
  int patch_quadtree_depth_step1 = 5;
  int patch_quadtree_depth_stepn = 4;
  double patch_quadtree_min_h_scale = PATCH_QUADTREE_MIN_H_SCALE;
  int adapter_resolve_negative_quadtree_depth = 1;
  int enable_shared_curve_sync = 1;
  int enable_hybrid_reconstruction = 1;
  int write_runtime_summary = 1;
};

std::string Trim(const std::string& value) {
  size_t start = 0;
  while (start < value.size() &&
         std::isspace(static_cast<unsigned char>(value[start])) != 0) {
    ++start;
  }
  size_t end = value.size();
  while (end > start &&
         std::isspace(static_cast<unsigned char>(value[end - 1])) != 0) {
    --end;
  }
  return value.substr(start, end - start);
}

std::unordered_map<std::string, std::string> ReadConfigFile(
    const std::string& path) {
  std::ifstream file(path.c_str());
  std::unordered_map<std::string, std::string> values;
  if (!file.is_open()) {
    throw std::runtime_error("Nao foi possivel abrir config: " + path);
  }
  std::string line;
  while (std::getline(file, line)) {
    const std::string trimmed = Trim(line);
    if (trimmed.empty() || trimmed[0] == '#') {
      continue;
    }
    const size_t equal_pos = trimmed.find('=');
    if (equal_pos == std::string::npos) {
      continue;
    }
    const std::string key = Trim(trimmed.substr(0, equal_pos));
    const std::string value = Trim(trimmed.substr(equal_pos + 1));
    if (!key.empty()) {
      values[key] = value;
    }
  }
  return values;
}

std::string GetConfigValue(
    const std::unordered_map<std::string, std::string>& values,
    const std::string& key, const std::string& fallback = "") {
  const auto it = values.find(key);
  return (it != values.end()) ? it->second : fallback;
}

RuntimeConfig LoadRuntimeConfig(const std::string& path) {
  const auto values = ReadConfigFile(path);
  RuntimeConfig config;
  config.num_processes = std::max(
      1, atoi(GetConfigValue(values, "NUM_PROCESSES", "1").c_str()));
  config.num_threads =
      std::max(1, atoi(GetConfigValue(values, "NUM_THREADS", "1").c_str()));
  config.input_model = GetConfigValue(values, "INPUT_MODEL");
  config.write_mode = GetConfigValue(values, "WRITE_MODE", "h");
  config.output_prefix = GetConfigValue(values, "OUTPUT_PREFIX");
  config.use_template = GetConfigValue(values, "USE_TEMPLATE", "y");
  config.adaptive_mode = GetConfigValue(
      values, "ADAPTIVE_MODE", "adaptive_stable");
  config.adaptive_intensity = atof(
      GetConfigValue(values, "ADAPTIVE_INTENSITY", "0.45").c_str());
  config.adaptive_quality_priority = atof(
      GetConfigValue(values, "ADAPTIVE_QUALITY_PRIORITY", "0.75").c_str());
  const std::string max_iterations = GetConfigValue(
      values, "ADAPTIVE_MAX_ITERATIONS",
      GetConfigValue(values, "ADAPTIVE_MAX_STEPS", "6"));
  config.adaptive_max_iterations = std::max(2, atoi(max_iterations.c_str()));
  config.adaptive_target_growth = atof(
      GetConfigValue(values, "ADAPTIVE_TARGET_GROWTH", "1.6").c_str());
  config.epsylon = atof(GetConfigValue(values, "EPSYLON", "0.0000001").c_str());
  config.min_improvement =
      atof(GetConfigValue(values, "MIN_IMPROVEMENT", "0.01").c_str());
  config.patience =
      std::max(1, atoi(GetConfigValue(values, "PATIENCE", "2").c_str()));
  config.tol_local = atof(GetConfigValue(values, "TOL_LOCAL", "0.0000001").c_str());
  config.smoothing_laplacian_number =
      atof(GetConfigValue(values, "SMOOTHING_LAPLACIAN_NUMBER", "7").c_str());
  config.smoothing_laplacian_factor =
      atof(GetConfigValue(values, "SMOOTHING_LAPLACIAN_FACTOR", "0.5").c_str());
  config.adaptation_relaxation = atof(
      GetConfigValue(values, "ADAPTATION_RELAXATION", "1.0").c_str());
  config.adaptation_max_delta = atof(
      GetConfigValue(values, "ADAPTATION_MAX_DELTA", "0.10").c_str());
  config.adaptive_retry_count = std::max(
      0, atoi(GetConfigValue(values, "ADAPTIVE_RETRY_COUNT", "0").c_str()));
  config.adaptive_retry_shrink = atof(
      GetConfigValue(values, "ADAPTIVE_RETRY_SHRINK", "1.0").c_str());
  config.patch_factor_min = atof(
      GetConfigValue(values, "PATCH_FACTOR_MIN", "0.80").c_str());
  config.patch_factor_max = atof(
      GetConfigValue(values, "PATCH_FACTOR_MAX", "1.12").c_str());
  config.patch_refinement_strength = atof(
      GetConfigValue(values, "PATCH_REFINEMENT_STRENGTH", "0.22").c_str());
  config.patch_coarsening_strength = atof(
      GetConfigValue(values, "PATCH_COARSENING_STRENGTH", "0.10").c_str());
  config.curve_adaptation_policy = atoi(
      GetConfigValue(values, "CURVE_ADAPTATION_POLICY", "0").c_str());
  config.curve_adaptation_blend = atof(
      GetConfigValue(values, "CURVE_ADAPTATION_BLEND", "0.75").c_str());
  config.curve_factor_sensitivity = atof(
      GetConfigValue(values, "CURVE_FACTOR_SENSITIVITY", "1.0").c_str());
  config.curve_point_budget_mode = atoi(
      GetConfigValue(values, "CURVE_POINT_BUDGET_MODE", "0").c_str());
  config.curve_point_growth_step1 = atof(
      GetConfigValue(values, "CURVE_POINT_GROWTH_STEP1", "2.5").c_str());
  config.curve_point_growth_stepn = atof(
      GetConfigValue(values, "CURVE_POINT_GROWTH_STEPN", "1.4").c_str());
  config.curve_point_budget_blend = atof(
      GetConfigValue(values, "CURVE_POINT_BUDGET_BLEND", "0.7").c_str());
  config.curve_point_min = std::max(
      2, atoi(GetConfigValue(values, "CURVE_POINT_MIN", "2").c_str()));
  config.curve_point_max = std::max(
      config.curve_point_min,
      atoi(GetConfigValue(values, "CURVE_POINT_MAX", "128").c_str()));
  config.quadtree_face_quality_threshold = atof(
      GetConfigValue(values, "QUADTREE_FACE_QUALITY_THRESHOLD", "0.0").c_str());
  config.quadtree_low_quality_h_factor = atof(
      GetConfigValue(values, "QUADTREE_LOW_QUALITY_H_FACTOR", "1.0").c_str());
  config.aft_local_postprocess_passes = std::max(
      0, atoi(GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_PASSES", "0").c_str()));
  config.aft_local_postprocess_quality_threshold = atof(
      GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD", "0.35").c_str());
  config.aft_local_postprocess_blend = atof(
      GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_BLEND", "0.35").c_str());
  config.step2_eligible_refinement_damp = atof(
      GetConfigValue(values, "STEP2_ELIGIBLE_REFINEMENT_DAMP", "0.65").c_str());
  config.patch_quadtree_depth_step1 = std::max(
      0, std::min(32, atoi(
              GetConfigValue(values, "PATCH_QUADTREE_DEPTH_STEP1", "5").c_str())));
  config.patch_quadtree_depth_stepn = std::max(
      0, std::min(32, atoi(
              GetConfigValue(values, "PATCH_QUADTREE_DEPTH_STEPN", "4").c_str())));
  config.patch_quadtree_min_h_scale = atof(
      GetConfigValue(values, "PATCH_QUADTREE_MIN_H_SCALE", "1.0").c_str());
  config.adapter_resolve_negative_quadtree_depth =
      atoi(GetConfigValue(values, "ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH", "1")
               .c_str()) != 0
          ? 1
          : 0;
  config.enable_shared_curve_sync =
      atoi(GetConfigValue(values, "ENABLE_SHARED_CURVE_SYNC", "1").c_str()) != 0
          ? 1
          : 0;
  config.enable_hybrid_reconstruction =
      atoi(GetConfigValue(values, "ENABLE_HYBRID_RECONSTRUCTION", "1").c_str()) != 0
          ? 1
          : 0;
  config.write_runtime_summary =
      atoi(GetConfigValue(values, "WRITE_RUNTIME_SUMMARY", "1").c_str()) != 0
          ? 1
          : 0;

  if (config.input_model.empty() || config.output_prefix.empty()) {
    throw std::runtime_error(
        "Config incompleta: INPUT_MODEL e OUTPUT_PREFIX sao obrigatorios");
  }

  config.adaptive_intensity =
      std::max(0.0, std::min(1.0, config.adaptive_intensity));
  config.adaptive_quality_priority =
      std::max(0.0, std::min(1.0, config.adaptive_quality_priority));
  config.adaptive_target_growth = std::max(1.0, config.adaptive_target_growth);
  config.adaptation_relaxation =
      std::max(0.0, std::min(1.0, config.adaptation_relaxation));
  config.adaptation_max_delta = std::max(0.0, config.adaptation_max_delta);
  config.adaptive_retry_shrink =
      std::max(0.05, std::min(1.0, config.adaptive_retry_shrink));
  config.patch_factor_min = std::max(0.1, config.patch_factor_min);
  config.patch_factor_max =
      std::max(config.patch_factor_min, config.patch_factor_max);
  config.patch_refinement_strength =
      std::max(0.0, std::min(1.0, config.patch_refinement_strength));
  config.patch_coarsening_strength =
      std::max(0.0, std::min(1.0, config.patch_coarsening_strength));
  config.curve_adaptation_blend =
      std::max(0.0, std::min(1.0, config.curve_adaptation_blend));
  config.curve_factor_sensitivity = std::max(0.0, config.curve_factor_sensitivity);
  config.curve_point_growth_step1 = std::max(1.0, config.curve_point_growth_step1);
  config.curve_point_growth_stepn = std::max(1.0, config.curve_point_growth_stepn);
  config.curve_point_budget_blend =
      std::max(0.0, std::min(1.0, config.curve_point_budget_blend));
  config.quadtree_face_quality_threshold =
      std::max(0.0, std::min(1.0, config.quadtree_face_quality_threshold));
  config.quadtree_low_quality_h_factor =
      std::max(0.1, std::min(1.5, config.quadtree_low_quality_h_factor));
  config.aft_local_postprocess_quality_threshold =
      std::max(0.0, std::min(1.0, config.aft_local_postprocess_quality_threshold));
  config.aft_local_postprocess_blend =
      std::max(0.0, std::min(1.0, config.aft_local_postprocess_blend));
  config.patch_quadtree_min_h_scale =
      std::max(0.5, std::min(1.5, config.patch_quadtree_min_h_scale));
  config.step2_eligible_refinement_damp =
      std::max(0.0, std::min(1.0, config.step2_eligible_refinement_damp));
  return config;
}

void ApplyRuntimeConfig(const RuntimeConfig& config) {
  INPUT_MODEL = config.input_model;
  WRITE_MESH = config.write_mode;
  NAME_MODEL = config.output_prefix;
  USE_TEMPLATE = config.use_template;
  EPSYLON = config.epsylon;
  MIN_IMPROVEMENT = config.min_improvement;
  PATIENCE = config.patience;
  TOL_LOCAL = config.tol_local;
  SMOOTHING_LAPLACIAN_NUMBER =
      std::max(5.0, std::min(7.0, config.smoothing_laplacian_number));
  SMOOTHING_LAPLACIAN_FACTOR = config.smoothing_laplacian_factor;
  ADAPTATION_RELAXATION = config.adaptation_relaxation;
  ADAPTATION_MAX_DELTA = config.adaptation_max_delta;
  ADAPTIVE_MODE = config.adaptive_mode;
  ADAPTIVE_INTENSITY = config.adaptive_intensity;
  ADAPTIVE_QUALITY_PRIORITY = config.adaptive_quality_priority;
  ADAPTIVE_MAX_STEPS = config.adaptive_max_iterations;
  ADAPTIVE_TARGET_GROWTH = config.adaptive_target_growth;
  ADAPTIVE_RETRY_COUNT = config.adaptive_retry_count;
  ADAPTIVE_RETRY_SHRINK = config.adaptive_retry_shrink;
  PATCH_FACTOR_MIN = config.patch_factor_min;
  PATCH_FACTOR_MAX = config.patch_factor_max;
  PATCH_REFINEMENT_STRENGTH = config.patch_refinement_strength;
  PATCH_COARSENING_STRENGTH = config.patch_coarsening_strength;
  CURVE_ADAPTATION_POLICY = config.curve_adaptation_policy;
  CURVE_ADAPTATION_BLEND = config.curve_adaptation_blend;
  CURVE_FACTOR_SENSITIVITY = config.curve_factor_sensitivity;
  CURVE_POINT_BUDGET_MODE = config.curve_point_budget_mode;
  CURVE_POINT_GROWTH_STEP1 = config.curve_point_growth_step1;
  CURVE_POINT_GROWTH_STEPN = config.curve_point_growth_stepn;
  CURVE_POINT_BUDGET_BLEND = config.curve_point_budget_blend;
  CURVE_POINT_MIN = config.curve_point_min;
  CURVE_POINT_MAX = config.curve_point_max;
  QUADTREE_FACE_QUALITY_THRESHOLD = config.quadtree_face_quality_threshold;
  QUADTREE_LOW_QUALITY_H_FACTOR = config.quadtree_low_quality_h_factor;
  AFT_LOCAL_POSTPROCESS_PASSES = config.aft_local_postprocess_passes;
  AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD =
      config.aft_local_postprocess_quality_threshold;
  AFT_LOCAL_POSTPROCESS_BLEND = config.aft_local_postprocess_blend;
  STEP2_ELIGIBLE_REFINEMENT_DAMP = config.step2_eligible_refinement_damp;
  PATCH_QUADTREE_DEPTH_STEP1 = config.patch_quadtree_depth_step1;
  PATCH_QUADTREE_DEPTH_STEPN = config.patch_quadtree_depth_stepn;
  PATCH_QUADTREE_MIN_H_SCALE = config.patch_quadtree_min_h_scale;
  ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH =
      config.adapter_resolve_negative_quadtree_depth;
  ENABLE_SHARED_CURVE_SYNC = config.enable_shared_curve_sync;
  ENABLE_HYBRID_RECONSTRUCTION = config.enable_hybrid_reconstruction;
  WRITE_RUNTIME_SUMMARY = config.write_runtime_summary;
  if (ENABLE_HYBRID_RECONSTRUCTION == 0) {
    USE_TEMPLATE = "n";
  }
}
}  // namespace

// argv[0] = "executavel: ./apmesh",
// argv[1] = "n° de process"
// argv[2] = "n° threads",
// argv[3] = "INPUT_MODEL",       OBS: Projects-> Comands line arguments ->
// ../../apMesh/INPUT_MODEL/mountain_289_patches.bp
// argv[4] = "WRITE_MESH" (m|q|h)
// argv[5] = "NAME_MODEL"
// argv[6] = "USE_TEMPLATE" -> y or n

int main(int argc, char **argv) {
#if USE_MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &SIZE_MPI);
  MPI_Comm_rank(MPI_COMM_WORLD, &RANK_MPI);
  MPI_Status status;

#endif

  const bool config_mode =
      (argc >= 3 && std::string(argv[1]) == "--config");
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
      std::vector<std::string> synthetic_args_storage = {
          argv[0],
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
        cout << "Metodo por config: mode=" << ADAPTIVE_MODE
             << ", input=" << INPUT_MODEL
             << ", output=" << NAME_MODEL
             << ", threads=" << config.num_threads << endl;
      }

      GeneratorAdaptive generator;
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
          const double pct = 100.0 * static_cast<double>(ix) /
                             static_cast<double>(fc);
          std::cout << "[FindUV] chamadas=" << fc
                    << " saidas_por_I_MAX=" << ix << " (" << std::fixed
                    << std::setprecision(2) << pct << "%)" << std::endl;
        }
      }
      return run_rc;
    } catch (const std::exception& ex) {
      cout << "Erro ao carregar config: " << ex.what() << endl;
      return -1;
    }
  }

  cout << "Erro: execucao legada por argv foi removida." << endl;
  cout << "Use: apmesh --config <arquivo.conf>" << endl;
#if USE_MPI
  MPI_Finalize();
#endif
  return -1;
}
