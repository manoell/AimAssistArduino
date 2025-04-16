import os
import time
import sys
import keyboard
import win32api
import threading
import winsound
import pyautogui
from screen_capture import ScreenCapture
from mouse_controller import MouseController
from target_detector import TargetDetector
from config_manager import ConfigManager
from utils import print_banner, clear_console, print_status

class EnhancedAimAssist:
    """
    Classe principal que integra todos os componentes do sistema de aim assist.
    Versão simplificada com foco exclusivo na detecção por cor.
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
        
        print_status("INFO", "Carregando configurações...")
        
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
        
        # Inicializar detector de alvos simplificado (apenas cor)
        print_status("INFO", "Inicializando detector baseado em cor...")
        self.target_detector = TargetDetector(
            self.lower_color,
            self.upper_color,
            self.aim_fov,
            self.target_offset
        )
        
        print_status("INFO", f"Conectando ao Arduino na porta {self.com_port}...")
        
        # Inicializar controlador do mouse
        try:
            self.mouse = MouseController(self.com_port)
            print_status("SUCESSO", "Arduino conectado com sucesso!")
        except Exception as e:
            print_status("ERRO", f"Erro ao conectar ao Arduino: {e}")
            print_status("INFO", "Verifique se o Arduino está conectado e a porta COM está correta.")
            print_status("INFO", "Saindo em 5 segundos...")
            time.sleep(5)
            sys.exit(1)

        # Status de execução
        self.running = True
        self.aim_toggle = False
        self.debug_mode = False
        
        # Inicializar histórico para smooth aiming
        self.x_history = [0] * self.history_length
        self.y_history = [0] * self.history_length
        
        # Variáveis para mostrar estatísticas
        self.last_stats_time = time.time()
        self.stats_interval = 5.0  # Intervalo em segundos para mostrar estatísticas
        
        # Configurar hotkeys
        self.setup_hotkeys()
        
        print_status("SUCESSO", "Sistema inicializado com sucesso!")
        print(f"\nPressione '{self.aim_toggle_key}' para ativar/desativar o aim assist")
        print(f"Segure '{self.aim_key_name}' para utilizar o aim assist quando ativado")
        print(f"Pressione '{self.debug_key}' para ativar/desativar modo de depuração")
        print(f"Pressione '{self.reload_key}' para recarregar as configurações")
        print(f"Pressione '{self.exit_key}' para sair do programa")
    
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
        
        # Configurações de conexão
        self.com_port = self.config.get('Connection', 'com_port')
        
        # Configurações de teclas
        self.aim_key = int(self.config.get('Hotkeys', 'aim_key'), 16)
        self.aim_key_name = self.config.get('Hotkeys', 'aim_key_name')
        self.aim_toggle_key = self.config.get('Hotkeys', 'aim_toggle')
        self.reload_key = self.config.get('Hotkeys', 'reload')
        self.exit_key = self.config.get('Hotkeys', 'exit')
        self.debug_key = self.config.get('Hotkeys', 'debug')
    
    def setup_hotkeys(self):
        """
        Configura as teclas de atalho para controlar o programa
        """
        # Teclas para ativar/desativar funções
        keyboard.add_hotkey(self.aim_toggle_key, self.toggle_aim)
        keyboard.add_hotkey(self.debug_key, self.toggle_debug)
        
        # Teclas de sistema
        keyboard.add_hotkey(self.reload_key, self.reload_config)
        keyboard.add_hotkey(self.exit_key, self.exit_program)
    
    def toggle_aim(self):
        """
        Alterna o status do aim assist
        """
        self.aim_toggle = not self.aim_toggle
        self.play_sound(1000 if self.aim_toggle else 800, 100)
        status = "ATIVADO" if self.aim_toggle else "DESATIVADO"
        print(f"\rAim Assist: {status}", end="")
    
    def toggle_debug(self):
        """
        Alterna o modo de depuração
        """
        self.debug_mode = not self.debug_mode
        self.target_detector.set_debug_mode(self.debug_mode)
        status = "ATIVADO" if self.debug_mode else "DESATIVADO"
        print(f"\rModo de depuração: {status}", end="")
        self.play_sound(1200 if self.debug_mode else 600, 100)
    
    def reload_config(self):
        """
        Recarrega as configurações do arquivo settings.ini
        """
        self.config.reload()
        self.load_settings()
        
        # Atualizar configurações no detector
        self.target_detector.update_colors(self.lower_color, self.upper_color)
        
        self.play_sound(1500, 200)
        print("\nConfigurações recarregadas!")
    
    def exit_program(self):
        """
        Finaliza o programa
        """
        print("\nFinalizando programa...")
        self.running = False
        self.mouse.close()
        time.sleep(0.5)
        os._exit(0)
    
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
    
    def show_stats(self):
        """
        Mostra estatísticas de desempenho quando em modo debug
        """
        current_time = time.time()
        
        # Mostrar estatísticas a cada intervalo definido
        if current_time - self.last_stats_time >= self.stats_interval:
            self.last_stats_time = current_time
            
            # Obter FPS da captura de tela
            capture_fps = self.screen_capturer.get_fps()
            
            # Construir mensagem de estatísticas
            stats = f"\rModo: COR | FPS: {capture_fps:.1f} | "
            
            # Mostrar estado
            stats += f"Status: {'ATIVADO' if self.aim_toggle else 'DESATIVADO'}"
            
            print(stats)
    
    def run(self):
        """
        Loop principal do programa
        """
        try:
            while self.running:
                if self.aim_toggle and win32api.GetAsyncKeyState(self.aim_key) < 0:
                    # Capturar tela
                    screen = self.screen_capturer.get_screen()
                    
                    # Detectar alvo usando o detector por cor
                    target_info = self.target_detector.detect_target(screen)
                    
                    if target_info:
                        target_x, target_y, distance = target_info
                        
                        # Verificar se está dentro da distância máxima
                        if distance < self.max_distance:
                            # Calcular movimento baseado nos fatores de velocidade
                            move_x = int(target_x * self.x_speed)
                            move_y = int(target_y * self.y_speed)
                            
                            # Aplicar suavização
                            smooth_x, smooth_y = self.apply_smoothing(move_x, move_y)
                            
                            # Enviar comando para o mouse
                            self.mouse.move(smooth_x, smooth_y)
                    
                    # Mostrar estatísticas se modo de depuração estiver ativado
                    if self.debug_mode:
                        self.show_stats()
                
                # Pequena pausa para reduzir o uso de CPU
                time.sleep(0.005)
                
        except KeyboardInterrupt:
            self.exit_program()
        except Exception as e:
            print(f"\nErro: {e}")
            self.exit_program()


if __name__ == "__main__":
    # Iniciar o sistema simplificado
    aim_assist = EnhancedAimAssist()
    aim_assist.run()