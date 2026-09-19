# Firmware Architecture Audit

**Scope:** verified source audit of `cerudn/Digivice_D-tector-V2_M5StickC-Plus2` at the asset-complete revision rooted at commit `160f85c`.

**Audit rule:** this document records only components and relationships found in the firmware source tree. It does not introduce sprite mappings, renderer changes, or new integration classes.

## Architecture Overview

The firmware is organized into four code areas:

- `src/main.cpp` is the Arduino/PlatformIO entry point.
- `game` contains game orchestration, logic, animation timing, save handling, data declarations, and state declarations.
- `render` contains `GameRenderer` and `SpriteRenderer`.
- `hal` defines hardware-neutral interfaces and M5-specific implementations under `hal/m5`.

The converted Unity assets are stored separately under `assets/`: 225 `characters_*.h` RGB565 headers and 225 `animations_*.h` RGB565 headers. The audit does not infer their semantic meaning from index values.

## Components

| Component | Real path | Responsibility | Dependencies | Consumed by | Status |
|---|---|---|---|---|---|
| Entry point | `src/main.cpp` | Arduino startup and main loop | M5 platform and game/HAL stack | Device runtime | Located and reviewed |
| GameManager | `include/game/core/GameManager.h`, `src/game/core/GameManager.cpp` | Top-level game coordination | Logic, rendering, animation, input/audio/storage interfaces | `main.cpp` | Located and reviewed |
| LogicManager | `include/game/core/LogicManager.h`, `src/game/core/LogicManager.cpp` | Game-state and gameplay progression | Game state/data and game services | GameManager | Located and reviewed |
| AnimationManager | `include/game/anim/AnimationManager.h`, `src/game/anim/AnimationManager.cpp` | Animation state/timing service | Timing and game-facing animation state | GameManager / renderer path | Located and reviewed |
| Game states | `include/game/state/GameStates.h` | Declares game state values/types | Core game code | LogicManager / GameManager | Located and reviewed |
| GameRenderer | `include/render/GameRenderer.h`, `src/render/GameRenderer.cpp` | Screen-level rendering | Display abstraction and game-facing state | GameManager | Located and reviewed |
| SpriteRenderer | `include/render/SpriteRenderer.h`, `src/render/SpriteRenderer.cpp` | Lower-level sprite drawing helper | Display abstraction | GameRenderer | Located and reviewed |
| CharacterData | `include/game/data/CharacterData.h` | Character-related data declarations | Core/game consumers | Logic and rendering consumers | Located and reviewed |
| SaveManager | `include/game/save/SaveManager.h`, `src/game/save/SaveManager.cpp` | Save/load coordination | Storage interface and SaveData | GameManager / gameplay | Located and reviewed |
| SaveData | `include/game/save/SaveData.h` | Persisted game-data structure | SaveManager | SaveManager | Located and reviewed |
| Display HAL | `include/hal/Display.h` | Abstract drawing surface | M5 display implementation | Renderer | Located and reviewed |
| Input HAL | `include/hal/Input.h` | Abstract input surface | M5 input implementation | GameManager / LogicManager | Located and reviewed |
| Audio HAL | `include/hal/Audio.h` | Abstract audio surface | M5 audio implementation | Game-facing code | Located and reviewed |
| Sensors HAL | `include/hal/Sensors.h` | Abstract sensor surface | M5 sensor implementation | Game-facing code | Located and reviewed |
| Storage HAL | `include/hal/Storage.h` | Abstract persistent storage | M5 storage implementation | SaveManager | Located and reviewed |
| M5 HAL | `include/hal/m5/*.h`, `src/hal/m5/*.cpp` | Concrete M5StickC Plus2 adapters | M5Unified/M5 platform APIs | HAL interface consumers | Located and reviewed |
| Tests | `fw_test/mocks.h`, `fw_test/test_animation.cpp`, `fw_test/test_main.cpp` | Native/unit test support and animation tests | Mocks and test runner | Test environment | Located and reviewed |

## Entry Point

`src/main.cpp` is the firmware entry point. It is responsible for initialization and continuous update execution in the Arduino/PlatformIO lifecycle. `GameManager` is the application-level coordinator reached from this path; rendering and game progression are not initialized directly from asset headers.

The entry point is therefore the ownership root for the runtime object graph. Asset integration should not be attached here: this file should remain responsible for bootstrapping and repeated update dispatch.

## GameManager

`GameManager` is the top-level gameplay coordinator declared in `include/game/core/GameManager.h` and implemented in `src/game/core/GameManager.cpp`. It is the appropriate boundary between the loop, game logic, animation updates, renderer invocation, and HAL-backed services.

The audit identified GameManager as the correct orchestration layer rather than a renderer replacement point. Future asset work should preserve its role: it should select high-level state/character/animation intent, while rendering remains below it.

## LogicManager

`LogicManager` is declared in `include/game/core/LogicManager.h` and implemented in `src/game/core/LogicManager.cpp`. It contains the current game-flow and state-progression logic and is used through the GameManager orchestration path.

