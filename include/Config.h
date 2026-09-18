#pragma once
#include <cstdint>

namespace dtec {

constexpr const char* GAME_VERSION = "0.1.0-esp32";

constexpr int LOGICAL_SCREEN_W = 32;
constexpr int LOGICAL_SCREEN_H = 32;

constexpr int DISPLAY_W = 135;
constexpr int DISPLAY_H = 240;
constexpr int GAME_SCALE = 4;
constexpr int GAME_VIEW_W = LOGICAL_SCREEN_W * GAME_SCALE;
constexpr int GAME_VIEW_H = LOGICAL_SCREEN_H * GAME_SCALE;
constexpr int GAME_VIEW_X = (DISPLAY_W - GAME_VIEW_W) / 2;
constexpr int GAME_VIEW_Y = 4;

constexpr uint32_t DISPLAY_REFRESH_MS = 50;
constexpr float ATTACK_TRAVEL_SPEED = 0.05f;
constexpr float CRUSH_TRAVEL_SPEED = 0.035f;

constexpr int MAX_SPIRIT_POWER = 99;
constexpr const char* DEFAULT_DIGIMON = "numemon";
constexpr const char* DEFAULT_SPIRIT_DIGIMON = "flamemon";

constexpr uint32_t INPUT_REPEAT_DELAY_MS = 350;
constexpr uint32_t INPUT_REPEAT_INTERVAL_MS = 120;
constexpr uint32_t LONG_PRESS_MS = 450;

constexpr const char* SAVE_NAMESPACE = "dtector_save";
constexpr uint16_t SAVE_SCHEMA_VERSION = 1;

} // namespace dtec
