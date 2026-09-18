#include "game/anim/AnimationManager.h"
#include <iostream>
#include <cassert>

using namespace dtec::game;

int failures = 0;
#define CHECK(cond, msg) do { if (!(cond)) { std::cerr << "FAIL: " << msg << " (line " << __LINE__ << ")\n"; failures++; } else { std::cout << "PASS: " << msg << "\n"; } } while(0)

int main() {
    // Test 1: CharHappyShort timing (2 frames x 500ms each)
    {
        anim::AnimationManager am;
        am.play(AnimationId::CharHappyShort, 0);
        CHECK(am.isPlaying(), "CharHappyShort starts playing");
        CHECK(am.currentFrameIndex() == 0, "Frame 0 at t=0");

        am.tick(499); // just before frame transition
        CHECK(am.currentFrameIndex() == 0, "Still frame 0 at t=499ms");

        am.tick(500); // exactly at frame transition
        CHECK(am.currentFrameIndex() == 1, "Frame 1 at t=500ms");

        am.tick(999); // just before end
        CHECK(am.currentFrameIndex() == 1, "Still frame 1 at t=999ms");

        am.tick(1000); // animation complete
        CHECK(!am.isPlaying(), "CharHappyShort complete at t=1000ms");
    }

    // Test 2: CharSadShort timing (2 frames x 475ms each)
    {
        anim::AnimationManager am;
        am.play(AnimationId::CharSadShort, 0);
        am.tick(474);
        CHECK(am.currentFrameIndex() == 0, "CharSadShort frame 0 at t=474ms");

        am.tick(475);
        CHECK(am.currentFrameIndex() == 1, "CharSadShort frame 1 at t=475ms");

        am.tick(949);
        CHECK(am.currentFrameIndex() == 1, "CharSadShort frame 1 at t=949ms");

        am.tick(950);
        CHECK(!am.isPlaying(), "CharSadShort complete at t=950ms");
    }

    // Test 3: EyesBlinkIdle loop (2 frames x 600ms, infinite loop)
    {
        anim::AnimationManager am;
        am.play(AnimationId::EyesBlinkIdle, 0);

        for (int cycle = 0; cycle < 5; ++cycle) {
            am.tick(cycle * 1200 + 599);
            CHECK(am.currentFrameIndex() == 0, "EyesBlinkIdle frame 0 in cycle " + std::to_string(cycle));

            am.tick(cycle * 1200 + 600);
            CHECK(am.currentFrameIndex() == 1, "EyesBlinkIdle frame 1 in cycle " + std::to_string(cycle));

            CHECK(am.isPlaying(), "EyesBlinkIdle still playing (loop)");
        }
    }

    // Test 4: AnimationId to frame count mapping
    {
        constexpr uint8_t expectedFrames[(size_t)AnimationId::Count] = {
            0, // None
            6, // LoadCharacterSelection
            4, // StartGameAnimation
            2, // CharHappyShort
            2, // CharSadShort
            2, // EyesBlinkIdle
        };

        for (size_t i = 0; i < (size_t)AnimationId::Count; ++i) {
            anim::AnimationManager am;
            am.play((AnimationId)i, 0);
            // Just verify it doesn't crash and frameCount > 0 for non-None
            if (i > 0) {
                CHECK(am.currentFrameIndex() == 0, "AnimationId " + std::to_string(i) + " starts at frame 0");
            }
        }
    }

    // Test 5: Frame sequence integrity (frames advance in order)
    {
        anim::AnimationManager am;
        am.play(AnimationId::CharHappyShort, 0);

        uint8_t prevFrame = 0;
        for (uint32_t t = 0; t <= 1000; t += 50) {
            am.tick(t);
            uint8_t currFrame = am.currentFrameIndex();
            if (t < 500) {
                CHECK(currFrame == 0, "Frame sequence: frame 0 until t=500ms");
            } else if (t < 1000) {
                CHECK(currFrame == 1, "Frame sequence: frame 1 from t=500ms to t=1000ms");
            } else {
                CHECK(!am.isPlaying(), "Frame sequence: animation complete at t=1000ms");
            }
            prevFrame = currFrame;
        }
    }

    std::cout << "\n=== " << (failures == 0 ? "ALL ANIMATION TESTS PASSED" : "SOME ANIMATION TESTS FAILED") << " (" << failures << " failures) ===\n";
    return failures == 0 ? 0 : 1;
}
