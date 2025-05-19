#include "LogitechMouse.h"

// Static variables for USB communication
static MouseReport_t CurrentMouseReport;
static KeyboardReport_t CurrentKeyboardReport;
static uint8_t GenericHIDBuffer[64];

// External variables from main
extern bool newCommandReceived;
extern LogitechCommand_t receivedCommand;

// Setup Hardware Function
void SetupHardware(void) {
  // Disable watchdog if enabled by bootloader/fuses
  MCUSR &= ~(1 << WDRF);
  wdt_disable();

  // Disable clock division before initializing the USB hardware
  clock_prescale_set(clock_div_1);

  // Initialize USB Stack
  USB_Init();
}

// USB Event Handlers

void EVENT_USB_Device_Connect(void) {
  // Device connected - could add LED indication here
}

void EVENT_USB_Device_Disconnect(void) {
  // Device disconnected - could add LED indication here
}

void EVENT_USB_Device_ConfigurationChanged(void) {
  bool ConfigSuccess = true;

  // Configure Mouse Endpoint
  ConfigSuccess &= Endpoint_ConfigureEndpoint(MOUSE_IN_EPADDR, EP_TYPE_INTERRUPT, MOUSE_EPSIZE, 1);

  // Configure Keyboard Endpoint  
  ConfigSuccess &= Endpoint_ConfigureEndpoint(KEYBOARD_IN_EPADDR, EP_TYPE_INTERRUPT, KEYBOARD_EPSIZE, 1);

  // Configure Generic HID Endpoint
  ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_IN_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
}

void EVENT_USB_Device_ControlRequest(void) {
  // Handle HID Class specific requests
  switch (USB_ControlRequest.bRequest) {
    case HID_REQ_GetReport:
      if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE)) {
        uint8_t* ReportData = NULL;
        uint16_t ReportSize = 0;

        // Determine which interface is being requested
        switch (USB_ControlRequest.wIndex) {
          case INTERFACE_ID_Mouse:
            ReportData = (uint8_t*)&CurrentMouseReport;
            ReportSize = sizeof(MouseReport_t);
            break;
          case INTERFACE_ID_Keyboard:
            ReportData = (uint8_t*)&CurrentKeyboardReport;
            ReportSize = sizeof(KeyboardReport_t);
            break;
          case INTERFACE_ID_Generic:
            ReportData = GenericHIDBuffer;
            ReportSize = sizeof(GenericHIDBuffer);
            break;
        }

        if (ReportData != NULL) {
          Endpoint_ClearSETUP();
          Endpoint_Write_Control_Stream_LE(ReportData, ReportSize);
          Endpoint_ClearOUT();
        }
      }
      break;

    case HID_REQ_SetReport:
      if (USB_ControlRequest.bmRequestType == (REQDIR_HOSTTODEVICE | REQTYPE_CLASS | REQREC_INTERFACE)) {
        uint8_t* ReportData = NULL;
        uint16_t ReportSize = 0;

        // Only Generic HID interface accepts input reports (for commands)
        if (USB_ControlRequest.wIndex == INTERFACE_ID_Generic) {
          ReportData = GenericHIDBuffer;
          ReportSize = sizeof(GenericHIDBuffer);

          Endpoint_ClearSETUP();
          Endpoint_Read_Control_Stream_LE(ReportData, ReportSize);
          Endpoint_ClearIN();

          // Process the received command
          processGenericHIDData(GenericHIDBuffer, ReportSize);
        }
      }
      break;

    case HID_REQ_GetProtocol:
      if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE)) {
        Endpoint_ClearSETUP();
        
        // Always report protocol mode (not boot mode)
        Endpoint_Write_8(0x01);
        
        Endpoint_ClearIN();
      }
      break;

    case HID_REQ_SetProtocol:
      if (USB_ControlRequest.bmRequestType == (REQDIR_HOSTTODEVICE | REQTYPE_CLASS | REQREC_INTERFACE)) {
        Endpoint_ClearSETUP();
        Endpoint_ClearStatusStage();
      }
      break;
  }
}

// HID Task Function
void HID_Task(void) {
  // Device must be connected and configured
  if (USB_DeviceState != DEVICE_STATE_Configured)
    return;

  // Handle Mouse Endpoint
  Endpoint_SelectEndpoint(MOUSE_IN_EPADDR);
  if (Endpoint_IsINReady()) {
    Endpoint_Write_Stream_LE(&CurrentMouseReport, sizeof(MouseReport_t), NULL);
    Endpoint_ClearIN();
  }

  // Handle Keyboard Endpoint (optional - can be used if needed)
  Endpoint_SelectEndpoint(KEYBOARD_IN_EPADDR);
  if (Endpoint_IsINReady()) {
    Endpoint_Write_Stream_LE(&CurrentKeyboardReport, sizeof(KeyboardReport_t), NULL);
    Endpoint_ClearIN();
  }

  // Handle Generic HID Endpoint (for receiving commands)
  Endpoint_SelectEndpoint(GENERIC_IN_EPADDR);
  if (Endpoint_IsOUTReceived()) {
    if (Endpoint_IsReadWriteAllowed()) {
      // Read command data
      Endpoint_Read_Stream_LE(GenericHIDBuffer, sizeof(GenericHIDBuffer), NULL);
      
      // Process the command
      processGenericHIDData(GenericHIDBuffer, sizeof(GenericHIDBuffer));
    }
    Endpoint_ClearOUT();
  }
}

// Send Mouse Report
void sendMouseReport(MouseReport_t* mouseReport) {
  // Update current mouse report
  memcpy(&CurrentMouseReport, mouseReport, sizeof(MouseReport_t));
  
  // Send will happen in HID_Task()
}

// Process Generic HID Data (Commands from AimAssist software)
void processGenericHIDData(uint8_t* buffer, uint16_t length) {
  // Check if we have enough data for a command
  if (length >= sizeof(LogitechCommand_t)) {
    // Copy command data
    memcpy(&receivedCommand, buffer, sizeof(LogitechCommand_t));
    
    // Signal that new command was received
    newCommandReceived = true;
  }
}