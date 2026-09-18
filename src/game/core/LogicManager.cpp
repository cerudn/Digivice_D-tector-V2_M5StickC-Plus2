#include "game/core/LogicManager.h"
#include "game/core/GameManager.h"

using namespace dtec::game;

namespace dtec::game::core {

void LogicManager::initialize() {
    currentScreen_ = Screen::Character;
    currentMainMenu_ = MainMenuTab::Map;
    currentMainMenu2_ = MainMenu2Tab::Database;
}

bool LogicManager::shakeDisabled() const {
    if (loadedApp_ != AppId::None && loadedApp_ != AppId::Status) return true;
    if (gm_.isCharacterDefeated()) return true;
    if (eventPending_) return true;
    return false;
}

void LogicManager::onShakeDetected() {
    if (shakeDisabled()) return;
    if (currentScreen_ == Screen::Character) {
        gm_.takeAStep();
    }
}

void LogicManager::inputA() {
    if (inputLocked_) return;

    if (currentScreen_ == Screen::Character) {
        if (eventPending_ && !gm_.isCharacterDefeated()) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            triggerPendingEvent();
        } else {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Status);
        }
        return;
    }

    if (currentScreen_ == Screen::MainMenu) {
        if (currentMainMenu_ == MainMenuTab::Camp) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Camp);
        } else if (gm_.isCharacterDefeated()) {
            gm_.audio().play(dtec::hal::SoundId::ButtonB);
        } else if (currentMainMenu_ == MainMenuTab::Map) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Map);
        } else if (currentMainMenu_ == MainMenuTab::Status) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Character);
        } else if (currentMainMenu_ == MainMenuTab::Spirits) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Spirits);
        }
        return;
    }

    if (currentScreen_ == Screen::MainMenu2) {
        if (gm_.isCharacterDefeated()) {
            gm_.audio().play(dtec::hal::SoundId::ButtonB);
        } else if (currentMainMenu2_ == MainMenu2Tab::Game) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            gamesMenuIndex_ = 0;
            currentScreen_ = Screen::GamesMenu;
        } else if (currentMainMenu2_ == MainMenu2Tab::Database) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Database);
        } else if (currentMainMenu2_ == MainMenu2Tab::Digits) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::CodeInput);
        } else if (currentMainMenu2_ == MainMenu2Tab::Finder) {
            gm_.audio().play(dtec::hal::SoundId::ButtonA);
            openApp(AppId::Finder);
        }
        return;
    }

    if (currentScreen_ == Screen::App) {
        return;
    }

    if (currentScreen_ == Screen::GamesMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        if (gamesMenuIndex_ == 0) openApp(AppId::JackpotBox);
        else if (gamesMenuIndex_ == 1) openApp(AppId::SpeedRunner);
        return;
    }

    if (currentScreen_ == Screen::CharSelection) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        if (isEndGame_) {
            isEndGame_ = false;
        } else {
            if (gm_.save().data().currentMap == 0) selectCharacterAndCreateGame();
            else selectCharacterPart2Game();
        }
        return;
    }
}

void LogicManager::inputB() {
    if (inputLocked_) return;

    if (currentScreen_ == Screen::Character) {
        if (eventPending_ && !gm_.isCharacterDefeated()) {
            gm_.audio().play(dtec::hal::SoundId::ButtonB);
            triggerPendingEvent();
        } else if (gm_.save().data().currentDistance == 1) {
            gm_.takeAStep();
        } else {
            gm_.audio().play(dtec::hal::SoundId::ButtonB);
        }
        return;
    }
    if (currentScreen_ == Screen::MainMenu || currentScreen_ == Screen::MainMenu2) {
        gm_.audio().play(dtec::hal::SoundId::ButtonB);
        closeGameMenu();
        return;
    }
    if (currentScreen_ == Screen::App) {
        return;
    }
    if (currentScreen_ == Screen::GamesMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonB);
        currentScreen_ = Screen::MainMenu2;
        return;
    }
    if (currentScreen_ == Screen::GamesRewardMenu || currentScreen_ == Screen::GamesTravelMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonB);
        currentScreen_ = Screen::GamesMenu;
        return;
    }
    if (currentScreen_ == Screen::CharSelection) {
        gm_.audio().play(dtec::hal::SoundId::ButtonB);
        return;
    }
}

