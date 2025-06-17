import os
import time
import sys
import random
import keyboard
import win32api
import threading
import winsound
import pyautogui
from screen_capture import ScreenCapture
from mouse_controller import MouseController
from target_detector import TargetDetector
from config_manager import ConfigManager
from utils import print_banner, clear_console

class EnhancedAimAssist:
    """
    Classe principal que integra todos os componentes do sistema de aim assist.
    Atualizada para usar Raw HID ultra-otimizado.
    """
    
    def __init__(self):
        """
        Inicializa o sistema de aim assist, carregando configurações e preparando componentes.
        """
        # Inicializar banner e console
        clear_console()
        print_banner()
        
        # Inicializar componentes
        self.config = ConfigManager('settings.ini')
        self.load_settings()
        
        # Humanização
        self.last_detection_time = 0
        self.base_reaction_time = 0.150  # 150ms tempo de reação humano base
        self.humanization_enabled = True  # Pode ser configurável
        
        print("Carregando configurações...")
        
        # Obter resolução da tela
        screen_size = pyautogui.size()
        self.center_x = screen_size.width // 2
        self.center_y = screen_size.height // 2
        
        # Inicializar captura de tela com base no FOV
        self.screen_capturer = ScreenCapture(
            self.center_x - self.aim_fov // 2,
            self.center_y - self.aim_fov // 2,
            self.aim_fov,
            self.aim_fov
        )
        
        # Inicializar detector de alvos
        self.target_detector = TargetDetector(
            self.lower_color,
            self.upper_color,
            self.aim_fov,
            self.target_offset
        )
        
        print(f"Conectando ao Arduino via Raw HID...")
        
        # Inicializar controlador do mouse (agora Raw HID)
        try:
            # NOTA: com_port é ignorado agora, mas mantido para compatibilidade
            self.mouse = MouseController(com_port=self.com_port)
            print("✅ Arduino conectado via Raw HID com sucesso!")
            
            # Mostrar estatísticas de conexão
            stats = self.mouse.get_performance_stats()
            print(f"   Modo de operação: {stats['current_timeout']}")
            print(f"   Latência mínima: {stats['min_latency_ms']:.1f}ms")
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao Arduino: {e}")
            print("Verifique se:")
            print("  1. Arduino está conectado via USB")
            print("  2. Firmware LUFA está carregado")
            print("  3. Dispositivo aparece como 'Logitech USB Receiver'")
            print("Saindo em 5 segundos...")
            time.sleep(5)
            sys.exit(1)

        # Status de execução
        self.running = True
        self.aim_toggle = False
        
        # Inicializar histórico para smooth aiming
        self.x_history = [0] * self.history_length
        self.y_history = [0] * self.history_length
        
        # Configurar hotkeys
        self.setup_hotkeys()
        
        print("\n✅ Sistema inicializado com sucesso!\n")
        print(f"🎯 Pressione '{self.aim_toggle_key}' para ativar/desativar")
        print(f"🎮 Segure '{self.aim_key_name}' para utilizar quando ativado")
        print(f"🔄 Pressione '{self.reload_key}' para recarregar as configurações")
        print(f"🚪 Pressione '{self.exit_key}' para sair do programa")
        print(f"📊 Use 'Ctrl+I' para ver estatísticas de performance\n")
        
        # Mostrar informações de performance
        self.show_performance_info()
    
    def load_settings(self):
        """
        Carrega todas as configurações do arquivo settings.ini
        """
        # Configurações de aim assist
        self.aim_fov = self.config.get_int('Aimbot', 'fov')
        self.x_speed = self.config.get_float('Aimbot', 'x_speed')
        self.y_speed = self.config.get_float('Aimbot', 'y_speed')
        # Carrega o offset e aplica um multiplicador para aumentar seu efeito
        raw_offset = self.config.get_float('Aimbot', 'target_offset')
        self.target_offset = raw_offset * 5.0  # Amplifica ainda mais o efeito do offset
        self.smoothing_factor = self.config.get_float('Aimbot', 'smoothing')
        self.max_distance = self.config.get_int('Aimbot', 'max_distance')
        self.history_length = self.config.get_int('Aimbot', 'history_length')
        
        # Configurações de cor para detecção
        self.lower_color = self.config.get_color('Color', 'lower_color')
        self.upper_color = self.config.get_color('Color', 'upper_color')
        
        # Configurações de conexão (mantido para compatibilidade)
        self.com_port = self.config.get('Connection', 'com_port')
        
        # Configurações de teclas
        self.aim_key = int(self.config.get('Hotkeys', 'aim_key'), 16)
        self.aim_key_name = self.config.get('Hotkeys', 'aim_key_name')
        self.aim_toggle_key = self.config.get('Hotkeys', 'aim_toggle')
        self.reload_key = self.config.get('Hotkeys', 'reload')
        self.exit_key = self.config.get('Hotkeys', 'exit')
        
        # Humanização
        self.humanization_config = self.config.get_humanization_config()
        
        # Aplicar configurações de humanização às variáveis da classe
        self.humanization_enabled = self.humanization_config['enabled']
        self.base_reaction_time = self.humanization_config['base_reaction_time']
        self.reaction_time_variance = self.humanization_config['reaction_time_variance']
        
        # Log das configurações de humanização (opcional)
        if self.humanization_enabled:
            print(f"🤖 Humanização ativada:")
            print(f"   Tempo de reação: {self.base_reaction_time*1000:.0f}ms (±{self.reaction_time_variance*1000:.0f}ms)")
            print(f"   Jitter natural: {'✅' if self.humanization_config['jitter_enabled'] else '❌'}")
            print(f"   Variação de timing: {'✅' if self.humanization_config['timing_variance_enabled'] else '❌'}")
    
    def setup_hotkeys(self):
        """
        Configura as teclas de atalho para controlar o programa
        """
        # Teclas para ativar/desativar funções
        keyboard.add_hotkey(self.aim_toggle_key, self.toggle_aim)
        
        # Teclas de sistema
        keyboard.add_hotkey(self.reload_key, self.reload_config)
        keyboard.add_hotkey(self.exit_key, self.exit_program)
        
        # Tecla para mostrar estatísticas (nova)
        keyboard.add_hotkey('ctrl+i', self.show_performance_info)
    
    def toggle_aim(self):
        """
        Alterna o status do aim assist
        """
        self.aim_toggle = not self.aim_toggle
        self.play_sound(1000 if self.aim_toggle else 800, 100)
        status = "✅ ATIVO" if self.aim_toggle else "🛑 INATIVO"
        print(f"\r🎯 Aim Assist: {status}", end="", flush=True)
    
    def reload_config(self):
        """
        Recarrega as configurações do arquivo settings.ini
        """
        self.config.reload()
        self.load_settings()
        self.play_sound(1500, 200)
        print("\n🔄 Configurações recarregadas!")
        self.show_performance_info()
    
    def exit_program(self):
        """
        Finaliza o programa
        """
        print("\n🚪 Finalizando programa...")
        self.running = False
        
        # Mostrar estatísticas finais
        if hasattr(self, 'mouse') and self.mouse:
            stats = self.mouse.get_performance_stats()
            print(f"📊 Estatísticas finais:")
            print(f"   Comandos enviados: {stats['commands_sent']}")
            print(f"   Taxa de sucesso: {stats['success_rate']*100:.1f}%")
            print(f"   Comandos de aimbot: {stats['aimbot_commands']}")
            print(f"   Latência média: {stats['avg_latency_ms']:.1f}ms")
            
            self.mouse.close()
        
        time.sleep(0.5)
        os._exit(0)
    
    def show_performance_info(self):
        """
        Mostra informações de performance do sistema
        """
        if hasattr(self, 'mouse') and self.mouse:
            stats = self.mouse.get_performance_stats()
            print(f"\n📊 PERFORMANCE INFO:")
            print(f"   🎯 Modo: {stats['current_timeout'].upper()}")
            print(f"   ⚡ Comandos enviados: {stats['commands_sent']}")
            print(f"   📈 Taxa de sucesso: {stats['success_rate']*100:.1f}%")
            print(f"   🎮 Comandos aimbot: {stats['aimbot_commands']}")
            print(f"   ⏱️ Latência: {stats['avg_latency_ms']:.1f}ms (min: {stats['min_latency_ms']:.1f}ms)")
            print(f"   📋 Filas: Normal({stats['queue_sizes']['normal']}) Priority({stats['queue_sizes']['priority']})")
            print(f"   🔗 Conectado: {'✅' if self.mouse.is_connected() else '❌'}")
        else:
            print("❌ MouseController não inicializado")
    
    def play_sound(self, frequency, duration):
        """
        Reproduz um som de notificação
        
        Args:
            frequency (int): Frequência do som em Hz
            duration (int): Duração do som em ms
        """
        try:
            winsound.Beep(frequency, duration)
        except:
            pass
    
    def apply_smoothing(self, target_x, target_y):
        """
        Aplica suavização aos movimentos do mouse baseado no histórico
        
        Args:
            target_x (float): Movimento alvo no eixo X
            target_y (float): Movimento alvo no eixo Y
            
        Returns:
            tuple: Movimento suavizado (x, y)
        """
        # Adicionar ao histórico
        self.x_history.append(target_x)
        self.y_history.append(target_y)
        
        # Remover valores antigos
        self.x_history.pop(0)
        self.y_history.pop(0)
        
        # Aplicar pesos diferentes para cada posição no histórico (mais recentes = mais importantes)
        x_smoothed = 0
        y_smoothed = 0
        total_weight = 0
        
        for i in range(self.history_length):
            # Peso exponencial: posições mais recentes têm muito mais peso
            weight = (i + 1) ** 2
            x_smoothed += self.x_history[i] * weight
            y_smoothed += self.y_history[i] * weight
            total_weight += weight
        
        # Normalizar pelos pesos
        x_smoothed /= total_weight
        y_smoothed /= total_weight
        
        # Interpolar entre o valor suavizado e o valor bruto usando o fator de suavização
        final_x = target_x * (1 - self.smoothing_factor) + x_smoothed * self.smoothing_factor
        final_y = target_y * (1 - self.smoothing_factor) + y_smoothed * self.smoothing_factor
        
        return int(final_x), int(final_y)
    
    def run(self):
        """
        Loop principal do programa com humanização anti-detecção
        """
        try:
            loop_count = 0
            last_performance_check = time.time()
            
            while self.running:
                if self.aim_toggle and win32api.GetAsyncKeyState(self.aim_key) < 0:
                    # Marcar tempo de início da detecção
                    detection_start = time.time()
                    
                    # Capturar tela
                    screen = self.screen_capturer.get_screen()
                    
                    # Detectar alvo
                    target_info = self.target_detector.detect_target(screen)
                    
                    if target_info:
                        target_x, target_y, distance = target_info
                        
                        # Verificar se está dentro da distância máxima
                        if distance < self.max_distance:
                            # *** HUMANIZAÇÃO 3: Tempo de Reação Realista ***
                            detection_time = time.time() - detection_start
                            if self.humanization_enabled and detection_time < self.base_reaction_time:
                                # Adicionar delay para simular tempo de reação humano
                                human_delay = self.base_reaction_time - detection_time
                                # Adicionar variação aleatória no delay
                                human_delay += random.uniform(-0.02, 0.05)  # ±20ms a +50ms
                                if human_delay > 0:
                                    time.sleep(human_delay)
                            
                            # Calcular movimento baseado nos fatores de velocidade
                            move_x_base = target_x * self.x_speed
                            move_y_base = target_y * self.y_speed
                            
                            # *** HUMANIZAÇÃO 2: Jitter Natural ***
                            if self.humanization_enabled:
                                # Simular tremor humano (mais sutil para aimbot)
                                jitter_x = random.uniform(-0.5, 0.5)  # Ajustado para aimbot
                                jitter_y = random.uniform(-0.5, 0.5)
                                move_x_base += jitter_x
                                move_y_base += jitter_y
                            
                            # Converter para inteiros
                            move_x = int(move_x_base)
                            move_y = int(move_y_base)
                            
                            # Aplicar suavização (já existente)
                            smooth_x, smooth_y = self.apply_smoothing(move_x, move_y)
                            
                            # *** HUMANIZAÇÃO 1: Timing Variável ***
                            if self.humanization_enabled:
                                # Adicionar variação no timing de envio
                                send_delay = random.uniform(-0.001, 0.003)  # -1ms a +3ms
                                if send_delay > 0:
                                    time.sleep(send_delay)
                            
                            # Enviar comando para o mouse com ALTA PRIORIDADE (aimbot)
                            self.mouse.move(smooth_x, smooth_y, priority=True)
                            
                            # Atualizar tempo da última detecção
                            self.last_detection_time = time.time()
                
                # Contador de performance
                loop_count += 1
                
                # Mostrar info de performance ocasionalmente
                current_time = time.time()
                if current_time - last_performance_check >= 30.0:  # A cada 30 segundos
                    if self.aim_toggle:
                        print(f"\n🔄 Sistema rodando... (loops: {loop_count})")
                        self.show_performance_info()
                    last_performance_check = current_time
                    loop_count = 0
                
                # *** HUMANIZAÇÃO 1: Delay Variável no Loop ***
                if self.humanization_enabled:
                    # Pequena pausa com variação para reduzir o uso de CPU
                    base_delay = 0.005
                    variable_delay = base_delay + random.uniform(-0.001, 0.002)  # ±1ms a +2ms
                    time.sleep(max(0.001, variable_delay))  # Mínimo 1ms
                else:
                    # Delay fixo original
                    time.sleep(0.005)
                
        except KeyboardInterrupt:
            self.exit_program()
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            self.exit_program()


if __name__ == "__main__":
    aim_assist = EnhancedAimAssist()
    aim_assist.run()
