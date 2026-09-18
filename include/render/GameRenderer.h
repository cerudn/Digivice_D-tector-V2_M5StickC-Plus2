#pragma once
#include "hal/Display.h"
#include "game/core/LogicManager.h"
#include "game/anim/AnimationManager.h"
#include "render/SpriteRenderer.h"

namespace dtec::render {

class GameRenderer {
public:
    explicit GameRenderer(dtec::hal::IDisplay& display)
        : display_(display), spriteRenderer_(display) {}

    void draw(const dtec::game::core::LogicManager& logic, const dtec::game::anim::AnimationManager& anim);

private:
    dtec::hal::IDisplay& display_;
    SpriteRenderer spriteRenderer_;

    void drawCharSelection(int charIndex, const dtec::game::anim::AnimationManager& anim);
    void drawCharacterScreen(const dtec::game::anim::AnimationManager& anim);
    void drawMainMenu(dtec::game::MainMenuTab tab);
    void drawMainMenu2(dtec::game::MainMenu2Tab tab);
    void drawGenericApp(dtec::game::AppId app);
    void drawIntroAnimation();
};

} // namespace dtec::render
