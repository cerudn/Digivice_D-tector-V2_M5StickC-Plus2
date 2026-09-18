#include "hal/Display.h"
#include "hal/Input.h"
#include "hal/Audio.h"
#include "hal/Sensors.h"
#include "hal/Storage.h"
#include <cstring>
#include <map>
#include <string>

using namespace dtec::hal;

class MockDisplay : public IDisplay {
public:
    void begin() override {}
    void beginFrame() override {}
    void endFrame() override {}
    void blit(int, int, int, int, const uint16_t*, bool) override {}
    void fillRect(int, int, int, int, Color565) override {}
    void clear(Color565) override {}
    void setBrightness(uint8_t) override {}
};

class MockInput : public IInput {
public:
    void begin() override {}
    void poll() override {}
    bool wasPressed(LogicalButton b) const override { return pressed_[(size_t)b]; }
    bool wasReleased(LogicalButton) const override { return false; }
    bool isHeld(LogicalButton) const override { return false; }
    uint32_t heldDurationMs(LogicalButton) const override { return 0; }

    bool pressed_[4] = {false,false,false,false};
};

class MockAudio : public IAudio {
public:
    void begin() override {}
    void play(SoundId id) override { lastPlayed = id; playCount++; }
    void playDelayed(SoundId, uint32_t) override {}
    void stop() override {}
    bool isPlaying() const override { return false; }
    void setVolume(uint8_t) override {}
    SoundId lastPlayed = SoundId::Count;
    int playCount = 0;
};

class MockSensors : public ISensors {
public:
    void begin() override {}
    void poll() override {}
    bool shakeDetected() override { return false; }
    uint32_t epochSeconds() const override { return 0; }
};

class MockStorage : public IStorage {
public:
    void begin() override {}
    bool loadBlob(const char* key, void* out, size_t maxLen, size_t& outLen) override {
        auto it = blobs_.find(key);
        if (it == blobs_.end()) return false;
        if (it->second.size() > maxLen) return false;
        memcpy(out, it->second.data(), it->second.size());
        outLen = it->second.size();
        return true;
    }
    bool saveBlob(const char* key, const void* data, size_t len) override {
        blobs_[key] = std::string((const char*)data, len);
        return true;
    }
    bool eraseBlob(const char* key) override { blobs_.erase(key); return true; }
    void setString(const char*, const char*) override {}
    bool getString(const char*, char*, size_t) override { return false; }
    void setInt(const char*, int32_t) override {}
    int32_t getInt(const char*, int32_t defaultValue) override { return defaultValue; }
private:
    std::map<std::string, std::string> blobs_;
};
