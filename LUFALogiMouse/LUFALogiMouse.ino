#include "LUFAConfig.h"

// Redefinir USB_HOST_SERIAL como Serial1 antes de incluir bibliotecas USB Host Shield
#define USB_HOST_SERIAL Serial1
// Desabilitar completamente o debugging para maior estabilidade
#define ENABLE_UHS_DEBUGGING 0

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

// Função para processar tarefas do USB Host (definida externamente)
extern "C" void ProcessUSBHost(void);

void setup() {
  // ============ INICIALIZAÇÃO OTIMIZADA ============
  
  // Inicializar Serial1 para debug (opcional)
  Serial1.begin(115200);
  
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
  
  // Debug message (opcional)
  Serial1.println(F("LUFALogiMouse inicializado"));
}

void loop() {
  // ============ LOOP PRINCIPAL ULTRA-OTIMIZADO ============
  
  // PRIORIDADE 1: USB Task - DEVE ser chamado o mais frequente possível
  USB_USBTask();
  
  // PRIORIDADE 2: HID Task - Processar endpoints imediatamente
  HID_Task();
  
  // PRIORIDADE 3: USB Host Task - Processar USB Host Shield
  ProcessUSBHost();
  
  // PRIORIDADE 4: Contador de performance (opcional, só para debug)
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
}

// ============ FUNÇÕES DE UTILIDADE OTIMIZADAS ============

// Função para contabilizar comando processado
void incrementCommandCounter() {
  command_count++;
}