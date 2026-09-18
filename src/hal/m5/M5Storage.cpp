#include "hal/m5/M5Storage.h"
#include "Config.h"

namespace dtec::hal::m5impl {

void M5Storage::begin() {
    prefs_.begin(dtec::SAVE_NAMESPACE, false);
}

bool M5Storage::loadBlob(const char* key, void* out, size_t maxLen, size_t& outLen) {
    outLen = prefs_.getBytesLength(key);
    if (outLen == 0 || outLen > maxLen) return false;
    return prefs_.getBytes(key, out, outLen) == outLen;
}

bool M5Storage::saveBlob(const char* key, const void* data, size_t len) {
    return prefs_.putBytes(key, data, len) == len;
}

bool M5Storage::eraseBlob(const char* key) {
    return prefs_.remove(key);
}

void M5Storage::setString(const char* key, const char* value) {
    prefs_.putString(key, value);
}

bool M5Storage::getString(const char* key, char* out, size_t maxLen) {
    String v = prefs_.getString(key, "");
    if (v.length() == 0) return false;
    v.toCharArray(out, maxLen);
    return true;
}

void M5Storage::setInt(const char* key, int32_t value) {
    prefs_.putInt(key, value);
}

int32_t M5Storage::getInt(const char* key, int32_t defaultValue) {
    return prefs_.getInt(key, defaultValue);
}

} // namespace dtec::hal::m5impl
