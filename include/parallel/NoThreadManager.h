#ifndef _PARALLEL_NO_THREAD_MANAGER_H_
#define _PARALLEL_NO_THREAD_MANAGER_H_

#include "Definitions.h"
#include "ThreadManager.h"

namespace Parallel {
class NoThreadManager : public ThreadManager {
 public:
  NoThreadManager(bool sharedParallelismEnabled = true);
  ~NoThreadManager() override;

  bool isSharedParallelismEnabled() const override;

  void setMaxThreads(Int maxThreads) override;
  Int getMaxThreads() const override;

  bool isInParallel() const override;

  Int numThreads() const override;

  Int threadId() const override;

 protected:
};
}  // namespace Parallel

#endif  //#ifndef _PARALLEL_NO_THREAD_MANAGER_H_
