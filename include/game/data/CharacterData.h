#pragma once
#include <cstdint>
#include "game/state/GameStates.h"

namespace dtec::game::data {

struct CharStats {
    int16_t HP, SP, ST, SK;
};

struct CharacterEntry {
    const char* name;
    uint8_t element;
    CharStats stats;
    CharStats lastStat;
    const char* spiritHuman;
    const char* spiritAnimal;
    bool disabled;
    int8_t order;
    int8_t number;
};

inline constexpr CharacterEntry kCharacters[6] = {
    { "takuya", 0, {6,5,5,7},  {110,160,120,115}, "agunimon",       "burninggreymon",    false, 1, 0 },
    { "koji",   0, {6,7,5,5},  {110,115,120,160}, "lobomon",        "kendogarurumon",    false, 2, 1 },
    { "jp",     0, {8,4,8,5},  {110,110,160,120}, "beetlemon",      "metalkabuterimon",  false, 3, 2 },
    { "zoe",    0, {5,5,4,7},  {105,100,120,140}, "kazemon",        "zephyrmon",         false, 4, 3 },
    { "tommy",  0, {5,7,5,4},  {100,130,130,130}, "kumamon",        "korikakumon",       true,  5, 4 },
    { "koichi", 0, {7,8,7,10}, {110,160,120,115}, "loweemon",       "kaiserleomon",      false, 6, 5 },
};

inline const CharacterEntry* findCharacter(dtec::game::GameChar c) {
    const uint8_t idx = (uint8_t)c;
    if (idx >= 6) return nullptr;
    return &kCharacters[idx];
}

} // namespace dtec::game::data
