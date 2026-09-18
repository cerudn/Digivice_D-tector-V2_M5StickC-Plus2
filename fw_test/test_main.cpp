#include "mocks.h"
#include "game/core/GameManager.h"
#include "game/data/CharacterData.h"
#include "game/anim/AnimationManager.h"
#include <iostream>
#include <string>

using namespace dtec;
using namespace dtec::game;
using namespace dtec::game::core;

int failures = 0;
#define CHECK(cond, msg) do { if (!(cond)) { std::cerr << "FAIL: " << msg << " (line " << __LINE__ << ")\n"; failures++; } else { std::cout << "PASS: " << msg << "\n"; } } while(0)

int main() {
    // Bloque 1: State Machine basica (12 tests heredados)
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        CHECK(gm.logic().currentScreen() == Screen::CharSelection, "Sin save previo, estado inicial es CharSelection");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        CHECK(gm.logic().charSelectionIndex() == 0, "Indice inicial de personaje es 0");
        gm.logic().inputRight();
        CHECK(gm.logic().charSelectionIndex() == 1, "Right avanza indice a 1");
        gm.logic().inputRight(); gm.logic().inputRight(); gm.logic().inputRight();
        CHECK(gm.logic().charSelectionIndex() == 0, "Right x4 vuelve a 0 (circular, mundo 0 = 4 opciones)");
        gm.logic().inputLeft();
        CHECK(gm.logic().charSelectionIndex() == 3, "Left desde 0 da 3 (circular hacia atras)");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputRight();
        gm.logic().inputA();
        CHECK(gm.logic().currentScreen() == Screen::Character, "Tras confirmar personaje, pasa a Screen::Character");
        CHECK(gm.save().data().gameChar == (uint8_t)GameChar::Koji, "SaveData.gameChar es Koji tras seleccion");
        CHECK(gm.save().data().spiritPower == dtec::MAX_SPIRIT_POWER, "SpiritPower inicial es 99");
        CHECK(gm.save().data().characterLost[(size_t)GameChar::Koichi] == 1, "Koichi se marca como perdido");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        for (int k = 0; k < 50; ++k) gm.loop();
        CHECK(gm.logic().inputLocked() == false, "Input se desbloquea tras animacion de intro");
        gm.logic().inputRight();
        CHECK(gm.logic().currentScreen() == Screen::MainMenu, "Right en Character abre MainMenu");
        CHECK(gm.logic().currentMainMenu() == MainMenuTab::Map, "MainMenu abre en pestaņa Map");
        gm.logic().inputB();
        CHECK(gm.logic().currentScreen() == Screen::Character, "B en MainMenu cierra a Character");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        for (int k = 0; k < 50; ++k) gm.loop();
        gm.logic().inputRight();
        for (int k = 0; k < 5; ++k) gm.logic().inputRight();
        CHECK(gm.logic().currentMainMenu() == MainMenuTab::Map, "5 Right en MainMenu vuelve a Map");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        for (int k = 0; k < 50; ++k) gm.loop();
        gm.logic().inputRight();
        gm.logic().inputLeft();
        CHECK(gm.logic().currentScreen() == Screen::MainMenu2, "Left en MainMenu abre MainMenu2");
        CHECK(gm.logic().currentMainMenu2() == MainMenu2Tab::Database, "MainMenu2 abre en Database");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        for (int k = 0; k < 50; ++k) gm.loop();
        gm.logic().inputRight();
        gm.logic().inputA();
        CHECK(gm.logic().currentScreen() == Screen::App, "A en tab Map -> Screen::App");
        CHECK(gm.logic().loadedApp() == AppId::Map, "App cargada es AppId::Map");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        gm.save().data().currentDistance = 2;
        int stepsBefore = gm.save().data().steps;
        gm.takeAStep();
        CHECK(gm.save().data().currentDistance == 1, "takeAStep reduce distancia de 2 a 1");
        CHECK(gm.save().data().steps == stepsBefore + 1, "takeAStep incrementa steps en 1");
        CHECK(gm.save().data().pendingEvent == 2, "Al llegar a distancia 1 se marca pendingEvent=2 (boss)");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        gm.logic().inputA();
        CHECK(gm.logic().shakeDisabled() == false, "Shake habilitado por defecto");
        gm.setCharacterDefeated(true);
        CHECK(gm.logic().shakeDisabled() == true, "Shake deshabilitado si personaje derrotado");
    }
    {
        MockStorage st;
        game::save::SaveManager sm(st);
        sm.createNew(GameChar::Zoe, -1, -1);
        game::save::SaveManager sm2(st);
        bool loaded = sm2.load();
        CHECK(loaded, "SaveManager recarga correctamente una partida guardada");
        CHECK(sm2.data().gameChar == (uint8_t)GameChar::Zoe, "Partida recargada conserva gameChar=Zoe");
    }
    {
        MockStorage st;
        game::save::SaveData bad{};
        bad.gameChar = (uint8_t)GameChar::Takuya;
        bad.checksum = 0xDEADBEEF;
        st.saveBlob("save_v1", &bad, sizeof(bad));
        game::save::SaveManager sm(st);
        bool loaded = sm.load();
        CHECK(loaded == false, "SaveManager rechaza blob con checksum invalido");
    }
    {
        CHECK(circularAdd(0, -1, 4) == 3, "circularAdd(0,-1,4) == 3");
        CHECK(circularAdd(3, 1, 4) == 0, "circularAdd(3,1,4) == 0");
        CHECK(circularAdd(2, 1, 4) == 3, "circularAdd(2,1,4) == 3");
    }

    // Bloque 2: Character Data
    {
        const auto* c = dtec::game::data::findCharacter(GameChar::Takuya);
        CHECK(c != nullptr, "findCharacter(Takuya) devuelve entrada valida");
        CHECK(std::string(c->name) == "takuya", "Nombre real de Takuya coincide con characters.json");
        CHECK(c->stats.HP == 6 && c->stats.SP == 5 && c->stats.ST == 5 && c->stats.SK == 7,
              "Stats base de Takuya coinciden con characters.json");
        CHECK(std::string(c->spiritHuman) == "agunimon" && std::string(c->spiritAnimal) == "burninggreymon",
              "Espiritus de Takuya coinciden con characters.json");
    }
    {
        const auto* tommy = dtec::game::data::findCharacter(GameChar::Tommy);
        CHECK(tommy != nullptr && tommy->disabled == true, "Tommy esta marcado disabled=true");
    }
    {
        const auto* invalid = dtec::game::data::findCharacter(GameChar::None);
        CHECK(invalid == nullptr, "findCharacter(None) devuelve nullptr");
    }

    // Bloque 3: Animation State Machine
    {
        dtec::game::anim::AnimationManager am;
        CHECK(am.isPlaying() == false, "AnimationManager arranca sin animacion activa");
        am.play(AnimationId::CharHappyShort, 1000);
        CHECK(am.isPlaying() == true, "play() activa isPlaying()");
        CHECK(am.current() == AnimationId::CharHappyShort, "current() devuelve la animacion activa");
        CHECK(am.currentFrameIndex() == 0, "Frame inicial es 0");

        am.tick(1000);
        CHECK(am.currentFrameIndex() == 0, "Sin avance de tiempo, el frame no cambia");

        am.tick(1500);
        CHECK(am.currentFrameIndex() == 1, "Tras 500ms avanza a frame 1 (CharHappyShort frame0 dura 500ms)");

        am.tick(2000);
        CHECK(am.isPlaying() == false, "CharHappyShort termina tras sus 2 frames (no es loop)");
    }
    {
        dtec::game::anim::AnimationManager am;
        am.play(AnimationId::EyesBlinkIdle, 0);
        am.tick(600);
        CHECK(am.isPlaying() == true, "EyesBlinkIdle sigue activa tras 1 ciclo (es loop=true)");
        am.tick(1200); am.tick(1800); am.tick(2400);
        CHECK(am.isPlaying() == true, "EyesBlinkIdle nunca termina sola (loop infinito)");
    }

    // Bloque 4: Intro animation bloquea input
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        CHECK(gm.logic().inputLocked() == true, "Tras begin() sin save, input bloqueado por LoadCharacterSelection");
        for (int k = 0; k < 100; ++k) gm.loop();
        CHECK(gm.logic().inputLocked() == false, "Input se desbloquea tras completar LoadCharacterSelection");
    }
    {
        MockDisplay d; MockInput i; MockAudio a; MockSensors s; MockStorage st;
        GameManager gm(d, i, a, s, st);
        gm.begin();
        for (int k = 0; k < 100; ++k) gm.loop();
        gm.logic().inputA();
        CHECK(gm.logic().inputLocked() == true, "Crear partida dispara StartGameAnimation y bloquea input");
        CHECK(gm.anim().current() == AnimationId::StartGameAnimation, "AnimationManager reproduce StartGameAnimation");
    }

    std::cout << "\n=== " << (failures == 0 ? "ALL TESTS PASSED" : "SOME TESTS FAILED") << " (" << failures << " failures) ===\n";
    return failures == 0 ? 0 : 1;
}
