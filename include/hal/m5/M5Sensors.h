#pragma once
#include "hal/Sensors.h"

namespace dtec::hal::m5impl {

class M5Sensors : public dtec::hal::ISensors {
public:
    void begin() override;
    void poll() override;
    bool shakeDetected() override;
    uint32_t epochSeconds() const override;

private:
    static constexpr float SHAKE_THRESHOLD_G = 1.6f;
    static constexpr uint32_t SHAKE_COOLDOWN_MS = 800;
    uint32_t lastShakeMs_ = 0;
    bool pendingEdge_ = false;
};

} // namespace dtec::hal::m5impl
