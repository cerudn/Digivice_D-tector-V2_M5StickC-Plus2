#include <Arduino.h>
#include <M5Unified.h>

#include "game/core/GameManager.h"
#include "hal/m5/M5Display.h"
#include "hal/m5/M5Input.h"
#include "hal/m5/M5Audio.h"
#include "hal/m5/M5Sensors.h"
#include "hal/m5/M5Storage.h"
#include "render/GameRenderer.h"

using namespace hal;
using namespace render;

M5Display display;
M5Input input;
M5Audio audio;
M5Sensors sensors;
M5Storage storage;

GameRenderer gameRenderer(display);
GameManager gameManager(display, input, audio, storage, gameRenderer);

void setup() {
    gameManager.init();
    display.clear(TFT_BLACK);

    // First sprite integration test: draw characters_0 at a fixed position.
    gameRenderer.drawTestSprite();
}

void loop() {
    gameManager.update();
    delay(16);  // ~60 FPS cap
}
