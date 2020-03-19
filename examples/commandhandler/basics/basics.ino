#include <CommandHandler.h>

CommandHandler cmdHdl;

// this constant won't change:
const int  buttonPin = 53;

// Variables will change:
int buttonPushCounter = 0;   // counter for the number of button presses
int buttonState = 0;         // current state of the button
int lastButtonState = 0;     // previous state of the button

void setup() {
  // initialize the button pin as a input:
  pinMode(buttonPin, INPUT_PULLUP);

  // initialize serial communication:
  Serial.begin(115200);

  cmdHdl.addCommand("CURRENT", sendCurrentState);
  cmdHdl.addCommand("NPUSH", sendNumberOfPush);
  cmdHdl.setDefaultHandler(unrecognized);

}

void loop() {

  cmdHdl.processSerial(Serial);

  // read the pushbutton input pin:
  buttonState = digitalRead(buttonPin);

  // compare the buttonState to its previous state
  if (buttonState != lastButtonState) {
    // if the state has changed, increment the counter
    if (buttonState == HIGH) {
      buttonPushCounter++;
      //
      cmdHdl.initCmd();
      cmdHdl.addCmdString("PRESS");
      cmdHdl.addCmdDelim();
      cmdHdl.addCmdInt(buttonState);
      cmdHdl.addCmdDelim();
      cmdHdl.addCmdInt(buttonPushCounter);
      cmdHdl.addCmdTerm();
      cmdHdl.sendCmdSerial();
    } else {
      cmdHdl.initCmd();
      cmdHdl.addCmdString("RELEASE");
      cmdHdl.addCmdDelim();
      cmdHdl.addCmdInt(buttonState);
      cmdHdl.addCmdDelim();
      cmdHdl.addCmdInt(buttonPushCounter);
      cmdHdl.addCmdTerm();
      cmdHdl.sendCmdSerial();
    }
    // Delay a little bit to avoid bouncing
    delay(100);
  }
  lastButtonState = buttonState;
}

void sendCurrentState() {
  cmdHdl.initCmd();
  cmdHdl.addCmdString("STATE");
  cmdHdl.addCmdDelim();
  cmdHdl.addCmdInt(buttonState);
  cmdHdl.addCmdTerm();
  cmdHdl.sendCmdSerial();
}

void sendNumberOfPush() {
  cmdHdl.initCmd();
  cmdHdl.addCmdString("NPUSH");
  cmdHdl.addCmdDelim();
  cmdHdl.addCmdInt(buttonPushCounter);
  cmdHdl.addCmdTerm();
  cmdHdl.sendCmdSerial();
}


// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command) {
  cmdHdl.initCmd();
  cmdHdl.addCmdString("What?");
  cmdHdl.addCmdTerm();
  cmdHdl.sendCmdSerial();
}
