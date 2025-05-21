#include "LUFAConfig.h"
#include <LUFA.h>
#include "LogitechMouse.h"
#include <inttypes.h>

// Variáveis globais para comunicação
volatile bool newCommandReceived = false;
volatile bool processingCommand = false;

// Variáveis para estado do mouse - int8_t (Boot Protocol)
int8_t mouse_x = 0;
int8_t mouse_y = 0;
uint8_t mouse_buttons = 0;
int8_t mouse_wheel = 0;

// OTIMIZAÇÃO: Contador de performance
volatile uint32_t loop_count = 0;
volatile uint32_t command_count = 0;

void setup() {
  // ============ INICIALIZAÇÃO OTIMIZADA ============
  
  // Initialize hardware PRIMEIRO E MAIS IMPORTANTE
  SetupHardware();
  
  // Habilitar interrupções IMEDIATAMENTE após setup
  GlobalInterruptEnable();
  
  // Initialize mouse state
  mouse_x = 0;
  mouse_y = 0;
  mouse_buttons = 0;
  mouse_wheel = 0;
  newCommandReceived = false;
  processingCommand = false;
  
  // Reset counters
  loop_count = 0;
  command_count = 0;
  
  // ============ INDICAÇÃO DE PRONTO ============
  // Piscar LED rapidamente para indicar que setup terminou
  pinMode(13, OUTPUT);
  for (int i = 0; i < 5; i++) {
    digitalWrite(13, HIGH);
    delay(50);
    digitalWrite(13, LOW);
    delay(50);
  }
}

void loop() {
  // ============ LOOP PRINCIPAL ULTRA-OTIMIZADO ============
  
  // PRIORIDADE 1: USB Task - DEVE ser chamado o mais frequente possível
  USB_USBTask();
  
  // PRIORIDADE 2: HID Task - Processar endpoints imediatamente
  HID_Task();
  
  // PRIORIDADE 3: Contador de performance (opcional, só para debug)
  loop_count++;
  
  // ============ OTIMIZAÇÕES CRÍTICAS ============
  
  // SEM DELAYS - NUNCA ADICIONAR DELAYS AQUI!
  // SEM PRINTS - Prints causam latência!
  // SEM OPERAÇÕES BLOQUEANTES - Manter o loop 100% non-blocking
  
  // OPCIONAL: Reset contadores para evitar overflow (a cada ~1 hora)
  if (loop_count >= 0xFFFFF0) {
    loop_count = 0;
    command_count = 0;
  }
  
  // Não colocar nada mais aqui! USB_USBTask e HID_Task são o suficiente!
}

// ============ FUNÇÕES DE UTILIDADE ============

// Função para contabilizar comando processado (chamada pelo LogitechMouse.c)
void incrementCommandCounter() {
  command_count++;
}