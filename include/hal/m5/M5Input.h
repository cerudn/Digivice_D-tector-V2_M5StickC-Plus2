#pragma once
#include "hal/Input.h"
#include "Config.h"
#include <array>

namespace dtec::hal::m5impl {

class M5Input : public dtec::hal::IInput {
public:
    void begin() override;
    void poll() override;
    bool wasPressed(dtec::hal::LogicalButton b) const override;
    bool wasReleased(dtec::hal::LogicalButton b) const override;
    bool isHeld(dtec::hal::LogicalButton b) const override;
    uint32_t heldDurationMs(dtec::hal::LogicalButton b) const override;

private:
    struct ButtonState {
        bool held = false;
        bool pressedEdge = false;
        bool releasedEdge = false;
        uint32_t pressStartMs = 0;
    };
    std::array<ButtonState, (size_t)dtec::hal::LogicalButton::Count> states_{};

    void updatePhysical(bool physA, bool physB);
};

} // namespace dtec::hal::m5impl
