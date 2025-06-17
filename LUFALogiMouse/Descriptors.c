#include "Descriptors.h"

// *** MOUSE HID REPORT DESCRIPTOR OTIMIZADO PARA 1000Hz ***
const USB_Descriptor_HIDReport_Datatype_t PROGMEM MouseHIDReport[] = {
  // Boot Protocol Mouse PADRÃO otimizado para gaming
  0x05, 0x01,        // Usage Page (Generic Desktop)
  0x09, 0x02,        // Usage (Mouse)
  0xA1, 0x01,        // Collection (Application)
  0x09, 0x01,        //   Usage (Pointer)
  0xA1, 0x00,        //   Collection (Physical)
  0x05, 0x09,        //     Usage Page (Buttons)
  0x19, 0x01,        //     Usage Minimum (1)
  0x29, 0x03,        //     Usage Maximum (3) - 3 botões Boot Protocol
  0x15, 0x00,        //     Logical Minimum (0)
  0x25, 0x01,        //     Logical Maximum (1)
  0x95, 0x03,        //     Report Count (3) - 3 botões
  0x75, 0x01,        //     Report Size (1)
  0x81, 0x02,        //     Input (Data,Var,Abs)
  0x95, 0x01,        //     Report Count (1) - Padding
  0x75, 0x05,        //     Report Size (5) - 5 bits de padding
  0x81, 0x01,        //     Input (Constant) - Padding
  0x05, 0x01,        //     Usage Page (Generic Desktop)
  0x09, 0x30,        //     Usage (X)
  0x09, 0x31,        //     Usage (Y)
  0x15, 0x81,        //     Logical Minimum (-127)
  0x25, 0x7F,        //     Logical Maximum (127)
  0x75, 0x08,        //     Report Size (8) - 8 bits
  0x95, 0x02,        //     Report Count (2) - X e Y
  0x81, 0x06,        //     Input (Data,Var,Rel)
  0xC0,              //   End Collection
  0xC0               // End Collection
  // Total: Boot Protocol padrão = 3 bytes (buttons + X + Y)
};

