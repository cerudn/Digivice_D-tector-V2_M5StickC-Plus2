#pragma once
#include <cstdint>

namespace dtec::hal {

struct Color565 {
    uint16_t v;
    constexpr Color565() : v(0) {}
    constexpr Color565(uint16_t value) : v(value) {}
};

class IDisplay {
public:
    virtual ~IDisplay() = default;
    virtual void begin() = 0;
    virtual void beginFrame() = 0;
    virtual void endFrame() = 0;
    virtual void blit(int x, int y, int w, int h, const uint16_t* data, bool transparentBlack) = 0;
    virtual void fillRect(int x, int y, int w, int h, Color565 color) = 0;
    virtual void clear(Color565 color) = 0;
    virtual void setBrightness(uint8_t percent) = 0;
};

} // namespace dtec::hal
