#pragma once

#include "../hal/Display.h"
#include "SpriteRenderer.h"

namespace render {

class GameRenderer {
public:
    explicit GameRenderer(hal::Display& display);
    void clear();
    void render();
    void drawTestSprite();

private:
    hal::Display& display_;
    SpriteRenderer spriteRenderer_;
};

} // namespace render
