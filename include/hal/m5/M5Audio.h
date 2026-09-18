#pragma once
#include "hal/Audio.h"

namespace dtec::hal::m5impl {

class M5Audio : public dtec::hal::IAudio {
public:
    void begin() override;
    void play(dtec::hal::SoundId id) override;
    void playDelayed(dtec::hal::SoundId id, uint32_t delayMs) override;
    void stop() override;
    bool isPlaying() const override;
    void setVolume(uint8_t percent) override;
    void tick();

private:
    dtec::hal::SoundId pendingId_ = dtec::hal::SoundId::Count;
    uint32_t pendingAtMs_ = 0;
    bool hasPending_ = false;
};

} // namespace dtec::hal::m5impl
