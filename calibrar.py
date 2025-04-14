import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from ctypes import windll
import time
import os
import sys

# Função para capturar a tela
def grab_screen(x1, y1, width, height):
    try:
        # Configurar dispositivos de contexto
        hwin = win32gui.GetDesktopWindow()
        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        
        # Criar bitmap para armazenar a captura
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)
        
        # Copiar da tela para o bitmap
        memdc.BitBlt((0, 0), (width, height), srcdc, (x1, y1), win32con.SRCCOPY)
        
        # Converter para um array numpy
        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4)
        
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

def test_hsv_values():
    # Obter tamanho da tela
    screen_width = windll.user32.GetSystemMetrics(0)
    screen_height = windll.user32.GetSystemMetrics(1)
    
    # Configurar a área de captura (centro da tela)
    fov = 200  # Campo de visão em pixels
    x1 = int((screen_width / 2) - (fov / 2))
    y1 = int((screen_height / 2) - (fov / 2))
    
    print("Iniciando teste de valores HSV para o roxo do Valorant")
    print("Vá para o treinamento do Valorant com bots visíveis")
    print("Este programa irá tirar 10 capturas de tela com diferentes valores HSV")
    print("Depois verifique as imagens na pasta 'hsv_tests' para encontrar os melhores valores")
    input("Pressione Enter para começar...")
    
    # Criar pasta para os testes
    os.makedirs("hsv_tests", exist_ok=True)
    
    # Lista de diferentes valores HSV para testar
    tests = [
        # Nome, H_min, S_min, V_min, H_max, S_max, V_max
        ("original_roxo", 120, 70, 70, 170, 255, 255),
        ("mais_magenta", 140, 100, 100, 165, 255, 255),
        ("roxo_estreito", 135, 120, 120, 150, 255, 255),
        ("roxo_valorant", 130, 100, 100, 155, 255, 255),
        ("tons_claros", 130, 50, 150, 160, 255, 255),
        ("tons_escuros", 130, 100, 50, 160, 255, 255),
        ("mais_vermelho", 145, 100, 100, 175, 255, 255),
        ("mais_azul", 125, 100, 100, 145, 255, 255),
        ("saturado", 135, 150, 100, 155, 255, 255),
        ("amplo", 125, 75, 75, 170, 255, 255)
    ]
    
    for i, (name, h_min, s_min, v_min, h_max, s_max, v_max) in enumerate(tests):
        print(f"Teste {i+1}/10: {name}")
        
        # Capturar a tela
        img = grab_screen(x1, y1, fov, fov)
        if img is None:
            print("Falha ao capturar tela. Pulando este teste.")
            continue
            
        # Salvar imagem original
        cv2.imwrite(f"hsv_tests/{i+1}_{name}_original.png", img)
        
        # Converter para HSV e aplicar máscara
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Salvar máscara
        cv2.imwrite(f"hsv_tests/{i+1}_{name}_mask.png", mask)
        
        # Aplicar máscara na imagem original para mostrar o que foi detectado
        result = cv2.bitwise_and(img, img, mask=mask)
        cv2.imwrite(f"hsv_tests/{i+1}_{name}_result.png", result)
        
        # Salvar os valores usados em um arquivo de texto
        with open(f"hsv_tests/{i+1}_{name}_values.txt", "w") as f:
            f.write(f"H_min: {h_min}, S_min: {s_min}, V_min: {v_min}\n")
            f.write(f"H_max: {h_max}, S_max: {s_max}, V_max: {v_max}\n")
            f.write(f"Valores Python: lower=np.array([{h_min}, {s_min}, {v_min}]), upper=np.array([{h_max}, {s_max}, {v_max}])")
        
        # Pequeno atraso para permitir alterações no jogo
        time.sleep(1)
    
    print("\nTestes concluídos! Verifique a pasta 'hsv_tests' para analisar os resultados.")
    print("Quando encontrar os melhores valores, atualize o arquivo colorbot_improved.py")
    
if __name__ == "__main__":
    test_hsv_values()