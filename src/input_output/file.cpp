#include "../../include/input_output/file.h"

File::File(const char* name) {
  this->INPUT_MODEL.open(name);
  if (this->INPUT_MODEL.fail())
    std::cout << "não abriu o arquivo em disco!" << std::endl;
  else
    this->name_ = name;
}

File::~File() { this->INPUT_MODEL.close(); }

// ler as linhas que definem as curvas
void File::ReadCurves(const std::string reading) {
  // "P" de point_1_ ou P2, os pontos inicial e final da curva
  // "D" de DP1 ou DP2, as derivadas nos pontos inicial e final
  if (reading[0] == 'P' or reading[0] == 'D') this->curves_.push_back(reading);
}

// ler as linhas que definem os patches
void File::ReadPatches(const std::string reading) {
  // "D" de DEFINE_PATCH
  if (reading[0] == 'D') this->patches_.push_back(reading);
}

// converta uma string em um char*, por causa do strtok() do C
char* File::ConvertString(std::string font) {
  char* destiny;

  destiny = (char*)malloc(font.length() * sizeof(char));

  for (unsigned int i = 0; i < font.length(); ++i) destiny[i] = font[i];

  return destiny;
}

std::string File::GetName() { return name_; }

// criar as curvas
void File::CreateCurvesTo() {
  char* temp = nullptr;
  char* str = nullptr;
  double pt0[3];   // ponto inicial
  double pt1[3];   // ponto final
  double dpt0[3];  // derivada no ponto inicial
  double dpt1[3];  // derivada no ponto final

  std::list<std::string>::iterator itr = this->curves_.begin();
  std::list<std::string>::iterator fim = this->curves_.end();

  // leia quatro strings da list para definir uma curva
  while (itr != fim) {
    // lê o ponto inicial
    temp = ConvertString(*itr);  // aloca temp em convertaString
    str = strtok(temp, " <");
    str = strtok(nullptr, "<,");
    pt0[0] = atof(str);
    str = strtok(nullptr, ",,");
    pt0[1] = atof(str);
    str = strtok(nullptr, ",>");
    pt0[2] = atof(str);
    ++itr;

    delete temp;  // deleta o temp alocado em convertaString

    // lê o ponto final
    temp = ConvertString(*itr);
    str = strtok(temp, " <");
    str = strtok(nullptr, "<,");
    pt1[0] = atof(str);
    str = strtok(nullptr, ",,");
    pt1[1] = atof(str);
    str = strtok(nullptr, ",>");
    pt1[2] = atof(str);
    ++itr;

    delete temp;  // deleta o temp alocado em convertaString

    // lê a derivada no ponto inicial
    temp = ConvertString(*itr);
    str = strtok(temp, " <");
    str = strtok(nullptr, "<,");
    dpt0[0] = atof(str);
    str = strtok(nullptr, ",,");
    dpt0[1] = atof(str);
    str = strtok(nullptr, ",>");
    dpt0[2] = atof(str);
    ++itr;

    delete temp;  // deleta o temp alocado em convertaString

    // lê a derivada no ponto final
    temp = ConvertString(*itr);
    str = strtok(temp, " <");
    str = strtok(nullptr, "<,");
    dpt1[0] = atof(str);
    str = strtok(nullptr, ",,");
    dpt1[1] = atof(str);
    str = strtok(nullptr, ",>");
    dpt1[2] = atof(str);
    ++itr;

    delete temp;  // deleta o temp alocado em convertaString

    // substituir pelo construtor de curvas
    std::cout << "\nContrui uma curva com ponto inicial ( " << pt0[0] << ", "
         << pt0[1] << ", " << pt0[2] << ")\n"
         << "ponto final: (" << pt1[0] << ", " << pt1[1] << ", " << pt1[2]
         << ")\n"
         << "Derivada no ponto inicial: (" << dpt0[0] << ", " << dpt0[1] << ", "
         << dpt0[2] << ")\n"
         << "Derivada no ponto final: (" << dpt1[0] << ", " << dpt1[1] << ", "
         << dpt1[2] << ")" << std::endl;

  }  // fim do while

  delete str;
}

// criar os patches
void File::CreatePatchesTo() {
  char* temp = nullptr;
  char* str = nullptr;

  std::list<std::string>::iterator itr = this->patches_.begin();
  std::list<std::string>::iterator fim = this->patches_.end();

  while (itr != fim) {
    temp = ConvertString(*itr);
    str = strtok(temp, " <");
    str = strtok(nullptr, "<,");
    std::cout << str << std::endl;
    str = strtok(nullptr, ",,");
    std::cout << str << std::endl;
    str = strtok(nullptr, ",,");
    std::cout << str << std::endl;
    str = strtok(nullptr, ",>");
    std::cout << str << std::endl;
    ++itr;

    delete temp;  // deleta o temp alocado em convertaString
  }               // fim do while

  delete str;
}

// ler um arquivo para definir um Modelo
void File::ReadFileTo() {
  std::string line;  // linha lida do arquivo

  std::string init_curves = "CURVAS_HERMITE";        // inicio do bloco de curvas
  bool read_curves = false;                     // pode ler uma linha de curva
  std::string end_of_curves = "FIM_CURVAS_HERMITE";  // fim do bloco de curvas

  std::string init_patches = "PATCHS_HERMITE";  // inicio do bloco de patches
  bool read_patches = false;               // pode ler uma linha de patch
  std::string end_of_patches = "FIM_DE_PATCHS_HERMITES";  // fim do bloco de patches

  while (INPUT_MODEL.good()) {
    getline(INPUT_MODEL, line);  // pega uma linha do arquivo

    if (line == init_curves)  // começa a definição das curvas no arquivo
    {
      read_curves = true;  // você pode ler as linhas e definir os pontos e suas
                           // derivadas das curvas
      continue;
    } else if (line == end_of_curves)  // não há mais definições de curvas
    {
      read_curves = false;  // pare de definir os pontos e derivadas
      continue;
    } else if (line == "")  // ignore linhas em branco
      continue;
    else if (read_curves)  // se está dentro de um bloco de definição de curvas
      ReadCurves(line);    // leia a linha e forme uma curva
    else if (line == init_patches)  // começa a definição dos patches no arquivo
    {
      read_patches = true;  // você pode ler as linhas e definir os patches
      continue;
    } else if (line == end_of_patches)  // não há mais definições de patches
    {
      read_patches = false;  // pare de definir os patches
      break;
    } else if (read_patches)  // leia a linha e defina um patch
      ReadPatches(line);
  }  // fim do while
  CreateCurvesTo();
  CreatePatchesTo();
}
