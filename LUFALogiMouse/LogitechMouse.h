#ifndef _LOGITECH_MOUSE_H_
#define _LOGITECH_MOUSE_H_

// Includes
#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/power.h>
#include <avr/interrupt.h>
#include <string.h>

#include "Descriptors.h"
#include <LUFA/LUFA/Drivers/USB/USB.h>
#include <LUFA/LUFA/Platform/Platform.h>

// Type Definitions

// CORREÇÃO CRÍTICA: Usar estrutura compatível com HID Boot Protocol
typedef struct {
  uint8_t buttons;    // Button bits: [0]Left [1]Right [2]Middle [3]Back [4]Forward [5-7]Reserved
  int8_t x;           // X movement (-127 to +127) - BOOT PROTOCOL PADRÃO
  int8_t y;           // Y movement (-127 to +127) - BOOT PROTOCOL PADRÃO  
  int8_t wheel;       // Vertical scroll wheel (-127 to +127)
} __attribute__((packed)) MouseReport_t;

// Keyboard Report Structure (basic)
typedef struct {
  uint8_t modifier;   // Modifier keys (Ctrl, Alt, etc.)
  uint8_t reserved;   // Reserved byte
  uint8_t keycodes[6]; // Array of 6 key codes
} __attribute__((packed)) KeyboardReport_t;

// Command Types for AimAssist Communication
typedef enum {
  CMD_MOVE_MOUSE = 0x01,
  CMD_CLICK      = 0x02,
  CMD_SCROLL     = 0x03,
  CMD_RESET      = 0x04,
  CMD_PING       = 0x05
} CommandType_t;

// Command Structure for Generic HID Interface
typedef struct {
  uint8_t commandType;  // Command type from CommandType_t
  int8_t  deltaX;       // X movement delta (-127 to +127)
  int8_t  deltaY;       // Y movement delta (-127 to +127)
  uint8_t buttons;      // Button states
  int8_t  wheel;        // Wheel delta
  uint8_t reserved[59]; // Pad to 64 bytes total
} __attribute__((packed)) LogitechCommand_t;

// Mouse Button Definitions
#define MOUSE_LEFT_BUTTON    (1 << 0)
#define MOUSE_RIGHT_BUTTON   (1 << 1)
#define MOUSE_MIDDLE_BUTTON  (1 << 2)
#define MOUSE_BACK_BUTTON    (1 << 3)
#define MOUSE_FORWARD_BUTTON (1 << 4)

// Function Prototypes
#ifdef __cplusplus
extern "C" {
#endif

// Setup Functions
void SetupHardware(void);

// USB Event Handlers
void EVENT_USB_Device_Connect(void);
void EVENT_USB_Device_Disconnect(void);
void EVENT_USB_Device_ConfigurationChanged(void);
void EVENT_USB_Device_ControlRequest(void);

// HID Functions
void HID_Task(void);
void sendMouseReport(MouseReport_t* mouseReport);
void processGenericHIDData(uint8_t* buffer, uint16_t length);

#ifdef __cplusplus
}
#endif

#endif