#pragma once
#include "hal/Display.h"
#include "Config.h"

namespace dtec::hal::m5impl {

class M5Display : public dtec::hal::IDisplay {
public:
    void begin() override;
    void beginFrame() override;
    void endFrame() override;
    void blit(int x, int y, int w, int h, const uint16_t* data, bool transparentBlack) override;
    void fillRect(int x, int y, int w, int h, Color565 color) override;
    void clear(Color565 color) override;
    void setBrightness(uint8_t percent) override;

private:
    static inline int scaleX(int lx) { return dtec::GAME_VIEW_X + lx * dtec::GAME_SCALE; }
    static inline int scaleY(int ly) { return dtec::GAME_VIEW_Y + ly * dtec::GAME_SCALE; }
};

} // namespace dtec::hal::m5impl
