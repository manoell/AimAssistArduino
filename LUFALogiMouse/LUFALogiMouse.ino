#include "LUFAConfig.h"
#include <LUFA.h>
#include "LogitechMouse.h"
#include <inttypes.h>

// Variáveis globais para comunicação (definidas aqui)
volatile bool newCommandReceived = false;
volatile bool processingCommand = false;

// Variáveis para estado do mouse (definidas aqui)
int16_t mouse_x = 0;
int16_t mouse_y = 0;
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
  // Process USB tasks
  HID_Task();
  
  // USB tasks
  USB_USBTask();
  
  // Small delay to prevent excessive CPU usage
  _delay_ms(1);
}