#ifndef _LUFA_CONFIG_H_
#define _LUFA_CONFIG_H_

#include <Arduino.h>
#define F_USB F_CPU

#if (ARCH == ARCH_AVR8)
    // ============ OTIMIZAÇÕES EXTREMAS PARA AIMBOT ============
    
    // Performance crítica - desabilitar tudo que não é essencial
    #define DISABLE_TERMINAL_CODES       
    #define NO_CLASS_DRIVER_AUTOFLUSH    
    #define NO_STREAM_CALLBACKS          
    #define NO_LIMITED_CONTROLLER_CONNECT 
    #define NO_SOF_EVENTS                
    #define NO_DEVICE_REMOTE_WAKEUP      
    #define NO_DEVICE_SELF_POWER         
    #define NO_INTERNAL_SERIAL           
    
    // USB configuração ultra-agressiva para 1000Hz
    #define USE_STATIC_OPTIONS           (USB_DEVICE_OPT_FULLSPEED | USB_OPT_REG_ENABLED | USB_OPT_AUTO_PLL)
    #define USB_DEVICE_ONLY              
    #define USB_STREAM_TIMEOUT_MS        1      // 1ms timeout ultra-agressivo
    #define ORDERED_EP_CONFIG            
    #define USE_FLASH_DESCRIPTORS        
    #define FIXED_CONTROL_ENDPOINT_SIZE  64     
    #define FIXED_NUM_CONFIGURATIONS     1      
    #define INTERRUPT_CONTROL_ENDPOINT   
    
    // Otimizações específicas para ATmega32U4 (Leonardo)
    #if defined(__AVR_ATmega32U4__)
        #define OPTIMIZE_FOR_GAMING_LEONARDO
        #define MAX_ENDPOINTS                6
        #define ENDPOINT_MEMORY_OPTIMIZED
        #define MINIMIZE_RAM_USAGE
        #define OPTIMIZE_ENDPOINT_BANKS      1   // Single bank = menor latência
        
        // CRÍTICO: Configuração para 1000Hz polling
        #define USB_POLLING_INTERVAL_MS      1   // 1ms = 1000Hz polling
        #define HID_INTERRUPT_INTERVAL       1   // 1ms para HID
        
        #define DEVICE_STATE_AS_GPIOR        0   
        #define ENDPOINT_STATE_AS_GPIOR      1   
        #define USB_ENDPOINT_BUFFER_SIZE     64  
        #define F_CPU_EXACT                  16000000UL
    #endif
    
    // Configurações de latência crítica para aimbot
    #define ULTRA_LOW_LATENCY_MODE       
    #define GAMING_OPTIMIZATIONS         
    #define PRIORITIZE_MOUSE_REPORTS     
    #define MINIMIZE_USB_OVERHEAD        
    #define FAST_ENDPOINT_PROCESSING     
    #define HIGH_PRIORITY_USB_INTERRUPTS 
    #define MINIMIZE_INTERRUPT_LATENCY   
    #define ATOMIC_USB_OPERATIONS        
    
    // Buffer management otimizado
    #define USB_BUFFER_MANAGEMENT_OPTIMIZED
    #define MINIMIZE_BUFFER_COPYING      
    #define DIRECT_ENDPOINT_ACCESS       
    #define ZERO_COPY_OPERATIONS         
    
    // Prioridades de endpoint
    #define MOUSE_ENDPOINT_PRIORITY      0   // Máxima prioridade
    #define GENERIC_ENDPOINT_PRIORITY    1   
    #define KEYBOARD_ENDPOINT_PRIORITY   2   
    
    // Configurações de compilação para velocidade
    #define OPTIMIZE_FOR_SPEED           
    #define INLINE_SMALL_FUNCTIONS       
    #define UNROLL_SMALL_LOOPS          
    #define MINIMIZE_FUNCTION_CALLS      
    #define ALIGN_USB_STRUCTURES         
    #define PACK_USB_DESCRIPTORS         
    #define OPTIMIZE_MEMORY_LAYOUT       

#else
    #error Unsupported architecture for gaming optimization
#endif

// Configurações específicas para aimbot
#define AIMBOT_OPTIMIZED                 
#define ULTRA_LOW_LATENCY_GAMING         
#define MOUSE_MOVEMENT_PRIORITY          
#define MINIMIZE_USB_JITTER              
#define CONSISTENT_TIMING                
#define HIGH_FREQUENCY_UPDATES           

// Validação crítica
#if !defined(USB_POLLING_INTERVAL_MS) || USB_POLLING_INTERVAL_MS != 1
    #error "Polling rate deve ser 1ms (1000Hz) para aimbot!"
#endif

// Constantes de performance
#define TARGET_POLLING_RATE_HZ           1000    
#define TARGET_LATENCY_MS                1       
#define MAX_ACCEPTABLE_JITTER_US         100     
#define TARGET_CPU_USAGE_PERCENT         30      

#endif