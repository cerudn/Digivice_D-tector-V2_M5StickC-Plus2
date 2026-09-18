#include "render/GameRenderer.h"
#include "game/data/CharacterData.h"
#include "Config.h"
#include <M5Unified.h>

// TODO: Include generated sprite headers after conversion
// #include "assets/takuya_idle.h"
// #include "assets/koji_idle.h"
// etc.

using namespace dtec::game;

namespace dtec::render {

namespace {
constexpr uint16_t COLOR_BG = 0x0000;
constexpr uint16_t COLOR_FG = 0x07E0;
constexpr uint16_t COLOR_DIM = 0x0320;

const char* charName(int idx) {
    const auto* c = dtec::game::data::findCharacter((GameChar)idx);
    return c ? c->name : "?";
}

// Placeholder: center position for character sprites
constexpr int CHAR_SPRITE_X = dtec::GAME_VIEW_X + (dtec::GAME_VIEW_W - 128) / 2;
constexpr int CHAR_SPRITE_Y = dtec::GAME_VIEW_Y + 20;
} // namespace

void GameRenderer::draw(const dtec::game::core::LogicManager& logic, const dtec::game::anim::AnimationManager& anim) {
    display_.clear(dtec::hal::Color565(COLOR_BG));

    M5.Display.setTextColor(COLOR_FG, COLOR_BG);
    M5.Display.setTextDatum(top_center);
    M5.Display.setTextSize(1);

    M5.Display.drawRect(dtec::GAME_VIEW_X - 1, dtec::GAME_VIEW_Y - 1,
                         dtec::GAME_VIEW_W + 2, dtec::GAME_VIEW_H + 2, COLOR_DIM);

    if (anim.isPlaying() && anim.current() == AnimationId::LoadCharacterSelection) {
        M5.Display.drawString("LOADING...", M5.Display.width() / 2, dtec::GAME_VIEW_Y + 60);
        return;
    }
    if (anim.isPlaying() && anim.current() == AnimationId::StartGameAnimation) {
        drawIntroAnimation();
        return;
    }

    switch (logic.currentScreen()) {
        case Screen::CharSelection: drawCharSelection(logic.charSelectionIndex(), anim); break;
        case Screen::Character:     drawCharacterScreen(anim); break;
        case Screen::MainMenu:      drawMainMenu(logic.currentMainMenu()); break;
        case Screen::MainMenu2:     drawMainMenu2(logic.currentMainMenu2()); break;
        case Screen::App:           drawGenericApp(logic.loadedApp()); break;
        default:
            M5.Display.drawString("...", M5.Display.width() / 2, dtec::GAME_VIEW_Y + 60);
            break;
    }
}

void GameRenderer::drawIntroAnimation() {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;
    M5.Display.drawString("A NEW ADVENTURE", cx, dtec::GAME_VIEW_Y + 6);
    M5.Display.setTextSize(2);
    M5.Display.drawString("BEGINS!", cx, cy - 8);
    M5.Display.setTextSize(1);
}

void GameRenderer::drawCharSelection(int charIndex, const dtec::game::anim::AnimationManager& anim) {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;

    M5.Display.drawString("SELECT CHARACTER", cx, dtec::GAME_VIEW_Y + 6);

    // TODO: Blit character sprite here
    // Example (after conversion):
    // if (charIndex == 0) {
    //     spriteRenderer_.blitSpriteFrame(CHAR_SPRITE_X, CHAR_SPRITE_Y,
    //         dtec::assets::TAKUYA_IDLE_width, dtec::assets::TAKUYA_IDLE_height,
    //         dtec::assets::TAKUYA_IDLE_frames, anim.currentFrameIndex(), true);
    // }

    M5.Display.setTextSize(2);
    M5.Display.drawString(charName(charIndex), cx, cy - 8);
    M5.Display.setTextSize(1);

    M5.Display.drawString("<", dtec::GAME_VIEW_X + 10, cy - 4);
    M5.Display.drawString(">", dtec::GAME_VIEW_X + dtec::GAME_VIEW_W - 10, cy - 4);

    M5.Display.drawString("A: CONFIRM", cx, dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H - 16);
}

void GameRenderer::drawCharacterScreen(const dtec::game::anim::AnimationManager& anim) {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;
    M5.Display.drawString("D-TECTOR", cx, dtec::GAME_VIEW_Y + 6);
    M5.Display.setTextSize(2);

    // TODO: Blit character sprite based on animation state
    // Example:
    // AnimationId currentAnim = anim.current();
    // if (currentAnim == AnimationId::CharHappyShort) {
    //     spriteRenderer_.blitSpriteFrame(CHAR_SPRITE_X, CHAR_SPRITE_Y,
    //         dtec::assets::TAKUYA_HAPPY_width, dtec::assets::TAKUYA_HAPPY_height,
    //         dtec::assets::TAKUYA_HAPPY_frames, anim.currentFrameIndex(), true);
    // } else if (currentAnim == AnimationId::CharSadShort) {
    //     spriteRenderer_.blitSpriteFrame(CHAR_SPRITE_X, CHAR_SPRITE_Y,
    //         dtec::assets::TAKUYA_SAD_width, dtec::assets::TAKUYA_SAD_height,
    //         dtec::assets::TAKUYA_SAD_frames, anim.currentFrameIndex(), true);
    // } else {
    //     spriteRenderer_.blitSpriteFrame(CHAR_SPRITE_X, CHAR_SPRITE_Y,
    //         dtec::assets::TAKUYA_IDLE_width, dtec::assets::TAKUYA_IDLE_height,
    //         dtec::assets::TAKUYA_IDLE_frames, anim.currentFrameIndex(), true);
    // }

    const char* label = "IDLE";
    if (anim.isPlaying() && anim.current() == AnimationId::CharHappyShort) label = "HAPPY";
    if (anim.isPlaying() && anim.current() == AnimationId::CharSadShort) label = "SAD";
    M5.Display.drawString(label, cx, cy - 8);
    M5.Display.setTextSize(1);
    M5.Display.drawString("A: STATUS  <>: MENU", cx, dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H - 16);
}

void GameRenderer::drawMainMenu(MainMenuTab tab) {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;
    const char* label = "?";
    switch (tab) {
        case MainMenuTab::Map: label = "MAP"; break;
        case MainMenuTab::Status: label = "STATUS"; break;
        case MainMenuTab::Spirits: label = "SPIRITS"; break;
        case MainMenuTab::Connect: label = "CONNECT"; break;
        case MainMenuTab::Camp: label = "CAMP"; break;
        default: break;
    }
    M5.Display.drawString("MAIN MENU", cx, dtec::GAME_VIEW_Y + 6);
    M5.Display.setTextSize(2);
    M5.Display.drawString(label, cx, cy - 8);
    M5.Display.setTextSize(1);
    M5.Display.drawString("A:OPEN B:BACK <>:NAV", cx, dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H - 16);
}

void GameRenderer::drawMainMenu2(MainMenu2Tab tab) {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;
    const char* label = "?";
    switch (tab) {
        case MainMenu2Tab::Database: label = "DATABASE"; break;
        case MainMenu2Tab::Digits: label = "DIGITS"; break;
        case MainMenu2Tab::Game: label = "GAME"; break;
        case MainMenu2Tab::Finder: label = "FINDER"; break;
        default: break;
    }
    M5.Display.drawString("MENU 2", cx, dtec::GAME_VIEW_Y + 6);
    M5.Display.setTextSize(2);
    M5.Display.drawString(label, cx, cy - 8);
    M5.Display.setTextSize(1);
}

void GameRenderer::drawGenericApp(AppId app) {
    const int cx = M5.Display.width() / 2;
    const int cy = dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H / 2;
    const char* label = "APP";
    switch (app) {
        case AppId::Status: label = "STATUS APP"; break;
        case AppId::Map: label = "MAP APP"; break;
        case AppId::Character: label = "CHAR APP"; break;
        case AppId::Spirits: label = "SPIRITS APP"; break;
        case AppId::Camp: label = "CAMP APP"; break;
        case AppId::Database: label = "DATABASE APP"; break;
        case AppId::CodeInput: label = "CODE INPUT"; break;
        case AppId::Finder: label = "FINDER"; break;
        case AppId::JackpotBox: label = "JACKPOT BOX"; break;
        case AppId::SpeedRunner: label = "SPEEDRUNNER"; break;
        default: break;
    }
    M5.Display.drawString("[APP - NOT IMPLEMENTED YET]", cx, dtec::GAME_VIEW_Y + 6);
    M5.Display.drawString(label, cx, cy - 8);
    M5.Display.drawString("B: CLOSE (pendiente)", cx, dtec::GAME_VIEW_Y + dtec::GAME_VIEW_H - 16);
}

} // namespace dtec::render
