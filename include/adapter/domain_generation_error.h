#ifndef APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H
#define APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H

#include <exception>
#include <string>
#include <utility>

namespace apmesh::adaptation {

// Own the completed attempt's status through stack unwinding. Construct from
// an existing string by move; diagnostics are formatted only by the CLI.
class DomainGenerationError final : public std::exception {
public:
  DomainGenerationError(int step, int patch, int retry, std::string&& status) noexcept
      : step_(step), patch_(patch), retry_(retry), status_(std::move(status)) {}

  const char* what() const noexcept override { return "domain generation failed"; }
  int Step() const noexcept { return step_; }
  int PatchIndex() const noexcept { return patch_; }
  int RetryIndex() const noexcept { return retry_; }
  const std::string& Status() const noexcept { return status_; }

private:
  int step_;
  int patch_;
  int retry_;
  std::string status_;
};

} // namespace apmesh::adaptation

#endif // APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H
