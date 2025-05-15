/*
 * MouseAPI.h - Interface API for G502 X PLUS spoof
 */

// Include guard
#pragma once

// Adicionar includes necessários para tipos de dados
#include <Arduino.h>

#define HID_REPORTID_MOUSE 1

// Flags para os botões do mouse
#define MOUSE_LEFT (1 << 0)
#define MOUSE_RIGHT (1 << 1)
#define MOUSE_MIDDLE (1 << 2)
#define MOUSE_BACK (1 << 3)
#define MOUSE_FORWARD (1 << 4)
#define MOUSE_ALL (MOUSE_LEFT | MOUSE_RIGHT | MOUSE_MIDDLE | MOUSE_BACK | MOUSE_FORWARD)

// Estrutura de dados do relatório HID
typedef struct
{
    uint8_t buttons;
    int8_t xAxis;
    int8_t yAxis;
    int8_t wheel;
} HID_MouseReport_Data_t;

// Classe base API do mouse
class MouseAPI
{
public:
    MouseAPI(void);
    void begin(void);
    void end(void);
    void click(uint8_t b = MOUSE_LEFT);
    void move(signed char x, signed char y, signed char wheel = 0);
    void press(uint8_t b = MOUSE_LEFT);
    void release(uint8_t b = MOUSE_LEFT);
    void releaseAll(void);
    bool isPressed(uint8_t b = MOUSE_LEFT);

    // Método para enviar o relatório
    virtual void SendReport(void *data, int length) = 0;

protected:
    uint8_t _buttons;
    void buttons(uint8_t b);
};