Future sprite integration must not encode Unity atlas indices in LogicManager. Logic should continue to express gameplay/state intent; a later mapping layer must resolve that intent to a renderable asset only at the rendering/animation boundary.

## Game States

The real state declarations are in `include/game/state/GameStates.h`. This file is the authoritative firmware definition for currently represented game states; no additional states are assumed by this audit.

State transitions are driven through the existing core logic path. Any future character-selection or animation visual behavior must be connected to verified states from this header and LogicManager rather than adding unverified state names from Unity analysis.

## AnimationManager

`AnimationManager` exists at `include/game/anim/AnimationManager.h` and `src/game/anim/AnimationManager.cpp`. It is the existing animation-timing/selection component and must be audited as the first candidate for extending frame sequencing before creating a separate animation system.

The current test tree contains `fw_test/test_animation.cpp`, confirming that animation behavior is already considered unit-testable. Future RGB565 integration should adapt the existing manager only after the Unity-to-firmware mapping is evidence-backed; no mapping is created by this audit.

## GameRenderer

`GameRenderer` is declared in `include/render/GameRenderer.h` and implemented in `src/render/GameRenderer.cpp`. It is the screen-level rendering component and its drawing route is mediated by the display abstraction rather than by direct asset handling in GameManager.

Future rendering of converted RGB565 headers belongs below or within this renderer path. This audit makes no rendering changes and does not claim that a specific existing placeholder maps to a specific Unity sprite.

## SpriteRenderer

`SpriteRenderer` is declared in `include/render/SpriteRenderer.h` and implemented in `src/render/SpriteRenderer.cpp`. It is the closest verified code-level location for receiving a single decoded/static RGB565 frame and forwarding it through the existing display interface.

The correct future direction is therefore: selected sprite data -> SpriteRenderer -> Display interface -> M5 display adapter. GameRenderer should decide composition/layout at the screen level; it should not require the entire asset set in RAM.

## CharacterData

`include/game/data/CharacterData.h` is the verified character-data declaration point. It should remain distinct from graphics data: character identity/game data and asset selection are separate responsibilities.

A future Unity-to-ESP32 mapping should refer to the existing character data types only where direct evidence links them to Unity character sprite references. The sequential `characters_N` filenames alone are not sufficient evidence.

## Save System

`SaveData` is declared in `include/game/save/SaveData.h`; `SaveManager` is declared in `include/game/save/SaveManager.h` and implemented in `src/game/save/SaveManager.cpp`. Save handling depends on the abstract `Storage` interface rather than directly on the M5 implementation.

No sprite data should be persisted merely to render static assets. Future saves may persist gameplay-level character or state choices only if the existing save model and game logic require it.

## HAL

The firmware exposes five platform-neutral interfaces under `include/hal/`:

- `Display.h`
- `Input.h`
- `Audio.h`
- `Sensors.h`
- `Storage.h`

Their M5StickC Plus2 implementations are under `include/hal/m5/` and `src/hal/m5/` as `M5Display`, `M5Input`, `M5Audio`, `M5Sensors`, and `M5Storage`.

This separation is an important constraint: renderer code should continue to depend on `Display`, while calls specific to M5Unified/M5GFX remain confined to `M5Display` unless the HAL interface must be deliberately extended.

## M5Unified / M5GFX APIs

The concrete M5 integration is isolated in the M5 HAL files. The audit confirmed those five implementation units exist and are the only verified hardware-specific implementation path in the source tree.

This audit does not claim use of a particular M5GFX drawing primitive, framebuffer, PSRAM allocation, image upload function, rotation value, or pixel-transfer API unless it is represented by the existing reviewed M5 display implementation. Any future extension for RGB565 must use the API already exposed by `Display` where sufficient, or extend the interface and M5 implementation together after implementation begins.

## Current Rendering Flow

The verified architectural rendering route is:

```text
main loop
  -> GameManager orchestration
    -> GameRenderer screen-level rendering
      -> SpriteRenderer sprite-level drawing
        -> Display abstraction
          -> M5Display concrete hardware implementation
```

This is the integration path to preserve. GameManager should not include individual `characters_*.h` or `animations_*.h` headers directly. The current audit intentionally does not alter placeholders or draw calls.

## Current Animation Flow

The verified animation route is:

```text
GameManager / game flow
  -> AnimationManager timing and animation state
  -> renderer consumption path
  -> SpriteRenderer / Display drawing
```

`AnimationManager` already exists and has dedicated unit-test source. Future work must first determine, from its existing API and evidence-backed Unity data, whether it can hold a sequence of asset references and durations. This audit neither introduces a new player nor assigns any converted frame to an existing animation.

## Test Architecture

The native test sources are:

- `fw_test/mocks.h`
- `fw_test/test_main.cpp`
- `fw_test/test_animation.cpp`

The presence of mocks and animation-specific tests establishes a unit-test seam around non-hardware animation behavior. Hardware display transfer, physical input buttons, audio output, sensor data, and flash/storage behavior require either hardware-backed verification or explicit HAL mocks.

