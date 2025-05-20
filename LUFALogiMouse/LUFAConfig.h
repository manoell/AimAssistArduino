#ifndef _LUFA_CONFIG_H_
#define _LUFA_CONFIG_H_

#include <Arduino.h>
#define F_USB F_CPU

#if (ARCH == ARCH_AVR8)
    // ============ CONFIGURAÇÕES DE PERFORMANCE ============
    
    // Non-USB Related Configuration Tokens
    #define DISABLE_TERMINAL_CODES    // Economizar espaço e ciclos

    // USB Class Driver Related Tokens
    #define NO_CLASS_DRIVER_AUTOFLUSH   // Controle manual do flush para otimização
    
    // ============ CONFIGURAÇÕES USB OTIMIZADAS ============
    
    // General USB Driver Related Tokens
    #define ORDERED_EP_CONFIG            // Configuração de endpoints em ordem
    #define USE_STATIC_OPTIONS           (USB_DEVICE_OPT_FULLSPEED | USB_OPT_REG_ENABLED | USB_OPT_AUTO_PLL)
    #define USB_DEVICE_ONLY              // Apenas device mode
    #define USB_STREAM_TIMEOUT_MS        50   // Timeout agressivo para latência mínima
    #define NO_LIMITED_CONTROLLER_CONNECT
    #define NO_SOF_EVENTS                // Desabilitar Start of Frame events para economia

    // ============ CONFIGURAÇÕES DE DEVICE MODE ============
    
    // USB Device Mode Driver Related Tokens
    #define USE_FLASH_DESCRIPTORS        // Descriptors na Flash (economia de RAM)
    #define NO_INTERNAL_SERIAL           // Desabilitar serial interno se não usado
    #define FIXED_CONTROL_ENDPOINT_SIZE  64   // Endpoint de controle fixo
    #define FIXED_NUM_CONFIGURATIONS     1    // Apenas 1 configuração
    #define INTERRUPT_CONTROL_ENDPOINT   // Controle por interrupt
    #define NO_DEVICE_REMOTE_WAKEUP      // Desabilitar remote wakeup
    #define NO_DEVICE_SELF_POWER         // Device não é self-powered

    // ============ OTIMIZAÇÕES ESPECÍFICAS ============
    
    // Configurações específicas para latência mínima
    #define FAST_STREAM_TRANSFERS        // Transferências rápidas (se disponível na versão LUFA)
    #define NO_STREAM_CALLBACKS          // Sem callbacks em streams
    
    // Configurações de memória otimizadas
    #define DEVICE_STATE_AS_GPIOR        0    // Usar GPIOR para device state
    
    // ============ CONFIGURAÇÕES DE DEBUG ============
    
    // Descomentar apenas para debug (aumenta latência!)
    // #define DEBUG_USB_COMMUNICATIONS
    // #define ENABLE_TELEMETRY
    
    // ============ CONFIGURAÇÕES AVR8 ESPECÍFICAS ============
    
    // Otimizações específicas para ATmega32U4 (Arduino Leonardo)
    #if defined(__AVR_ATmega32U4__)
        // Leonardo tem 2.5KB de RAM - otimizar uso
        #define OPTIMIZE_FOR_LEONARDO
        
        // Configurar endpoints de forma otimizada para o Leonardo
        // Leonardo suporta até 6 endpoints + controle
        #define MAX_ENDPOINTS                6
        
        // Configuração de memória de endpoint otimizada
        // Control: 64 bytes, Mouse: 64 bytes, Keyboard: 64 bytes, Generic: 128 bytes
        #define ENDPOINT_MEMORY_OPTIMIZED
    #endif

#elif (ARCH == ARCH_XMEGA)
    // ============ CONFIGURAÇÕES XMEGA ============
    
    // Non-USB Related Configuration Tokens
    #define DISABLE_TERMINAL_CODES

    // USB Class Driver Related Tokens  
    #define NO_CLASS_DRIVER_AUTOFLUSH

    // General USB Driver Related Tokens
    #define USE_STATIC_OPTIONS               (USB_DEVICE_OPT_FULLSPEED | USB_OPT_RC32MCLKSRC | USB_OPT_BUSEVENT_PRIHIGH)
    #define USB_STREAM_TIMEOUT_MS            50
    #define NO_LIMITED_CONTROLLER_CONNECT
    #define NO_SOF_EVENTS

    // USB Device Mode Driver Related Tokens
    #define USE_FLASH_DESCRIPTORS
    #define NO_INTERNAL_SERIAL
    #define FIXED_CONTROL_ENDPOINT_SIZE      64
    #define FIXED_NUM_CONFIGURATIONS         1
    #define MAX_ENDPOINT_INDEX               3
    #define NO_DEVICE_REMOTE_WAKEUP
    #define NO_DEVICE_SELF_POWER

#else
    #error Unsupported architecture for this LUFA configuration file.
#endif

// ============ CONFIGURAÇÕES CUSTOMIZADAS PARA AIMBOT ============

// Configurações específicas para aplicação de aimbot
#define AIMBOT_OPTIMIZED                 // Flag para identificar build otimizado

// Configurações de latência crítica
#define ULTRA_LOW_LATENCY_MODE           // Ativa todas as otimizações de latência
#define PRIORITIZE_MOUSE_ENDPOINT        // Prioridade máxima para endpoint do mouse

// Configurações de segurança (anti-detection)
#define STEALTH_MODE                     // Ativa recursos de stealth
#define RANDOMIZE_TIMING                 // Randomizar timing para evitar detecção

#endif