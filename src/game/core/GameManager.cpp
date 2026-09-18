#include "game/core/GameManager.h"

#ifdef ARDUINO
#include <Arduino.h>
#else
static uint32_t g_fakeMillis = 0;
static uint32_t millis() { return g_fakeMillis += 10; }
#endif

namespace dtec::game::core {

GameManager::GameManager(dtec::hal::IDisplay& display,
                          dtec::hal::IInput& input,
                          dtec::hal::IAudio& audio,
                          dtec::hal::ISensors& sensors,
                          dtec::hal::IStorage& storage)
    : display_(display), input_(input), audio_(audio), sensors_(sensors),
      storage_(storage), saveMgr_(storage), logic_(*this) {}

void GameManager::begin() {
    display_.begin();
    input_.begin();
    audio_.begin();
    sensors_.begin();
    storage_.begin();

    logic_.initialize();

    const bool hasSave = saveMgr_.load();
    if (!hasSave) {
        logic_.forceScreen(dtec::game::Screen::CharSelection);
        animMgr_.play(dtec::game::AnimationId::LoadCharacterSelection, millis());
        logic_.setInputLocked(true);
    } else {
        logic_.forceScreen(dtec::game::Screen::Character);
    }
}

void GameManager::playIntroAnimation() {
    nowMs_ = millis();
    animMgr_.play(dtec::game::AnimationId::StartGameAnimation, nowMs_);
    logic_.setInputLocked(true);
}

void GameManager::loop() {
    nowMs_ = millis();

    input_.poll();
    sensors_.poll();

    animMgr_.tick(nowMs_);
    if (logic_.inputLocked() && !animMgr_.isPlaying()) {
        logic_.setInputLocked(false);
    }

    if (sensors_.shakeDetected() && !logic_.shakeDisabled()) {
        logic_.onShakeDetected();
    }

    using LB = dtec::hal::LogicalButton;
    if (input_.wasPressed(LB::A)) logic_.inputA();
    if (input_.wasPressed(LB::B)) logic_.inputB();
    if (input_.wasPressed(LB::Left)) logic_.inputLeft();
    if (input_.wasPressed(LB::Right)) logic_.inputRight();

    if (nowMs_ - lastDisplayMs_ >= dtec::DISPLAY_REFRESH_MS) {
        lastDisplayMs_ = nowMs_;
    }

    saveMgr_.tick(nowMs_);
}

void GameManager::takeAStep() {
    auto& d = saveMgr_.data();
    d.steps += 1;
    if (d.currentDistance > 0) d.currentDistance -= 1;
    if (d.currentDistance == 1) {
        d.pendingEvent = 2;
    }
}

} // namespace dtec::game::core
