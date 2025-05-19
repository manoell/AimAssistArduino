#include "LogitechMouse.h"

// Static variables for USB communication
static MouseReport_t CurrentMouseReport;
static KeyboardReport_t CurrentKeyboardReport;
static uint8_t GenericHIDBuffer[64];

// Variables for mouse state and movement processing (defined in main .ino)
extern int16_t mouse_x;
extern int16_t mouse_y;
extern uint8_t mouse_buttons;
extern int8_t mouse_wheel;

// Smoothing and acceleration variables (static to this file only)
static float velocity_x = 0.0f;
static float velocity_y = 0.0f;
static float acceleration_factor = 1.5f;
static float dampening_factor = 0.85f;

// Communication flags (declared in main .ino file)
extern volatile bool newCommandReceived;
extern volatile bool processingCommand;

// Command structure for HID communication
typedef struct {
    uint8_t command_type;    // 0x01=move, 0x02=click, 0x03=scroll, 0x04=reset
    int16_t delta_x;         // X movement delta (-32767 to +32767)
    int16_t delta_y;         // Y movement delta (-32767 to +32767)
    uint8_t buttons;         // Button state
    int8_t wheel;            // Wheel delta
    uint8_t speed_factor;    // Speed multiplier (1-10)
    uint8_t smooth_factor;   // Smoothing intensity (1-10)
    uint8_t reserved[55];    // Padding to 64 bytes
} __attribute__((packed)) AimAssistCommand_t;

// External variables - removed since we define them locally

