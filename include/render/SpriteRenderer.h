#pragma once
#include "hal/Display.h"
#include <cstdint>

namespace dtec::render {

class SpriteRenderer {
public:
    explicit SpriteRenderer(dtec::hal::IDisplay& display) : display_(display) {}

    // Blit single frame from PROGMEM array
    void blitSprite(int x, int y, int w, int h, const uint16_t* frameData, bool transparent);

    // Blit specific frame from frame array
    void blitSpriteFrame(int x, int y, int w, int h, const uint16_t* const* frames, uint8_t frameIndex, bool transparent);

private:
    dtec::hal::IDisplay& display_;
};

} // namespace dtec::render