// Keyboard HID Report Descriptor (mantém igual)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM KeyboardHIDReport[] = {
  HID_RI_USAGE_PAGE(8, 0x01),     // Generic Desktop
  HID_RI_USAGE(8, 0x06),          // Keyboard
  HID_RI_COLLECTION(8, 0x01),     // Application
    // Modifier keys
    HID_RI_USAGE_PAGE(8, 0x07),   // Keyboard/Keypad
    HID_RI_USAGE_MINIMUM(8, 0xE0), // Left Control
    HID_RI_USAGE_MAXIMUM(8, 0xE7), // Right GUI
    HID_RI_LOGICAL_MINIMUM(8, 0x00),
    HID_RI_LOGICAL_MAXIMUM(8, 0x01),
    HID_RI_REPORT_COUNT(8, 0x08),
    HID_RI_REPORT_SIZE(8, 0x01),
    HID_RI_INPUT(8, HID_IOF_DATA | HID_IOF_VARIABLE | HID_IOF_ABSOLUTE),
    // Reserved byte
    HID_RI_REPORT_COUNT(8, 0x01),
    HID_RI_REPORT_SIZE(8, 0x08),
    HID_RI_INPUT(8, HID_IOF_CONSTANT),
    // Key codes
    HID_RI_USAGE_PAGE(8, 0x07),   // Keyboard/Keypad
    HID_RI_USAGE_MINIMUM(8, 0x00),
    HID_RI_USAGE_MAXIMUM(8, 0x65),
    HID_RI_LOGICAL_MINIMUM(8, 0x00),
    HID_RI_LOGICAL_MAXIMUM(8, 0x65),
    HID_RI_REPORT_COUNT(8, 0x06),
    HID_RI_REPORT_SIZE(8, 0x08),
    HID_RI_INPUT(8, HID_IOF_DATA | HID_IOF_ARRAY),
    // Output report (LEDs)
    HID_RI_USAGE_PAGE(8, 0x08),   // LEDs
    HID_RI_USAGE_MINIMUM(8, 0x01), // Num Lock
    HID_RI_USAGE_MAXIMUM(8, 0x05), // Kana
    HID_RI_REPORT_COUNT(8, 0x05),
    HID_RI_REPORT_SIZE(8, 0x01),
    HID_RI_OUTPUT(8, HID_IOF_DATA | HID_IOF_VARIABLE | HID_IOF_ABSOLUTE),
    HID_RI_REPORT_COUNT(8, 0x03),
    HID_RI_REPORT_SIZE(8, 0x01),
    HID_RI_OUTPUT(8, HID_IOF_CONSTANT),
    // Consumer controls (reduced set)
    HID_RI_USAGE_PAGE(8, 0x0C),   // Consumer
    HID_RI_USAGE(8, 0x01),        // Consumer Control
    HID_RI_COLLECTION(8, 0x01),   // Application
      HID_RI_USAGE(16, 0x00E2),   // Mute
      HID_RI_USAGE(16, 0x00E9),   // Volume Up
      HID_RI_USAGE(16, 0x00EA),   // Volume Down
      HID_RI_USAGE(16, 0x00CD),   // Play/Pause
      HID_RI_USAGE(16, 0x00B7),   // Stop
      HID_RI_USAGE(16, 0x00B6),   // Previous Track
      HID_RI_USAGE(16, 0x00B5),   // Next Track
      HID_RI_USAGE(16, 0x0183),   // Media Player
      HID_RI_LOGICAL_MINIMUM(8, 0x00),
      HID_RI_LOGICAL_MAXIMUM(8, 0x01),
      HID_RI_REPORT_COUNT(8, 0x08),
      HID_RI_REPORT_SIZE(8, 0x01),
      HID_RI_INPUT(8, HID_IOF_DATA | HID_IOF_VARIABLE | HID_IOF_ABSOLUTE),
    HID_RI_END_COLLECTION(0),
    // System controls
    HID_RI_USAGE_PAGE(8, 0x01),   // Generic Desktop
    HID_RI_USAGE(8, 0x80),        // System Control
    HID_RI_COLLECTION(8, 0x01),   // Application
      HID_RI_USAGE(8, 0x81),      // System Power Down
      HID_RI_USAGE(8, 0x82),      // System Sleep
      HID_RI_USAGE(8, 0x83),      // System Wake Up
      HID_RI_LOGICAL_MINIMUM(8, 0x00),
      HID_RI_LOGICAL_MAXIMUM(8, 0x01),
      HID_RI_REPORT_COUNT(8, 0x03),
      HID_RI_REPORT_SIZE(8, 0x01),
      HID_RI_INPUT(8, HID_IOF_DATA | HID_IOF_VARIABLE | HID_IOF_ABSOLUTE),
      HID_RI_REPORT_COUNT(8, 0x05),
      HID_RI_REPORT_SIZE(8, 0x01),
      HID_RI_INPUT(8, HID_IOF_CONSTANT),
    HID_RI_END_COLLECTION(0),
  HID_RI_END_COLLECTION(0)
};

// Generic HID Report Descriptor (mantém igual)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM GenericHIDReport[] = {
  0x06, 0x00, 0xFF,  // Usage Page (Vendor Defined)
  0x09, 0x01,        // Usage (unk)
  0xA1, 0x01,        // Collection (Application)
  
  // Input Report (para status via IN endpoint)
  0x09, 0x02,        //   Usage (unk)
  0x15, 0x00,        //   Logical Minimum (0)
  0x26, 0xFF, 0x00,  //   Logical Maximum (255)
  0x75, 0x08,        //   Report Size (8)
  0x95, 0x40,        //   Report Count (64)
  0x81, 0x02,        //   Input (Data,Var,Abs)
  
  // Output Report (para receber comandos via OUT endpoint)
  0x09, 0x03,        //   Usage (unk)
  0x15, 0x00,        //   Logical Minimum (0)
  0x26, 0xFF, 0x00,  //   Logical Maximum (255)
  0x75, 0x08,        //   Report Size (8)
  0x95, 0x40,        //   Report Count (64)
  0x91, 0x02,        //   Output (Data,Var,Abs)
  
  0xC0               // End Collection
};

// Device Descriptor (mantém igual)
const USB_Descriptor_Device_t PROGMEM DeviceDescriptor = {
  .Header                 = {.Size = sizeof(USB_Descriptor_Device_t), .Type = DTYPE_Device},
  .USBSpecification       = VERSION_BCD(2,0,0),
  .Class                  = USB_CSCP_NoDeviceClass,
  .SubClass               = USB_CSCP_NoDeviceSubclass,
  .Protocol               = USB_CSCP_NoDeviceProtocol,
  .Endpoint0Size          = FIXED_CONTROL_ENDPOINT_SIZE,
  
  .VendorID               = 0x046D,    // Logitech Inc.
  .ProductID              = 0xC547,    // USB Receiver
  .ReleaseNumber          = VERSION_BCD(4,0,2),
  
  .ManufacturerStrIndex   = STRING_ID_Manufacturer,
  .ProductStrIndex        = STRING_ID_Product,
  .SerialNumStrIndex      = NO_DESCRIPTOR,
  .NumberOfConfigurations = FIXED_NUM_CONFIGURATIONS
};

