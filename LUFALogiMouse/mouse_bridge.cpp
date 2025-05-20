#include <Arduino.h>
#include "mouse_bridge.h"

// Definir USB_HOST_SERIAL como Serial1
#define USB_HOST_SERIAL Serial1
// Desabilitar debugging para evitar problemas
#define ENABLE_UHS_DEBUGGING 0

// Macros para gerenciar interrupções USB do LUFA
#ifndef USB_INT_DISABLE
#define USB_INT_DISABLE() do { UDIEN = 0; } while(0)
#endif

#ifndef USB_INT_ENABLE
#define USB_INT_ENABLE() do { UDIEN = ((1 << RXSTPE) | (1 << SOFE)); } while(0)
#endif

#include <SPI.h>
#include <hidboot.h>
#include <usbhub.h>

// Variáveis para armazenar estado do mouse
static int8_t last_mouse_x = 0;
static int8_t last_mouse_y = 0;
static uint8_t last_mouse_buttons = 0;
static int8_t last_mouse_wheel = 0;
static uint8_t new_mouse_data = 0;

// Instâncias USB
USB Usb;
HIDBoot<USB_HID_PROTOCOL_MOUSE> HidMouse(&Usb);

// Parser de relatórios do mouse
class MouseRptParser : public MouseReportParser {
protected:
    void Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf);
    void OnMouseMove(USBHID *hid, uint8_t buttons, int8_t x, int8_t y, int8_t wheel);
    void OnLeftButtonDown(USBHID *hid);
    void OnLeftButtonUp(USBHID *hid);
    void OnRightButtonDown(USBHID *hid);
    void OnRightButtonUp(USBHID *hid);
    void OnMiddleButtonDown(USBHID *hid);
    void OnMiddleButtonUp(USBHID *hid);
    void OnWheelMove(USBHID *hid, int8_t wheel);
};

static MouseRptParser Parser;

void MouseRptParser::Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf) {
    // Chamar o parser pai para processar os eventos
    MouseReportParser::Parse(hid, is_rpt_id, len, buf);
}

void MouseRptParser::OnMouseMove(USBHID *hid, uint8_t buttons, int8_t x, int8_t y, int8_t wheel) {
    last_mouse_x = x;
    last_mouse_y = y;
    last_mouse_buttons = buttons;
    last_mouse_wheel = wheel;
    new_mouse_data = 1;
}

void MouseRptParser::OnWheelMove(USBHID *hid, int8_t wheel) {
    last_mouse_wheel = wheel;
    new_mouse_data = 1;
}

void MouseRptParser::OnLeftButtonDown(USBHID *hid) {
    last_mouse_buttons |= 0x01;
    new_mouse_data = 1;
}

void MouseRptParser::OnLeftButtonUp(USBHID *hid) {
    last_mouse_buttons &= ~0x01;
    new_mouse_data = 1;
}

void MouseRptParser::OnRightButtonDown(USBHID *hid) {
    last_mouse_buttons |= 0x02;
    new_mouse_data = 1;
}

void MouseRptParser::OnRightButtonUp(USBHID *hid) {
    last_mouse_buttons &= ~0x02;
    new_mouse_data = 1;
}

void MouseRptParser::OnMiddleButtonDown(USBHID *hid) {
    last_mouse_buttons |= 0x04;
    new_mouse_data = 1;
}

void MouseRptParser::OnMiddleButtonUp(USBHID *hid) {
    last_mouse_buttons &= ~0x04;
    new_mouse_data = 1;
}

// Funções de interface C
uint8_t initializeUSBHost(void) {
    // Inicializar SPI com configurações conservadoras
    SPI.begin();
    SPI.setClockDivider(SPI_CLOCK_DIV8);
    
    // Comentado: Defina pinos SPI específicos se necessário
    // Usb.gpioInit(SS_PIN, INT_PIN);
    
    // Inicializar o USB Host Shield e retornar o código de resultado
    uint8_t err = Usb.Init();

    // Se inicialização bem-sucedida, registrar o parser
    if (err == 0) {
        HidMouse.SetReportParser(0, &Parser);
        
        // Piscar LED duas vezes para indicar sucesso
        pinMode(13, OUTPUT);
        for (int i = 0; i < 2; i++) {
            digitalWrite(13, HIGH);
            delay(50);
            digitalWrite(13, LOW);
            delay(50);
        }
    }
    
    return err;
}

void processUSBHostTasks(void) {
    // Desabilitar temporariamente interrupções USB
    USB_INT_DISABLE();
    
    // Executar tarefas USB Host
    Usb.Task();
    
    // Reabilitar interrupções USB
    USB_INT_ENABLE();
}

int8_t getLastMouseX(void) {
    return last_mouse_x;
}

int8_t getLastMouseY(void) {
    return last_mouse_y;
}

uint8_t getLastMouseButtons(void) {
    return last_mouse_buttons;
}

int8_t getLastMouseWheel(void) {
    return last_mouse_wheel;
}

uint8_t hasNewMouseData(void) {
    return new_mouse_data;
}

void clearNewMouseDataFlag(void) {
    new_mouse_data = 0;
    // Resetamos X e Y para evitar movimentos repetidos
    last_mouse_x = 0;
    last_mouse_y = 0;
    last_mouse_wheel = 0;
}