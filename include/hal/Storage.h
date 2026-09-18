#pragma once
#include <cstdint>
#include <cstddef>

namespace dtec::hal {

class IStorage {
public:
    virtual ~IStorage() = default;
    virtual void begin() = 0;
    virtual bool loadBlob(const char* key, void* out, size_t maxLen, size_t& outLen) = 0;
    virtual bool saveBlob(const char* key, const void* data, size_t len) = 0;
    virtual bool eraseBlob(const char* key) = 0;
    virtual void setString(const char* key, const char* value) = 0;
    virtual bool getString(const char* key, char* out, size_t maxLen) = 0;
    virtual void setInt(const char* key, int32_t value) = 0;
    virtual int32_t getInt(const char* key, int32_t defaultValue) = 0;
};

} // namespace dtec::hal
