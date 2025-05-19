#include "Descriptors.h"

// Mouse HID Report Descriptor (Simplificado para 84 bytes)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM MouseHIDReport[] = {
  // Descriptor ultra simplificado para atingir exatos 84 bytes
  0x05, 0x01,        // Usage Page (Generic Desktop)
  0x09, 0x02,        // Usage (Mouse)
  0xA1, 0x01,        // Collection (Application)
  0x09, 0x01,        //   Usage (Pointer)
  0xA1, 0x00,        //   Collection (Physical)
  0x05, 0x09,        //     Usage Page (Buttons)
  0x19, 0x01,        //     Usage Minimum (1)
  0x29, 0x08,        //     Usage Maximum (8)
  0x15, 0x00,        //     Logical Minimum (0)
  0x25, 0x01,        //     Logical Maximum (1)
  0x95, 0x08,        //     Report Count (8)
  0x75, 0x01,        //     Report Size (1)
  0x81, 0x02,        //     Input (Data,Var,Abs)
  0x05, 0x01,        //     Usage Page (Generic Desktop)
  0x09, 0x30,        //     Usage (X)
  0x09, 0x31,        //     Usage (Y)
  0x16, 0x01, 0x80,  //     Logical Minimum (-32767)
  0x26, 0xFF, 0x7F,  //     Logical Maximum (32767)
  0x95, 0x02,        //     Report Count (2)
  0x75, 0x10,        //     Report Size (16)
  0x81, 0x06,        //     Input (Data,Var,Rel)
  0x09, 0x38,        //     Usage (Wheel)
  0x15, 0x81,        //     Logical Minimum (-127)
  0x25, 0x7F,        //     Logical Maximum (127)
  0x95, 0x01,        //     Report Count (1)
  0x75, 0x08,        //     Report Size (8)
  0x81, 0x06,        //     Input (Data,Var,Rel)
  0x05, 0x0C,        //     Usage Page (Consumer)
  0x0A, 0x38, 0x02,  //     Usage (AC Pan)
  0x15, 0x81,        //     Logical Minimum (-127)
  0x25, 0x7F,        //     Logical Maximum (127)
  0x95, 0x01,        //     Report Count (1)
  0x75, 0x08,        //     Report Size (8)
  0x81, 0x06,        //     Input (Data,Var,Rel)
  // Vendor area para completar exatos 84 bytes
  0x06, 0xFF, 0x00,  //     Usage Page (Vendor)
  0x09, 0x01,        //     Usage (unk)
  0x95, 0x01,        //     Report Count (1)
  0x75, 0x08,        //     Report Size (8)
  0x81, 0x02,        //     Input (Data,Var,Abs)
  0xC0,              //   End Collection
  0xC0               // End Collection
  // Total: 84 bytes exatos
};

// Keyboard HID Report Descriptor (133 bytes - tamanho exato)
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

// Generic HID Report Descriptor (66 bytes - APENAS IN, sem OUT endpoint)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM GenericHIDReport[] = {
  // Descriptor simplificado - apenas INPUT (IN endpoint)
  0x06, 0x00, 0xFF,  // Usage Page (Vendor Defined)
  0x09, 0x01,        // Usage (unk)
  0xA1, 0x01,        // Collection (Application)
  
  // Input Report (apenas para debug/status via IN endpoint)
  0x09, 0x02,        //   Usage (unk)
  0x15, 0x00,        //   Logical Minimum (0)
  0x26, 0xFF, 0x00,  //   Logical Maximum (255)
  0x75, 0x08,        //   Report Size (8)
  0x95, 0x40,        //   Report Count (64)
  0x81, 0x02,        //   Input (Data,Var,Abs)
  
  // IMPORTANTE: NÃO incluir Output Report
  // LUFA HID recebe dados via control endpoint, não via OUT endpoint
  
  0xC0               // End Collection
  // Total: 23 bytes (muito menor que antes)
};

// Device Descriptor - Cópia exata do Logitech C547
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

// Configuration Descriptor - 3 interfaces, MAS sem OUT endpoint na interface 2
const USB_Descriptor_Configuration_t PROGMEM ConfigurationDescriptor = {
  .Config = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Configuration_Header_t), .Type = DTYPE_Configuration},
    .TotalConfigurationSize = sizeof(USB_Descriptor_Configuration_t),
    .TotalInterfaces        = 3,
    .ConfigurationNumber    = 1,
    .ConfigurationStrIndex  = STRING_ID_Configuration,
    .ConfigAttributes       = 0xA0,  // Bit7=1 (reserved) + Bit5=1 (Remote Wakeup)
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

  .HID_MouseEndpoint = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = MOUSE_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = MOUSE_EPSIZE,
    .PollingIntervalMS      = 0x01 // 1ms
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

  .HID_KeyboardEndpoint = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = KEYBOARD_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = KEYBOARD_EPSIZE,
    .PollingIntervalMS      = 0x01 // 1ms
  },

  // Interface 2 - HID Genérico (APENAS 1 ENDPOINT IN, sem OUT)
  .HID_GenericInterface = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Interface_t), .Type = DTYPE_Interface},
    .InterfaceNumber        = INTERFACE_ID_Generic,
    .AlternateSetting       = 0x00,
    .TotalEndpoints         = 1,  // APENAS 1 endpoint (IN)
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

  // APENAS endpoint IN - sem endpoint OUT
  .HID_GenericEndpointIN = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = GENERIC_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = GENERIC_EPSIZE,
    .PollingIntervalMS      = 0x01 // 1ms
  }

  // IMPORTANTE: HID_GenericEndpointOUT removido!
  // LUFA HID recebe dados via control endpoint
};

// String Descriptors
const USB_Descriptor_String_t PROGMEM LanguageString = USB_STRING_DESCRIPTOR_ARRAY(LANGUAGE_ID_ENG);

const USB_Descriptor_String_t PROGMEM ManufacturerString = USB_STRING_DESCRIPTOR(L"Logitech");

const USB_Descriptor_String_t PROGMEM ProductString = USB_STRING_DESCRIPTOR(L"USB Receiver");

const USB_Descriptor_String_t PROGMEM ConfigurationString = USB_STRING_DESCRIPTOR(L"MPR04.02_B0009");

// Callback para USB_GetDescriptor
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