#include "LUFAConfig.h"
#include <LUFA.h>
#include "LogitechMouse.h"
#include <inttypes.h>

// Variáveis globais para comunicação
volatile bool newCommandReceived = false;
volatile bool processingCommand = false;

// Variáveis para estado do mouse
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
  
  // Reset movement após processamento (se necessário)
  static uint16_t reset_counter = 0;
  reset_counter++;
  if (reset_counter > 50) {  // Reset a cada ~50 loops
    if (!newCommandReceived) {
      // Manter mouse_x/y até serem enviados pelo HID_Task
      // Não resetar aqui - deixar o HID_Task fazer isso
    }
    newCommandReceived = false;
    reset_counter = 0;
  }
  
  // Delay mínimo para não sobrecarregar
  _delay_ms(1);
}