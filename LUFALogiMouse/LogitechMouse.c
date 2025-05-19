#include "LogitechMouse.h"

// Static variables for USB communication
static MouseReport_t CurrentMouseReport;
static KeyboardReport_t CurrentKeyboardReport;
static uint8_t GenericHIDBuffer[64];

// Variables for mouse state (defined in main .ino)
extern int16_t mouse_x;
extern int16_t mouse_y;
extern uint8_t mouse_buttons;
extern int8_t mouse_wheel;

// Communication flags (declared in main .ino file)
extern volatile bool newCommandReceived;
extern volatile bool processingCommand;

// Debug/status variables
static uint32_t commands_received = 0;
static uint8_t last_command_type = 0;
static uint8_t communication_status = 0;

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
    
    // Reset variables
    mouse_x = 0;
    mouse_y = 0;
    mouse_buttons = 0;
    mouse_wheel = 0;
    
    // Reset communication status
    commands_received = 0;
    last_command_type = 0;
    communication_status = 0xFF; // Indica que está pronto
    
    // Configure LED pin for debug (Pin 13 = PC7)
    DDRC |= (1 << 7);   // Pin 13 as output
    PORTC &= ~(1 << 7); // LED off initially
}

// USB Event Handlers
void EVENT_USB_Device_Connect(void) {
    communication_status = 0x01; // Conectado
}

void EVENT_USB_Device_Disconnect(void) {
    communication_status = 0x00; // Desconectado
}

// EVENT_USB_Device_ConfigurationChanged - CORRIGIDO COM ENDPOINT OUT
void EVENT_USB_Device_ConfigurationChanged(void) {
    bool ConfigSuccess = true;

    // Configure Mouse Endpoint
    ConfigSuccess &= Endpoint_ConfigureEndpoint(MOUSE_IN_EPADDR, EP_TYPE_INTERRUPT, MOUSE_EPSIZE, 1);

    // Configure Keyboard Endpoint  
    ConfigSuccess &= Endpoint_ConfigureEndpoint(KEYBOARD_IN_EPADDR, EP_TYPE_INTERRUPT, KEYBOARD_EPSIZE, 1);

    // Configure Generic HID IN Endpoint
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_IN_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
    
    // Configure Generic HID OUT Endpoint (ENDPOINT 3 OUT)
    ConfigSuccess &= Endpoint_ConfigureEndpoint(GENERIC_OUT_EPADDR, EP_TYPE_INTERRUPT, GENERIC_EPSIZE, 1);
    
    if (ConfigSuccess) {
        communication_status = 0x02; // Configurado com sucesso
        // Piscar LED 2 vezes para indicar configuração bem-sucedida
        for (int i = 0; i < 2; i++) {
            PORTC |= (1 << 7);
            _delay_ms(100);
            PORTC &= ~(1 << 7);
            _delay_ms(100);
        }
    } else {
        communication_status = 0xEE; // Erro de configuração
        // LED permanece ligado em caso de erro
        PORTC |= (1 << 7);
    }
}

