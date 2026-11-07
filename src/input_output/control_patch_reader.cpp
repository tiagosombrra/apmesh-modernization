#include "input_output/patch_reader.h"

#include <memory>
#include <utility>

PatchReader::PatchReader() = default;
PatchReader::~PatchReader() = default;

std::list<std::unique_ptr<PatchBezier>> PatchReader::LoaderBPFile(std::string filename) {
  return ReadBezierControlPatches(filename, "Error opening the .bp file");
}

std::list<std::unique_ptr<PatchBezier>>
PatchReader::ReadBezierControlPatches(const std::string& filename, const char* empty_message) {
  std::list<std::unique_ptr<PatchBezier>> patches;
  auto patch = std::make_unique<PatchBezier>();

  if (!filename.empty()) {
    std::ifstream fin(filename);
    // Propagate resource failures instead of indexing an incompletely parsed row.
    // Ordinary EOF/failbit behavior and legacy record interpretation are unchanged.
    fin.exceptions(std::ios::badbit);

    if (fin) {
      while (fin) {
        std::string line;
        std::vector<double> v;
        std::vector<PointAdaptive> vectorControlPoints;
        std::vector<long> p;
        long id_ponto = 0;

        while (std::getline(fin, line)) {
          if (line[0] == 'v') {
            line = line.erase(0, 1);
            std::istringstream iss(line);
            iss.exceptions(std::ios::badbit);
            double n;
            while (iss >> n) {
              v.push_back(n);
            }

            PointAdaptive ponto(v[0], v[1], v[2], id_ponto);
            id_ponto++;
            vectorControlPoints.push_back(ponto);
            v.erase(v.begin(), v.end());
          }

          if (line[0] == 'p') {
            line = line.erase(0, 1);
            std::istringstream iss(line);
            iss.exceptions(std::ios::badbit);
            long n;
            while (iss >> n) {
              p.push_back(n);
            }

            for (unsigned int i = 0; i < p.size(); i++) {
              if (i == 0) {
                patch->SetPt00(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 1) {
                patch->SetPt10(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 2) {
                patch->SetPt20(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 3) {
                patch->SetPt30(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 4) {
                patch->SetPt01(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 5) {
                patch->SetPt11(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 6) {
                patch->SetPt21(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 7) {
                patch->SetPt31(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 8) {
                patch->SetPt02(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 9) {
                patch->SetPt12(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 10) {
                patch->SetPt22(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 11) {
                patch->SetPt32(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 12) {
                patch->SetPt03(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 13) {
                patch->SetPt13(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 14) {
                patch->SetPt23(FindControlPoint(vectorControlPoints, p[i]));
              } else if (i == 15) {
                patch->SetPt33(FindControlPoint(vectorControlPoints, p[i]));
              }
            }

            p.erase(p.begin(), p.end());
            patches.push_back(std::move(patch));
            patch = std::make_unique<PatchBezier>();
          }
        }
      }
    } else {
      std::cout << "Error: file .bp is not readable." << std::endl;
    }

    fin.close();

  } else {
    std::cout << empty_message << std::endl;
  }

  return patches;
}

PointAdaptive PatchReader::GetPointVectorControlPoints(std::vector<PointAdaptive> vectorPoints,
                                                       unsigned long idPoint) {
  return FindControlPoint(vectorPoints, idPoint);
}

PointAdaptive PatchReader::FindControlPoint(const std::vector<PointAdaptive>& vectorPoints,
                                            unsigned long idPoint) {
  for (std::vector<PointAdaptive>::const_iterator it = vectorPoints.begin();
       it != vectorPoints.end(); ++it) {
    if ((*it).GetId() == idPoint) {
      return (*it);
    }
  }

  PointAdaptive ponto;
  return ponto;
}
