# Digivice D-Tector V2 -- Firmware M5StickC Plus2

Port nativo (sin Unity) del videojuego Digivice D-Tector V2 para M5Stack M5StickC Plus2 (ESP32-PICO-V3-02), usando PlatformIO + M5Unified.

Unity (`cerudn/Digivice_D-tector-V2_Unity-`) es la referencia funcional del proyecto. El analisis completo vive en `Docs/` de ese repositorio (`DTECTOR_V2_ANALYSIS.md`, `ASSET_CATALOG.md`, `PORTING_STATUS.md`).

## Estado actual (ver Docs/PORTING_STATUS.md para detalle por componente)

**Milestone 1 alcanzado**: boot -> M5.begin() -> HAL (Display/Input/Audio/Sensors/Storage) -> GameManager -> LogicManager (maquina de estados real) -> AnimationManager (animaciones reales con timing extraido de Unity) -> GameRenderer (render de texto de pantalla real: CharSelection/Character/MainMenu/MainMenu2/App) -> input funcional con botones reales + Left/Right sintetizados por pulsacion larga -> SaveManager (CRC32, 1.2KB) -> CharacterData (tabla real de 6 personajes extraida de characters.json).

## Compilar (requiere PlatformIO)

```
pio run
```

## Subir al M5StickC Plus2

```
pio run --target upload
```

## Monitor serie

```
pio device monitor -b 115200
```

**IMPORTANTE**: la compilacion con PlatformIO/toolchain ESP32 y la ejecucion en hardware real (M5StickC Plus2, pantalla ST7789, botones, IMU MPU6886, RTC, audio, almacenamiento NVS) **no han podido verificarse en el entorno de desarrollo actual** (sin acceso a PlatformIO ni a internet). Queda como PLATFORMIO-BUILD-PENDING / HARDWARE-TEST-PENDING explicito -- ver Docs/PORTING_STATUS.md.

## Tests nativos (sin hardware, sin PlatformIO)

La logica de juego (GameManager, LogicManager, SaveManager, AnimationManager) esta desacoplada del hardware via interfaces `hal::I*` (ver `include/hal/`). Esto permite compilarla y testearla con un compilador C++ nativo (g++), usando mocks de HAL, sin necesitar el ESP32 ni PlatformIO:

```
g++ -std=c++17 -Wall -Wextra -Ifw/include -Ifw_test fw_test/test_main.cpp fw/src/game/core/GameManager.cpp fw/src/game/core/LogicManager.cpp fw/src/game/save/SaveManager.cpp fw/src/game/anim/AnimationManager.cpp -o run_tests
./run_tests
```

**28 tests unitarios** cubren:
- Estado inicial de la maquina de estados
- Navegacion circular en CharSelection/MainMenu/MainMenu2
- Creacion de partida
- Transiciones Character<->MainMenu<->App
- `takeAStep()` (progresion de distancia y disparo de evento de jefe)
- `shakeDisabled()`
- Ciclo completo de guardado/carga/deteccion de corrupcion de `SaveManager` (checksum CRC32)
- **NUEVO**: CharacterData (tabla real de personajes, stats y espiritus)
- **NUEVO**: AnimationManager (maquina de estados de animacion con timing real extraido de Unity)
- **NUEVO**: Bloqueo de input durante animaciones (equivalente a LockInput/UnlockInput de Unity)

## Estructura

```
include/
  Config.h                 Configuracion global (resolucion, timing, reglas de juego)
  hal/                      Interfaces de hardware (Display, Input, Audio, Sensors, Storage)
  hal/m5/                   Implementaciones concretas sobre M5Unified (unica capa que la incluye)
  game/state/               Enums de estado extraidos 1:1 de Logic/MenuEnums.cs (Unity)
  game/data/                CharacterData.h (tabla real de 6 personajes)
  game/anim/                AnimationManager.h/cpp (maquina de estados de animacion)
  game/core/                GameManager + LogicManager (maquina de estados real)
  game/save/                SaveData (struct binario, 1.2KB) + SaveManager (checksum CRC32)
  render/                   GameRenderer (render de texto real)
src/
  main.cpp                  Entry point
  hal/m5/                   .cpp de implementaciones M5Unified
  game/                     .cpp de core, save, anim
  render/                   .cpp de render
fw_test/                    Mocks de HAL + test suite nativo (no se compila con PlatformIO)
```

## Arquitectura

```
GAME LOGIC   (game/core/LogicManager, game/save/*, game/anim/*)
     v
GAME STATE   (game/state/GameStates.h)
     v
RENDER / INPUT / AUDIO / SENSORS   (render/*, hal/*)
     v
M5StickC Plus2   (hal/m5/* -- unica capa que incluye M5Unified.h)
```

La logica de juego nunca incluye `M5Unified.h` ni depende de hardware; solo conoce las interfaces `hal::I*`. Verificado compilando y testeando esa capa de forma completamente nativa (ver seccion Tests).

## Flujo jugable actual (Milestone 1)

```
BOOT
 ↓
INITIAL SCREEN (CharSelection con animacion LoadCharacterSelection)
 ↓
INPUT (Left/Right/A/B reales, Left/Right sintetizados por long-press)
 ↓
CHARACTER SELECTION (Takuya/Koji/JP/Zoe -- circular, 4 opciones en mundo 0)
 ↓
CHARACTER DATA (datos reales de characters.json: stats, espiritus, disabled flag)
 ↓
NAME / CONFIGURATION (name[] en SaveData, gameChar, spiritPower=99, Koichi perdido)
 ↓
INTRO (StartGameAnimation, input bloqueado hasta terminar)
 ↓
IDLE (Character screen, estado "IDLE" por defecto)
 ↓
MOVEMENT (shake -> takeAStep(), reduce distancia, marca boss en distancia=1)
 ↓
GAMEPLAY STATE (MainMenu/Map/Status/Spirits/App -- navegacion circular real)
```

## Proximo milestone (en desarrollo)

- Render de sprites reales (pipeline: asset original -> conversion/optimizacion -> formato ESP32 -> flash/PROGMEM -> blit en M5Display)
- Animaciones completas (frames reales extraidos de Unity: CharHappyShort, CharSadShort, PAFlashEyesEffect, etc.)
- Apps funcionales (Status, Map, Spirits, Camp, Database, CodeInput, Finder, JackpotBox, SpeedRunner, etc.)
- Sistema de batalla (Battle.cs logic, AttackChooser, timers, eventos)
- Persistencia completa de Digimon (digimonLevel[], digicodeUnlocked[], spiritLost[])
- Progreso de mundo (areasCompleted[], semibossGroup[], statRandom[])
