#ifndef HIDCUSTOM_H
#define HIDCUSTOM_H

#include <Arduino.h>
#include <hidboot.h>
#include "ImprovedMouse.h"

// Estrutura que armazena informações do mouse
struct CUSTOMMOUSEINFO
{
  uint8_t buttons;
  int8_t dX;
  int8_t dY;
  int8_t wheel;
};

// Parser de relatórios do mouse
class MouseRptParser : public MouseReportParser
{
  union
  {
    CUSTOMMOUSEINFO mouseInfo;
    uint8_t bInfo[sizeof(CUSTOMMOUSEINFO)];
  } prevState;

protected:
  void Parse(USBHID *hid, bool is_rpt_id, uint8_t len, uint8_t *buf);

  void OnMouseMove(CUSTOMMOUSEINFO *mi);
  void OnWheelMove(CUSTOMMOUSEINFO *mi);

  void OnLeftButtonUp(CUSTOMMOUSEINFO *mi);
  void OnLeftButtonDown(CUSTOMMOUSEINFO *mi);

  void OnRightButtonUp(CUSTOMMOUSEINFO *mi);
  void OnRightButtonDown(CUSTOMMOUSEINFO *mi);

  void OnMiddleButtonUp(CUSTOMMOUSEINFO *mi);
  void OnMiddleButtonDown(CUSTOMMOUSEINFO *mi);

  void OnBackButtonUp(CUSTOMMOUSEINFO *mi);
  void OnBackButtonDown(CUSTOMMOUSEINFO *mi);

  void OnForwardButtonUp(CUSTOMMOUSEINFO *mi);
  void OnForwardButtonDown(CUSTOMMOUSEINFO *mi);
};

#endif // HIDCUSTOM_H