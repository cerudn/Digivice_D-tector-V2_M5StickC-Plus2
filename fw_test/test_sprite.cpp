#include "test_sprite.h"
#include "mocks.h"
#include <cstdint>
#include <cassert>

// Test asset
#include "../assets/characters/characters_0.h"

#include "../include/hal/Display.h"

void test_sprite() {
    // Verify the asset array is non-null.
    assert(character_0_data != nullptr);

    // Verify dimensions match expected 32x32.
    constexpr uint16_t kExpectedWidth = 32;
    constexpr uint16_t kExpectedHeight = 32;
    constexpr size_t kExpectedElements = kExpectedWidth * kExpectedHeight; // 1024

    // Build a Bitmap descriptor as the renderer would.
    hal::Bitmap bitmap{
        .data = character_0_data,
        .width = kExpectedWidth,
        .height = kExpectedHeight
    };

    assert(bitmap.data != nullptr);
    assert(bitmap.width == kExpectedWidth);
    assert(bitmap.height == kExpectedHeight);

    // Optional sanity check: ensure we can read a pixel without fault.
    // This does not validate visual content, only memory accessibility.
    volatile uint16_t sample = bitmap.data[0];
    (void)sample;

    // Verify the array size at compile time via sizeof.
    // character_0_data is an array of 1024 uint16_t values.
    static_assert(sizeof(character_0_data) == kExpectedElements * sizeof(uint16_t),
                  "character_0_data size mismatch");
}
