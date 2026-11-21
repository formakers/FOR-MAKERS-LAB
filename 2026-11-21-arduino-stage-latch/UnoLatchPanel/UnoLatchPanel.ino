#include <LiquidCrystal.h>

// LCD 단자 순서: RS, E, DB4, DB5, DB6, DB7
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
const byte keypadPin = A0;
const byte relayPin = A1;
const byte sensorPin = 2;
const byte relayOn = HIGH;     // 실물에서 확인한 작동 극성
const byte relayOff = LOW;
const byte lockedLevel = LOW;  // 잠겼을 때 도통되는 무전압 접점
const unsigned int pulseMs = 500;
bool armed = false;

// D2 상태가 바뀔 때만 LCD 첫 줄을 갱신합니다.
void showLockState() {
  static int previousLevel = -1;
  int level = digitalRead(sensorPin);
  if (level == previousLevel) return;
  previousLevel = level;
  lcd.setCursor(0, 0);
  lcd.print(level == lockedLevel ? "LOCKED  " : "UNLOCKED");
}

void setup() {
  digitalWrite(relayPin, relayOff);
  pinMode(relayPin, OUTPUT);
  pinMode(sensorPin, INPUT_PULLUP);
  lcd.begin(16, 2);
  showLockState();
  lcd.setCursor(0, 1);
  lcd.print("SELECT: release ");
}

void loop() {
  showLockState();
  // A0의 버튼 전압을 30ms 간격으로 두 번 확인합니다.
  int first = analogRead(keypadPin);
  delay(30);
  int second = analogRead(keypadPin);

  // 버튼을 놓은 뒤에만 새 명령을 받습니다.
  if (first > 1000 && second > 1000) {
    armed = true;
    return;
  }
  bool selectPressed = first >= 600 && first <= 900 &&
                       second >= 600 && second <= 900;
  if (!armed || !selectPressed) return;
  armed = false;

  lcd.setCursor(0, 1);
  lcd.print("Releasing...    ");
  // A1을 통해 릴레이를 0.5초 켭니다. 래치는 외부 12V로 구동됩니다.
  digitalWrite(relayPin, relayOn);
  delay(pulseMs);
  digitalWrite(relayPin, relayOff);

  // 전원을 끈 뒤 실제 걸쇠 접점으로 결과를 갱신합니다.
  showLockState();
  lcd.setCursor(0, 1);
  lcd.print("SELECT: release ");
}
