#include "hal/m5/M5Display.h"
#include <M5Unified.h>

namespace dtec::hal::m5impl {

void M5Display::begin() {
    M5.Display.setRotation(0);
    M5.Display.setColorDepth(16);
    M5.Display.fillScreen(TFT_BLACK);
    M5.Display.setBrightness(80);
}

void M5Display::beginFrame() { M5.Display.startWrite(); }
void M5Display::endFrame() { M5.Display.endWrite(); }

void M5Display::blit(int x, int y, int w, int h, const uint16_t* data, bool transparentBlack) {
    const int px = scaleX(x);
    const int py = scaleY(y);
    if (transparentBlack) {
        M5.Display.pushImage(px, py, w, h, data, (uint16_t)0x0000);
    } else {
        M5.Display.pushImage(px, py, w, h, data);
    }
}

void M5Display::fillRect(int x, int y, int w, int h, Color565 color) {
    M5.Display.fillRect(scaleX(x), scaleY(y), w * dtec::GAME_SCALE, h * dtec::GAME_SCALE, color.v);
}

void M5Display::clear(Color565 color) {
    M5.Display.fillScreen(color.v);
}

void M5Display::setBrightness(uint8_t percent) {
    if (percent > 100) percent = 100;
    M5.Display.setBrightness((uint8_t)((percent * 255u) / 100u));
}

} // namespace dtec::hal::m5impl