// *** CONFIGURATION DESCRIPTOR OTIMIZADO PARA 1000Hz ***
const USB_Descriptor_Configuration_t PROGMEM ConfigurationDescriptor = {
  .Config = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Configuration_Header_t), .Type = DTYPE_Configuration},
    .TotalConfigurationSize = sizeof(USB_Descriptor_Configuration_t),
    .TotalInterfaces        = 3,
    .ConfigurationNumber    = 1,
    .ConfigurationStrIndex  = STRING_ID_Configuration,
    .ConfigAttributes       = 0xA0,
    .MaxPowerConsumption    = USB_CONFIG_POWER_MA(98)
  },

  // Interface 0 - Mouse (Boot Protocol) 
  .HID_MouseInterface = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Interface_t), .Type = DTYPE_Interface},
    .InterfaceNumber        = INTERFACE_ID_Mouse,
    .AlternateSetting       = 0x00,
    .TotalEndpoints         = 1,
    .Class                  = HID_CSCP_HIDClass,
    .SubClass               = HID_CSCP_BootSubclass,
    .Protocol               = HID_CSCP_MouseBootProtocol,
    .InterfaceStrIndex      = NO_DESCRIPTOR
  },

  .HID_MouseHID = {
    .Header                 = {.Size = sizeof(USB_HID_Descriptor_HID_t), .Type = HID_DTYPE_HID},
    .HIDSpec                = VERSION_BCD(1,1,1),
    .CountryCode            = 0x00,
    .TotalReportDescriptors = 1,
    .HIDReportType          = HID_DTYPE_Report,
    .HIDReportLength        = sizeof(MouseHIDReport)
  },

  // *** MOUSE ENDPOINT OTIMIZADO PARA 1000Hz ***
  .HID_MouseEndpoint = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = MOUSE_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = MOUSE_EPSIZE,
    .PollingIntervalMS      = 0x01   // *** 1ms = 1000Hz POLLING RATE ***
  },

  // Interface 1 - Keyboard (Boot Protocol)  
  .HID_KeyboardInterface = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Interface_t), .Type = DTYPE_Interface},
    .InterfaceNumber        = INTERFACE_ID_Keyboard,
    .AlternateSetting       = 0x00,
    .TotalEndpoints         = 1,
    .Class                  = HID_CSCP_HIDClass,
    .SubClass               = HID_CSCP_BootSubclass,
    .Protocol               = HID_CSCP_KeyboardBootProtocol,
    .InterfaceStrIndex      = NO_DESCRIPTOR
  },

  .HID_KeyboardHID = {
    .Header                 = {.Size = sizeof(USB_HID_Descriptor_HID_t), .Type = HID_DTYPE_HID},
    .HIDSpec                = VERSION_BCD(1,1,1),
    .CountryCode            = 0x00,
    .TotalReportDescriptors = 1,
    .HIDReportType          = HID_DTYPE_Report,
    .HIDReportLength        = sizeof(KeyboardHIDReport)
  },

  // *** KEYBOARD ENDPOINT OTIMIZADO PARA 1000Hz ***
  .HID_KeyboardEndpoint = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = KEYBOARD_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = KEYBOARD_EPSIZE,
    .PollingIntervalMS      = 0x01   // *** 1ms = 1000Hz POLLING RATE ***
  },

  // Interface 2 - HID Genérico
  .HID_GenericInterface = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Interface_t), .Type = DTYPE_Interface},
    .InterfaceNumber        = INTERFACE_ID_Generic,
    .AlternateSetting       = 0x00,
    .TotalEndpoints         = 2,
    .Class                  = HID_CSCP_HIDClass,
    .SubClass               = HID_CSCP_NonBootSubclass,
    .Protocol               = HID_CSCP_NonBootProtocol,
    .InterfaceStrIndex      = NO_DESCRIPTOR
  },

  .HID_GenericHID = {
    .Header                 = {.Size = sizeof(USB_HID_Descriptor_HID_t), .Type = HID_DTYPE_HID},
    .HIDSpec                = VERSION_BCD(1,1,1),
    .CountryCode            = 0x00,
    .TotalReportDescriptors = 1,
    .HIDReportType          = HID_DTYPE_Report,
    .HIDReportLength        = sizeof(GenericHIDReport)
  },

  // *** GENERIC ENDPOINT IN OTIMIZADO PARA 1000Hz ***
  .HID_GenericEndpointIN = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = GENERIC_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = GENERIC_EPSIZE,
    .PollingIntervalMS      = 0x01   // *** 1ms = 1000Hz POLLING RATE ***
  },

  // *** GENERIC ENDPOINT OUT OTIMIZADO PARA 1000Hz - CRÍTICO PARA AIMBOT ***
  .HID_GenericEndpointOUT = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = GENERIC_OUT_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = GENERIC_EPSIZE,
    .PollingIntervalMS      = 0x01   // *** 1ms = 1000Hz POLLING RATE - CRÍTICO! ***
  }
};

