/*
 * lib5.ino - Programa principal para G502 X PLUS Spoof
 * Baseado na Lib5 com modificações para spoofar o Logitech G502 X PLUS
 */

#include <Arduino.h>
#include <SPI.h>
#include "hidcustom.h"

#define CHECK_BIT(var, pos) ((var)&pos)

// Estados dos botões
signed char leftMouseButton = 0;
signed char rightMouseButton = 0;
signed char middleMouseButton = 0;
signed char backMouseButton = 0;
signed char forwardMouseButton = 0;

// Estado do movimento
signed char wheel = 0;
int dx = 0;
int dy = 0;

// Variáveis para comandos especiais
int smurf_dx;
int smurf_dy;
int dxn;
int dyn;
int index;
int num_size;
int jump = 127;

// Implementação do parser de mouse
void MouseRptParser::Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf)
{
  CUSTOMMOUSEINFO *pmi = (CUSTOMMOUSEINFO *)buf;

  // Verificar mudanças nos botões
  if (CHECK_BIT(prevState.mouseInfo.buttons, MOUSE_LEFT) != CHECK_BIT(pmi->buttons, MOUSE_LEFT))
  {
    if (CHECK_BIT(pmi->buttons, MOUSE_LEFT))
      OnLeftButtonDown(pmi);
    else
      OnLeftButtonUp(pmi);
  }

  if (CHECK_BIT(prevState.mouseInfo.buttons, MOUSE_RIGHT) != CHECK_BIT(pmi->buttons, MOUSE_RIGHT))
  {
    if (CHECK_BIT(pmi->buttons, MOUSE_RIGHT))
      OnRightButtonDown(pmi);
    else
      OnRightButtonUp(pmi);
  }

  if (CHECK_BIT(prevState.mouseInfo.buttons, MOUSE_MIDDLE) != CHECK_BIT(pmi->buttons, MOUSE_MIDDLE))
  {
    if (CHECK_BIT(pmi->buttons, MOUSE_MIDDLE))
      OnMiddleButtonDown(pmi);
    else
      OnMiddleButtonUp(pmi);
  }

  if (CHECK_BIT(prevState.mouseInfo.buttons, MOUSE_BACK) != CHECK_BIT(pmi->buttons, MOUSE_BACK))
  {
    if (CHECK_BIT(pmi->buttons, MOUSE_BACK))
      OnBackButtonDown(pmi);
    else
      OnBackButtonUp(pmi);
  }

  if (CHECK_BIT(prevState.mouseInfo.buttons, MOUSE_FORWARD) != CHECK_BIT(pmi->buttons, MOUSE_FORWARD))
  {
    if (CHECK_BIT(pmi->buttons, MOUSE_FORWARD))
      OnForwardButtonDown(pmi);
    else
      OnForwardButtonUp(pmi);
  }

  // Verificar movimento do mouse
  if (pmi->dX || pmi->dY)
    OnMouseMove(pmi);

  // Verificar movimento da roda
  if (len > 3)
    OnWheelMove(pmi);

  // Salvar estado atual
  prevState.bInfo[0] = buf[0];
  if (len > 3)
    prevState.bInfo[3] = buf[3];
}

// Callbacks de eventos do mouse
void MouseRptParser::OnMouseMove(CUSTOMMOUSEINFO *mi)
{
  dx = mi->dX;
  dy = mi->dY;
}

void MouseRptParser::OnWheelMove(CUSTOMMOUSEINFO *mi)
{
  wheel = mi->wheel;
}

void MouseRptParser::OnLeftButtonDown(CUSTOMMOUSEINFO *mi)
{
  leftMouseButton = 1;
}

void MouseRptParser::OnLeftButtonUp(CUSTOMMOUSEINFO *mi)
{
  leftMouseButton = 0;
}

void MouseRptParser::OnRightButtonDown(CUSTOMMOUSEINFO *mi)
{
  rightMouseButton = 1;
}

void MouseRptParser::OnRightButtonUp(CUSTOMMOUSEINFO *mi)
{
  rightMouseButton = 0;
}

void MouseRptParser::OnMiddleButtonDown(CUSTOMMOUSEINFO *mi)
{
  middleMouseButton = 1;
}

void MouseRptParser::OnMiddleButtonUp(CUSTOMMOUSEINFO *mi)
{
  middleMouseButton = 0;
}

void MouseRptParser::OnBackButtonDown(CUSTOMMOUSEINFO *mi)
{
  backMouseButton = 1;
}

void MouseRptParser::OnBackButtonUp(CUSTOMMOUSEINFO *mi)
{
  backMouseButton = 0;
}

void MouseRptParser::OnForwardButtonDown(CUSTOMMOUSEINFO *mi)
{
  forwardMouseButton = 1;
}

void MouseRptParser::OnForwardButtonUp(CUSTOMMOUSEINFO *mi)
{
  forwardMouseButton = 0;
}

// Inicialização do USB Host
#include <usbhub.h>
USB Usb;
USBHub Hub(&Usb);
HIDBoot<USB_HID_PROTOCOL_MOUSE> HidMouse(&Usb);
MouseRptParser Prs;

void setup()
{
  // Configurar comunicação serial
  Serial.begin(115200);
  Serial.setTimeout(1);

  // Aguardar a inicialização do serial
  uint8_t attempts = 30;
  while (!Serial && attempts--)
    delay(100);

  // Inicializar o USB e o mouse
  Usb.Init();
  HidMouse.SetReportParser(0, &Prs);
  Mouse.begin();
}

