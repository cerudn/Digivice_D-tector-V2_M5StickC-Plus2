#pragma once
#include <cstdint>

namespace dtec::hal {

enum class SoundId : uint16_t {
    ButtonA, ButtonB, UnpleasantBeep,
    GameStart, CharHappy, CharHappyLong, CharSad, CharSadLong,
    SummonDigimon, UnlockDigimon, UnlockCode, LoseDigimon,
    LevelUp, LevelDown, Reward, Punishment, TriggerEvent, TravelMap, Digistorm,
    ChangeDock,
    EncounterDigimon, EncounterDigimonBoss, LaunchAttack, LaunchAttackLong,
    AttackTravelVeryLong, Explosion, Deport, DeportSpirit,
    EvolutionRegular, EvolutionSpirit, EvolutionAncient, EvolutionArmor,
    DigiPowerFailed, DigiPowerSucceed, LevelDownDigimon,
    BeepLow,
    SpeedRunnerStart, SpeedRunnerAsteroid, SpeedRunnerFinish, SpeedRunnerCrash,
    DigiHunterStart,
    StealAllSpirits, DestroySpirits,
    Count
};

class IAudio {
public:
    virtual ~IAudio() = default;
    virtual void begin() = 0;
    virtual void play(SoundId id) = 0;
    virtual void playDelayed(SoundId id, uint32_t delayMs) = 0;
    virtual void stop() = 0;
    virtual bool isPlaying() const = 0;
    virtual void setVolume(uint8_t percent) = 0;
};

} // namespace dtec::hal
