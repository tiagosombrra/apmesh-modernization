#include "allocation_observer.h"

#include <new>

// Deliberately invalid standalone control: the native leak detector must reject it.
void TerminalControlLeak() {
  void* storage = ::operator new(sizeof(int));
  auto* value = ::new (storage) int(73);
  static_cast<void>(*static_cast<volatile int*>(value));
}
