/*
 * ImprovedMouse.cpp - Logitech G502 X PLUS Spoof Implementation
 * Based on Lib5 with custom device descriptors
 */

#include <Arduino.h>
#include "ImprovedMouse.h"

// HID Mouse descriptor que imita exatamente o G502 X PLUS
static const uint8_t _hidMultiReportDescriptorMouse[] PROGMEM = {
    // Interface 0: HID Boot Mouse
    0x05, 0x01,               // USAGE_PAGE (Generic Desktop)
    0x09, 0x02,               // USAGE (Mouse)
    0xa1, 0x01,               // COLLECTION (Application)
    0x09, 0x01,               //   USAGE (Pointer)
    0xa1, 0x00,               //   COLLECTION (Physical)
    0x85, 0x01,               //     REPORT_ID (1)
    0x05, 0x09,               //     USAGE_PAGE (Button)
    0x19, 0x01,               //     USAGE_MINIMUM (Button 1)
    0x29, 0x05,               //     USAGE_MAXIMUM (Button 5)
    0x15, 0x00,               //     LOGICAL_MINIMUM (0)
    0x25, 0x01,               //     LOGICAL_MAXIMUM (1)
    0x95, 0x05,               //     REPORT_COUNT (5)
    0x75, 0x01,               //     REPORT_SIZE (1)
    0x81, 0x02,               //     INPUT (Data,Var,Abs)
    0x95, 0x01,               //     REPORT_COUNT (1)
    0x75, 0x03,               //     REPORT_SIZE (3)
    0x81, 0x03,               //     INPUT (Cnst,Var,Abs)
    0x05, 0x01,               //     USAGE_PAGE (Generic Desktop)
    0x09, 0x30,               //     USAGE (X)
    0x09, 0x31,               //     USAGE (Y)
    0x09, 0x38,               //     USAGE (Wheel)
    0x15, 0x81,               //     LOGICAL_MINIMUM (-127)
    0x25, 0x7f,               //     LOGICAL_MAXIMUM (127)
    0x75, 0x08,               //     REPORT_SIZE (8)
    0x95, 0x03,               //     REPORT_COUNT (3)
    0x81, 0x06,               //     INPUT (Data,Var,Rel)
    0xc0,                     //   END_COLLECTION
    0xc0,                     // END_COLLECTION
};

Mouse_::Mouse_(void)
{
    static HIDSubDescriptor node(_hidMultiReportDescriptorMouse, sizeof(_hidMultiReportDescriptorMouse));
    HID().AppendDescriptor(&node);
}

void Mouse_::SendReport(void *data, int length)
{
    // Report ID 1 para mouse
    HID().SendReport(HID_REPORTID_MOUSE, data, length);
}

Mouse_ Mouse;