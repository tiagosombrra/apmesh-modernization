#include "estimate/charge_estimate_process.h"

#include <array>

// Samples are automatic values. Only the historical populated prefix is read.
double ChargeEstimateProcess::CalculateKaMedioPatch(PatchBezier* patch, int points) {
  if (points < 4) {
    cout << "At least 4 curvature samples are required; historical sample levels are 4, 9, 17 and "
            "25."
         << endl;
    return 0.0;
  }

  std::array<double, 25> curvatures;
  int i = 0;

  if (points <= 25) {
    if (points >= 4) {
      PointAdaptive sample_a = patch->Parameterize(0.25, 0.25);

      PointAdaptive sample_b = patch->Parameterize(0.75, 0.25);

      PointAdaptive sample_c = patch->Parameterize(0.25, 0.75);

      PointAdaptive sample_d = patch->Parameterize(0.75, 0.75);

      CurvatureAnalytical analytical_a(sample_a, *patch);
      CurvatureAnalytical analytical_b(sample_b, *patch);
      CurvatureAnalytical analytical_c(sample_c, *patch);
      CurvatureAnalytical analytical_d(sample_d, *patch);

      double curvature_a = analytical_a.CalculateGaussCurvature();
      if (fabs(curvature_a) < 0.0001) {
        curvature_a = analytical_a.CalculateMeanCurvature();
      }

      curvatures[i] = fabs(curvature_a);
      i++;

      double curvature_b = analytical_b.CalculateGaussCurvature();
      if (fabs(curvature_b) < 0.0001) {
        curvature_b = analytical_b.CalculateMeanCurvature();
      }

      curvatures[i] = fabs(curvature_b);
      i++;

      double curvature_c = analytical_c.CalculateGaussCurvature();
      if (fabs(curvature_c) < 0.0001) {
        curvature_c = analytical_c.CalculateMeanCurvature();
      }

      curvatures[i] = fabs(curvature_c);
      i++;

      double curvature_d = analytical_d.CalculateGaussCurvature();
      if (fabs(curvature_d) < 0.0001) {
        curvature_d = analytical_d.CalculateMeanCurvature();
      }

      curvatures[i] = fabs(curvature_d);
      i++;

      if (points >= 9) {
        PointAdaptive sample_e = patch->Parameterize(0.5, 0.5);

        PointAdaptive sample_f = patch->Parameterize(0.0, 0.0);

        PointAdaptive sample_g = patch->Parameterize(1.0, 0.0);

        PointAdaptive sample_h = patch->Parameterize(0.0, 1.0);

        PointAdaptive sample_i = patch->Parameterize(1.0, 1.0);

        CurvatureAnalytical analytical_e(sample_e, *patch);
        CurvatureAnalytical analytical_f(sample_f, *patch);
        CurvatureAnalytical analytical_g(sample_g, *patch);
        CurvatureAnalytical analytical_h(sample_h, *patch);
        CurvatureAnalytical analytical_i(sample_i, *patch);

        double curvature_e = analytical_e.CalculateGaussCurvature();
        if (fabs(curvature_e) < 0.0001) {
          curvature_e = analytical_e.CalculateMeanCurvature();
        }

        curvatures[i] = fabs(curvature_e);
        i++;

        double curvature_f = analytical_f.CalculateGaussCurvature();
        if (fabs(curvature_f) < 0.0001) {
          curvature_f = analytical_f.CalculateMeanCurvature();
        }

        curvatures[i] = fabs(curvature_f);
        i++;

        double curvature_g = analytical_g.CalculateGaussCurvature();
        if (fabs(curvature_g) < 0.0001) {
          curvature_g = analytical_g.CalculateMeanCurvature();
        }

        curvatures[i] = fabs(curvature_g);
        i++;

        double curvature_h = analytical_h.CalculateGaussCurvature();
        if (fabs(curvature_h) < 0.0001) {
          curvature_h = analytical_h.CalculateMeanCurvature();
        }

        curvatures[i] = fabs(curvature_h);
        i++;

        double curvature_i = analytical_i.CalculateGaussCurvature();
        if (fabs(curvature_i) < 0.0001) {
          curvature_i = analytical_i.CalculateMeanCurvature();
        }

        curvatures[i] = fabs(curvature_i);
        i++;

        if (points >= 17) {
          PointAdaptive sample_j = patch->Parameterize(0.125, 0.125);

          PointAdaptive sample_l = patch->Parameterize(0.5, 0.125);

          PointAdaptive sample_m = patch->Parameterize(0.875, 0.125);

          PointAdaptive sample_n = patch->Parameterize(0.125, 0.5);

          PointAdaptive sample_o = patch->Parameterize(0.875, 0.5);

          PointAdaptive sample_p = patch->Parameterize(0.125, 0.875);

          PointAdaptive sample_q = patch->Parameterize(0.5, 0.875);

          PointAdaptive sample_r = patch->Parameterize(0.875, 0.875);

          CurvatureAnalytical analytical_j(sample_j, *patch);
          CurvatureAnalytical analytical_l(sample_l, *patch);
          CurvatureAnalytical analytical_m(sample_m, *patch);
          CurvatureAnalytical analytical_n(sample_n, *patch);
          CurvatureAnalytical analytical_o(sample_o, *patch);
          CurvatureAnalytical analytical_p(sample_p, *patch);
          CurvatureAnalytical analytical_q(sample_q, *patch);
          CurvatureAnalytical analytical_r(sample_r, *patch);

          double curvature_j = analytical_j.CalculateGaussCurvature();
          if (fabs(curvature_j) < 0.0001) {
            curvature_j = analytical_j.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_j);
          i++;

          double curvature_l = analytical_l.CalculateGaussCurvature();
          if (fabs(curvature_l) < 0.0001) {
            curvature_l = analytical_l.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_l);
          i++;

          double curvature_m = analytical_m.CalculateGaussCurvature();
          if (fabs(curvature_m) < 0.0001) {
            curvature_m = analytical_m.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_m);
          i++;

          double curvature_n = analytical_n.CalculateGaussCurvature();
          if (fabs(curvature_n) < 0.0001) {
            curvature_n = analytical_n.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_n);
          i++;

          double curvature_o = analytical_o.CalculateGaussCurvature();
          if (fabs(curvature_o) < 0.0001) {
            curvature_o = analytical_o.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_o);
          i++;

          double curvature_p = analytical_p.CalculateGaussCurvature();
          if (fabs(curvature_p) < 0.0001) {
            curvature_p = analytical_p.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_p);
          i++;

          double curvature_q = analytical_q.CalculateGaussCurvature();
          if (fabs(curvature_q) < 0.0001) {
            curvature_q = analytical_q.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_q);
          i++;

          double curvature_r = analytical_r.CalculateGaussCurvature();
          if (fabs(curvature_r) < 0.0001) {
            curvature_r = analytical_r.CalculateMeanCurvature();
          }

          curvatures[i] = fabs(curvature_r);
          i++;

          if (points == 25) {
            PointAdaptive sample_s = patch->Parameterize(0.25, 0.0);

            PointAdaptive sample_t = patch->Parameterize(0.75, 0.0);

            PointAdaptive sample_u = patch->Parameterize(0.0, 0.25);

            PointAdaptive sample_v = patch->Parameterize(1.0, 0.25);

            PointAdaptive sample_w = patch->Parameterize(0.0, 0.75);

            PointAdaptive sample_x = patch->Parameterize(1.0, 0.75);

            PointAdaptive sample_y = patch->Parameterize(0.25, 1.0);

            PointAdaptive sample_z = patch->Parameterize(0.75, 1.0);

            CurvatureAnalytical analytical_s(sample_s, *patch);
            CurvatureAnalytical analytical_t(sample_t, *patch);
            CurvatureAnalytical analytical_u(sample_u, *patch);
            CurvatureAnalytical analytical_v(sample_v, *patch);
            CurvatureAnalytical analytical_w(sample_w, *patch);
            CurvatureAnalytical analytical_x(sample_x, *patch);
            CurvatureAnalytical analytical_y(sample_y, *patch);
            CurvatureAnalytical analytical_z(sample_z, *patch);

            double curvature_s = analytical_s.CalculateGaussCurvature();
            if (fabs(curvature_s) < 0.0001) {
              curvature_s = analytical_s.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_s);
            i++;

            double curvature_t = analytical_t.CalculateGaussCurvature();
            if (fabs(curvature_t) < 0.0001) {
              curvature_t = analytical_t.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_t);
            i++;

            double curvature_u = analytical_u.CalculateGaussCurvature();
            if (fabs(curvature_u) < 0.0001) {
              curvature_u = analytical_u.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_u);
            i++;

            double curvature_v = analytical_v.CalculateGaussCurvature();
            if (fabs(curvature_v) < 0.0001) {
              curvature_v = analytical_v.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_v);
            i++;

            double curvature_w = analytical_w.CalculateGaussCurvature();
            if (fabs(curvature_w) < 0.0001) {
              curvature_w = analytical_w.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_w);
            i++;

            double curvature_x = analytical_x.CalculateGaussCurvature();
            if (fabs(curvature_x) < 0.0001) {
              curvature_x = analytical_x.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_x);
            i++;

            double curvature_y = analytical_y.CalculateGaussCurvature();
            if (fabs(curvature_y) < 0.0001) {
              curvature_y = analytical_y.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_y);
            i++;

            double curvature_z = analytical_z.CalculateGaussCurvature();
            if (fabs(curvature_z) < 0.0001) {
              curvature_z = analytical_z.CalculateMeanCurvature();
            }

            curvatures[i] = fabs(curvature_z);
            i++;
          }
        }
      }
    }
  }

  double result = 0.0;
  for (int j = 0; j < i; j++) {
    result += curvatures[j];
  }

  return result / points;
}
