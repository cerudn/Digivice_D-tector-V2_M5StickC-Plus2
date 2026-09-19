#include "SpriteRenderer.h"

namespace render {

SpriteRenderer::SpriteRenderer(hal::Display& display)
    : display_(display) {
}

void SpriteRenderer::drawBitmap(int x, int y, const hal::Bitmap& bitmap) {
    display_.drawBitmap(x, y, bitmap);
}

} // namespace render
