#pragma once

#include "../hal/Display.h"

namespace render {

class SpriteRenderer {
public:
    explicit SpriteRenderer(hal::Display& display);
    void drawBitmap(int x, int y, const hal::Bitmap& bitmap);

private:
    hal::Display& display_;
};

} // namespace render