void LogicManager::inputLeft() {
    if (inputLocked_) return;

    if (eventPending_ && !gm_.isCharacterDefeated()) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        triggerPendingEvent();
        return;
    }
    if (currentScreen_ == Screen::App) {
        return;
    }
    if (currentScreen_ == Screen::Character || currentScreen_ == Screen::MainMenu2) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        openGameMenu();
        return;
    }
    if (currentScreen_ == Screen::MainMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        openGameMenu2();
        return;
    }
    if (currentScreen_ == Screen::GamesMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesMenuIndex_ = circularAdd(gamesMenuIndex_, -1, 2);
        return;
    }
    if (currentScreen_ == Screen::GamesRewardMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesRewardMenuIndex_ = circularAdd(gamesRewardMenuIndex_, -1, 4);
        return;
    }
    if (currentScreen_ == Screen::GamesTravelMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesTravelMenuIndex_ = circularAdd(gamesTravelMenuIndex_, -1, 4);
        return;
    }
    if (currentScreen_ == Screen::CharSelection) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        if (!isEndGame_) {
            const int maxChars = (gm_.save().data().currentMap == 0) ? 4 : 5;
            charSelectionIndex_ = circularAdd(charSelectionIndex_, -1, maxChars);
        }
        return;
    }
}

void LogicManager::inputRight() {
    if (inputLocked_) return;

    if (eventPending_ && !gm_.isCharacterDefeated()) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        triggerPendingEvent();
        return;
    }
    if (currentScreen_ == Screen::App) {
        return;
    }
    if (currentScreen_ == Screen::Character) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        openGameMenu();
        return;
    }
    if (currentScreen_ == Screen::MainMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        currentMainMenu_ = circularNext(currentMainMenu_, (uint8_t)MainMenuTab::Count);
        return;
    }
    if (currentScreen_ == Screen::MainMenu2) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        currentMainMenu2_ = circularNext(currentMainMenu2_, (uint8_t)MainMenu2Tab::Count);
        return;
    }
    if (currentScreen_ == Screen::GamesMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesMenuIndex_ = circularAdd(gamesMenuIndex_, 1, 2);
        return;
    }
    if (currentScreen_ == Screen::GamesRewardMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesRewardMenuIndex_ = circularAdd(gamesRewardMenuIndex_, 1, 4);
        return;
    }
    if (currentScreen_ == Screen::GamesTravelMenu) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        gamesTravelMenuIndex_ = circularAdd(gamesTravelMenuIndex_, 1, 4);
        return;
    }
    if (currentScreen_ == Screen::CharSelection) {
        gm_.audio().play(dtec::hal::SoundId::ButtonA);
        if (!isEndGame_) {
            const int maxChars = (gm_.save().data().currentMap == 0) ? 4 : 5;
            charSelectionIndex_ = circularAdd(charSelectionIndex_, 1, maxChars);
        }
        return;
    }
}

void LogicManager::openGameMenu() {
    currentMainMenu_ = MainMenuTab::Map;
    currentScreen_ = Screen::MainMenu;
}

void LogicManager::openGameMenu2() {
    currentMainMenu2_ = MainMenu2Tab::Database;
    currentScreen_ = Screen::MainMenu2;
}

void LogicManager::closeGameMenu() {
    currentScreen_ = Screen::Character;
}

void LogicManager::openApp(AppId app) {
    currentScreen_ = Screen::App;
    loadedApp_ = app;
}

void LogicManager::closeLoadedApp(Screen newScreen) {
    if (loadedApp_ == AppId::None) return;
    loadedApp_ = AppId::None;
    currentScreen_ = eventPending_ ? Screen::Character : newScreen;
}

void LogicManager::triggerPendingEvent() {
    eventPending_ = false;
    eventRecoveryPending_ = false;
    gm_.save().data().pendingEvent = 0;
}

void LogicManager::selectCharacterAndCreateGame() {
    gm_.save().createNew((GameChar)charSelectionIndex_, -1, -1);
    currentScreen_ = Screen::Character;
    gm_.playIntroAnimation();
}

void LogicManager::selectCharacterPart2Game() {
    gm_.save().data().gameChar = (uint8_t)charSelectionIndex_;
    currentScreen_ = Screen::Character;
}

} // namespace dtec::game::core
