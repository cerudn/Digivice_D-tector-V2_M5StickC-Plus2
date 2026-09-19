# Sprite Integration – First RGB565 Path

## Purpose

Demonstrate a working end-to-end path for a single RGB565 sprite:

`assets/characters/characters_0.h` → `hal::Bitmap` → `SpriteRenderer` → `hal::Display` → `M5Display` → `M5.Display.pushImage()` → screen.

No semantic mapping to Unity characters or animations is implied by this test.

## Asset Used

- **File:** `assets/characters/characters_0.h`
- **Data symbol:** `static const uint16_t characters_0[1024];`
- **Dimensions:** 32×³2 pixels
- **Format:** RGB565, row-major, no padding
- **Elements:** 1024 `uint16_t` values
- **Bytes:** 1024 × 2 = 2048 bytes of pixel data

The header is treated as an opaque RGB565 frame. Its index (`0`) carries no gameplay meaning in this phase.

## Architecture Path

The rendering path follows the audited architecture:

- `GameRenderer::drawTestSprite()` constructs a `hal::Bitmap` referencing `characters_0`.
- `SpriteRenderer::drawBitmap()` forwards the bitmap to the display abstraction.
- `hal::Display::drawBitmap()` is implemented by `M5Display::drawBitmap()`.
- `M5Display` calls `M5.Display.pushImage()` from M5GFX/M5Unified to transfer the RGB565 pixels.

No direct M5GFX dependency is introduced in `GameManager`, `LogicManager`, or `AnimationManager`.

## Display API Changes

### `include/hal/Display.h`

Added:

```cpp
struct Bitmap {
    const uint16_t* data;
    uint16_t width;
    uint16_t height;
};

virtual void drawBitmap(int x, int y, const Bitmap& bitmap) = 0;
```

### `include/hal/m5/M5Display.h` / `src/hal/m5/M5Display.cpp`

Implemented:

```cpp
void M5Display::drawBitmap(int x, int y, const Bitmap& bitmap) {
    lcd().pushImage(x, y, bitmap.width, bitmap.height, bitmap.data);
}
```

This uses M5GFX's `pushImage` which accepts RGB565 data directly.

## SpriteRenderer Changes

`SpriteRenderer` now exposes:

```cpp
void drawBitmap(int x, int y, const hal::Bitmap& bitmap);
```

Implementation simply delegates to `display_.drawBitmap(x, y, bitmap);`.

## GameRenderer Integration

A method was added:

```cpp
void GameRenderer::drawTestSprite();
```

It:

- Includes `assets/characters/characters_0.h`.
- Builds a `hal::Bitmap` from `characters_0`.
- Calls `spriteRenderer_.drawBitmap(10, 10, bitmap);`.

Position `(10, 10)` is chosen for easy visual verification on the 135×²40 screen.

## Memory Strategy

- The asset array is declared as `static const uint16_t characters_0[1024]` in the generated header.
- Static const arrays in ESP32 toolchain typically reside in flash/program memory by default, but exact placement depends on `platformio.ini` and linker script.
- No full-frame buffer of 450 sprites is allocated in RAM.
- Only a `Bitmap` descriptor (pointer + width + height) is created on the stack for the active frame.
- M5GFX's `pushImage` reads directly from the provided pointer; no intermediate copy is introduced by this code.

**Limitation:** Internal buffering by M5GFX `pushImage` cannot be excluded without inspecting M5GFX source. This integration only guarantees no extra copy in our code.

## RGB565 Format and Endianness

- The conversion pipeline generated `uint16_t` arrays in native RGB565 layout.
- M5GFX `pushImage` expects RGB565 in the host's native 16-bit endianness.
- No byte-swapping or format conversion is applied in this integration.
- If visual color corruption appears on hardware, the next step would be to verify the generator's packing order against M5GFX expectations; this has not been changed here.

## Tests

Native tests added/updated:

- `fw_test/test_sprite.h` / `fw_test/test_sprite.cpp` — RGB565 resource test using `characters_0`
- `fw_test/test_main.cpp` — runner that calls `test_sprite()`

`test_sprite()` verifies:

- `characters_0` is non-null.
- A `hal::Bitmap` can be constructed with width/height 32.
- The descriptor fields are correctly set.
- `sizeof(characters_0)` equals 1024 × sizeof(uint16_t) at compile time.
- A sample pixel can be read without fault.

This test does not validate on-screen rendering; that requires hardware.

## Build and Validation

### Compilation

- **Status:** NOT VERIFIED IN THIS SESSION
- The code is structured to compile under PlatformIO with the existing `platformio.ini`, but this session did not execute `pio run` or equivalent.
- Files involved: `Display.h`, `M5Display.h/.cpp`, `SpriteRenderer.h/.cpp`, `GameRenderer.h/.cpp`, `main.cpp`, and inclusion of `characters_0.h`.

### Tests

- **Status:** NOT VERIFIED IN THIS SESSION
- The test structure is consistent with the existing native test pattern, but this session did not execute the native test build/run.

### Hardware

- **Status:** NOT PERFORMED
- Expected result on a real M5StickC Plus2:
  - 32×³2 image visible near (10, 10) after boot
  - Correct orientation (subject to `setRotation(1)` in `M5Display` constructor)
  - Correct colors if RGB565 packing matches M5GFX expectations
  - No corruption if pointer and dimensions are correct

## Limitations

- Only `characters_0` is integrated; no mapping to Unity characters exists yet.
- No animation sequencing is implemented.
- `AnimationManager` is unchanged and coexists without using this sprite path yet.
- The test sprite is drawn once in `setup()` via `drawTestSprite()`; it is not refreshed each frame.
- Memory placement (flash vs RAM) is not explicitly controlled beyond `static const`.
- Internal buffering by M5GFX `pushImage` is possible; this integration only guarantees no extra copy in our code.

## Next Steps (Not Implemented Here)

- Evidence-backed mapping from Unity characters/animations to `characters_N` / `animations_N`.
- Dynamic selection of sprites per game state.
- Frame sequencing using `AnimationManager`.
- Integration into proper screens (title, character select, battle, etc.).
- Optional: explicit flash/PROGMEM/PSRAM strategy if build-size or RAM pressure requires it.

## Files Modified

- `include/hal/Display.h`
- `include/hal/m5/M5Display.h`
- `src/hal/m5/M5Display.cpp`
- `include/render/SpriteRenderer.h`
- `src/render/SpriteRenderer.cpp`
- `include/render/GameRenderer.h`
- `src/render/GameRenderer.cpp`
- `src/main.cpp`
- `fw_test/test_sprite.h`
- `fw_test/test_sprite.cpp`
- `fw_test/test_main.cpp`
- `Docs/SPRITE_INTEGRATION.md`

## Verification Summary

| Item | Status |
|---|---|
| Build (PlatformIO) | NOT VERIFIED IN THIS SESSION |
| Native tests | NOT VERIFIED IN THIS SESSION |
| Hardware rendering | NOT PERFORMED |
| Asset symbol | `characters_0`, `static const uint16_t[1024]`, 2048 bytes |
| Render flow | `main.cpp` → `GameRenderer::drawTestSprite()` → `SpriteRenderer::drawBitmap()` → `Display::drawBitmap()` → `M5Display::drawBitmap()` → `M5.Display.pushImage()` |
| Memory strategy | Static const array; no full 450-sprite RAM load; no extra copy in our code |
| AnimationManager | Unmodified |
| Assets/pipeline | Unmodified |
