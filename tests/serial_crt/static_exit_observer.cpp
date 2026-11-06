extern "C" void SerialCrtAfterExecutableStatics();

namespace {
struct FinalObserver {
  ~FinalObserver() { SerialCrtAfterExecutableStatics(); }
};
} // namespace

// Register before user-priority owners; actual static-owner controls verify this order.
#pragma init_seg(lib)
namespace {
FinalObserver final_observer;
}
