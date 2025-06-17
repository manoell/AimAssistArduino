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
    // ============ LOOP ULTRA-AGRESSIVO PARA AIMBOT ============
    
    // EXECUÇÃO MÚLTIPLA POR CICLO - Fundamental para alta performance
    
    // Executar USB_USBTask múltiplas vezes por ciclo
    USB_USBTask();
    USB_USBTask();  // 2x para garantir processamento
    
    // Executar HID_Task múltiplas vezes por ciclo  
    HID_Task();
    HID_Task();     // 2x para processar mais comandos
    HID_Task();     // 3x para garantir throughput máximo
    
    // Terceira rodada para casos extremos
    USB_USBTask();
    HID_Task();
    
    // Contador simples (sem overhead)
    loop_count++;
    
    // Reset ocasional para evitar overflow
    if (loop_count == 0) {  // Overflow natural
        command_count = 0;
    }
    
    // ============ CRITICAL: SEM DELAYS! ============
    // Cada ciclo deve ser o mais rápido possível
    // NUNCA adicionar delays, sleeps ou prints aqui!
}

// ============ FUNÇÕES DE UTILIDADE ============

// Função para contabilizar comando processado (chamada pelo LogitechMouse.c)
void incrementCommandCounter() {
  command_count++;
}