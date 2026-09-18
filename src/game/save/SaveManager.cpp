#include "game/save/SaveManager.h"
#include <cstring>

#ifdef ARDUINO
#include <esp_system.h>
#else
#include <cstdlib>
static uint32_t esp_random() { return (uint32_t)rand(); }
#endif

namespace dtec::game::save {

static uint32_t crc32_update(uint32_t crc, const uint8_t* bytes, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        crc ^= bytes[i];
        for (int b = 0; b < 8; ++b) {
            uint32_t mask = (crc & 1u) ? 0xFFFFFFFFu : 0u;
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return crc;
}

uint32_t SaveManager::computeChecksum() const {
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&data_);
    const size_t len = sizeof(SaveData) - sizeof(data_.checksum);
    return ~crc32_update(0xFFFFFFFFu, bytes, len);
}

bool SaveManager::load() {
    SaveData tmp{};
    size_t outLen = 0;
    if (!storage_.loadBlob(kBlobKey, &tmp, sizeof(tmp), outLen)) return false;
    if (outLen != sizeof(SaveData)) return false;
    if (tmp.magic != 0x44544332u) return false;
    if (tmp.schemaVersion != dtec::SAVE_SCHEMA_VERSION) return false;

    SaveData check = tmp;
    check.checksum = 0;
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&check);
    const size_t len = sizeof(SaveData) - sizeof(check.checksum);
    uint32_t crc = ~crc32_update(0xFFFFFFFFu, bytes, len);
    if (crc != tmp.checksum) return false;

    data_ = tmp;
    dirty_ = false;
    return data_.gameChar != (uint8_t)dtec::game::GameChar::None;
}

void SaveManager::createNew(dtec::game::GameChar chosenChar, int16_t startingSpiritIndex, int16_t startingInitialIndex) {
    data_ = SaveData{};
    data_.gameChar = (uint8_t)chosenChar;
    data_.cheatsUsed = false;
    data_.stepsToNextEvent = 300;
    data_.spiritPower = dtec::MAX_SPIRIT_POWER;
    data_.currentMap = 0;
    data_.currentArea = 0;
    data_.battleSeed[0] = (int32_t)esp_random();
    data_.battleSeed[1] = (int32_t)esp_random();
    data_.battleSeed[2] = (int32_t)esp_random();

    if (startingSpiritIndex >= 0 && startingSpiritIndex < MAX_DIGIMON_SLOTS)
        data_.digimonLevel[startingSpiritIndex] = 1;
    if (startingInitialIndex >= 0 && startingInitialIndex < MAX_DIGIMON_SLOTS)
        data_.digimonLevel[startingInitialIndex] = 1;

    if ((size_t)dtec::game::GameChar::Koichi < MAX_CHARACTERS) {
        data_.characterLost[(size_t)dtec::game::GameChar::Koichi] = 1;
    }

    dirty_ = true;
    forceFlush();
}

void SaveManager::tick(uint32_t nowMs) {
    if (dirty_ && (nowMs - lastFlushMs_) >= kFlushIntervalMs) {
        writeToStorage();
        lastFlushMs_ = nowMs;
    }
}

void SaveManager::forceFlush() {
    writeToStorage();
}

void SaveManager::writeToStorage() {
    data_.checksum = 0;
    data_.checksum = computeChecksum();
    storage_.saveBlob(kBlobKey, &data_, sizeof(data_));
    dirty_ = false;
}

} // namespace dtec::game::save
