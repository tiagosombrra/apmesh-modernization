#ifndef APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H
#define APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H

#include <exception>
#include <memory>
#include <string>
#include <utility>

namespace apmesh::adaptation {

// Prepare owned status before throwing, then transfer only its owner during
// propagation. Preparation and explicit copies may allocate; moves do not.
class DomainGenerationError final : public std::exception {
public:
  DomainGenerationError(int step, int patch, int retry, std::string&& status)
      : step_(step), patch_(patch), retry_(retry), status_(std::make_unique<std::string>(status)) {}

  DomainGenerationError(const DomainGenerationError& other)
      : std::exception(other), step_(other.step_), patch_(other.patch_), retry_(other.retry_),
        status_(std::make_unique<std::string>(*other.status_)) {}
  DomainGenerationError(DomainGenerationError&&) noexcept = default;
  DomainGenerationError& operator=(const DomainGenerationError& other) {
    if (this != &other) {
      auto status = std::make_unique<std::string>(*other.status_);
      std::exception::operator=(other);
      step_ = other.step_;
      patch_ = other.patch_;
      retry_ = other.retry_;
      status_ = std::move(status);
    }
    return *this;
  }
  DomainGenerationError& operator=(DomainGenerationError&&) noexcept = default;

  const char* what() const noexcept override { return "domain generation failed"; }
  int Step() const noexcept { return step_; }
  int PatchIndex() const noexcept { return patch_; }
  int RetryIndex() const noexcept { return retry_; }
  // As with other exclusive owners, a moved-from error is only retired or assigned.
  const std::string& Status() const noexcept { return *status_; }

private:
  int step_;
  int patch_;
  int retry_;
  std::unique_ptr<std::string> status_;
};

} // namespace apmesh::adaptation

#endif // APMESH_ADAPTER_DOMAIN_GENERATION_ERROR_H
