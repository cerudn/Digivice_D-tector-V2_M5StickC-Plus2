#include "hal/m5/M5Input.h"
#include <M5Unified.h>

using dtec::hal::LogicalButton;

namespace dtec::hal::m5impl {

namespace {
struct DecodeResult {
    bool tapPressedEdge = false;
    bool tapReleasedEdge = false;
    bool longPressedEdge = false;
    bool longReleasedEdge = false;
};

struct PhysicalDecoder {
    bool physHeldPrev = false;
    uint32_t pressStartMs = 0;
    bool longFired = false;
    bool tapActive = false;

    DecodeResult update(bool physHeld, uint32_t now, uint32_t longPressMs) {
        DecodeResult r;
        if (physHeld && !physHeldPrev) {
            pressStartMs = now;
            longFired = false;
            tapActive = true;
            r.tapPressedEdge = true;
        } else if (physHeld && physHeldPrev) {
            if (!longFired && (now - pressStartMs) >= longPressMs) {
                longFired = true;
                if (tapActive) { r.tapReleasedEdge = true; tapActive = false; }
                r.longPressedEdge = true;
            }
        } else if (!physHeld && physHeldPrev) {
            if (longFired) r.longReleasedEdge = true;
            else if (tapActive) { r.tapReleasedEdge = true; tapActive = false; }
        }
        physHeldPrev = physHeld;
        return r;
    }
};

PhysicalDecoder g_decoderA;
PhysicalDecoder g_decoderB;
} // namespace

void M5Input::begin() {}

void M5Input::poll() {
    M5.update();
    updatePhysical(M5.BtnA.isPressed(), M5.BtnB.isPressed());
}

void M5Input::updatePhysical(bool physA, bool physB) {
    const uint32_t now = millis();
    for (auto& s : states_) { s.pressedEdge = false; s.releasedEdge = false; }

    DecodeResult da = g_decoderA.update(physA, now, dtec::LONG_PRESS_MS);
    auto& a = states_[(size_t)LogicalButton::A];
    auto& right = states_[(size_t)LogicalButton::Right];
    if (da.tapPressedEdge) { a.held = true; a.pressStartMs = now; a.pressedEdge = true; }
    if (da.tapReleasedEdge) { a.held = false; a.releasedEdge = true; }
    if (da.longPressedEdge) { right.held = true; right.pressStartMs = now; right.pressedEdge = true; }
    if (da.longReleasedEdge) { right.held = false; right.releasedEdge = true; }

    DecodeResult db = g_decoderB.update(physB, now, dtec::LONG_PRESS_MS);
    auto& b = states_[(size_t)LogicalButton::B];
    auto& left = states_[(size_t)LogicalButton::Left];
    if (db.tapPressedEdge) { b.held = true; b.pressStartMs = now; b.pressedEdge = true; }
    if (db.tapReleasedEdge) { b.held = false; b.releasedEdge = true; }
    if (db.longPressedEdge) { left.held = true; left.pressStartMs = now; left.pressedEdge = true; }
    if (db.longReleasedEdge) { left.held = false; left.releasedEdge = true; }
}

bool M5Input::wasPressed(LogicalButton b) const { return states_[(size_t)b].pressedEdge; }
bool M5Input::wasReleased(LogicalButton b) const { return states_[(size_t)b].releasedEdge; }
bool M5Input::isHeld(LogicalButton b) const { return states_[(size_t)b].held; }
uint32_t M5Input::heldDurationMs(LogicalButton b) const {
    const auto& s = states_[(size_t)b];
    return s.held ? (millis() - s.pressStartMs) : 0;
}

} // namespace dtec::hal::m5impl