void loop()
{
  // Resetar valores a cada ciclo
  dx = 0;
  dy = 0;
  wheel = 0;

  // Processar eventos USB
  Usb.Task();

  // Processar estados dos botões
  if (leftMouseButton == 0)
    Mouse.release(MOUSE_LEFT);
  else if (leftMouseButton == 1)
    Mouse.press(MOUSE_LEFT);

  if (rightMouseButton == 0)
    Mouse.release(MOUSE_RIGHT);
  else if (rightMouseButton == 1)
    Mouse.press(MOUSE_RIGHT);

  if (middleMouseButton == 0)
    Mouse.release(MOUSE_MIDDLE);
  else if (middleMouseButton == 1)
    Mouse.press(MOUSE_MIDDLE);

  if (backMouseButton == 0)
    Mouse.release(MOUSE_BACK);
  else if (backMouseButton == 1)
    Mouse.press(MOUSE_BACK);
    
  if (forwardMouseButton == 0)
    Mouse.release(MOUSE_FORWARD);
  else if (forwardMouseButton == 1)
    Mouse.press(MOUSE_FORWARD);

  // Processar comandos seriais
  if (Serial.available() > 0 && Serial.available() != 4)
  {
    String smurfed = Serial.readString();
    
    // Comando syl3nt - move, clica e retorna
    if (smurfed.substring(0,6) == "syl3nt")
    {
      // Obter coordenadas
      smurfed.remove(0,6);
      index = 0;
      num_size = smurfed.indexOf(":", index);
      smurf_dx = smurfed.substring(index,num_size).toInt();
      smurfed.remove(0,num_size+1);
      smurf_dy = smurfed.toInt();
      dxn = smurf_dx *-1;
      dyn = smurf_dy *-1;

      // Mover na direção X
      if (smurf_dx > 0){
        while (smurf_dx > 127) {
          smurf_dx -= 127;
          Mouse.move(127,0);
        }
        Mouse.move(smurf_dx,0);
      }
      else if (smurf_dx < 0){
        while (smurf_dx < -127) {
          smurf_dx += 127;
          Mouse.move(-127,0);
        }
        Mouse.move(smurf_dx,0);
      }
      
      // Mover na direção Y
      if (smurf_dy > 0){
        while (smurf_dy > 127) {
          smurf_dy -= 127;
          Mouse.move(0,127);
        }
        Mouse.move(0,smurf_dy);
      }
      else if (smurf_dy < 0){
        while (smurf_dy < -127) {
          smurf_dy += 127;
          Mouse.move(0,-127);
        }
        Mouse.move(0,smurf_dy);
      }
      
      // Clicar
      Mouse.click();
      
      // Voltar para a posição original
      if (dxn > 0){
        while (dxn > 127) {
          dxn -= 127;
          Mouse.move(127,0);
        }
        Mouse.move(dxn,0);
      }
      else if (dxn < 0){
        while (dxn < -127) {
          dxn += 127;
          Mouse.move(-127,0);
        }
        Mouse.move(dxn,0);
      }
      
      if (dyn > 0){
        while (dyn > 127) {
          dyn -= 127;
          Mouse.move(0,127);
        }
        Mouse.move(0,dyn);
      }
      else if (dyn < 0){
        while (dyn < -127) {
          dyn += 127;
          Mouse.move(0,-127);
        }
        Mouse.move(0,dyn);
      }
    }
    
    // Comando movsht - move e clica
    else if (smurfed.substring(0,6) == "movsht")
    {
      // Obter coordenadas
      smurfed.remove(0,6);
      index = 0;
      num_size = smurfed.indexOf(":", index);
      smurf_dx = smurfed.substring(index,num_size).toInt();
      smurfed.remove(0,num_size+1);
      smurf_dy = smurfed.toInt();
      
      // Mover na direção X
      if (smurf_dx > 0){
        while (smurf_dx > 127) {
          smurf_dx -= 127;
          Mouse.move(127,0);
        }
        Mouse.move(smurf_dx,0);
      }
      else if (smurf_dx < 0){
        while (smurf_dx < -127) {
          smurf_dx += 127;
          Mouse.move(-127,0);
        }
        Mouse.move(smurf_dx,0);
      }
      
      // Mover na direção Y
      if (smurf_dy > 0){
        while (smurf_dy > 127) {
          smurf_dy -= 127;
          Mouse.move(0,127);
        }
        Mouse.move(0,smurf_dy);
      }
      else if (smurf_dy < 0){
        while (smurf_dy < -127) {
          smurf_dy += 127;
          Mouse.move(0,-127);
        }
        Mouse.move(0,smurf_dy);
      }
      
      // Clicar
      Mouse.click();
    }
  }
  
  // Protocolo de 4 bytes
  else if (Serial.available() > 0 && Serial.available() == 4) {
    byte bytes[4];
    for (byte i = 0; i < 4; i++) {
      bytes[i] = Serial.read();
    }
    
    // Protocolo de movimento normal
    if ((bytes[0] == 0x7E) && (bytes[3] == 0x7E)) {
      uint8_t data[2];
      data[0] = bytes[1];
      data[1] = bytes[2];
      Mouse.move(data[0], data[1], 0);
    }
    
    // Protocolo de movimento invertido
    if ((bytes[0] == 0x7B) && (bytes[3] == 0x7B)) {
      uint8_t data[2];
      data[0] = bytes[1];
      data[1] = bytes[2];
      Mouse.move(-data[0], -data[1], 0);
    }
    
    // Protocolo de clique
    if ((bytes[0] == 0x5E) && (bytes[3] == 0x5E)) {
      Mouse.click();
    }
  }
  
  // Movimento normal do mouse conectado
  else {
    Mouse.move(dx, dy, wheel);
  }
}