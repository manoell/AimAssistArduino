#include "LogitechMouse.h"
#include <util/delay.h>

// Static variables for USB communication
static MouseReport_t CurrentMouseReport;
static KeyboardReport_t CurrentKeyboardReport;
static uint8_t GenericHIDBuffer[64];

// Variables for mouse state
extern int8_t mouse_x;
extern int8_t mouse_y;
extern uint8_t mouse_buttons;
extern int8_t mouse_wheel;

// Communication flags
extern volatile bool newCommandReceived;
extern volatile bool processingCommand;

// Debug variables
static uint32_t commands_received = 0;
static uint8_t last_command_type = 0;
static uint8_t communication_status = 0;

// Setup Hardware Function
void SetupHardware(void) {
    // Disable watchdog
    MCUSR &= ~(1 << WDRF);
    wdt_disable();

    // Disable clock division
    clock_prescale_set(clock_div_1);
    
    // USB Fix para Leonardo
    USB_Disable();
    _delay_ms(100);
    
    USBCON &= ~(1 << USBE);
    USBCON &= ~(1 << OTGPADE);
    _delay_ms(50);
    
    UDCON = 0;
    UDIEN = 0;
    UDINT = 0;
    
    USBCON |= (1 << OTGPADE);
    USBCON |= (1 << VBUSTE);
    _delay_ms(100);
    
    USBCON |= (1 << USBE);
    _delay_ms(50);
    
    // Initialize LUFA
    USB_Init();
    
    // Initialize reports
    memset(&CurrentMouseReport, 0, sizeof(MouseReport_t));
    memset(&CurrentKeyboardReport, 0, sizeof(KeyboardReport_t));
    memset(GenericHIDBuffer, 0, sizeof(GenericHIDBuffer));
    
    // Reset states
    mouse_x = 0;
    mouse_y = 0;
    mouse_buttons = 0;
    mouse_wheel = 0;
    commands_received = 0;
    last_command_type = 0;
    communication_status = 0xFF;
    
    // Configure LED debug
    DDRC |= (1 << 7);   // Pin 13 as output
    PORTC &= ~(1 << 7); // LED off
    
    // Blink LED to show setup complete
    for (int i = 0; i < 3; i++) {
        PORTC |= (1 << 7);
        _delay_ms(100);
        PORTC &= ~(1 << 7);
        _delay_ms(100);
    }
}

// USB Event Handlers
void EVENT_USB_Device_Connect(void) {
    communication_status = 0x01;
    PORTC |= (1 << 7);
    _delay_ms(50);
    PORTC &= ~(1 << 7);
}

void EVENT_USB_Device_Disconnect(void) {
    communication_status = 0x00;
}

void EVENT_USB_Device_ConfigurationChanged(void) {
    bool ConfigSuccess = true;

    ConfigSuccess &= Endpoint_ConfigureEndpoint(MOUSE_IN_EPADDR, EP_TYPE_INTERRUPT, MOUSE_EPSIZE, 1);
    ConfigSuccess &= Endpoint_ConfigureEndpoint(KEYBOARD_IN_EPADDR, EP_TYPE_INTERRUPT, KEYBOARD_EPSIZE, 1);
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_IN_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_OUT_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
    
    if (ConfigSuccess) {
        communication_status = 0x02;
        for (int i = 0; i < 3; i++) {
            PORTC |= (1 << 7);
            _delay_ms(50);
            PORTC &= ~(1 << 7);
            _delay_ms(50);
        }
    } else {
        communication_status = 0xEE;
        PORTC |= (1 << 7);
    }
}

// DEBUG LED FUNCTION
void debugBlink(uint8_t times) {
    for (uint8_t i = 0; i < times; i++) {
        PORTC |= (1 << 7);
        _delay_ms(50);
        PORTC &= ~(1 << 7);
        if (i < times - 1) {
            _delay_ms(50);
        }
    }
}

// *** FUNÇÃO CORRIGIDA: Boot Protocol padrão de 3 bytes ***
void sendMouseReportNow(int8_t x, int8_t y, uint8_t buttons) {
    // Verificar se USB está configurado
    if (USB_DeviceState != DEVICE_STATE_Configured) {
        return;
    }
    
    // Selecionar endpoint de mouse
    Endpoint_SelectEndpoint(MOUSE_IN_EPADDR);
    
    // Verificar se endpoint está pronto
    if (!Endpoint_IsINReady()) {
        return;
    }
    
    // *** BOOT PROTOCOL PADRÃO: apenas 3 bytes ***
    // Byte 0: buttons
    // Byte 1: X movement (int8_t)
    // Byte 2: Y movement (int8_t)
    // SEM wheel no Boot Protocol padrão!
    
    Endpoint_Write_8(buttons);  // Buttons
    Endpoint_Write_8(x);        // X movement
    Endpoint_Write_8(y);        // Y movement
    
    // Enviar imediatamente
    Endpoint_ClearIN();
    
    // Debug LED: piscar rapidamente
    PORTC |= (1 << 7);
    _delay_ms(10);
    PORTC &= ~(1 << 7);
}

