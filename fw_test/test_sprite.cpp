#include "test_sprite.h"
#include "mocks.h"
#include <cstdint>
#include <cassert>

#include "../assets/characters/characters_0.h"
#include "../include/hal/Display.h"

void test_sprite() {
    assert(characters_0 != nullptr);

    constexpr uint16_t kExpectedWidth = 32;
    constexpr uint16_t kExpectedHeight = 32;
    constexpr size_t kExpectedElements = kExpectedWidth * kExpectedHeight;

    hal::Bitmap bitmap{
        .data = characters_0,
        .width = kExpectedWidth,
        .height = kExpectedHeight
    };

    assert(bitmap.data != nullptr);
    assert(bitmap.width == kExpectedWidth);
    assert(bitmap.height == kExpectedHeight);

    volatile uint16_t sample = bitmap.data[0];
    (void)sample;

    static_assert(sizeof(characters_0) == kExpectedElements * sizeof(uint16_t),
                  "characters_0 size mismatch");
}
