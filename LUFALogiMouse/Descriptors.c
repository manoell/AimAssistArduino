#include "Descriptors.h"

// Mouse HID Report Descriptor - COPIADO EXATO do adaptador (83 bytes)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM MouseHIDReport[] = {
  // HEX exato do adaptador: 05 01 09 02 A1 01 09 01 A1 00 05 09 19 01 29 08 15 00 25 01 95 08 75 01 81 02 05 01 09 30 09 31 16 01 80 26 FF 7F 95 02 75 10 81 06 09 38 15 81 25 7F 95 01 75 08 81 06 05 0C 0A 38 02 15 81 25 7F 95 01 75 08 81 06 06 FF 00 09 01 75 08 81 02 C0 C0 00
  0x05, 0x01, 0x09, 0x02, 0xA1, 0x01, 0x09, 0x01, 0xA1, 0x00, 0x05, 0x09, 0x19, 0x01, 0x29, 0x08,
  0x15, 0x00, 0x25, 0x01, 0x95, 0x08, 0x75, 0x01, 0x81, 0x02, 0x05, 0x01, 0x09, 0x30, 0x09, 0x31,
  0x16, 0x01, 0x80, 0x26, 0xFF, 0x7F, 0x95, 0x02, 0x75, 0x10, 0x81, 0x06, 0x09, 0x38, 0x15, 0x81,
  0x25, 0x7F, 0x95, 0x01, 0x75, 0x08, 0x81, 0x06, 0x05, 0x0C, 0x0A, 0x38, 0x02, 0x15, 0x81, 0x25,
  0x7F, 0x95, 0x01, 0x75, 0x08, 0x81, 0x06, 0x06, 0xFF, 0x00, 0x09, 0x01, 0x75, 0x08, 0x81, 0x02,
  0xC0, 0xC0, 0x00
};

// Keyboard HID Report Descriptor - COPIADO EXATO do adaptador (133 bytes)
const USB_Descriptor_HIDReport_Datatype_t PROGMEM KeyboardHIDReport[] = {
  // HEX exato do adaptador: 05 01 09 06 A1 01 05 07 19 E0 29 E7 15 00 25 01 95 08 75 01 81 02 95 01 75 08 81 01 05 07 19 00 29 65 15 00 25 65 95 06 75 08 81 00 05 08 19 01 29 05 95 05 75 01 91 02 95 03 75 01 91 01 05 0C 09 01 A1 01 0A E2 00 0A E9 00 0A EA 00 0A CD 00 0A B7 00 0A B6 00 0A B5 00 0A 83 01 15 00 25 01 95 08 75 01 81 02 C0 05 01 09 80 A1 01 09 81 09 82 09 83 15 00 25 01 95 03 75 01 81 02 95 05 75 01 81 01 C0 C0
  0x05, 0x01, 0x09, 0x06, 0xA1, 0x01, 0x05, 0x07, 0x19, 0xE0, 0x29, 0xE7, 0x15, 0x00, 0x25, 0x01,
  0x95, 0x08, 0x75, 0x01, 0x81, 0x02, 0x95, 0x01, 0x75, 0x08, 0x81, 0x01, 0x05, 0x07, 0x19, 0x00,
  0x29, 0x65, 0x15, 0x00, 0x25, 0x65, 0x95, 0x06, 0x75, 0x08, 0x81, 0x00, 0x05, 0x08, 0x19, 0x01,
  0x29, 0x05, 0x95, 0x05, 0x75, 0x01, 0x91, 0x02, 0x95, 0x03, 0x75, 0x01, 0x91, 0x01, 0x05, 0x0C,
  0x09, 0x01, 0xA1, 0x01, 0x0A, 0xE2, 0x00, 0x0A, 0xE9, 0x00, 0x0A, 0xEA, 0x00, 0x0A, 0xCD, 0x00,
  0x0A, 0xB7, 0x00, 0x0A, 0xB6, 0x00, 0x0A, 0xB5, 0x00, 0x0A, 0x83, 0x01, 0x15, 0x00, 0x25, 0x01,
  0x95, 0x08, 0x75, 0x01, 0x81, 0x02, 0xC0, 0x05, 0x01, 0x09, 0x80, 0xA1, 0x01, 0x09, 0x81, 0x09,
  0x82, 0x09, 0x83, 0x15, 0x00, 0x25, 0x01, 0x95, 0x03, 0x75, 0x01, 0x81, 0x02, 0x95, 0x05, 0x75,
  0x01, 0x81, 0x01, 0xC0, 0xC0
};

// Generic HID Report Descriptor - EXATAMENTE 54 bytes como adaptador (ANTI-VANGUARD)
const uint8_t PROGMEM GenericHIDReport[54] = {
  // HEX EXATO do adaptador (apenas os 54 bytes que existem no original)
  0x06, 0x00, 0xFF, 0x09, 0x01, 0xA1, 0x01, 0x09, 0x02, 0x15, 0x00, 0x26, 0xFF, 0x00, 0x75, 0x08,
  0x95, 0x40, 0x81, 0x02, 0x09, 0x03, 0x15, 0x00, 0x26, 0xFF, 0x00, 0x75, 0x08, 0x95, 0x40, 0x91,
  0x02, 0x09, 0x04, 0x15, 0x00, 0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0xB1, 0x02, 0x09, 0x05, 0x15,
  0x00, 0x25, 0x0F, 0x75, 0x04, 0x95, 0x01, 0xB1, 0x02
  // Para aqui - exatamente como no adaptador original (54 bytes)
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

// Configuration Descriptor - 3 interfaces como o original
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

  // Interface 2 - HID Genérico (para receber comandos)
  .HID_GenericInterface = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Interface_t), .Type = DTYPE_Interface},
    .InterfaceNumber        = INTERFACE_ID_Generic,
    .AlternateSetting       = 0x00,
    .TotalEndpoints         = 1,
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
    .HIDReportLength        = 54
  },

  .HID_GenericEndpoint = {
    .Header                 = {.Size = sizeof(USB_Descriptor_Endpoint_t), .Type = DTYPE_Endpoint},
    .EndpointAddress        = GENERIC_IN_EPADDR,
    .Attributes             = (EP_TYPE_INTERRUPT | ENDPOINT_ATTR_NO_SYNC | ENDPOINT_USAGE_DATA),
    .EndpointSize           = GENERIC_EPSIZE,
    .PollingIntervalMS      = 0x01 // 1ms
  }
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