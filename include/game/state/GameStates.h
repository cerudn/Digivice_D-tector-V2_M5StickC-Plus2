#pragma once
#include <cstdint>

namespace dtec::game {

enum class Direction : uint8_t { Left, Right, Up, Down, None };

enum class Screen : uint8_t {
    CharSelection, Character, MainMenu, MainMenu2,
    App, GamesMenu, GamesRewardMenu, GamesTravelMenu, END
};

enum class MainMenuTab : uint8_t { Map, Status, Spirits, Connect, Camp, Count };
enum class MainMenu2Tab : uint8_t { Database, Digits, Game, Finder, Count };
enum class GameMenuTab : uint8_t { Reward, Travel };
enum class GameRewardMenuTab : uint8_t { FindBattle, JackpotBox, EnergyWars, DigiCatch };
enum class GameTravelMenuTab : uint8_t { SpeedRunner, Asteroids, DigiHunter, Maze };

enum class AppId : uint8_t {
    Map, Status, Spirits, Database, CodeInput, Camp, Connect,
    Finder, Battle, JackpotBox, EnergyWars, DigiCatch,
    SpeedRunner, Asteroids, DigiHunter, Maze, Character, End,
    None
};

enum class Reward : uint8_t {
    None, Empty,
    IncreaseDistance300, IncreaseDistance500, IncreaseDistance2000,
    ReduceDistance500, ReduceDistance1000,
    PunishDigimon, RewardDigimon,
    UnlockDigicodeOwned, UnlockDigicodeNotOwned,
    DataStorm,
    LoseSpiritPower10, LoseSpiritPower50,
    GainSpiritPower10, GainSpiritPowerMax,
    LevelDown, LevelUp, ForceLevelDown, ForceLevelUp,
    TriggerBattle
};

enum class GameChar : uint8_t { Takuya = 0, Koji = 1, JP = 2, Zoe = 3, Tommy = 4, Koichi = 5, None = 6 };

enum class AnimationId : uint8_t {
    None,
    LoadCharacterSelection,
    StartGameAnimation,
    CharHappyShort,
    CharSadShort,
    EyesBlinkIdle,
    Count
};

template <typename EnumT>
inline EnumT circularNext(EnumT value, uint8_t count) {
    uint8_t v = (uint8_t)value;
    v = (uint8_t)((v + 1) % count);
    return (EnumT)v;
}

template <typename EnumT>
inline EnumT circularPrev(EnumT value, uint8_t count) {
    uint8_t v = (uint8_t)value;
    v = (uint8_t)((v + count - 1) % count);
    return (EnumT)v;
}

inline int circularAdd(int value, int amount, int exclusiveMax) {
    int v = (value + amount) % exclusiveMax;
    if (v < 0) v += exclusiveMax;
    return v;
}

} // namespace dtec::game
