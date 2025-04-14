import cv2
import numpy as np
import serial
import os
import time
import configparser
import threading
import win32api
import win32gui
import win32ui
import win32con
import sys
from ctypes import windll

#https://github.com/astrapy/ArduinoColorbotValorant

class PhantomWare:
    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        self.config = configparser.ConfigParser()
        self.config_file = "settings.ini"
        self.load_config()

        # Obtenha tamanho da tela usando Win32
        self.screen_width = windll.user32.GetSystemMetrics(0)
        self.screen_height = windll.user32.GetSystemMetrics(1)
        
        # Calcular coordenadas para captura com base no FOV
        self.calc_screenshot_area()

        # Valores HSV para detecção de roxo (contornos de inimigos)
        # Ajustados para melhor detecção do roxo do Valorant
        self.lower = np.array([125, 75, 75])   # Valores HSV mais amplos 
        self.upper = np.array([170, 255, 255]) # para melhor detecção

        # Variáveis para assistência de mira mais natural
        self.smoothing_factor = 0.6  # Quanto maior, mais suave o movimento (0.0-1.0)
        self.assist_strength = 0.7   # Força da assistência (0.0-1.0)
        self.max_distance = 100      # Distância máxima para aplicar assistência

        # Flag para debug
        self.debug_mode = True
        
        # Histórico de alvos para suavização
        self.last_targets = []
        self.history_length = 3

        self.arduino = None
        self.connect()

        d_thread = threading.Thread(target=self.detection, daemon=True)
        d_thread.start()

        conf_thread = threading.Thread(target=self.update_conf, daemon=True)
        conf_thread.start()

        self.main_loop()

    def calc_screenshot_area(self):
        """Calcula a área de captura baseada no FOV atual"""
        self.x1 = int((self.screen_width / 2) - (self.fov / 2))
        self.y1 = int((self.screen_height / 2) - (self.fov / 2))
        self.x2 = int((self.screen_width / 2) + (self.fov / 2))
        self.y2 = int((self.screen_height / 2) + (self.fov / 2))
        self.fov_width = self.x2 - self.x1
        self.fov_height = self.y2 - self.y1

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config["Aimbot"] = {
                "fov": "100",
                "x_speed": "1.0",
                "y_speed": "1.0"
            }
            self.config["Connection"] = {
                "com_port": "COM5"  # Atualizado para usar COM5
            }
            self.config["Keybinds"] = {
                "keybind": "0x02"
            }
            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)

        self.config.read(self.config_file)

        self.fov = int(self.config.get("Aimbot", "fov"))
        self.x_speed = float(self.config.get("Aimbot", "x_speed"))
        self.y_speed = float(self.config.get("Aimbot", "y_speed"))
        self.com_port = self.config.get("Connection", "com_port")
        self.keybind = int(self.config.get("Keybinds", "keybind"), 16)

    def update_conf(self):
        new_conf = os.path.getmtime(self.config_file)
        old_config = dict(self.config["Aimbot"])
        
        while True:
            old_conf = os.path.getmtime(self.config_file)
            if old_conf != new_conf:

                self.load_config()
                self.calc_screenshot_area()  # Recalcular área de captura quando o FOV mudar

                changed_set = []
                for setting in self.config["Aimbot"]:
                    if self.config["Aimbot"][setting] != old_config.get(setting, None):
                        changed_set.append(f"{setting}: {old_config.get(setting, 'N/A')} -> {self.config['Aimbot'][setting]}")

                if changed_set:
                    for change in changed_set:
                        print(f"Succesfully updated {change}")

                old_config = dict(self.config["Aimbot"])
                new_conf = old_conf

            time.sleep(1)

    def connect(self):
        while True:
            try:
                self.arduino = serial.Serial(self.com_port, 115200)
                print(f"Successfully connected to Arduino on {self.com_port}")
                break
            except serial.SerialException:
                print(f"Failed to connect to {self.com_port}")
                self.com_port = input("Enter new COM port: ").strip()

    def m_movement(self, x, y):
        if self.arduino:
            command = f"m{int(x)},{int(y)}\n"
            try:
                self.arduino.write(command.encode())
            except Exception as e:
                print(f"Erro ao enviar comando para Arduino: {e}")

    def smooth_movement(self, x, y):
        """Aplica suavização de movimento para tornar a assistência mais natural"""
        if len(self.last_targets) > 0:
            # Calcula a média ponderada com os alvos anteriores
            sum_x, sum_y, sum_weights = 0, 0, 0
            
            # Dá mais peso aos alvos mais recentes
            for i, (prev_x, prev_y) in enumerate(self.last_targets):
                weight = (i + 1) / len(self.last_targets)
                sum_x += prev_x * weight
                sum_y += prev_y * weight
                sum_weights += weight
            
            avg_x = sum_x / sum_weights
            avg_y = sum_y / sum_weights
            
            # Aplicar smoothing factor
            smooth_x = int(avg_x * (1 - self.smoothing_factor) + x * self.smoothing_factor)
            smooth_y = int(avg_y * (1 - self.smoothing_factor) + y * self.smoothing_factor)
            
            return smooth_x, smooth_y
        return x, y

    def grab_screen(self):
        """Captura a tela usando Win32 API diretamente"""
        try:
            # Configurar dispositivos de contexto
            hwin = win32gui.GetDesktopWindow()
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            
            # Criar bitmap para armazenar a captura
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, self.fov_width, self.fov_height)
            memdc.SelectObject(bmp)
            
            # Copiar da tela para o bitmap
            memdc.BitBlt((0, 0), (self.fov_width, self.fov_height), srcdc, (self.x1, self.y1), win32con.SRCCOPY)
            
            # Converter para um array numpy
            signedIntsArray = bmp.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype='uint8')
            img.shape = (self.fov_height, self.fov_width, 4)
            
            # Limpar recursos
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())
            
            # Converter de BGRA para BGR (remover o canal alpha)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print(f"Erro ao capturar tela: {e}")
            return None

    def detection(self):
        center_x = self.fov_width / 2
        center_y = self.fov_height / 2
        
        while True:
            if win32api.GetAsyncKeyState(self.keybind) < 0:
                try:
                    # Captura a tela usando Win32 API
                    img = self.grab_screen()
                    
                    if img is None or img.size == 0:
                        continue
                    
                    # Processamento da imagem
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, self.lower, self.upper)
                    
                    # Debug - Salvar a máscara para ajuste
                    if self.debug_mode and time.time() % 5 < 0.1:  # A cada ~5 segundos
                        cv2.imwrite('debug_mask.png', mask)
                        cv2.imwrite('debug_screen.png', img)

                    kernel = np.ones((3, 3), np.uint8)
                    dilated = cv2.dilate(mask, kernel, iterations=1)
                    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    closest_t = None
                    closest_dist = float('inf')
                    min_area = 50  # Reduzindo a área mínima para detectar alvos menores

                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if area > min_area:
                            # Calcular o centro do contorno
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cont_x = int(M["m10"] / M["m00"])
                                cont_y = int(M["m01"] / M["m00"])
                                
                                # Para mira na cabeça, podemos ajustar para o ponto mais alto do contorno
                                # Usamos pontos altos do contorno (potencialmente a cabeça)
                                highest_points = sorted(contour, key=lambda p: p[0][1])[:5]
                                highest_x = sum([p[0][0] for p in highest_points]) / len(highest_points)
                                highest_y = sum([p[0][1] for p in highest_points]) / len(highest_points)

                                # Ajuste para mirar mais abaixo (offset positivo move para baixo)
                                y_offset = 5  # Ajuste este valor conforme necessário (5-10 pixels geralmente é bom)
                                                                
                                # Ajustar para usar o ponto mais alto como alvo + offset
                                cont_x, cont_y = int(highest_x), int(highest_y + y_offset)
                                
                                distance = np.sqrt((cont_x - center_x) ** 2 + (cont_y - center_y) ** 2)
                                
                                if distance < closest_dist:
                                    closest_dist = distance
                                    closest_t = (cont_x, cont_y)
    
                    if closest_t and closest_dist < self.max_distance:
                        cont_x, cont_y = closest_t
                        diff_x = cont_x - center_x
                        diff_y = cont_y - center_y
                        
                        # Aplicar força de assistência
                        diff_x *= self.assist_strength
                        diff_y *= self.assist_strength
                        
                        # Aplicar os multiplicadores de velocidade (invertendo o X)
                        target_x = int(diff_x * self.x_speed)
                        target_y = int(diff_y * self.y_speed)
                        
                        # Aplicar suavização
                        target_x, target_y = self.smooth_movement(target_x, target_y)
                        
                        # Adicionar ao histórico
                        self.last_targets.append((target_x, target_y))
                        if len(self.last_targets) > self.history_length:
                            self.last_targets.pop(0)
                        
                        # Envia o movimento para o Arduino se um alvo foi encontrado
                        self.m_movement(target_x, target_y)
                        
                        if self.debug_mode:
                            print(f"Alvo detectado: ({target_x}, {target_y}) - Distância: {closest_dist:.1f}")

                except Exception as e:
                    print(f"Erro na detecção: {e}")
                    time.sleep(0.1)  # Pequena pausa em caso de erro

            time.sleep(0.01)  # Pequena pausa para evitar uso intenso da CPU

    def main_loop(self):
        print("Sistema iniciado. Pressione Ctrl+C para sair.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nFinalizando...")
            if self.arduino:
                self.arduino.close()
            sys.exit(0)

if __name__ == "__main__":
    PhantomWare()