#pragma once
#include "game/state/GameStates.h"
#include <cstdint>
#include <cstddef>

namespace dtec::game::anim {

struct AnimFrame {
    uint8_t spriteIndex;
    uint16_t durationMs;
};

constexpr int kMaxFrames = 8;

struct AnimationDef {
    AnimFrame frames[kMaxFrames];
    uint8_t frameCount;
    bool loop;
};

inline constexpr AnimationDef kAnimations[(size_t)AnimationId::Count] = {
    { {}, 0, false },
    { { {0,150},{1,250},{0,150},{1,250},{0,62},{1,62} }, 6, false },
    { { {0,62},{1,62},{0,62},{1,62} }, 4, false },
    { { {0,500},{1,500} }, 2, false },
    { { {0,475},{1,475} }, 2, false },
    { { {0,600},{1,600} }, 2, true },
};

class AnimationManager {
public:
    void play(AnimationId id, uint32_t nowMs);
    void tick(uint32_t nowMs);
    bool isPlaying() const { return current_ != AnimationId::None; }
    AnimationId current() const { return current_; }
    uint8_t currentFrameIndex() const { return frameIdx_; }
    uint8_t currentSpriteIndex() const;

private:
    AnimationId current_ = AnimationId::None;
    uint8_t frameIdx_ = 0;
    uint32_t frameStartMs_ = 0;
};

} // namespace dtec::game::anim
