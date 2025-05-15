/*
 * MouseAPI.hpp - Implementação inline da API do mouse
 */

// Include guard
#pragma once

// Definição do ATTRIBUTE_PACKED se não estiver definido
#ifndef ATTRIBUTE_PACKED
#define ATTRIBUTE_PACKED __attribute__((packed, aligned(1)))
#endif

// Implementação das funções inline
MouseAPI::MouseAPI(void) : _buttons(0)
{
    // Sem inicialização adicional necessária
}

void MouseAPI::begin(void)
{
    end();
}

void MouseAPI::end(void)
{
    _buttons = 0;
    move(0, 0, 0);
}

void MouseAPI::click(uint8_t b)
{
    _buttons = b;
    move(0, 0, 0);
    _buttons = 0;
    move(0, 0, 0);
}

void MouseAPI::move(signed char x, signed char y, signed char wheel)
{
    // Cria o relatório HID para o mouse
    HID_MouseReport_Data_t report;
    report.buttons = _buttons;
    report.xAxis = x;
    report.yAxis = y;
    report.wheel = wheel;
    
    // Envia o relatório HID para o PC
    SendReport(&report, sizeof(report));
}

void MouseAPI::buttons(uint8_t b)
{
    if (b != _buttons)
    {
        _buttons = b;
        move(0, 0, 0);
    }
}

void MouseAPI::press(uint8_t b)
{
    buttons(_buttons | b);
}

void MouseAPI::release(uint8_t b)
{
    buttons(_buttons & ~b);
}

void MouseAPI::releaseAll(void)
{
    _buttons = 0;
    move(0, 0, 0);
}

bool MouseAPI::isPressed(uint8_t b)
{
    return ((_buttons & b) != 0);
}

// Implementações das funções USB para configuração do dispositivo
void USB_SetVID(uint16_t vid) {
    USBDevice.setVendorId(vid);
}

void USB_SetPID(uint16_t pid) {
    USBDevice.setProductId(pid);
}

void USB_SetProductVersion(uint16_t version) {
    USBDevice.setDeviceVersion(version);
}

void USB_SetManufacturerString(const char* manufacturer) {
    USBDevice.setManufacturerString(manufacturer);
}

void USB_SetProductString(const char* product) {
    USBDevice.setProductString(product);
}

void USB_SetSerialNumber(const char* serial) {
    USBDevice.setSerialNumberString(serial);
}