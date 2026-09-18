#pragma once
#include <cstdint>
#include "Config.h"
#include "game/state/GameStates.h"

namespace dtec::game::save {

constexpr int MAX_DIGIMON_SLOTS = 700;
constexpr int MAX_CHARACTERS = 6;
constexpr int MAX_DDOCKS = 4;
constexpr int MAX_WORLDS = 4;
constexpr int MAX_AREAS_PER_WORLD = 12;

#pragma pack(push, 1)
struct SaveData {
    uint16_t schemaVersion = dtec::SAVE_SCHEMA_VERSION;
    uint32_t magic = 0x44544332;

    char name[16] = {0};
    uint8_t gameChar = (uint8_t)dtec::game::GameChar::None;
    bool cheatsUsed = false;

    uint8_t pendingEvent = 0;
    bool isPlayerInsured = false;
    bool isLeaverBusterActive = false;
    uint32_t leaverBusterExpLoss = 0;
    int16_t leaverBusterDigimonIndex = -1;
    bool isPlayerDefeated = false;
    int32_t jackpotValue = 0;

    int32_t currentMap = 0;
    int32_t currentArea = 0;
    int32_t currentDistance = 0;
    int32_t steps = 0;
    int32_t stepsToNextEvent = 300;
    int32_t playerExperience = 0;
    int32_t spiritPower = 0;
    int32_t battleSeed[3] = {0, 0, 0};
    int32_t totalBattles = 0;
    int32_t totalWins = 0;
    int16_t ddockDigimon[MAX_DDOCKS] = {-1, -1, -1, -1};

    uint8_t digimonLevel[MAX_DIGIMON_SLOTS] = {0};
    uint8_t digicodeUnlocked[(MAX_DIGIMON_SLOTS + 7) / 8] = {0};
    uint8_t characterLost[MAX_CHARACTERS] = {0};
    uint8_t spiritLost[(MAX_DIGIMON_SLOTS + 7) / 8] = {0};

    uint8_t areasCompleted[MAX_WORLDS][MAX_AREAS_PER_WORLD] = {{0}};
    int32_t statRandom[MAX_CHARACTERS][4] = {{0}};
    int32_t statBeforeRandom[MAX_CHARACTERS][4] = {{0}};
    int16_t semibossGroup[MAX_WORLDS] = {0};

    uint32_t checksum = 0;
};
#pragma pack(pop)

inline bool getBit(const uint8_t* bits, int index) {
    return (bits[index / 8] >> (index % 8)) & 1;
}
inline void setBit(uint8_t* bits, int index, bool value) {
    if (value) bits[index / 8] |= (uint8_t)(1u << (index % 8));
    else bits[index / 8] &= (uint8_t)~(1u << (index % 8));
}

} // namespace dtec::game::save
