#include "test_animation.h"
#include "mocks.h"
#include <cstdint>
#include <cassert>

// Mock animation frame data for native tests
static const uint16_t kTestFrameA[] = {
    0x0000, 0x001F, 0x07E0, 0x07FF,
    0xF800, 0xF81F, 0xFFE0, 0xFFFF
};
static const uint16_t kTestFrameB[] = {
    0xFFFF, 0xF81F, 0xFFE0, 0x07FF,
    0x07E0, 0x001F, 0x0000, 0xF800
};

static const uint16_t* kTestFrames[] = {kTestFrameA, kTestFrameB};

void test_animation() {
    // Verify basic frame array properties
    assert(kTestFrames[0] != nullptr);
    assert(kTestFrames[1] != nullptr);

    // Verify we can read pixels without fault
    volatile uint16_t pixelA = kTestFrames[0][0];
    volatile uint16_t pixelB = kTestFrames[1][7];
    (void)pixelA;
    (void)pixelB;

    // Verify frame count
    constexpr int kExpectedFrameCount = 2;
    static_assert(sizeof(kTestFrames) / sizeof(kTestFrames[0]) == kExpectedFrameCount,
                  "Test frame count mismatch");
}
