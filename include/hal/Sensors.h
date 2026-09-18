#pragma once
#include <cstdint>

namespace dtec::hal {

class ISensors {
public:
    virtual ~ISensors() = default;
    virtual void begin() = 0;
    virtual void poll() = 0;
    virtual bool shakeDetected() = 0;
    virtual uint32_t epochSeconds() const = 0;
};

} // namespace dtec::hal
