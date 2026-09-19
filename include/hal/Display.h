#pragma once

#include <stdint.h>

namespace hal {

struct Bitmap {
    const uint16_t* data;
    uint16_t width;
    uint16_t height;
};

class Display {
public:
    virtual ~Display() = default;
    virtual void clear(uint16_t color) = 0;
    virtual void drawPixel(int x, int y, uint16_t color) = 0;
    virtual void drawRect(int x, int y, int w, int h, uint16_t color) = 0;
    virtual void fillRect(int x, int y, int w, int h, uint16_t color) = 0;
    virtual void drawBitmap(int x, int y, const Bitmap& bitmap) = 0;
};

} // namespace hal