No test result is recorded in this document because the audit process did not execute PlatformIO in a local shell environment. A subsequent implementation phase must run the exact test command supported by `platformio.ini` and record its output before claiming a pass.

## Memory / Asset Constraints

The converted asset set has a raw RGB565 payload of:

```text
450 sprites x 32 x 32 pixels x 2 bytes = 921,600 bytes
```

This is approximately 900 KiB of pixel data before C++ header/text overhead. Loading every decoded sprite into ordinary RAM simultaneously is not an acceptable default strategy.

The generated assets are compile-time headers, so their arrays can be referenced statically by compiled firmware code. The audit did not verify an explicit `PROGMEM` declaration, PSRAM allocator, framebuffer allocation, or streaming filesystem path in the currently inspected source. Therefore, the only safe documented recommendation is to avoid runtime copies of the entire corpus and to render selected static frame data through the existing renderer/Display path.

Whether the complete generated header corpus fits the final application binary/flash partition must be verified during a future PlatformIO build. Whether a temporary frame buffer is needed depends on the actual M5Display primitive exposed by the current code and must be verified during implementation.

## Unity -> ESP32 Mapping Status

| Mapping scope | Status | Evidence / limitation |
|---|---|---|
| Unity atlas slicing to individual RGB565 headers | CONFIRMED | Asset pipeline result: 225 `characters_*` plus 225 `animations_*` headers |
| Header filename to Unity sprite name/index | PARTIAL | Manifest/header naming preserves sequential generated names; semantic identity is not established by index alone |
| Character identity to `characters_N` | UNMAPPED | Requires direct evidence from Unity `SpriteDatabase`, serialized references, or equivalent source linkage |
| Unity animation action to `animations_N` sequence | UNMAPPED | Requires direct evidence from Unity animation/script references and frame order |
| Firmware character data to Unity sprite mapping | UNMAPPED | No evidence-backed mapping table has been created |

## Integration Points

The following are the verified future integration points. They are intentionally not implemented in this audit.

1. **Asset declaration/registration boundary — new data-only source near `assets/`:** future code must include only the selected `assets/characters/characters_N.h` and `assets/animations/animations_N.h` resources needed by the firmware build. The resolver must not infer semantic identity from `N`; it must consume a separately evidence-backed mapping.
2. **Single-frame transfer — `include/render/SpriteRenderer.h` / `src/render/SpriteRenderer.cpp`:** this is the closest existing renderer component for accepting a pointer/reference to one RGB565 frame plus dimensions and screen position. It should be the first candidate to receive static header data.
3. **Screen composition — `include/render/GameRenderer.h` / `src/render/GameRenderer.cpp`:** GameRenderer should choose placement and ordering for character-selection and gameplay visuals, then delegate per-frame output to SpriteRenderer. It should not own the entire 450-frame corpus in RAM.
4. **Display transfer — `include/hal/Display.h` and `include/hal/m5/M5Display.h`, `src/hal/m5/M5Display.cpp`:** if SpriteRenderer cannot currently express RGB565 frame transfer through the Display interface, this interface and its M5 implementation must be extended together. Hardware-specific M5GFX calls should remain in M5Display.
5. **Frame timing — `include/game/anim/AnimationManager.h` / `src/game/anim/AnimationManager.cpp`:** this existing manager is the first candidate to select/advance a frame index over time. It should expose an already-resolved frame or frame identifier to rendering only after a mapping has evidence from Unity.
6. **High-level intent — `GameManager` and `LogicManager`:** these managers should continue to express state, selected character, and gameplay action. They should not directly include generated sprite headers unless source inspection later proves that is the established ownership model.
7. **Unity mapping ownership — not yet implemented:** mapping must be an explicit data responsibility outside `CharacterData` unless Unity evidence shows it belongs directly to character data. It must be created only after cross-referencing Unity `SpriteDatabase`, `Animations.cs`, serialized assets/prefabs, and animation references.

## Current Limitations

- The 450 converted frame headers are available, but no evidence-backed semantic mapping from atlas index to character/action exists in this firmware audit.
- No graphics integration has been implemented; existing renderer and animation code remain unchanged.
- The audit did not run PlatformIO tests because no local shell/PlatformIO execution mechanism was available in this session.
- Build-size and flash-partition headroom for including every header remain unverified until PlatformIO compilation is run.
- Hardware-specific behavior requires later verification on the M5StickC Plus2 or with complete HAL mocks.

## Audit Outcome

The firmware has a separable architecture appropriate for incremental asset integration: game orchestration is in `GameManager`, game flow in `LogicManager`, animation timing in `AnimationManager`, composition in `GameRenderer`, single-sprite drawing in `SpriteRenderer`, and hardware access behind the Display HAL/M5Display adapter.

The next phase may begin only after preserving these boundaries and establishing an evidence-backed Unity-to-ESP32 mapping for the relevant minimum set of characters and animation frames.