// Process commands - VERSÃO CORRIGIDA
void processGenericHIDData(uint8_t* buffer, uint16_t length) {
    if (length < 1) {
        return;
    }
    
    // Extrair comando
    uint8_t command_type = buffer[0];
    last_command_type = command_type;
    
    // Se primeiro byte é Report ID 0x00, pular
    if (command_type == 0x00 && length > 1) {
        command_type = buffer[1];
        buffer++;
        length--;
        last_command_type = command_type;
    }
    
    // PROCESSAR COMANDOS
    switch (command_type) {
        case 0x01: // Movimento
            {
                if (length >= 7) {
                    // Formato completo: [cmd][x_low][x_high][y_low][y_high][btn][wheel]
                    int16_t delta_x_16 = (int16_t)(buffer[1] | (buffer[2] << 8));
                    int16_t delta_y_16 = (int16_t)(buffer[3] | (buffer[4] << 8));
                    
                    // CORREÇÃO CRÍTICA: LIMITAR A 8-BIT PARA BOOT PROTOCOL
                    if (delta_x_16 > 127) mouse_x = 127;
                    else if (delta_x_16 < -127) mouse_x = -127;
                    else mouse_x = (int16_t)delta_x_16;
                    
                    if (delta_y_16 > 127) mouse_y = 127;
                    else if (delta_y_16 < -127) mouse_y = -127;
                    else mouse_y = (int16_t)delta_y_16;
                    
                    if (length > 5) mouse_buttons = buffer[5];
                    if (length > 6) mouse_wheel = (int8_t)buffer[6];
                    
                    newCommandReceived = true;
                    commands_received++;
                }
                else if (length >= 3) {
                    // Formato simples: [cmd][x][y] 
                    int8_t delta_x = (int8_t)buffer[1];
                    int8_t delta_y = (int8_t)buffer[2];
                    
                    mouse_x = (int16_t)delta_x;
                    mouse_y = (int16_t)delta_y;
                    
                    newCommandReceived = true;
                    commands_received++;
                }
            }
            break;
            
        case 0x02: // Clique
            {
                if (length >= 2) {
                    mouse_buttons = buffer[1];
                    newCommandReceived = true;
                    commands_received++;
                }
            }
            break;
            
        case 0x03: // Scroll
            {
                if (length >= 2) {
                    mouse_wheel = (int8_t)buffer[1];
                    newCommandReceived = true;
                    commands_received++;
                }
            }
            break;
            
        case 0x04: // Reset
            {
                mouse_x = 0;
                mouse_y = 0;
                mouse_buttons = 0;
                mouse_wheel = 0;
                newCommandReceived = true;
                commands_received++;
            }
            break;
            
        default:
            // Se não é comando conhecido, interpretar como movimento simples
            if (length >= 3) {
                mouse_x = (int16_t)((int8_t)buffer[1]);
                mouse_y = (int16_t)((int8_t)buffer[2]);
                newCommandReceived = true;
                commands_received++;
            }
            break;
    }
}

