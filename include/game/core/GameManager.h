#pragma once
#include "hal/Display.h"
#include "hal/Input.h"
#include "hal/Audio.h"
#include "hal/Sensors.h"
#include "hal/Storage.h"
#include "game/save/SaveManager.h"
#include "game/state/GameStates.h"
#include "game/core/LogicManager.h"
#include "game/anim/AnimationManager.h"

namespace dtec::game::core {

class GameManager {
public:
    GameManager(dtec::hal::IDisplay& display,
                dtec::hal::IInput& input,
                dtec::hal::IAudio& audio,
                dtec::hal::ISensors& sensors,
                dtec::hal::IStorage& storage);

    void begin();
    void loop();

    dtec::hal::IDisplay& display() { return display_; }
    dtec::hal::IInput& input() { return input_; }
    dtec::hal::IAudio& audio() { return audio_; }
    dtec::hal::ISensors& sensors() { return sensors_; }
    dtec::game::save::SaveManager& save() { return saveMgr_; }
    dtec::game::anim::AnimationManager& anim() { return animMgr_; }

    LogicManager& logic() { return logic_; }

    void takeAStep();

    bool isCharacterDefeated() const { return saveMgr_.data().isPlayerDefeated; }
    void setCharacterDefeated(bool v) { saveMgr_.data().isPlayerDefeated = v; }

    void playIntroAnimation();

private:
    dtec::hal::IDisplay& display_;
    dtec::hal::IInput& input_;
    dtec::hal::IAudio& audio_;
    dtec::hal::ISensors& sensors_;
    dtec::hal::IStorage& storage_;
    dtec::game::save::SaveManager saveMgr_;
    dtec::game::anim::AnimationManager animMgr_;
    LogicManager logic_;

    uint32_t lastDisplayMs_ = 0;
    uint32_t nowMs_ = 0;
};

} // namespace dtec::game::core