// Setup Hardware Function
void SetupHardware(void) {
    // Disable watchdog if enabled by bootloader/fuses
    MCUSR &= ~(1 << WDRF);
    wdt_disable();

    // Disable clock division before initializing the USB hardware
    clock_prescale_set(clock_div_1);

    // Initialize USB Stack
    USB_Init();
    
    // Initialize mouse state
    memset(&CurrentMouseReport, 0, sizeof(MouseReport_t));
    memset(&CurrentKeyboardReport, 0, sizeof(KeyboardReport_t));
    memset(GenericHIDBuffer, 0, sizeof(GenericHIDBuffer));
    
    // Reset movement variables
    mouse_x = 0;
    mouse_y = 0;
    mouse_buttons = 0;
    mouse_wheel = 0;
    velocity_x = 0.0f;
    velocity_y = 0.0f;
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

    // Configure Generic HID Endpoints (IN and OUT)
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_IN_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_OUT_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
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

// Advanced Movement Processing with Smoothing and Acceleration
void processMouseMovement(int16_t raw_x, int16_t raw_y, uint8_t speed_factor, uint8_t smooth_factor) {
    // Convert speed factor from 1-10 to 0.1-2.0 multiplier
    float speed_multiplier = (float)speed_factor / 5.0f;
    
    // Convert smooth factor from 1-10 to smoothing intensity
    float smoothing = (float)smooth_factor / 10.0f;
    
    // Apply speed to raw input
    float target_x = (float)raw_x * speed_multiplier;
    float target_y = (float)raw_y * speed_multiplier;
    
    // Apply acceleration (gradual velocity buildup)
    velocity_x += (target_x - velocity_x) * acceleration_factor * 0.1f;
    velocity_y += (target_y - velocity_y) * acceleration_factor * 0.1f;
    
    // Apply smoothing (blend current velocity with target)
    velocity_x = velocity_x * smoothing + target_x * (1.0f - smoothing);
    velocity_y = velocity_y * smoothing + target_y * (1.0f - smoothing);
    
    // Apply dampening to prevent oscillation
    velocity_x *= dampening_factor;
    velocity_y *= dampening_factor;
    
    // Convert back to integer movement
    mouse_x = (int16_t)velocity_x;
    mouse_y = (int16_t)velocity_y;
    
    // Clamp to valid HID range
    if (mouse_x > 32767) mouse_x = 32767;
    if (mouse_x < -32767) mouse_x = -32767;
    if (mouse_y > 32767) mouse_y = 32767;
    if (mouse_y < -32767) mouse_y = -32767;
}

// Process commands received via Generic HID Interface
void processGenericHIDData(uint8_t* buffer, uint16_t length) {
    // Debug: Verificar se chegaram dados
    if (length < 1) {
        return;
    }
    
    // Extract command from buffer (método simplificado)
    uint8_t command_type = buffer[0];
    
    // Processar diferentes tipos de comando
    switch (command_type) {
        case 0x01: // Move mouse
            {
                if (length >= 9) {
                    // Extrair dados do comando
                    int16_t delta_x = (int16_t)(buffer[1] | (buffer[2] << 8));
                    int16_t delta_y = (int16_t)(buffer[3] | (buffer[4] << 8));
                    uint8_t speed_factor = (length > 7) ? buffer[7] : 5;
                    uint8_t smooth_factor = (length > 8) ? buffer[8] : 5;
                    
                    // Aplicar movimento diretamente (sem smoothing complexo por enquanto)
                    mouse_x = delta_x;
                    mouse_y = delta_y;
                    
                    // Marcar que há novos dados para enviar
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x02: // Mouse click
            {
                if (length >= 6) {
                    mouse_buttons = buffer[5];
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x03: // Mouse scroll
            {
                if (length >= 7) {
                    mouse_wheel = (int8_t)buffer[6];
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x04: // Reset/stop
            {
                // Reset todos os valores
                mouse_x = 0;
                mouse_y = 0;
                mouse_buttons = 0;
                mouse_wheel = 0;
                velocity_x = 0.0f;
                velocity_y = 0.0f;
                newCommandReceived = true;
            }
            break;
            
        default:
            // Comando desconhecido - ignorar
            break;
    }
}

// HID Task Function with Enhanced Generic Interface Handling
void HID_Task(void) {
    // Device must be connected and configured
    if (USB_DeviceState != DEVICE_STATE_Configured)
        return;

    // Handle Mouse Endpoint - Send current mouse state
    Endpoint_SelectEndpoint(MOUSE_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        // Update mouse report
        CurrentMouseReport.buttons = mouse_buttons;
        CurrentMouseReport.x = mouse_x;
        CurrentMouseReport.y = mouse_y;
        CurrentMouseReport.wheel = mouse_wheel;
        CurrentMouseReport.hWheel = 0; // No horizontal wheel support
        
        // Send the report
        Endpoint_Write_Stream_LE(&CurrentMouseReport, sizeof(MouseReport_t), NULL);
        Endpoint_ClearIN();
        
        // Reset movement deltas after sending (one-shot movement)
        mouse_x = 0;
        mouse_y = 0;
        mouse_wheel = 0;
    }

    // Handle Keyboard Endpoint (optional - maintained for compatibility)
    Endpoint_SelectEndpoint(KEYBOARD_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        Endpoint_Write_Stream_LE(&CurrentKeyboardReport, sizeof(KeyboardReport_t), NULL);
        Endpoint_ClearIN();
    }

    // Handle Generic HID Endpoint - Receive commands from PC
    Endpoint_SelectEndpoint(GENERIC_OUT_EPADDR);
    
    // Check for incoming data (commands from PC)
    if (Endpoint_IsOUTReceived()) {
        if (Endpoint_IsReadWriteAllowed()) {
            // Read command data
            uint8_t tempBuffer[64];
            memset(tempBuffer, 0, sizeof(tempBuffer));
            
            // Read the available data
            uint16_t bytesRead = 0;
            while (Endpoint_IsReadWriteAllowed() && bytesRead < sizeof(tempBuffer)) {
                tempBuffer[bytesRead++] = Endpoint_Read_8();
            }
            
            // Process the command if we got data
            if (bytesRead > 0) {
                processGenericHIDData(tempBuffer, bytesRead);
            }
        }
        Endpoint_ClearOUT();
    }
    
    // Handle Generic HID IN endpoint - Send status to PC
    Endpoint_SelectEndpoint(GENERIC_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        // Send status or acknowledgment data if needed
        memset(GenericHIDBuffer, 0, sizeof(GenericHIDBuffer));
        GenericHIDBuffer[0] = 0xAA; // Status byte
        Endpoint_Write_Stream_LE(GenericHIDBuffer, sizeof(GenericHIDBuffer), NULL);
        Endpoint_ClearIN();
    }
}

// Send Mouse Report (utility function)
void sendMouseReport(MouseReport_t* mouseReport) {
    // Update current mouse report
    memcpy(&CurrentMouseReport, mouseReport, sizeof(MouseReport_t));
    
    // The actual sending happens in HID_Task()
    // This function just updates the internal state
}

// Utility function to set mouse movement directly
void setMouseMovement(int16_t x, int16_t y) {
    mouse_x = x;
    mouse_y = y;
    newCommandReceived = true;
}

// Utility function to set mouse buttons
void setMouseButtons(uint8_t buttons) {
    mouse_buttons = buttons;
    newCommandReceived = true;
}

// Utility function to set mouse wheel
void setMouseWheel(int8_t wheel) {
    mouse_wheel = wheel;
    newCommandReceived = true;
}

// Get current mouse state (for debugging/monitoring)
void getMouseState(int16_t* x, int16_t* y, uint8_t* buttons, int8_t* wheel) {
    if (x) *x = mouse_x;
    if (y) *y = mouse_y;
    if (buttons) *buttons = mouse_buttons;
    if (wheel) *wheel = mouse_wheel;
}