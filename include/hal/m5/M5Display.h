#pragma once

#include "../Display.h"
#include <M5Unified.h>

namespace hal {

class M5Display : public Display {
public:
    M5Display();

    void clear(uint16_t color) override;
    void drawPixel(int x, int y, uint16_t color) override;
    void drawRect(int x, int y, int w, int h, uint16_t color) override;
    void fillRect(int x, int y, int w, int h, uint16_t color) override;
    void drawBitmap(int x, int y, const Bitmap& bitmap) override;

private:
    lgfx::LGFX_Sprite& lcd();
};

} // namespace hal
