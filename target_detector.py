import cv2
import numpy as np
import time
import os
import sys
import logging
from ultralytics import YOLO

# Configurar logging para capturar a saída do YOLO
logging.basicConfig(filename='yolo.log', level=logging.ERROR)

# Redirecionar stderr para arquivo de log
sys.stderr = open('yolo_stderr.log', 'w')

class TargetDetector:
    """
    Classe responsável por detectar alvos na tela usando múltiplos modos:
    1. HÍBRIDO: Detecção por cor + confirmação YOLO (máxima precisão)
    2. YOLO: Apenas detecção YOLO em toda a tela (preciso, mais pesado)
    3. COR: Apenas detecção por cor (rápido, menos preciso)
    
    Todos os modos usam EXATAMENTE o mesmo processamento final para 
    garantir uma experiência de movimentação idêntica.
    """
    
    # Constantes para modos de detecção
    MODE_HYBRID = 0
    MODE_YOLO_ONLY = 1
    MODE_COLOR_ONLY = 2
    
    MODE_NAMES = {
        MODE_HYBRID: "HÍBRIDO (Cor + YOLO)",
        MODE_YOLO_ONLY: "YOLO",
        MODE_COLOR_ONLY: "COR"
    }
    
    def __init__(self, lower_color, upper_color, fov, target_offset=0, model_path="my_yolo_model.pt",
                 base_processing_time=0.015, max_compensation=2.0, compensation_exponent=0.7):
        """
        Inicializa o detector de alvos com múltiplos modos de detecção.
        
        Args:
            lower_color (numpy.ndarray): Limite inferior para detecção de cor (HSV)
            upper_color (numpy.ndarray): Limite superior para detecção de cor (HSV)
            fov (int): Campo de visão (diâmetro)
            target_offset (float): Deslocamento vertical para mira (valores positivos = mais baixo)
            model_path (str): Caminho para o modelo YOLO treinado
            base_processing_time (float): Tempo base de processamento esperado em segundos
            max_compensation (float): Fator máximo de compensação de velocidade
            compensation_exponent (float): Expoente para cálculo de compensação não-linear
        """
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.fov = fov
        self.target_offset = target_offset
        self.center = fov // 2
        
        # Parâmetros de compensação de velocidade
        self.base_processing_time = base_processing_time
        self.max_compensation = max_compensation
        self.compensation_exponent = compensation_exponent
        
        # Modo atual de detecção (padrão: híbrido)
        self.detection_mode = self.MODE_HYBRID
        
        # Kernel para operações morfológicas
        self.kernel = np.ones((3, 3), np.uint8)
        
        # Carregar o modelo YOLO silenciosamente
        print(f"Carregando modelo YOLO de {model_path}...")
        try:
            # Redirecionar stdout/stderr temporariamente
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            
            # Carregar modelo
            self.yolo_model = YOLO(model_path)
            
            # Restaurar stdout/stderr
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            print("Modelo YOLO carregado com sucesso!")
            
            # Obter classes do modelo para referência
            self.class_names = self.yolo_model.names
            print(f"Classes detectadas pelo modelo: {self.class_names}")
            self.headshot_keyword = "headshot"  # Palavra-chave para detecção de cabeça
            self.model_loaded = True
        except Exception as e:
            print(f"Erro ao carregar modelo YOLO: {e}")
            print("Continuando apenas com detecção por cor...")
            self.model_loaded = False
            # Se YOLO não carregou, forçar modo de detecção por cor
            self.detection_mode = self.MODE_COLOR_ONLY
        
        # Configurações para detecção
        self.confidence_threshold = 0.4  # Confiança mínima para considerar uma detecção
        
        # Variáveis para debug e otimização
        self.last_detection_time = time.time()
        self.frame_start_time = time.time()
        self.processing_times = []  # Lista para armazenar tempos de processamento recentes
        self.max_processing_times = 30  # Número de amostras para média móvel
        self.debug_mode = False
        self.debug_counter = 0
        
        # Estatísticas
        self.total_detections = 0
        self.yolo_confirmations = 0
        self.false_positives = 0
        
        # Estado do alvo e histórico para suavização de movimento
        self.has_target = False
        self.last_target_x = 0
        self.last_target_y = 0
        
        # Histórico para média ponderada (como no modo COR)
        self.movement_history = []
        self.max_history = 10
        
        # Fator de suavização bem alto para movimento natural
        self.smoothing = 0.9
    
    def detect_target(self, screen):
        """
        Detecta o alvo usando o modo de detecção atualmente selecionado
        e aplica o mesmo processamento final para todos os modos.
        
        Args:
            screen (numpy.ndarray): Imagem capturada da tela
            
        Returns:
            tuple: (diff_x, diff_y, distance) se um alvo for encontrado, None caso contrário
        """
        # Registrar o tempo de início do processamento do frame
        self.frame_start_time = time.time()
        
        # IMPORTANTE: Converter BGRA para BGR (remover canal alpha)
        if screen.shape[2] == 4:  # Se a imagem tem 4 canais (BGRA)
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        
        # Detectar alvo com base no modo selecionado
        # Cada modo retorna (x, y) absolutas na tela ou None
        target = None
        
        if self.detection_mode == self.MODE_HYBRID and self.model_loaded:
            target = self._get_hybrid_target(screen)
        elif self.detection_mode == self.MODE_YOLO_ONLY and self.model_loaded:
            target = self._get_yolo_target(screen)
        else:
            target = self._get_color_target(screen)
        
        # Registrar o tempo de processamento deste frame
        processing_time = time.time() - self.frame_start_time
        self._update_processing_times(processing_time)
        
        # Processo unificado para todos os modos a partir daqui
        # Isso garante movimentação idêntica independente do modo
        return self._process_target_movement(target)
    
    def _update_processing_times(self, processing_time):
        """
        Atualiza a lista de tempos de processamento para cálculo de médias.
        
        Args:
            processing_time (float): Tempo de processamento do frame atual em segundos
        """
        self.processing_times.append(processing_time)
        if len(self.processing_times) > self.max_processing_times:
            self.processing_times.pop(0)
    
    def get_speed_compensation_factor(self):
        """
        Calcula um fator de compensação de velocidade baseado no tempo de processamento recente.
        
        Returns:
            float: Fator de compensação (>1.0 = mais rápido, 1.0 = normal)
        """
        # Se não estamos usando YOLO (modo COR), não há compensação necessária
        if self.detection_mode == self.MODE_COLOR_ONLY:
            return 1.0
        
        # Se não temos amostras suficientes, não compensa
        if not self.processing_times:
            return 1.0
        
        # Calculamos a média dos tempos de processamento recentes
        avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        # Limitar o tempo de processamento para cálculos (evita valores extremos)
        capped_time = min(max(avg_processing_time, 0.005), 0.1)
        
        # Se o tempo está abaixo do base, não precisamos compensar
        if capped_time <= self.base_processing_time:
            return 1.0
        
        # Compensação não-linear para tempos maiores que o esperado
        # Quanto maior o delay, maior a compensação
        relative_delay = (capped_time - self.base_processing_time) / self.base_processing_time
        compensation = 1.0 + pow(relative_delay, self.compensation_exponent) * 0.5
        
        # Limitar ao fator máximo de compensação
        return min(compensation, self.max_compensation)
    
    def _process_target_movement(self, target):
        """
        Processa o alvo detectado para produzir uma movimentação suave.
        Este método é único para todos os modos, garantindo consistência.
        
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
    
    def _get_hybrid_target(self, screen):
        """
        Implementa o modo híbrido: detecção por cor + confirmação YOLO.
        
        Args:
            screen (numpy.ndarray): Imagem da tela
            
        Returns:
            tuple: (x, y, distance) do alvo se encontrado, ou None
        """
        # 1. Encontrar contornos roxos na imagem
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        dilated = cv2.dilate(mask, self.kernel, iterations=3)
        opening = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, self.kernel, iterations=1)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Se não há contornos, não há alvo
        if not contours:
            return None
        
        # Filtrar contornos muito pequenos
        valid_contours = [c for c in contours if cv2.contourArea(c) > 30]
        if not valid_contours:
            return None
        
        # 2. Para cada contorno, verificar com YOLO
        confirmed_targets = []
        
        # Redirecionar stdout/stderr para evitar logs
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        try:
            for contour in valid_contours:
                # Extrair região de interesse (ROI)
                x, y, w, h = cv2.boundingRect(contour)
                padding = 10
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(screen.shape[1], x + w + padding)
                y2 = min(screen.shape[0], y + h + padding)
                
                roi = screen[y1:y2, x1:x2]
                
                # Ignorar ROIs muito pequenas
                if roi.shape[0] < 10 or roi.shape[1] < 10:
                    continue
                
                # Executar YOLO na ROI
                results = self.yolo_model(roi, conf=self.confidence_threshold)[0]
                
                # Se YOLO encontrou algo, processar as detecções
                if len(results.boxes) > 0:
                    for box in results.boxes:
                        # Extrair coordenadas
                        roi_x1, roi_y1, roi_x2, roi_y2 = map(int, box.xyxy[0])
                        cls_id = int(box.cls[0])
                        label = self.class_names[cls_id]
                        
                        # Converter para coordenadas globais
                        abs_x1 = roi_x1 + x1
                        abs_y1 = roi_y1 + y1
                        abs_x2 = roi_x2 + x1
                        abs_y2 = roi_y2 + y1
                        
                        # Calcular centro e ajustar para mirar
                        cx = (abs_x1 + abs_x2) // 2
                        
                        # Determinar posição vertical baseada no tipo
                        if self.headshot_keyword in label.lower():
                            cy = (abs_y1 + abs_y2) // 2
                            priority = 1  # Prioridade máxima
                        else:
                            # Mirar no topo + offset
                            cy = abs_y1 + int((abs_y2 - abs_y1) * 0.1)  # Bem próximo ao topo
                            cy += int(self.target_offset)
                            priority = 2
                        
                        # Calcular distância ao centro
                        distance = np.sqrt((cx - self.center) ** 2 + (cy - self.center) ** 2)
                        
                        # Adicionar à lista de alvos confirmados
                        confirmed_targets.append((cx, cy, distance, priority))
        finally:
            # Restaurar stdout/stderr
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # Se encontramos alvos confirmados, pegar o melhor
        if confirmed_targets:
            # Ordenar por prioridade e distância
            confirmed_targets.sort(key=lambda t: (t[3], t[2]))
            best_target = confirmed_targets[0]
            return best_target[:3]  # Retornar (x, y, distance)
        
        # Nenhum alvo confirmado
        return None
    
    def _get_yolo_target(self, screen):
        """
        Implementa o modo YOLO: detecção apenas com YOLO.
        
        Args:
            screen (numpy.ndarray): Imagem da tela
            
        Returns:
            tuple: (x, y, distance) do alvo se encontrado, ou None
        """
        # Redirecionar stdout/stderr para evitar logs
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        try:
            # Executar YOLO na tela inteira
            results = self.yolo_model(screen, conf=self.confidence_threshold)[0]
            
            # Se não há detecções, não há alvo
            if len(results.boxes) == 0:
                return None
            
            # Processar detecções
            best_target = None
            min_score = float('inf')
            
            for box in results.boxes:
                # Extrair coordenadas
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                label = self.class_names[cls_id]
                
                # Calcular centro e ajustar para mirar
                cx = (x1 + x2) // 2
                
                # Determinar posição vertical baseada no tipo
                if self.headshot_keyword in label.lower():
                    cy = (y1 + y2) // 2
                    priority = 1  # Prioridade máxima
                else:
                    # Mirar no topo + offset
                    cy = y1 + int((y2 - y1) * 0.1)  # Bem próximo ao topo
                    cy += int(self.target_offset)
                    priority = 2
                
                # Calcular distância ao centro
                distance = np.sqrt((cx - self.center) ** 2 + (cy - self.center) ** 2)
                
                # Calcular pontuação
                score = priority * distance
                
                # Atualizar melhor alvo
                if score < min_score:
                    min_score = score
                    best_target = (cx, cy, distance)
            
            return best_target
                
        except Exception as e:
            if self.debug_mode:
                print(f"Erro ao processar YOLO: {e}")
            return None
            
        finally:
            # Restaurar stdout/stderr
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _get_color_target(self, screen):
        """
        Implementa o modo COR: detecção apenas por cor.
        
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
            # Obter bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calcular centro e ajustar para mirar
            cx = x + w // 2
            cy = y + int(h * 0.1)  # Próximo ao topo
            cy += int(self.target_offset)
            
            # Calcular distância ao centro
            distance = np.sqrt((cx - self.center) ** 2 + (cy - self.center) ** 2)
            
            # Considerar posição vertical
            height_factor = 1.0
            if y / self.fov > 0.7:  # Se estiver muito abaixo
                height_factor = 2.0
            
            # Ajustar distância
            adjusted_distance = distance * height_factor
            
            # Atualizar melhor alvo
            if adjusted_distance < min_distance:
                min_distance = adjusted_distance
                best_target = (cx, cy, distance)
        
        return best_target
    
    def set_detection_mode(self, mode):
        """
        Define o modo de detecção.
        
        Args:
            mode (int): Modo de detecção (0: Híbrido, 1: YOLO, 2: Cor)
        
        Returns:
            bool: True se o modo foi alterado com sucesso, False caso contrário
        """
        # Verificar se o modo é válido
        if mode not in self.MODE_NAMES:
            return False
            
        # Se o modo requer YOLO, verificar se o modelo está carregado
        if (mode == self.MODE_HYBRID or mode == self.MODE_YOLO_ONLY) and not self.model_loaded:
            print(f"Não é possível alternar para o modo {self.MODE_NAMES[mode]} porque o modelo YOLO não está carregado.")
            return False
            
        # Resetar o estado de movimento ao mudar de modo
        self.has_target = False
        self.last_target_x = 0
        self.last_target_y = 0
        self.movement_history = []
        self.processing_times = []  # Limpar histórico de tempos de processamento
            
        # Alterar o modo
        self.detection_mode = mode
        print(f"Modo de detecção alterado para: {self.MODE_NAMES[mode]}")
        return True
    
    def cycle_detection_mode(self):
        """
        Alterna ciclicamente entre os modos de detecção disponíveis.
        
        Returns:
            str: Nome do novo modo de detecção
        """
        current_mode = self.detection_mode
        
        # Se o modelo YOLO está carregado, ciclar entre todos os modos
        if self.model_loaded:
            new_mode = (current_mode + 1) % 3
        else:
            # Se o modelo YOLO não está carregado, só temos o modo de cor
            new_mode = self.MODE_COLOR_ONLY
            
        self.set_detection_mode(new_mode)
        return self.MODE_NAMES[new_mode]
    
    def get_current_mode_name(self):
        """
        Retorna o nome do modo de detecção atual.
        
        Returns:
            str: Nome do modo de detecção
        """
        return self.MODE_NAMES[self.detection_mode]
    
    def set_compensation_parameters(self, base_time, max_compensation, exponent):
        """
        Atualiza os parâmetros de compensação de velocidade.
        
        Args:
            base_time (float): Tempo base de processamento esperado em segundos
            max_compensation (float): Fator máximo de compensação
            exponent (float): Expoente para cálculo não-linear
        """
        self.base_processing_time = base_time
        self.max_compensation = max_compensation
        self.compensation_exponent = exponent
        
        # Limpar histórico de processamento ao alterar parâmetros
        self.processing_times = []
    
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
            label (str): Classe detectada
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
            cv2.putText(debug_img, f"Class: {label}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(debug_img, f"Mode: {self.get_current_mode_name()}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Adicionar informações de compensação
            if self.detection_mode != self.MODE_COLOR_ONLY:
                comp_factor = self.get_speed_compensation_factor()
                cv2.putText(debug_img, f"Comp: {comp_factor:.2f}x", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Salvar imagem
            filename = f"debug/detection_{timestamp}_{self.debug_counter}.png"
            cv2.imwrite(filename, debug_img)
            
        except Exception as e:
            print(f"Erro ao salvar imagem de debug: {e}")