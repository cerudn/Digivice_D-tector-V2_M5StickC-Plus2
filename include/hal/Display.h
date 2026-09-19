#pragma once

#include <stdint.h>
#include <stddef.h>

namespace hal {

/**
 * Minimal RGB565 bitmap resource descriptor.
 * Data is expected to reside in flash/static storage; this struct only references it.
 */
struct Bitmap {
    const uint16_t* data;  ///< Pointer to RGB565 pixel data (row-major, no padding)
    uint16_t width;        ///< Width in pixels
    uint16_t height;       ///< Height in pixels
};

class Display {
public:
    virtual ~Display() = default;

    virtual void clear(uint16_t color) = 0;
    virtual void drawPixel(int x, int y, uint16_t color) = 0;
    virtual void drawRect(int x, int y, int w, int h, uint16_t color) = 0;
    virtual void fillRect(int x, int y, int w, int h, uint16_t color) = 0;

    /**
     * Draw an RGB565 bitmap at the specified screen position.
     * The bitmap data is read-only and must remain valid for the duration of the call.
     */
    virtual void drawBitmap(int x, int y, const Bitmap& bitmap) = 0;
};

} // namespace hal
