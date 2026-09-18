#pragma once
#include "game/state/GameStates.h"
#include <cstdint>

namespace dtec::game::core {

class GameManager;

class LogicManager {
public:
    explicit LogicManager(GameManager& gm) : gm_(gm) {}

    void initialize();

    void inputA();
    void inputB();
    void inputLeft();
    void inputRight();

    dtec::game::Screen currentScreen() const { return currentScreen_; }
    dtec::game::MainMenuTab currentMainMenu() const { return currentMainMenu_; }
    dtec::game::MainMenu2Tab currentMainMenu2() const { return currentMainMenu2_; }
    int charSelectionIndex() const { return charSelectionIndex_; }

    bool isEventPending() const { return eventPending_; }
    bool isEndGame() const { return isEndGame_; }

    dtec::game::AppId loadedApp() const { return loadedApp_; }
    bool isAppLoaded() const { return loadedApp_ != dtec::game::AppId::None; }

    bool shakeDisabled() const;
    void onShakeDetected();

    void forceScreen(dtec::game::Screen screen) { currentScreen_ = screen; }

    bool inputLocked() const { return inputLocked_; }
    void setInputLocked(bool v) { inputLocked_ = v; }

private:
    GameManager& gm_;

    dtec::game::Screen currentScreen_ = dtec::game::Screen::Character;
    dtec::game::MainMenuTab currentMainMenu_ = dtec::game::MainMenuTab::Map;
    dtec::game::MainMenu2Tab currentMainMenu2_ = dtec::game::MainMenu2Tab::Database;

    int charSelectionIndex_ = 0;
    int gamesMenuIndex_ = 0;
    int gamesRewardMenuIndex_ = 0;
    int gamesTravelMenuIndex_ = 0;

    dtec::game::AppId loadedApp_ = dtec::game::AppId::None;
    bool eventPending_ = false;
    bool eventRecoveryPending_ = false;
    bool isEndGame_ = false;
    bool inputLocked_ = false;

    void openGameMenu();
    void openGameMenu2();
    void closeGameMenu();
    void openApp(dtec::game::AppId app);
    void closeLoadedApp(dtec::game::Screen newScreen);

    void triggerPendingEvent();
    void selectCharacterAndCreateGame();
    void selectCharacterPart2Game();
};

} // namespace dtec::game::core
