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
  
  // ============ CONFIGURAR TIMERS PARA MÁXIMA PERFORMANCE ============
  
  // Timer 0 já é usado pelo Arduino core (delay/millis)
  // Timer 1: Configurar para operação de baixa latência (se necessário)
  // Timer 3: Reservar para uso futuro
  
  // OPCIONAL: Desabilitar recursos desnecessários para economizar ciclos
  // ADCSRA &= ~(1 << ADEN);  // Desabilitar ADC se não usado
  // ACSR |= (1 << ACD);      // Desabilitar Analog Comparator se não usado
  
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
  
  // ============ MONITORAMENTO DE PERFORMANCE (DEBUG) ============
  // Descomentar apenas para debug - remove para produção
  /*
  static uint32_t last_report_time = 0;
  uint32_t current_time = millis();
  
  if (current_time - last_report_time >= 5000) { // A cada 5 segundos
    uint32_t loops_per_second = loop_count / 5;
    uint32_t commands_per_second = command_count / 5;
    
    // Reset counters
    loop_count = 0;
    command_count = 0;
    last_report_time = current_time;
    
    // Output via Serial (apenas para debug)
    Serial.print("Loops/s: ");
    Serial.print(loops_per_second);
    Serial.print(" | Commands/s: ");
    Serial.println(commands_per_second);
  }
  */
}

// ============ FUNÇÕES DE UTILIDADE OTIMIZADAS ============

// Função para contabilizar comando processado (chamada pelo LogitechMouse.c)
void incrementCommandCounter() {
  command_count++;
}

// Função para LED debug (otimizada)
void debugBlink(uint8_t times) {
  for (uint8_t i = 0; i < times; i++) {
    digitalWrite(13, HIGH);
    delayMicroseconds(500); // Micro delay para não afetar performance
    digitalWrite(13, LOW);
    delayMicroseconds(500);
  }
}

// ============ FUNÇÕES AVANÇADAS (OPCIONAIS) ============

// Função para configurar Clock prescaler (se necessário)
void optimizeSystemClock() {
  // Garantir que estamos rodando na velocidade máxima
  clock_prescale_set(clock_div_1); // 16MHz full speed
}

// Função para configurar registradores USB para latência mínima
void optimizeUSBRegisters() {
  // Essas otimizações são handle pelo LUFA, mas podem ser customizadas aqui
  // se necessário para casos específicos
  
  // Exemplo: Configurar timeouts USB mais agressivos
  // USB_STREAM_TIMEOUT_MS definido no LUFAConfig.h
}

// ============ INTERRUPT SERVICE ROUTINES ============

// ISR personalizado para USB (se necessário)
// NOTA: LUFA já fornece ISRs otimizados, usar apenas se precisar de customização

/*
ISR(USB_GEN_vect) {
  // Custom USB interrupt handling
  // Chamar ISR do LUFA primeiro
  LUFA_USB_GENERAL_INTERRUPT_HANDLER();
  
  // Custom handling aqui (se necessário)
}
*/

// ============ CONFIGURAÇÕES ESPECÍFICAS DE HARDWARE ============

// Função para configurar pinos específicos do Leonardo (se necessário)
void configureLeornardoSpecific() {
  // Leonardo tem peculiaridades específicas que podem ser configuradas aqui
  
  // Configurar pinos não usados como INPUT_PULLUP para economizar energia
  for (uint8_t pin = 2; pin <= 12; pin++) {
    if (pin != 13) { // Exceto LED
      pinMode(pin, INPUT_PULLUP);
    }
  }
  
  // Configurar portas analógicas não usadas
  for (uint8_t pin = A0; pin <= A5; pin++) {
    pinMode(pin, INPUT_PULLUP);
  }
}

// ============ WATCHDOG CONFIGURATION (OPCIONAL) ============

// Configurar watchdog para reset automático em caso de hang
void setupWatchdog() {
  // Configurar watchdog para 2 segundos
  // NOTA: Usar apenas se necessário, pois o LUFA já gerencia resets USB
  
  /*
  cli();
  wdt_reset();
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR = (1<<WDIE) | (1<<WDE) | (1<<WDP2) | (1<<WDP1) | (1<<WDP0); // 2 seconds
  sei();
  */
}

/*
// Watchdog ISR (se habilitado)
ISR(WDT_vect) {
  // Watchdog timeout - fazer reset ou handling específico
  wdt_disable();
  // Opcionalmente fazer soft reset:
  // asm volatile ("  jmp 0");
}
*/