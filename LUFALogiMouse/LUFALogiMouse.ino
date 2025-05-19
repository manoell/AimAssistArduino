#include "LUFAConfig.h"
#include <LUFA.h>
#include "LogitechMouse.h"
#include <inttypes.h>

// Variáveis globais para comunicação
volatile bool newCommandReceived = false;
volatile bool processingCommand = false;

// Variáveis para estado do mouse - CORRIGIDAS PARA int8_t (Boot Protocol)
int8_t mouse_x = 0;
int8_t mouse_y = 0;
uint8_t mouse_buttons = 0;
int8_t mouse_wheel = 0;

void setup() {
  // Initialize hardware
  SetupHardware();
  GlobalInterruptEnable();
  
  // Initialize mouse state
  mouse_x = 0;
  mouse_y = 0;
  mouse_buttons = 0;
  mouse_wheel = 0;
  newCommandReceived = false;
  processingCommand = false;
}

void loop() {
  // CRUCIAL: Process USB tasks PRIMEIRO E SEMPRE
  USB_USBTask();
  
  // CRUCIAL: Process HID tasks LOGO EM SEGUIDA
  HID_Task();
  
  // SEM DELAYS - NUNCA ADICIONAR DELAYS NO LOOP PRINCIPAL
  // O loop deve executar o mais rápido possível para latência mínima
}