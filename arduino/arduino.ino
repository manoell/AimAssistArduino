#include <hidboot.h>
#include <usbhub.h>
#include "HID-Project.h"

// Declaração para o USB Host Shield
USB Usb;
USBHub Hub(&Usb);
HIDBoot<USB_HID_PROTOCOL_MOUSE> HidMouse(&Usb);

// Variáveis globais
String command = "";
bool isClicking = false;
unsigned long clickStartTime = 0;
unsigned long clickDuration = 0;

// Classe para tratar eventos do mouse
class MouseRptParser : public MouseReportParser {
  protected:
    void OnMouseMove(MOUSEINFO *mi);
    void OnLeftButtonUp(MOUSEINFO *mi);
    void OnLeftButtonDown(MOUSEINFO *mi);
    void OnRightButtonUp(MOUSEINFO *mi);
    void OnRightButtonDown(MOUSEINFO *mi);
    void OnMiddleButtonUp(MOUSEINFO *mi);     // Readicionado
    void OnMiddleButtonDown(MOUSEINFO *mi);   // Readicionado
    void Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf);
};

void MouseRptParser::OnMouseMove(MOUSEINFO *mi) {
  // Envia o movimento para o computador - sem prints para não atrasar
  Mouse.move(mi->dX, mi->dY, 0);
}

void MouseRptParser::OnLeftButtonUp(MOUSEINFO *mi) {
  Mouse.release(MOUSE_LEFT);
}

void MouseRptParser::OnLeftButtonDown(MOUSEINFO *mi) {
  Mouse.press(MOUSE_LEFT);
}

void MouseRptParser::OnRightButtonUp(MOUSEINFO *mi) {
  Mouse.release(MOUSE_RIGHT);
}

void MouseRptParser::OnRightButtonDown(MOUSEINFO *mi) {
  Mouse.press(MOUSE_RIGHT);
}

// Readicionados os métodos para o botão do meio
void MouseRptParser::OnMiddleButtonUp(MOUSEINFO *mi) {
  Mouse.release(MOUSE_MIDDLE);
}

void MouseRptParser::OnMiddleButtonDown(MOUSEINFO *mi) {
  Mouse.press(MOUSE_MIDDLE);
}

// Implementação do método Parse para capturar o scroll
void MouseRptParser::Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf) {
  // Chama o método Parse original
  MouseReportParser::Parse(hid, is_rpt_id, len, buf);
  
  // Se o mouse suportar scroll e este for o 4º byte
  if (len > 3) {
    int8_t wheel = (int8_t)buf[3];
    if (wheel != 0) {
      Mouse.move(0, 0, wheel);
    }
  }
}

MouseRptParser Prs;

void setup() {
  // Inicializar comunicação serial
  Serial.begin(115200);
  Serial.setTimeout(1);
  
  // Seed aleatória
  randomSeed(analogRead(0));
  
  // Sem wait pelo Serial, apenas inicia
  
  if (Usb.Init() == -1) {
    if (Serial) Serial.println("USB Host Shield não inicializado!");
    while (1); //Trava se falhar
  }
  
  // Conecta o parser ao mouse USB
  HidMouse.SetReportParser(0, &Prs);
  
  // Inicializa as funções de emulação de mouse
  Mouse.begin();
}

void loop() {
  // Executar tarefas USB Host Shield
  Usb.Task();
  
  // Verificar comandos seriais (sem bloquear o fluxo)
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim();
    
    // Comando de movimento: M<X>,<Y>
    if (command.startsWith("M")) {
      int commaIndex = command.indexOf(',');
      if (commaIndex != -1) {
        int deltaX = command.substring(1, commaIndex).toInt();
        int deltaY = command.substring(commaIndex + 1).toInt();
        
        // Mover o mouse de uma vez só, sem delays
        Mouse.move(deltaX, deltaY);
      }
    }
    
    // Comando de clique: C
    else if (command.startsWith("C")) {
      if (!isClicking) {
        Mouse.press(MOUSE_LEFT);
        clickStartTime = millis();
        clickDuration = random(40, 80);
        isClicking = true;
      }
    }
    
    // Comando de teste: TEST
    else if (command == "TEST") {
      Serial.println("OK");
    }
  }
  
  // Liberar o clique após o tempo definido
  if (isClicking && (millis() - clickStartTime >= clickDuration)) {
    Mouse.release(MOUSE_LEFT);
    isClicking = false;
  }
  
  // Sem delay no final do loop!
}