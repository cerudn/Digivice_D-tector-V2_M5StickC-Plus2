#pragma once
#include "game/save/SaveData.h"
#include "hal/Storage.h"

namespace dtec::game::save {

class SaveManager {
public:
    static constexpr uint32_t kFlushIntervalMs = 5000;
    static constexpr const char* kBlobKey = "save_v1";

    explicit SaveManager(dtec::hal::IStorage& storage) : storage_(storage) {}

    bool load();
    void createNew(dtec::game::GameChar chosenChar, int16_t startingSpiritIndex, int16_t startingInitialIndex);

    SaveData& data() { dirty_ = true; return data_; }
    const SaveData& data() const { return data_; }

    void tick(uint32_t nowMs);
    void forceFlush();

private:
    dtec::hal::IStorage& storage_;
    SaveData data_{};
    bool dirty_ = false;
    uint32_t lastFlushMs_ = 0;

    uint32_t computeChecksum() const;
    void writeToStorage();
};

} // namespace dtec::game::save
