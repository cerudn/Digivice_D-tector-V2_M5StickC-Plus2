#pragma once

#include "../hal/Display.h"
#include "SpriteRenderer.h"

namespace render {

class GameRenderer {
public:
    explicit GameRenderer(hal::Display& display);

    void clear();
    void render();

    /**
     * Temporary test: draw the first character sprite (characters_0) at a fixed position.
     * This is a proof-of-path integration only; no semantic mapping is implied.
     */
    void drawTestSprite();

private:
    hal::Display& display_;
    SpriteRenderer spriteRenderer_;
};

} // namespace render
