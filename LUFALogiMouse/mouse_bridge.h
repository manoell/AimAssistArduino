#ifndef MOUSE_BRIDGE_H
#define MOUSE_BRIDGE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Funções de inicialização
uint8_t initializeUSBHost(void);  // Retorna 0 se sucesso, diferente de 0 se erro
void processUSBHostTasks(void);

// Funções para obter estados do mouse
int8_t getLastMouseX(void);
int8_t getLastMouseY(void);
uint8_t getLastMouseButtons(void);
int8_t getLastMouseWheel(void);

// Flag para indicar novos dados
uint8_t hasNewMouseData(void);
void clearNewMouseDataFlag(void);

// Funções avançadas para gestão de interrupções
void suspendUSBHostTasks(void);
void resumeUSBHostTasks(void);
bool isUSBHostBusy(void);

#ifdef __cplusplus
}
#endif

#endif // MOUSE_BRIDGE_H