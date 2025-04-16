import cv2
import numpy as np
import time
import os

class TargetDetector:
    """
    Classe responsável por detectar alvos na tela usando detecção por cor.
    Versão simplificada focada exclusivamente em detecção baseada em HSV.
    """
    
    def __init__(self, lower_color, upper_color, fov, target_offset=0):
        """
        Inicializa o detector de alvos otimizado para detecção por cor.
        
        Args:
            lower_color (numpy.ndarray): Limite inferior para detecção de cor (HSV)
            upper_color (numpy.ndarray): Limite superior para detecção de cor (HSV)
            fov (int): Campo de visão (diâmetro)
            target_offset (float): Deslocamento vertical para mira (valores positivos = mais baixo)
        """
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.fov = fov
        self.target_offset = target_offset
        self.center = fov // 2
        
        # Kernel para operações morfológicas
        self.kernel = np.ones((3, 3), np.uint8)
        
        # Variáveis para debug e otimização
        self.debug_mode = False
        self.debug_counter = 0
        
        # Estado do alvo e histórico para suavização de movimento
        self.has_target = False
        self.last_target_x = 0
        self.last_target_y = 0
        
        # Histórico para média ponderada
        self.movement_history = []
        self.max_history = 10
        
        # Fator de suavização para movimento natural
        self.smoothing = 0.9
    
    def detect_target(self, screen):
        """
        Detecta o alvo usando detecção por cor HSV e aplica suavização.
        
        Args:
            screen (numpy.ndarray): Imagem capturada da tela
            
        Returns:
            tuple: (diff_x, diff_y, distance) se um alvo for encontrado, None caso contrário
        """
        # IMPORTANTE: Converter BGRA para BGR (remover canal alpha)
        if screen.shape[2] == 4:  # Se a imagem tem 4 canais (BGRA)
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        
        # Detectar alvo usando cores
        target = self._get_color_target(screen)
        
        # Processar o movimento usando o mesmo pipeline de processamento
        return self._process_target_movement(target)
    
    def _process_target_movement(self, target):
        """
        Processa o alvo detectado para produzir uma movimentação suave.
        
        Args:
            target: Tuple (x, y, distance) ou None
            
        Returns:
            tuple: (diff_x, diff_y, distance) processado e suavizado, ou None
        """
        # Se não temos alvo agora
        if target is None:
            # Se tínhamos um alvo antes, desacelerar gradualmente
            if self.has_target:
                # Reduzir movimento anterior em 20% a cada frame
                self.last_target_x *= 0.8
                self.last_target_y *= 0.8
                
                # Se o movimento se tornou muito pequeno, considere que não há alvo
                if abs(self.last_target_x) < 0.5 and abs(self.last_target_y) < 0.5:
                    self.has_target = False
                    self.movement_history = []
                    return None
                
                # Caso contrário, retorne o movimento residual
                return (self.last_target_x, self.last_target_y, 999)
            return None
        
        # Temos um alvo - extrair coordenadas
        x, y, distance = target
        
        # Calcular diferença em relação ao centro
        diff_x = x - self.center
        diff_y = y - self.center
        
        # Adicionar ao histórico de movimento (usado para média ponderada)
        self.movement_history.append((diff_x, diff_y))
        if len(self.movement_history) > self.max_history:
            self.movement_history.pop(0)
        
        # Calcular média ponderada (mais peso para movimentos recentes)
        weighted_x = 0
        weighted_y = 0
        total_weight = 0
        
        for i, (hist_x, hist_y) in enumerate(self.movement_history):
            # Peso exponencial - realça valores recentes
            weight = (i + 1) ** 2
            weighted_x += hist_x * weight
            weighted_y += hist_y * weight
            total_weight += weight
        
        # Calcular média ponderada
        avg_x = weighted_x / total_weight if total_weight > 0 else diff_x
        avg_y = weighted_y / total_weight if total_weight > 0 else diff_y
        
        # Aplicar suavização (interpolar entre valor atual e média ponderada)
        smooth_x = diff_x * (1 - self.smoothing) + avg_x * self.smoothing
        smooth_y = diff_y * (1 - self.smoothing) + avg_y * self.smoothing
        
        # Atualizar último alvo conhecido
        self.last_target_x = smooth_x
        self.last_target_y = smooth_y
        self.has_target = True
        
        return (smooth_x, smooth_y, distance)
    
    def _get_color_target(self, screen):
        """
        Implementa a detecção por cor HSV.
        
        Args:
            screen (numpy.ndarray): Imagem da tela
            
        Returns:
            tuple: (x, y, distance) do alvo se encontrado, ou None
        """
        # Extrair contornos roxos
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        dilated = cv2.dilate(mask, self.kernel, iterations=3)
        opening = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, self.kernel, iterations=1)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Se não há contornos, não há alvo
        if not contours:
            return None
        
        # Filtrar contornos
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filtrar por tamanho
            if area < 30 or area > 10000:
                continue
            
            # Calcular compacidade
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            compactness = 4 * np.pi * area / (perimeter * perimeter)
            
            # Calcular razão de aspecto
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Filtrar por forma
            if 0.2 <= aspect_ratio <= 0.8 and compactness > 0.2 and h >= 15:
                valid_contours.append(contour)
        
        if not valid_contours:
            return None
        
        # Encontrar o melhor contorno
        best_target = None
        min_distance = float('inf')
        
        for contour in valid_contours:
            # Extrair pontos do contorno e ordená-los por coordenada Y
            points = np.array(sorted(contour[:, 0, :], key=lambda p: p[1]))
            
            if len(points) > 0:
                # Usar os pontos superiores do contorno para mira precisa
                top_points = points[:min(5, len(points))]
                
                # Calcular o ponto médio dos pontos superiores (para centralizar na cabeça)
                target_x = int(np.mean(top_points[:, 0]))
                
                # Para Y, pegar o ponto mais alto (menor Y) e aplicar offset
                target_y = int(np.min(top_points[:, 1])) + int(self.target_offset)
            else:
                # Caso falhe, usar bounding box
                x, y, w, h = cv2.boundingRect(contour)
                target_x = x + w // 2
                target_y = y + int(self.target_offset)
            
            # Calcular distância ao centro
            distance = np.sqrt((target_x - self.center) ** 2 + (target_y - self.center) ** 2)
            
            # Considerar posição vertical
            height_factor = 1.0
            if y / self.fov > 0.7:  # Se estiver muito abaixo
                height_factor = 2.0
            
            # Ajustar distância
            adjusted_distance = distance * height_factor
            
            # Atualizar melhor alvo
            if adjusted_distance < min_distance:
                min_distance = adjusted_distance
                best_target = (target_x, target_y, distance)
        
        # Salvar imagem de debug se necessário
        if self.debug_mode and best_target is not None:
            self._save_debug_image(screen, "cor", best_target[0], best_target[1])
        
        return best_target
    
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
        if enabled:
            # Criar pasta de debug se não existir
            os.makedirs("debug", exist_ok=True)
            print("Modo de debug ativado. Imagens serão salvas na pasta 'debug'.")
        else:
            print("Modo de debug desativado.")
    
    def _save_debug_image(self, image, label, target_x, target_y):
        """
        Salva imagens de debug para análise de detecção.
        
        Args:
            image (numpy.ndarray): Imagem original
            label (str): Rótulo para a imagem
            target_x (int): Coordenada X do alvo
            target_y (int): Coordenada Y do alvo
        """
        try:
            self.debug_counter += 1
            if self.debug_counter % 10 != 0:  # Salvar apenas a cada 10 frames para não lotar o disco
                return
                
            # Criar pasta de debug se não existir
            os.makedirs("debug", exist_ok=True)
            
            # Timestamp
            timestamp = int(time.time())
            
            # Criar cópia da imagem para desenhar
            debug_img = image.copy()
            
            # Desenhar marcações
            cv2.circle(debug_img, (target_x, target_y), 5, (0, 255, 0), -1)  # Alvo
            cv2.circle(debug_img, (self.center, self.center), 3, (0, 0, 255), -1)  # Centro
            
            # Adicionar texto informativo
            cv2.putText(debug_img, f"Mode: COLOR", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Salvar imagem
            filename = f"debug/detection_{timestamp}_{self.debug_counter}.png"
            cv2.imwrite(filename, debug_img)
            
        except Exception as e:
            print(f"Erro ao salvar imagem de debug: {e}")