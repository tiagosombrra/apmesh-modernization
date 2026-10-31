#include "estimate/initial_mesh_estimate.h"
#include "estimate/triangle_count_estimate.h"
#include <memory>

#include "../../include/estimate/charge_estimate_process.h"

extern std::string INPUT_MODEL;

ChargeEstimateProcess::ChargeEstimateProcess()
    : minor_error_(10000), minor_degree_(0) {}

ChargeEstimateProcess::~ChargeEstimateProcess() {}

std::vector<PointAdaptive> ChargeEstimateProcess::InterpolateControlPointsCurve(
    const PointAdaptive p0, const PointAdaptive p1, const PointAdaptive p2,
    const PointAdaptive p3, const double u, const double v) {
  double a = 0.0, b = 0.0, c = 0.0, d = 0.0, det = 0.0;

  PointAdaptive q1;
  PointAdaptive q2;
  PointAdaptive pc1;
  PointAdaptive pc2;

  if ((u <= 0.0) || (u >= 1.0) || (v <= 0.0) || (v >= 1.0) || (u >= v)) {
    std::cout << "erro u or v out of range" << std::endl;
  }

  a = 3 * (1 - u) * (1 - u) * u;
  b = 3 * (1 - u) * u * u;
  c = 3 * (1 - v) * (1 - v) * v;
  d = 3 * (1 - v) * v * v;
  det = a * d - b * c;

  /* unnecessary, but just in case... */
  if (det == 0.0) {
    std::cout << "erro det == 0" << std::endl;
  }

  q1.SetX((p1.GetX() -
           ((1 - u) * (1 - u) * (1 - u) * p0.GetX() + u * u * u * p3.GetX())));
  q1.SetY((p1.GetY() -
           ((1 - u) * (1 - u) * (1 - u) * p0.GetY() + u * u * u * p3.GetY())));
  q1.SetZ((p1.GetZ() -
           ((1 - u) * (1 - u) * (1 - u) * p0.GetZ() + u * u * u * p3.GetZ())));

  q2.SetX((p2.GetX() -
           ((1 - v) * (1 - v) * (1 - v) * p0.GetX() + v * v * v * p3.GetX())));
  q2.SetY((p2.GetY() -
           ((1 - v) * (1 - v) * (1 - v) * p0.GetY() + v * v * v * p3.GetY())));
  q2.SetZ((p2.GetZ() -
           ((1 - v) * (1 - v) * (1 - v) * p0.GetZ() + v * v * v * p3.GetZ())));

  pc1.SetX((d * q1.GetX() - b * q2.GetX()));
  pc1.SetY((d * q1.GetY() - b * q2.GetY()));
  pc1.SetZ((d * q1.GetZ() - b * q2.GetZ()));

  pc1.SetX((pc1.GetX() / det));
  pc1.SetY((pc1.GetY() / det));
  pc1.SetZ((pc1.GetZ() / det));

  pc2.SetX(((-c) * q1.GetX() + a * q2.GetX()));
  pc2.SetY(((-c) * q1.GetY() + a * q2.GetY()));
  pc2.SetZ(((-c) * q1.GetZ() + a * q2.GetZ()));

  pc2.SetX((pc2.GetX() / det));
  pc2.SetY((pc2.GetY() / det));
  pc2.SetZ((pc2.GetZ() / det));

  std::vector<PointAdaptive> list_pcs;

  list_pcs.push_back(pc1);
  list_pcs.push_back(pc2);

  return list_pcs;
}

double ChargeEstimateProcess::CalculateAreaPatch(PatchBezier* patch,
                                                 int pointsGaussLegandre) {
  VectorAdaptive V;
  double I = 0.0;
  std::unique_ptr<double[]> beta(new double[pointsGaussLegandre]);
  std::unique_ptr<double[]> peso(new double[pointsGaussLegandre]);
  double u = 0.0, v = 0.0;

  switch (pointsGaussLegandre) {
    case 3: {
      // Gauss–Legendre, valores para 3 pontos
      beta[0] = -sqrt(3.0 / 5.0);
      beta[1] = 0.0;
      beta[2] = sqrt(3.0 / 5.0);
      peso[0] = 5.0 / 9.0;
      peso[1] = 8.0 / 9.0;
      peso[2] = 5.0 / 9.0;
      //   mult = 0.25;
      break;
    }

    case 4: {
      // Gauss–Legendre, valores para 4 pontos
      beta[0] = -0.861136;
      beta[1] = -0.339981;
      beta[2] = 0.339981;
      beta[3] = 0.861136;
      peso[0] = 0.347855;
      peso[1] = peso[2] = 0.652145;
      peso[3] = 0.347855;
      //  mult = 0.25;
      break;
    }
    case 5: {
      // Gauss–Legendre, valores para 5 pontos
      //  beta[0] = -sqrt(3.0/5.0); beta[1] = 0.0; beta[2] = sqrt(3.0/5.0);
      //  peso[0] = 5.0/9.0; peso[1] = 8.0/9.0; peso[2] = 5.0/9.0;
      //  mult = 0.;

      break;
    }
  }

  for (int i = 0; i < pointsGaussLegandre; ++i) {
    u = 0.5 * (1 + beta[i]);

    for (int j = 0; j < pointsGaussLegandre; ++j) {
      v = 0.5 * (1 + beta[j]);

      VectorAdaptive Pu = patch->Qu(u, v);
      VectorAdaptive Pv = patch->Qv(u, v);

      V.SetX(Pu.GetY() * Pv.GetZ() - Pu.GetZ() * Pv.GetY());
      V.SetY(Pu.GetZ() * Pv.GetX() - Pu.GetX() * Pv.GetZ());
      V.SetZ(Pu.GetX() * Pv.GetY() - Pu.GetY() * Pv.GetX());

      I = I +
          0.25 *
              ((sqrt(pow(V.GetX(), 2) + pow(V.GetY(), 2) + pow(V.GetZ(), 2))) *
               peso[i] * peso[j]);
    }
  }

  return I;
}

double ChargeEstimateProcess::CalculateAreaTriangleMedioRad(
    PatchBezier* patch) {
  double Kam = patch->GetKaMedio();

  // cout << "Kam " << Kam << endl;

  double raio = 1.0 / Kam;
  // cout << "Raio " << raio << endl;

  double rad = (1.0 / 20) * raio;

  // cout << "Rad " << rad << endl;

  // double lado = (rad * 180) / M_PI;

  // cout << "Lado " << lado << endl;

  double area = pow(rad, 2) * sqrt(3) / 4;

  // cout << "Area " << area << endl;

  return area;
}

long ChargeEstimateProcess::CalculateNumbersTriangle(PatchBezier* patch,
                                                     int degree) {
  return apmesh::estimation::CountEstimateTriangles(patch, degree);
}

// grau tem que ser multiplo de grau == 2^n
SubMesh* ChargeEstimateProcess::InitialMeshEstimate(PatchCoons* patch, int degree) {
  return apmesh::estimation::BuildInitialEstimateSubMesh(patch, degree).release();
}
