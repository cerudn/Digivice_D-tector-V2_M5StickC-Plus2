#include "GameRenderer.h"
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
    // Placeholder for full scene rendering
}

void GameRenderer::drawTestSprite() {
    hal::Bitmap bitmap{
        .data = characters_0,
        .width = 32,
        .height = 32
    };
    spriteRenderer_.drawBitmap(10, 10, bitmap);
}

} // namespace render
