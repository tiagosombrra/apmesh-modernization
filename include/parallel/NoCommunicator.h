#ifndef _PARALLEL_NO_COMMUNICATOR_H_
#define _PARALLEL_NO_COMMUNICATOR_H_

#include "Communicator.h"
#include "Definitions.h"

namespace Parallel {
class NoCommunicator : public Communicator {
 public:
  NoCommunicator();
  ~NoCommunicator() override;

  Int root() const override;

  Int rank() const override;

  Int numProcesses() const override;

  std::string processorName() const override;

  bool isMaster() const override;
  bool isSlave() const override;

  bool isParallel() const override;
  bool isSerial() const override;

  Int numWorkers() const override;

  void init() const override;
  void init(Int &argc, char **&argv) const override;
  void finalize() const override;
  void abort(Int error) const override;

  bool isInitialized() const override;
  bool isFinalized() const override;

  void barrier() const override;

  using Parallel::Communicator::packSize;
  Int packSize(UInt num, enum Type type) const override;

  using Parallel::Communicator::pack;
  void pack(const void *val, Int size, void *buffer, Int bufferSize,
                    Int &position, enum Type type) const override;

  using Parallel::Communicator::unpack;
  void unpack(void *val, Int size, const void *buffer, Int bufferSize,
                      Int &position, enum Type type) const override;

  void deleteRequest(UInt id) const override;
  void removeRequest(UInt id, bool posponeDeletion = false) const override;
  Transferable *testRequest(UInt id) const override;
  Transferable *waitRequest(UInt id) const override;

  using Parallel::Communicator::broadcast;
  void broadcast(void *val, Int size, enum Type type, Int root) const override;

  using Parallel::Communicator::scatter;
  void scatter(const void *sendBuffer, Int sendCount,
                       void *receiveBuffer, Int receiveCount, enum Type type,
                       Int root) const override;
  using Parallel::Communicator::scatterv;
  void scatterv(const void *sendBuffer, const Int sendCounts[],
                        const Int displacements[], void *receiveBuffer,
                        Int receiveCount, enum Type type, Int root) const override;

  using Parallel::Communicator::gather;
  void gather(const void *sendBuffer, Int sendCount,
                      void *receiveBuffer, Int receiveCount, enum Type type,
                      Int root) const override;
  using Parallel::Communicator::gatherv;
  void gatherv(const void *sendBuffer, Int sendCount,
                       void *receiveBuffer, const Int receiveCounts[],
                       const Int displacements[], enum Type type,
                       Int root) const override;

  using Parallel::Communicator::allGather;
  void allGather(const void *sendBuffer, void *receiveBuffer, Int count,
                         enum Type type) const override;
  using Parallel::Communicator::allGatherv;
  void allGatherv(const void *sendBuffer, Int sendCount,
                          void *receiveBuffer, const Int receiveCounts[],
                          const Int displacements[], enum Type type) const override;

  using Parallel::Communicator::allToAll;
  void allToAll(const void *sendBuffer, void *receiveBuffer, Int count,
                        enum Type type) const override;
  using Parallel::Communicator::allToAllv;
  void allToAllv(const void *sendBuffer, const Int sendCounts[],
                         const Int sendDisplacements[], void *receiveBuffer,
                         const Int receiveCounts[],
                         const Int receiveDisplacements[],
                         enum Type type) const override;

  using Parallel::Communicator::send;
  void send(const void *buffer, Int size, enum Type type, Int process,
                    Int tag) const override;
  using Parallel::Communicator::ssend;
  void ssend(const void *buffer, Int size, enum Type type, Int process,
                     Int tag) const override;
  using Parallel::Communicator::bsend;
  void bsend(const void *buffer, Int size, enum Type type, Int process,
                     Int tag) const override;
  using Parallel::Communicator::rsend;
  void rsend(const void *buffer, Int size, enum Type type, Int process,
                     Int tag) const override;

  using Parallel::Communicator::isend;
  UInt isend(const void *buffer, Int size, enum Type type, Int process,
                     Int tag) const override;
  using Parallel::Communicator::issend;
  UInt issend(const void *buffer, Int size, enum Type type, Int process,
                      Int tag) const override;
  using Parallel::Communicator::ibsend;
  UInt ibsend(const void *buffer, Int size, enum Type type, Int process,
                      Int tag) const override;
  using Parallel::Communicator::irsend;
  UInt irsend(const void *buffer, Int size, enum Type type, Int process,
                      Int tag) const override;

  using Parallel::Communicator::receive;
  void receive(void *buffer, Int size, enum Type type, Int process,
                       Int tag) const override;
  using Parallel::Communicator::ireceive;
  UInt ireceive(void *buffer, Int size, enum Type type, Int process,
                        Int tag) const override;

  using Parallel::Communicator::reduce;
  void reduce(const void *sendBuffer, void *receiveBuffer, Int size,
                      enum Type type, enum Operation operation, Int root) const override;

  using Parallel::Communicator::allReduce;
  void allReduce(const void *sendBuffer, void *receiveBuffer, Int size,
                         enum Type type, enum Operation operation) const override;

  using Parallel::Communicator::reduceScatter;
  void reduceScatter(const void *sendBuffer, void *receiveBuffer,
                             Int receiveCounts[], enum Type type,
                             enum Operation operation) const override;

  Transferable *unpack(Package &p) const override;

 protected:
};
}  // namespace Parallel

#endif  //#ifndef _PARALLEL_NO_COMMUNICATOR_H_
