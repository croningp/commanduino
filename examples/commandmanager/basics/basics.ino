#include "CommandHandler.h"
#include "CommandManager.h"

#include "CommandDigitalWrite.h"

#define PIN1 4
#define PIN2 5
#define PIN3 6

CommandManager mgr;
CommandDigitalWrite p1(PIN1);
CommandDigitalWrite p2(PIN2);
CommandDigitalWrite p3(PIN3);

void setup() {
  Serial.begin(115200);

  p1.registerToCommandManager(mgr, "P1");
  p2.registerToCommandManager(mgr, "P2");
  p3.registerToCommandManager(mgr, "P3");

  mgr.init();
}

void loop() {
  mgr.update();
}
