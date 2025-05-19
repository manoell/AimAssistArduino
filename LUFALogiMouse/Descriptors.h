#ifndef _DESCRIPTORS_H_
#define _DESCRIPTORS_H_

#include "LUFAConfig.h"
#include <avr/pgmspace.h>
#include <LUFA/LUFA/Drivers/USB/USB.h>

// Macros

// Interface IDs
enum InterfaceDescriptors_t {
  INTERFACE_ID_Mouse    = 0, // Mouse interface (Boot protocol)
  INTERFACE_ID_Keyboard = 1, // Keyboard interface (Boot protocol)  
  INTERFACE_ID_Generic  = 2, // Generic HID interface (for commands)
};

// String Descriptor IDs
enum StringDescriptors_t {
  STRING_ID_Language      = 0, // Supported languages
  STRING_ID_Manufacturer  = 1, // "Logitech"
  STRING_ID_Product       = 2, // "USB Receiver"
  STRING_ID_Configuration = 4, // "MPR04.02_B0009"
};

// Endpoint Addresses
#define MOUSE_IN_EPADDR    (ENDPOINT_DIR_IN  | 1)  // Endpoint 1 IN
#define KEYBOARD_IN_EPADDR (ENDPOINT_DIR_IN  | 2)  // Endpoint 2 IN  
#define GENERIC_IN_EPADDR  (ENDPOINT_DIR_IN  | 3)  // Endpoint 3 IN

// Endpoint Sizes (64 bytes como o original)
#define MOUSE_EPSIZE       64
#define KEYBOARD_EPSIZE    64
#define GENERIC_EPSIZE     64

// HID Class Descriptor Types
#define DTYPE_HID          0x21
#define DTYPE_Report       0x22

// Type Defines

// Configuration Descriptor Structure
typedef struct {
  USB_Descriptor_Configuration_Header_t Config;

  // Mouse Interface
  USB_Descriptor_Interface_t            HID_MouseInterface;
  USB_HID_Descriptor_HID_t              HID_MouseHID;
  USB_Descriptor_Endpoint_t             HID_MouseEndpoint;

  // Keyboard Interface
  USB_Descriptor_Interface_t            HID_KeyboardInterface;
  USB_HID_Descriptor_HID_t              HID_KeyboardHID;
  USB_Descriptor_Endpoint_t             HID_KeyboardEndpoint;

  // Generic HID Interface
  USB_Descriptor_Interface_t            HID_GenericInterface;
  USB_HID_Descriptor_HID_t              HID_GenericHID;
  USB_Descriptor_Endpoint_t             HID_GenericEndpoint;
} USB_Descriptor_Configuration_t;

// HID Report Descriptors (external declarations)
extern const USB_Descriptor_HIDReport_Datatype_t PROGMEM MouseHIDReport[];
extern const USB_Descriptor_HIDReport_Datatype_t PROGMEM KeyboardHIDReport[];
extern const uint8_t PROGMEM GenericHIDReport[];

// Function Prototypes
uint16_t CALLBACK_USB_GetDescriptor(const uint16_t wValue,
                                    const uint16_t wIndex,
                                    const void** const DescriptorAddress)
                                    ATTR_WARN_UNUSED_RESULT ATTR_NON_NULL_PTR_ARG(3);

#endif