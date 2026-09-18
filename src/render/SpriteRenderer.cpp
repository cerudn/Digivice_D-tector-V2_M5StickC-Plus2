#include "render/SpriteRenderer.h"
#include <M5Unified.h>

namespace dtec::render {

void SpriteRenderer::blitSprite(int x, int y, int w, int h, const uint16_t* frameData, bool transparent) {
    // M5Unified.pushImage handles PROGMEM data directly
    // For transparency, we need to handle it manually or use a mask
    // For now, pass transparent flag to display blit
    display_.blit(x, y, w, h, frameData, transparent);
}

void SpriteRenderer::blitSpriteFrame(int x, int y, int w, int h, const uint16_t* const* frames, uint8_t frameIndex, bool transparent) {
    const uint16_t* frameData = frames[frameIndex];
    blitSprite(x, y, w, h, frameData, transparent);
}

} // namespace dtec::render
