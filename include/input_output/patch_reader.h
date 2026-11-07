#ifndef INPUT_OUTPUT_PATCH_READER_H
#define INPUT_OUTPUT_PATCH_READER_H

#include <fstream>
#include <iostream>
#include <list>
#include <memory>
#include <sstream>

#include "../data/model.h"
#include "../data/patch/patch_bezier.h"
#include "../data/patch/patch_hermite.h"
#include "../data/point_adaptive.h"

extern std::string INPUT_MODEL;
extern int RANK_MPI;

class PatchReader {
public:
  PatchReader();
  ~PatchReader();

  std::list<PatchBezier*> ParsePatchesBezier();
  std::list<PatchBezier*> LoaderRibFile();
  // Each call transfers its control-only patches to one owning result.
  // Partial reads and exceptions release every unpublished patch.
  std::list<std::unique_ptr<PatchBezier>> LoaderBPFile(string filename);
  std::list<PatchHermite*> LoaderBPFileHermite();
  std::list<PatchBezier*> LoaderOBJFile();
  std::list<PatchBezier*> OrderVectorToListBezierPatches(std::vector<double>);
  PointAdaptive GetPointVectorControlPoints(std::vector<PointAdaptive>, unsigned long);
  // Each call transfers independent control-only owners; partial reads release them.
  std::list<std::unique_ptr<PatchBezier>> LoaderBezierPatchFile(string fileName);
  Geometry* ReaderFilePatches(Geometry* geometry, string fileName);

private:
  std::list<std::unique_ptr<PatchBezier>> ReadBezierControlPatches(const std::string& filename,
                                                                   const char* empty_message);

  static PointAdaptive FindControlPoint(const std::vector<PointAdaptive>& vectorPoints,
                                        unsigned long idPoint);

protected:
  std::list<PatchBezier*> patches_;
  std::list<PatchHermite*> patches_hermite_;
  PatchBezier* patch_;
  PatchHermite* patch_hermite_;
};

#endif // INPUT_OUTPUT_PATCH_READER_H