// String Descriptors (mantém igual)
const USB_Descriptor_String_t PROGMEM LanguageString = USB_STRING_DESCRIPTOR_ARRAY(LANGUAGE_ID_ENG);
const USB_Descriptor_String_t PROGMEM ManufacturerString = USB_STRING_DESCRIPTOR(L"Logitech");
const USB_Descriptor_String_t PROGMEM ProductString = USB_STRING_DESCRIPTOR(L"USB Receiver");
const USB_Descriptor_String_t PROGMEM ConfigurationString = USB_STRING_DESCRIPTOR(L"MPR04.02_B0009");

// Callback para USB_GetDescriptor (mantém igual)
uint16_t CALLBACK_USB_GetDescriptor(const uint16_t wValue,
                                    const uint16_t wIndex,
                                    const void** const DescriptorAddress) {
  const uint8_t  DescriptorType   = (wValue >> 8);
  const uint8_t  DescriptorNumber = (wValue & 0xFF);

  const void* Address = NULL;
  uint16_t    Size    = NO_DESCRIPTOR;

  switch (DescriptorType) {
    case DTYPE_Device:
      Address = &DeviceDescriptor;
      Size    = sizeof(USB_Descriptor_Device_t);
      break;
      
    case DTYPE_Configuration:
      Address = &ConfigurationDescriptor;
      Size    = sizeof(USB_Descriptor_Configuration_t);
      break;
      
    case DTYPE_String:
      switch (DescriptorNumber) {
        case STRING_ID_Language:
          Address = &LanguageString;
          Size    = pgm_read_byte(&LanguageString.Header.Size);
          break;
        case STRING_ID_Manufacturer:
          Address = &ManufacturerString;
          Size    = pgm_read_byte(&ManufacturerString.Header.Size);
          break;
        case STRING_ID_Product:
          Address = &ProductString;
          Size    = pgm_read_byte(&ProductString.Header.Size);
          break;
        case STRING_ID_Configuration:
          Address = &ConfigurationString;
          Size    = pgm_read_byte(&ConfigurationString.Header.Size);
          break;
      }
      break;
      
    case DTYPE_HID:
      switch (wIndex) {
        case INTERFACE_ID_Mouse:
          Address = &ConfigurationDescriptor.HID_MouseHID;
          Size    = sizeof(USB_HID_Descriptor_HID_t);
          break;
        case INTERFACE_ID_Keyboard:
          Address = &ConfigurationDescriptor.HID_KeyboardHID;
          Size    = sizeof(USB_HID_Descriptor_HID_t);
          break;
        case INTERFACE_ID_Generic:
          Address = &ConfigurationDescriptor.HID_GenericHID;
          Size    = sizeof(USB_HID_Descriptor_HID_t);
          break;
      }
      break;
      
    case DTYPE_Report:
      switch (wIndex) {
        case INTERFACE_ID_Mouse:
          Address = &MouseHIDReport;
          Size    = sizeof(MouseHIDReport);
          break;
        case INTERFACE_ID_Keyboard:
          Address = &KeyboardHIDReport;
          Size    = sizeof(KeyboardHIDReport);
          break;
        case INTERFACE_ID_Generic:
          Address = &GenericHIDReport;
          Size    = sizeof(GenericHIDReport);
          break;
      }
      break;
  }

  *DescriptorAddress = Address;
  return Size;
}