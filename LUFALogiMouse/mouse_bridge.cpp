#include "mouse_bridge.h"
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
void initializeUSBHost(void) {
    // Inicializar USB Host Shield
    if (Usb.Init() == -1) {
        // Erro na inicialização - piscar LED ou algo similar
        return;
    }
    
    // Registrar parser
    HidMouse.SetReportParser(0, &Parser);
}

void processUSBHostTasks(void) {
    Usb.Task();
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
    last_mouse_x = 0;
    last_mouse_y = 0;
    last_mouse_wheel = 0;
}