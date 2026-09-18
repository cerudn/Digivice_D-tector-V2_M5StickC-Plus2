#pragma once
#include <cstdint>

namespace dtec::hal {

enum class LogicalButton : uint8_t { A = 0, B = 1, Left = 2, Right = 3, Count = 4 };

class IInput {
public:
    virtual ~IInput() = default;
    virtual void begin() = 0;
    virtual void poll() = 0;
    virtual bool wasPressed(LogicalButton b) const = 0;
    virtual bool wasReleased(LogicalButton b) const = 0;
    virtual bool isHeld(LogicalButton b) const = 0;
    virtual uint32_t heldDurationMs(LogicalButton b) const = 0;
};

} // namespace dtec::hal