// *** FUNÇÃO PRINCIPAL: Process commands - FINAL ***
void processGenericHIDData(uint8_t* buffer, uint16_t length) {
    if (length < 1) {
        return;
    }
    
    // Extract command
    uint8_t* data = buffer;
    if (buffer[0] == 0x00 && length > 1) {
        data = buffer + 1;
        length--;
    }
    
    if (length < 1) {
        return;
    }
    
    uint8_t command_type = data[0];
    last_command_type = command_type;
    commands_received++;
    
    switch (command_type) {
        case 0x01: // Movement command
            {
                debugBlink(1);
                
                if (length >= 3) {
                    // *** FORMATO SIMPLES: X e Y como int8_t direto ***
                    int8_t x_movement = (int8_t)data[1];
                    int8_t y_movement = (int8_t)data[2];
                    
                    uint8_t buttons = (length > 3) ? data[3] : 0;
                    
                    // *** ENVIAR IMEDIATAMENTE - SÓ 3 BYTES ***
                    sendMouseReportNow(x_movement, y_movement, buttons);
                    
                    // Atualizar variáveis globais
                    mouse_x = x_movement;
                    mouse_y = y_movement;
                    mouse_buttons = buttons;
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x02: // Click
            {
                debugBlink(1);
                if (length >= 2) {
                    uint8_t buttons = data[1];
                    sendMouseReportNow(0, 0, buttons);
                    mouse_buttons = buttons;
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x03: // Scroll - IGNORADO no Boot Protocol
            {
                debugBlink(1);
                // Boot Protocol não suporta wheel
                // Apenas registrar o comando
                if (length >= 2) {
                    mouse_wheel = (int8_t)data[1];
                    newCommandReceived = true;
                }
            }
            break;
            
        case 0x04: // Reset
            {
                debugBlink(2);
                mouse_x = 0;
                mouse_y = 0;
                mouse_buttons = 0;
                mouse_wheel = 0;
                sendMouseReportNow(0, 0, 0);
                newCommandReceived = true;
            }
            break;
            
        case 0x05: // Ping
            {
                debugBlink(1);
                communication_status = 0x05;
            }
            break;
            
        default:
            debugBlink(2);
            break;
    }
}

// Control Request Handler
void EVENT_USB_Device_ControlRequest(void) {
    switch (USB_ControlRequest.bRequest) {
        case HID_REQ_GetReport:
            if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE)) {
                uint8_t* ReportData = NULL;
                uint16_t ReportSize = 0;

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
                Endpoint_ClearSETUP();
                
                uint8_t TempBuffer[64];
                memset(TempBuffer, 0, sizeof(TempBuffer));
                
                uint16_t BytesReceived = 0;
                if (USB_ControlRequest.wLength > 0) {
                    BytesReceived = Endpoint_Read_Control_Stream_LE(TempBuffer, 
                                        (USB_ControlRequest.wLength < sizeof(TempBuffer)) ? 
                                        USB_ControlRequest.wLength : sizeof(TempBuffer));
                }
                
                Endpoint_ClearIN();
                
                if (BytesReceived > 0) {
                    processGenericHIDData(TempBuffer, BytesReceived);
                }
            }
            break;

        case HID_REQ_GetProtocol:
            if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE)) {
                Endpoint_ClearSETUP();
                Endpoint_Write_8(0x00); // Boot Protocol (não Report Protocol!)
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

// HID Task
void HID_Task(void) {
    if (USB_DeviceState != DEVICE_STATE_Configured)
        return;

    // Processar comandos recebidos
    Endpoint_SelectEndpoint(GENERIC_OUT_EPADDR);
    if (Endpoint_IsOUTReceived()) {
        uint8_t ReceivedData[GENERIC_EPSIZE];
        uint16_t BytesReceived = 0;
        
        while (Endpoint_IsReadWriteAllowed() && BytesReceived < GENERIC_EPSIZE) {
            ReceivedData[BytesReceived++] = Endpoint_Read_8();
        }
        
        Endpoint_ClearOUT();
        
        if (BytesReceived > 0) {
            processGenericHIDData(ReceivedData, BytesReceived);
        }
    }

    // Status report ocasional
    static uint16_t status_counter = 0;
    status_counter++;
    
    if (status_counter >= 500) {
        status_counter = 0;
        
        Endpoint_SelectEndpoint(GENERIC_IN_EPADDR);
        if (Endpoint_IsINReady()) {
            GenericHIDBuffer[0] = 0xAA;
            GenericHIDBuffer[1] = communication_status;
            GenericHIDBuffer[2] = last_command_type;
            GenericHIDBuffer[3] = commands_received & 0xFF;
            GenericHIDBuffer[4] = (commands_received >> 8) & 0xFF;
            GenericHIDBuffer[5] = mouse_x;
            GenericHIDBuffer[6] = mouse_y;
            GenericHIDBuffer[7] = mouse_buttons;
            
            Endpoint_Write_Stream_LE(GenericHIDBuffer, GENERIC_EPSIZE, NULL);
            Endpoint_ClearIN();
        }
    }
}

// Utility functions
void sendMouseReport(MouseReport_t* mouseReport) {
    sendMouseReportNow(mouseReport->x, mouseReport->y, mouseReport->buttons);
}

void setMouseMovement(int8_t x, int8_t y) {
    sendMouseReportNow(x, y, mouse_buttons);
    mouse_x = x;
    mouse_y = y;
    newCommandReceived = true;
}

void setMouseButtons(uint8_t buttons) {
    sendMouseReportNow(0, 0, buttons);
    mouse_buttons = buttons;
    newCommandReceived = true;
}

void setMouseWheel(int8_t wheel) {
    // Boot Protocol não suporta wheel
    mouse_wheel = wheel;
    newCommandReceived = true;
}

void getMouseState(int8_t* x, int8_t* y, uint8_t* buttons, int8_t* wheel) {
    if (x) *x = mouse_x;
    if (y) *y = mouse_y;
    if (buttons) *buttons = mouse_buttons;
    if (wheel) *wheel = mouse_wheel;
}

// Debug functions
uint32_t getCommandsReceived(void) {
    return commands_received;
}

uint8_t getLastCommandType(void) {
    return last_command_type;
}

uint8_t getCommunicationStatus(void) {
    return communication_status;
}