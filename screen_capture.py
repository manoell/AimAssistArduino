import numpy as np
import threading
import time
from mss import mss

class ScreenCapture:
    """
    Classe responsável por capturar a região da tela de forma eficiente.
    Utiliza threading para otimizar a velocidade de captura.
    """
    
    def __init__(self, x, y, width, height):
        """
        Inicializa o capturador de tela.
        
        Args:
            x (int): Posição X do início da região
            y (int): Posição Y do início da região
            width (int): Largura da região
            height (int): Altura da região
        """
        self.monitor = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }
        
        # Variáveis para captura contínua
        self.screen = np.zeros((height, width, 4), np.uint8)
        self.lock = threading.Lock()
        self.running = True
        
        # Estatísticas de desempenho
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        
        # Iniciar thread de captura
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _capture_loop(self):
        """
        Loop contínuo de captura de tela em thread separada.
        """
        with mss() as sct:
            while self.running:
                with self.lock:
                    # Capturar tela e converter para array numpy
                    screenshot = sct.grab(self.monitor)
                    self.screen = np.array(screenshot)
                
                # Atualizar estatísticas de FPS
                self._update_fps()
                
                # Pequena pausa para evitar uso excessivo de CPU
                time.sleep(0.001)
    
    def _update_fps(self):
        """
        Atualiza as estatísticas de FPS da captura.
        """
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        
        # Atualizar FPS a cada segundo
        if elapsed_time >= 1.0:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
    
    def get_screen(self):
        """
        Retorna a captura mais recente da tela.
        
        Returns:
            numpy.ndarray: Array numpy contendo a imagem capturada
        """
        with self.lock:
            # Retorna uma cópia para evitar alterações externas
            return self.screen.copy()
    
    def get_fps(self):
        """
        Retorna o FPS atual da captura.
        
        Returns:
            float: Frames por segundo
        """
        return self.fps
    
    def stop(self):
        """
        Para o loop de captura.
        """
        self.running = False
        if self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
