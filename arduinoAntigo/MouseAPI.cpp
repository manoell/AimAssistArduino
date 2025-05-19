#include "MouseAPI.h"
#include <Arduino.h>

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