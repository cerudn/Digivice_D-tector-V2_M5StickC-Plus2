#include "hal/m5/M5Sensors.h"
#include <M5Unified.h>
#include <cmath>

namespace dtec::hal::m5impl {

void M5Sensors::begin() {}

void M5Sensors::poll() {
    float ax, ay, az;
    if (!M5.Imu.getAccel(&ax, &ay, &az)) return;

    const float magnitude = sqrtf(ax * ax + ay * ay + az * az);
    const float delta = fabsf(magnitude - 1.0f);

    const uint32_t now = millis();
    if (delta >= SHAKE_THRESHOLD_G && (now - lastShakeMs_) >= SHAKE_COOLDOWN_MS) {
        lastShakeMs_ = now;
        pendingEdge_ = true;
    }
}

bool M5Sensors::shakeDetected() {
    if (pendingEdge_) { pendingEdge_ = false; return true; }
    return false;
}

uint32_t M5Sensors::epochSeconds() const {
    return (uint32_t)millis() / 1000u;
}

} // namespace dtec::hal::m5impl
