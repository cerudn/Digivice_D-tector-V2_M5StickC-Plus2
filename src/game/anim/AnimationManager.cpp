#include "game/anim/AnimationManager.h"

namespace dtec::game::anim {

void AnimationManager::play(AnimationId id, uint32_t nowMs) {
    current_ = id;
    frameIdx_ = 0;
    frameStartMs_ = nowMs;
}

void AnimationManager::tick(uint32_t nowMs) {
    if (current_ == AnimationId::None) return;
    const AnimationDef& def = kAnimations[(size_t)current_];
    if (def.frameCount == 0) { current_ = AnimationId::None; return; }

    const AnimFrame& f = def.frames[frameIdx_];
    if (nowMs - frameStartMs_ >= f.durationMs) {
        frameStartMs_ = nowMs;
        frameIdx_++;
        if (frameIdx_ >= def.frameCount) {
            if (def.loop) {
                frameIdx_ = 0;
            } else {
                current_ = AnimationId::None;
                frameIdx_ = 0;
            }
        }
    }
}

uint8_t AnimationManager::currentSpriteIndex() const {
    if (current_ == AnimationId::None) return 0;
    const AnimationDef& def = kAnimations[(size_t)current_];
    if (frameIdx_ >= def.frameCount) return 0;
    return def.frames[frameIdx_].spriteIndex;
}

} // namespace dtec::game::anim
