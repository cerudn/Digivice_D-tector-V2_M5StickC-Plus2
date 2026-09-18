#include <M5Unified.h>

#include "hal/m5/M5Display.h"
#include "hal/m5/M5Input.h"
#include "hal/m5/M5Audio.h"
#include "hal/m5/M5Sensors.h"
#include "hal/m5/M5Storage.h"

#include "game/core/GameManager.h"
#include "render/GameRenderer.h"

using namespace dtec;

static hal::m5impl::M5Display g_display;
static hal::m5impl::M5Input g_input;
static hal::m5impl::M5Audio g_audio;
static hal::m5impl::M5Sensors g_sensors;
static hal::m5impl::M5Storage g_storage;

static game::core::GameManager g_gameManager(g_display, g_input, g_audio, g_sensors, g_storage);
static render::GameRenderer g_renderer(g_display);

static game::Screen g_lastRenderedScreen = game::Screen::END;
static int g_lastCharIndex = -1;
static game::AppId g_lastApp = game::AppId::None;
static game::AnimationId g_lastAnim = game::AnimationId::None;

void setup() {
    auto cfg = M5.config();
    cfg.internal_imu = true;
    cfg.internal_rtc = true;
    cfg.internal_spk = true;
    M5.begin(cfg);

    Serial.begin(115200);
    Serial.println("[D-Tector V2] Boot -- M5StickC Plus2 firmware");

    g_gameManager.begin();

    Serial.printf("[D-Tector V2] Estado inicial: Screen=%d\n",
                  (int)g_gameManager.logic().currentScreen());

    g_renderer.draw(g_gameManager.logic(), g_gameManager.anim());
}

void loop() {
    g_gameManager.loop();
    g_audio.tick();

    const auto& logic = g_gameManager.logic();
    const auto& anim = g_gameManager.anim();
    if (logic.currentScreen() != g_lastRenderedScreen ||
        logic.charSelectionIndex() != g_lastCharIndex ||
        logic.loadedApp() != g_lastApp ||
        anim.current() != g_lastAnim) {
        g_renderer.draw(logic, anim);
        g_lastRenderedScreen = logic.currentScreen();
        g_lastCharIndex = logic.charSelectionIndex();
        g_lastApp = logic.loadedApp();
        g_lastAnim = anim.current();

        Serial.printf("[D-Tector V2] Screen=%d CharIdx=%d App=%d Anim=%d\n",
                      (int)g_lastRenderedScreen, g_lastCharIndex, (int)g_lastApp, (int)g_lastAnim);
    }

    delay(1);
}
