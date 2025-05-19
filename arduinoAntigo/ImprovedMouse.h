#ifndef IMPROVED_MOUSE_H
#define IMPROVED_MOUSE_H

#include <Arduino.h>
#include <HID.h>
#include "MouseAPI.h"

// Definições do dispositivo Logitech G502 X PLUS
#define LOGITECH_VID 0x046D
#define G502X_PLUS_PID 0xC095
#define G502X_DEVICE_VERSION 0x2700

class Mouse_ : public MouseAPI
{
public:
    Mouse_(void);

protected: 
    virtual void SendReport(void* data, int length) override;
};
extern Mouse_ Mouse;

#endif // IMPROVED_MOUSE_H