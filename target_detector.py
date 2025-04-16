import cv2
import numpy as np
import time

class TargetDetector:
    """
    Classe responsável por detectar alvos na tela baseado na cor.
    Implementa técnicas avançadas de processamento de imagem para detecção precisa.
    """
    
    def __init__(self, lower_color, upper_color, fov, target_offset=0):
        """
        Inicializa o detector de alvos.
        
        Args:
            lower_color (numpy.ndarray): Limite inferior para detecção de cor (HSV)
            upper_color (numpy.ndarray): Limite superior para detecção de cor (HSV)
            fov (int): Campo de visão (diâmetro)
            target_offset (float): Deslocamento vertical para mirar em pontos específicos (como cabeça)
        """
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.fov = fov
        self.target_offset = target_offset
        self.center = fov // 2
        
        # Kernel para operações morfológicas
        self.kernel = np.ones((3, 3), np.uint8)
        
        # Variáveis para debug e otimização
        self.last_detection_time = 0
        self.debug_mode = False
    
    def detect_target(self, screen):
        """
        Detecta o alvo mais adequado na tela capturada.
        
        Args:
            screen (numpy.ndarray): Imagem capturada da tela
            
        Returns:
            tuple: (diff_x, diff_y, distance) se um alvo for encontrado, None caso contrário
                  diff_x: diferença no eixo X do centro
                  diff_y: diferença no eixo Y do centro
                  distance: distância do alvo ao centro
        """
        # Converter para HSV
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        
        # Criar máscara de cor
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Aplicar operações morfológicas para melhorar a detecção
        dilated = cv2.dilate(mask, self.kernel, iterations=3)
        opening = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, self.kernel, iterations=1)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Se nenhum contorno for encontrado, retornar None
        if not contours:
            return None
        
        # Filtrar contornos muito pequenos (ruído)
        valid_contours = [c for c in contours if cv2.contourArea(c) > 30]
        
        if not valid_contours:
            return None
        
        # Encontrar o melhor alvo baseado na proximidade ao centro e tamanho
        best_target = None
        min_distance = float('inf')
        
        for contour in valid_contours:
            # Obter retângulo delimitador
            x, y, w, h = cv2.boundingRect(contour)
            
            # Obter centro do contorno
            cx = x + w // 2
            cy = y + h // 2
            
            # Começamos mirando bem no topo do contorno (região da cabeça)
            vertical_position = y + int(h * 0.05)  # 5% do topo do contorno
            
            # Aplicar offset personalizado
            # Valores positivos sempre movem a mira para BAIXO (em direção ao corpo)
            # Valores negativos movem para CIMA (acima da cabeça)
            target_y = vertical_position + int(self.target_offset)
            
            # Calcular distância ao centro
            distance = np.sqrt((cx - self.center) ** 2 + (target_y - self.center) ** 2)
            
            # Calcular área do contorno como fator de importância
            area = cv2.contourArea(contour)
            
            # Pontuação combinada (distância menor e área maior é melhor)
            # Usar logaritmo da área para evitar que alvos enormes dominem completamente
            score = distance / (np.log(area + 10) + 1)
            
            if score < min_distance:
                min_distance = score
                best_target = (cx, target_y, distance)
        
        if best_target:
            cx, cy, distance = best_target
            # Calcular diferença do centro
            diff_x = cx - self.center
            diff_y = cy - self.center
            
            # Registrar tempo da última detecção
            self.last_detection_time = time.time()
            
            # Debug
            if self.debug_mode and time.time() % 3 < 0.1:  # Salvar debug a cada ~3 segundos
                self._save_debug_image(screen, hsv, mask, closing, cx, cy)
            
            return (diff_x, diff_y, distance)
        
        return None
    
    def update_colors(self, lower_color, upper_color):
        """
        Atualiza os limites de cor para detecção.
        
        Args:
            lower_color (numpy.ndarray): Novo limite inferior
            upper_color (numpy.ndarray): Novo limite superior
        """
        self.lower_color = lower_color
        self.upper_color = upper_color
    
    def set_debug_mode(self, enabled):
        """
        Ativa ou desativa o modo de debug.
        
        Args:
            enabled (bool): True para ativar, False para desativar
        """
        self.debug_mode = enabled
    
    def _save_debug_image(self, original, hsv, mask, processed, target_x, target_y):
        """
        Salva imagens de debug para análise de detecção.
        
        Args:
            original (numpy.ndarray): Imagem original
            hsv (numpy.ndarray): Imagem HSV
            mask (numpy.ndarray): Máscara inicial
            processed (numpy.ndarray): Máscara processada
            target_x (int): Coordenada X do alvo
            target_y (int): Coordenada Y do alvo
        """
        try:
            # Criar pasta de debug se não existir
            import os
            os.makedirs("debug", exist_ok=True)
            
            # Timestamp
            timestamp = int(time.time())
            
            # Marcar o alvo na imagem original
            debug_img = original.copy()
            cv2.circle(debug_img, (target_x, target_y), 5, (0, 255, 0), -1)
            cv2.circle(debug_img, (self.center, self.center), 3, (0, 0, 255), -1)
            
            # Salvar imagens
            cv2.imwrite(f"debug/original_{timestamp}.png", debug_img)
            
            # Converter máscara para imagem colorida para visualização
            mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            processed_colored = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            
            # Combinar imagens para visualização
            h, w = original.shape[:2]
            combined = np.zeros((h, w * 3, 3), dtype=np.uint8)
            combined[:, :w] = debug_img
            combined[:, w:w*2] = mask_colored
            combined[:, w*2:] = processed_colored
            
            cv2.imwrite(f"debug/detection_{timestamp}.png", combined)
        except Exception as e:
            print(f"Erro ao salvar imagem de debug: {e}")