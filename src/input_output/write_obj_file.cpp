#include "../../include/input_output/write_obj_file.h"

WriteOBJFile::WriteOBJFile() {}

WriteOBJFile::~WriteOBJFile() {}

void WriteOBJFile::WriteCurvaturePatches(std::vector<double> patches,
                                         double max_value) {
  std::stringstream name_file;
  name_file << NAME_MODEL + "_analise_curvature_patches.log";

  std::ofstream file(name_file.str().c_str());

  file << "File Analise Curvature" << std::endl << std::endl;

  std::vector<double> vec_0_10;
  std::vector<double> vec_10_20;
  std::vector<double> vec_20_30;
  std::vector<double> vec_30_40;
  std::vector<double> vec_40_50;
  std::vector<double> vec_50_60;
  std::vector<double> vec_60_70;
  std::vector<double> vec_70_80;
  std::vector<double> vec_80_90;
  std::vector<double> vec_90_100;

  for (std::vector<double>::iterator it = patches.begin(); it != patches.end();
       it++) {
    double value;
    value = (*it) / max_value;
    // cout<<value<<endl;
    if (0.0 <= value and value <= 0.1) {
      vec_0_10.push_back(value);
    } else if (0.1 < value and value <= 0.2) {
      vec_10_20.push_back(value);
    } else if (0.2 < value and value <= 0.3) {
      vec_20_30.push_back(value);
    } else if (0.3 < value and value <= 0.4) {
      vec_30_40.push_back(value);
    } else if (0.4 < value and value <= 0.5) {
      vec_40_50.push_back(value);
    } else if (0.5 < value and value <= 0.6) {
      vec_50_60.push_back(value);
    } else if (0.6 < value and value <= 0.7) {
      vec_60_70.push_back(value);
    } else if (0.7 < value and value <= 0.8) {
      vec_70_80.push_back(value);
    } else if (0.8 < value and value <= 0.9) {
      vec_80_90.push_back(value);
    } else if (0.9 < value and value <= 1) {
      vec_90_100.push_back(value);
    }
  }

  file << vec_0_10.size() / (double)patches.size() << std::endl;
  file << vec_10_20.size() / (double)patches.size() << std::endl;
  file << vec_20_30.size() / (double)patches.size() << std::endl;
  file << vec_30_40.size() / (double)patches.size() << std::endl;
  file << vec_40_50.size() / (double)patches.size() << std::endl;
  file << vec_50_60.size() / (double)patches.size() << std::endl;
  file << vec_60_70.size() / (double)patches.size() << std::endl;
  file << vec_70_80.size() / (double)patches.size() << std::endl;
  file << vec_80_90.size() / (double)patches.size() << std::endl;
  file << vec_90_100.size() / (double)patches.size() << std::endl;

  file.flush();

  file.close();
}

bool WriteOBJFile::WriteMeshOBJFile(MeshAdaptive* mesh, unsigned int step,
                                    int process) {
  std::stringstream name_file;
  name_file << "mesh_";
  name_file << step;
  name_file << "_process_";
  name_file << process;
  name_file << ".obj";

  std::ofstream file(name_file.str().c_str());

  file << " File Wavefront OBJ generated apMesh" << std::endl << std::endl;

  time_t t = time(0);  // get time now
  struct tm* now = localtime(&t);
  file << "# File created: " << (now->tm_year + 1900) << '-'
       << (now->tm_mon + 1) << '-' << now->tm_mday << std::endl;

  unsigned long int Nv, Nt;
  Nv = Nt = 0;

  for (unsigned int i = 0; i < mesh->GetNumberSubMeshesAdaptive(); i++) {
    SubMesh* sub = mesh->GetSubMeshAdaptiveByPosition(i);

    Nv += sub->GetNumberNos();
    Nt += sub->GetNumberElements();
  }

  file << "# of vertices" << std::endl << Nv << std::endl << std::endl;

  for (unsigned int i = 0; i < mesh->GetNumberSubMeshesAdaptive(); i++) {
    SubMesh* sub = mesh->GetSubMeshAdaptiveByPosition(i);

    for (unsigned int j = 0; j < sub->GetNumberNos(); j++) {
      NodeAdaptive* n = sub->GetNoh(j);
      file << "v " << n->GetX() << " " << n->GetY() << " " << n->GetZ() << std::endl;
    }
  }

  file << "# of faces " << std::endl << Nt << std::endl;

  for (unsigned int i = 0; i < mesh->GetNumberSubMeshesAdaptive(); i++) {
    SubMesh* sub = mesh->GetSubMeshAdaptiveByPosition(i);

    for (unsigned int j = 0; j < sub->GetNumberElements(); j++) {
      TriangleAdaptive* t = (TriangleAdaptive*)sub->GetElement(j);
      file << "f " << t->GetNoh(1).GetId() << " " << t->GetNoh(2).GetId() << " "
           << t->GetNoh(3).GetId() << std::endl;
    }
  }

  file.flush();

  file.close();

  return true;
}
