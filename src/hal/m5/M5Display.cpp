#include "M5Display.h"

namespace hal {

M5Display::M5Display() {
    M5.begin();
    M5.Display.setRotation(1);
    M5.Display.clear(TFT_BLACK);
}

lgfx::LGFX_Sprite& M5Display::lcd() {
    return M5.Display;
}

void M5Display::clear(uint16_t color) {
    lcd().clear(color);
}

void M5Display::drawPixel(int x, int y, uint16_t color) {
    lcd().drawPixel(x, y, color);
}

void M5Display::drawRect(int x, int y, int w, int h, uint16_t color) {
    lcd().drawRect(x, y, w, h, color);
}

void M5Display::fillRect(int x, int y, int w, int h, uint16_t color) {
    lcd().fillRect(x, y, w, h, color);
}

void M5Display::drawBitmap(int x, int y, const Bitmap& bitmap) {
    lcd().pushImage(x, y, bitmap.width, bitmap.height, bitmap.data);
}

} // namespace hal