// Control Request (mantido para compatibilidade)
void EVENT_USB_Device_ControlRequest(void) {
    // Handle HID Class specific requests
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
                
                // Buffer para receber dados
                uint8_t TempBuffer[64];
                memset(TempBuffer, 0, sizeof(TempBuffer));
                
                // Ler dados do control stream
                uint16_t BytesReceived = 0;
                if (USB_ControlRequest.wLength > 0) {
                    BytesReceived = Endpoint_Read_Control_Stream_LE(TempBuffer, 
                                        (USB_ControlRequest.wLength < sizeof(TempBuffer)) ? 
                                        USB_ControlRequest.wLength : sizeof(TempBuffer));
                }
                
                Endpoint_ClearIN();
                
                // PROCESSAR DADOS RECEBIDOS
                if (BytesReceived > 0) {
                    processGenericHIDData(TempBuffer, BytesReceived);
                }
            }
            break;

        case HID_REQ_GetProtocol:
            if (USB_ControlRequest.bmRequestType == (REQDIR_DEVICETOHOST | REQTYPE_CLASS | REQREC_INTERFACE)) {
                Endpoint_ClearSETUP();
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

// HID Task - VERSÃO COMPLETAMENTE CORRIGIDA
void HID_Task(void) {
    // Device must be connected and configured
    if (USB_DeviceState != DEVICE_STATE_Configured)
        return;

    // Handle Mouse Endpoint (ENVIAR movimento)
    Endpoint_SelectEndpoint(MOUSE_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        // Atualizar relatório do mouse
        CurrentMouseReport.buttons = mouse_buttons;
        
        // CORREÇÃO CRÍTICA: MANTER VALORES 16-BIT COMPLETOS!
        // NÃO LIMITAR A 8-BIT COMO NO CÓDIGO ORIGINAL
        CurrentMouseReport.x = mouse_x;  // int16_t completo!
        CurrentMouseReport.y = mouse_y;  // int16_t completo!
        CurrentMouseReport.wheel = mouse_wheel;
        //CurrentMouseReport.hWheel = 0;
        
        // Enviar relatório (6 bytes: buttons(1) + x(2) + y(2) + wheel(1) + hWheel(1))
        Endpoint_Write_Stream_LE(&CurrentMouseReport, sizeof(MouseReport_t), NULL);
        Endpoint_ClearIN();
        
        // Reset movement após envio
        mouse_x = 0;
        mouse_y = 0;
        mouse_wheel = 0;
    }

    // Handle Keyboard Endpoint
    Endpoint_SelectEndpoint(KEYBOARD_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        Endpoint_Write_Stream_LE(&CurrentKeyboardReport, sizeof(KeyboardReport_t), NULL);
        Endpoint_ClearIN();
    }

    // Handle Generic HID IN (para status)
    Endpoint_SelectEndpoint(GENERIC_IN_EPADDR);
    if (Endpoint_IsINReady()) {
        // Enviar status para debug
        memset(GenericHIDBuffer, 0, sizeof(GenericHIDBuffer));
        GenericHIDBuffer[0] = 0xAA;              // Status signature
        GenericHIDBuffer[1] = communication_status;
        GenericHIDBuffer[2] = last_command_type;
        GenericHIDBuffer[3] = commands_received & 0xFF;
        GenericHIDBuffer[4] = (commands_received >> 8) & 0xFF;
        GenericHIDBuffer[5] = mouse_x & 0xFF;
        GenericHIDBuffer[6] = mouse_y & 0xFF;
        GenericHIDBuffer[7] = mouse_buttons;
        
        Endpoint_Write_Stream_LE(GenericHIDBuffer, sizeof(GenericHIDBuffer), NULL);
        Endpoint_ClearIN();
    }
    
    // Handle Generic HID OUT (RECEBER comandos) - VERSÃO COMPLETAMENTE CORRIGIDA
    Endpoint_SelectEndpoint(GENERIC_OUT_EPADDR);
    if (Endpoint_IsOUTReceived()) {
        // LED ON para indicar recepção de dados
        PORTC |= (1 << 7);
        
        // Buffer para receber dados
        uint8_t TempBuffer[64];
        memset(TempBuffer, 0, sizeof(TempBuffer));
        
        // MÉTODO CORRIGIDO: Ler byte por byte
        uint16_t BytesReceived = 0;
        
        // Verifica se há dados para ler
        if (Endpoint_IsReadWriteAllowed()) {
            // Lê todos os bytes disponíveis
            while (Endpoint_IsReadWriteAllowed() && BytesReceived < 64) {
                TempBuffer[BytesReceived] = Endpoint_Read_8();
                BytesReceived++;
            }
        }
        
        // SEMPRE limpar endpoint OUT
        Endpoint_ClearOUT();
        
        // Processar dados se recebidos
        if (BytesReceived > 0) {
            // Piscar LED para indicar processamento
            for (int i = 0; i < 3; i++) {
                PORTC ^= (1 << 7);  // Toggle LED
                _delay_ms(50);
            }
            
            // Processar comandos recebidos
            processGenericHIDData(TempBuffer, BytesReceived);
        }
        
        // LED OFF após processamento
        PORTC &= ~(1 << 7);
    }
}

// Utility functions (mantidas iguais)
void sendMouseReport(MouseReport_t* mouseReport) {
    memcpy(&CurrentMouseReport, mouseReport, sizeof(MouseReport_t));
}

void setMouseMovement(int16_t x, int16_t y) {
    mouse_x = x;
    mouse_y = y;
    newCommandReceived = true;
}

void setMouseButtons(uint8_t buttons) {
    mouse_buttons = buttons;
    newCommandReceived = true;
}

void setMouseWheel(int8_t wheel) {
    mouse_wheel = wheel;
    newCommandReceived = true;
}

void getMouseState(int16_t* x, int16_t* y, uint8_t* buttons, int8_t* wheel) {
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