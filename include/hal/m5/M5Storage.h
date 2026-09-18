#pragma once
#include "hal/Storage.h"
#include <Preferences.h>

namespace dtec::hal::m5impl {

class M5Storage : public dtec::hal::IStorage {
public:
    void begin() override;
    bool loadBlob(const char* key, void* out, size_t maxLen, size_t& outLen) override;
    bool saveBlob(const char* key, const void* data, size_t len) override;
    bool eraseBlob(const char* key) override;
    void setString(const char* key, const char* value) override;
    bool getString(const char* key, char* out, size_t maxLen) override;
    void setInt(const char* key, int32_t value) override;
    int32_t getInt(const char* key, int32_t defaultValue) override;

private:
    Preferences prefs_;
};

} // namespace dtec::hal::m5impl
