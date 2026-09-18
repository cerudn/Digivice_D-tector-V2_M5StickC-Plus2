#include "hal/m5/M5Audio.h"
#include <M5Unified.h>

using dtec::hal::SoundId;

namespace dtec::hal::m5impl {

struct Tone { uint16_t freq; uint16_t ms; };

static Tone toneFor(SoundId id) {
    switch (id) {
        case SoundId::ButtonA: return {880, 40};
        case SoundId::ButtonB: return {440, 40};
        case SoundId::UnpleasantBeep: return {200, 250};
        case SoundId::GameStart: return {660, 300};
        case SoundId::CharHappy: case SoundId::CharHappyLong: return {988, 150};
        case SoundId::CharSad: case SoundId::CharSadLong: return {330, 200};
        case SoundId::SummonDigimon: return {523, 200};
        case SoundId::UnlockDigimon: case SoundId::UnlockCode: return {784, 250};
        case SoundId::LoseDigimon: return {196, 400};
        case SoundId::LevelUp: return {1046, 180};
        case SoundId::LevelDown: case SoundId::LevelDownDigimon: return {262, 300};
        case SoundId::Reward: return {700, 150};
        case SoundId::Punishment: return {150, 300};
        case SoundId::TriggerEvent: return {600, 120};
        case SoundId::TravelMap: return {500, 200};
        case SoundId::Digistorm: return {300, 500};
        case SoundId::ChangeDock: return {450, 100};
        case SoundId::EncounterDigimon: return {392, 200};
        case SoundId::EncounterDigimonBoss: return {196, 500};
        case SoundId::LaunchAttack: case SoundId::LaunchAttackLong: return {900, 80};
        case SoundId::AttackTravelVeryLong: return {750, 600};
        case SoundId::Explosion: return {110, 350};
        case SoundId::Deport: case SoundId::DeportSpirit: return {550, 200};
        case SoundId::EvolutionRegular: case SoundId::EvolutionSpirit:
        case SoundId::EvolutionAncient: case SoundId::EvolutionArmor: return {1200, 400};
        case SoundId::DigiPowerFailed: return {180, 250};
        case SoundId::DigiPowerSucceed: return {900, 250};
        case SoundId::BeepLow: return {250, 80};
        case SoundId::SpeedRunnerStart: return {600, 200};
        case SoundId::SpeedRunnerAsteroid: return {150, 100};
        case SoundId::SpeedRunnerFinish: return {1000, 300};
        case SoundId::SpeedRunnerCrash: return {100, 400};
        case SoundId::DigiHunterStart: return {600, 200};
        case SoundId::StealAllSpirits: case SoundId::DestroySpirits: return {130, 500};
        default: return {440, 100};
    }
}

void M5Audio::begin() {
    auto cfg = M5.Speaker.config();
    cfg.sample_rate = 48000;
    M5.Speaker.config(cfg);
    M5.Speaker.setVolume(128);
}

void M5Audio::play(SoundId id) {
    hasPending_ = false;
    const Tone t = toneFor(id);
    M5.Speaker.stop();
    M5.Speaker.tone((float)t.freq, (uint32_t)t.ms);
}

void M5Audio::playDelayed(SoundId id, uint32_t delayMs) {
    pendingId_ = id;
    pendingAtMs_ = millis() + delayMs;
    hasPending_ = true;
}

void M5Audio::tick() {
    if (hasPending_ && (int32_t)(millis() - pendingAtMs_) >= 0) {
        hasPending_ = false;
        play(pendingId_);
    }
}

void M5Audio::stop() { M5.Speaker.stop(); }
bool M5Audio::isPlaying() const { return M5.Speaker.isPlaying(); }
void M5Audio::setVolume(uint8_t percent) {
    if (percent > 100) percent = 100;
    M5.Speaker.setVolume((uint8_t)((percent * 255u) / 100u));
}

} // namespace dtec::hal::m5impl
