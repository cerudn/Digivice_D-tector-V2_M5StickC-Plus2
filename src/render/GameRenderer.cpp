#include "GameRenderer.h"

// First sprite test asset (no semantic mapping implied)
#include "../../assets/characters/characters_0.h"

namespace render {

GameRenderer::GameRenderer(hal::Display& display)
    : display_(display)
    , spriteRenderer_(display) {
}

void GameRenderer::clear() {
    display_.clear(TFT_BLACK);
}

void GameRenderer::render() {
    // Placeholder for full scene rendering; not modified in this integration phase.
}

void GameRenderer::drawTestSprite() {
    // Wrap the generated RGB565 array in a Bitmap descriptor.
    // The asset header defines: static const uint16_t characters_0[1024];
    hal::Bitmap bitmap{
        .data = characters_0,
        .width = 32,
        .height = 32
    };

    // Draw at a known screen position for visual verification.
    spriteRenderer_.drawBitmap(10, 10, bitmap);
}

} // namespace render
