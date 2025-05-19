#include "LUFAConfig.h"
#include <LUFA.h>
#include "LogitechMouse.h"
#include <inttypes.h>

// Mouse state
int8_t mouseX = 0;
int8_t mouseY = 0;
uint8_t mouseButtons = 0;
int8_t mouseWheel = 0;

// Command receiving buffer
LogitechCommand_t receivedCommand;
bool newCommandReceived = false;

void setup() {
  // Initialize hardware
  SetupHardware();
  GlobalInterruptEnable();
  
  // Initialize mouse state
  mouseX = 0;
  mouseY = 0;
  mouseButtons = 0;
  mouseWheel = 0;
  newCommandReceived = false;
}

void loop() {
  // Process any received commands
  if (newCommandReceived) {
    processCommand(&receivedCommand);
    newCommandReceived = false;
  }
  
  // Send mouse report
  generateAndSendMouseReport();
  
  // Process HID tasks
  HID_Task();
  
  // USB tasks
  USB_USBTask();
}

void processCommand(LogitechCommand_t* cmd) {
  switch(cmd->commandType) {
    case CMD_MOVE_MOUSE:
      mouseX = cmd->deltaX;
      mouseY = cmd->deltaY;
      break;
      
    case CMD_CLICK:
      mouseButtons = cmd->buttons;
      break;
      
    case CMD_SCROLL:
      mouseWheel = cmd->wheel;
      break;
      
    case CMD_RESET:
      mouseX = 0;
      mouseY = 0;
      mouseButtons = 0;
      mouseWheel = 0;
      break;
      
    default:
      break;
  }
}

void generateAndSendMouseReport() {
  static uint8_t reportCounter = 0;
  
  // Send mouse report every 1ms (1000Hz)
  if (++reportCounter >= 1) {
    reportCounter = 0;
    
    // Create mouse report
    MouseReport_t mouseReport;
    mouseReport.buttons = mouseButtons;
    mouseReport.x = mouseX;
    mouseReport.y = mouseY;
    mouseReport.wheel = mouseWheel;
    mouseReport.hWheel = 0; // No horizontal wheel
    
    // Send the report
    sendMouseReport(&mouseReport);
    
    // Clear deltas after sending (for one-shot movements)
    mouseX = 0;
    mouseY = 0;
    mouseWheel = 0;
    // Keep buttons as they are (sticky until explicitly changed)
  }
}