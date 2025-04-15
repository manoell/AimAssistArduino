import os
import re
import time
import random
import requests
import zipfile
import subprocess
import win32com.client
import sys
from utils import print_banner, clear_console, print_status

class MouseSpoofer:
    """
    Classe responsável por detectar, clonar e configurar o Arduino para imitar
    a identidade de um mouse USB existente.
    """
    
    # Caminho padrão para o boards.txt do Arduino
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")
    ARDUINO_CLI_PATH = os.path.join(os.getcwd(), "arduino/arduino-cli.exe")
    SKETCH_PATH = os.path.join(os.getcwd(), "spoofer/arduino.ino")
    
    def __init__(self):
        """
        Inicializa o spoofer.
        """
        clear_console()
        print_banner()
        print("===== Mouse Clone Utility =====\n")
        
        # Verificar se o Arduino CLI existe, se não, baixá-lo
        if not os.path.exists(self.ARDUINO_CLI_PATH):
            self.download_arduino_cli()
        
        # Verificar se o diretório de sketch existe
        if not os.path.exists(os.path.dirname(self.SKETCH_PATH)):
            os.makedirs(os.path.dirname(self.SKETCH_PATH))
        
        # Garantir que o arquivo boards.txt exista
        if not os.path.exists(self.BOARDS_TXT_PATH):
            self.install_avr_core()
    
    def download_arduino_cli(self):
        """
        Baixa e extrai o Arduino CLI.
        """
        print_status("INFO", "Arduino CLI não encontrado, baixando...")
        
        # Criar diretório arduino se não existir
        os.makedirs("arduino", exist_ok=True)
        
        # Baixar o Arduino CLI
        try:
            url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"
            print_status("INFO", f"Baixando de {url}...")
            
            response = requests.get(url, stream=True)
            zip_path = os.path.join("arduino", "arduino-cli.zip")
            
            with open(zip_path, "wb") as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int(downloaded * 100 / total_size) if total_size > 0 else 0
                        print_status("INFO", f"Download: {percent}%", end="\r")
            
            print("\n")
            print_status("INFO", "Download concluído, extraindo...")
            
            # Extrair o arquivo zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("arduino")
            
            print_status("SUCESSO", "Arduino CLI instalado com sucesso!")
            
        except Exception as e:
            print_status("ERRO", f"Falha ao baixar Arduino CLI: {e}")
            sys.exit(1)
    
    def install_avr_core(self):
        """
        Instala o core AVR Arduino necessário para programar o Leonardo.
        """
        print_status("INFO", "Instalando core AVR...")
        
        try:
            result = subprocess.run(
                [self.ARDUINO_CLI_PATH, "core", "install", "arduino:avr@1.8.6"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print_status("ERRO", f"Falha ao instalar core AVR: {result.stderr}")
                sys.exit(1)
            
            print_status("SUCESSO", "Core AVR instalado com sucesso!")
            
        except Exception as e:
            print_status("ERRO", f"Falha ao instalar core AVR: {e}")
            sys.exit(1)
    
    def detect_mouse_devices(self):
        """
        Detecta todos os dispositivos de mouse conectados.
        
        Returns:
            list: Lista de tuplas (nome_dispositivo, vid, pid)
        """
        print_status("INFO", "Detectando dispositivos de mouse conectados...")
        
        try:
            # Conectar ao WMI
            wmi_service = win32com.client.GetObject("winmgmts:")
            
            # Obter dispositivos apontadores
            mouse_devices = wmi_service.InstancesOf("Win32_PointingDevice")
            
            # Lista para armazenar os mouses detectados
            detected_mice = []
            
            # Processar cada dispositivo
            for device in mouse_devices:
                device_name = device.Name or "Unknown Mouse"
                pnp_id = device.PNPDeviceID or ""
                
                # Extrair VID e PID do PNPDeviceID
                vid_match = re.search(r'VID_([0-9A-F]{4})', pnp_id)
                pid_match = re.search(r'PID_([0-9A-F]{4})', pnp_id)
                
                vid = vid_match.group(1) if vid_match else None
                pid = pid_match.group(1) if pid_match else None
                
                if vid and pid:
                    detected_mice.append((device_name, vid, pid))
            
            print_status("SUCESSO", f"Detectados {len(detected_mice)} dispositivos de mouse!")
            return detected_mice
            
        except Exception as e:
            print_status("ERRO", f"Falha ao detectar mouses: {e}")
            return []
    
    def select_mouse_device(self, devices):
        """
        Permite que o usuário selecione um mouse para clonar.
        
        Args:
            devices (list): Lista de dispositivos de mouse detectados
        
        Returns:
            tuple: (vid, pid) do mouse selecionado
        """
        if not devices:
            print_status("ERRO", "Nenhum mouse detectado!")
            sys.exit(1)
        
        print("\nMouses disponíveis para clonar:")
        print("-------------------------------")
        
        for i, (name, vid, pid) in enumerate(devices, 1):
            print(f"{i}. {name} [VID: {vid}, PID: {pid}]")
        
        print()
        
        while True:
            try:
                choice = int(input("Selecione o número do mouse que deseja clonar: "))
                if 1 <= choice <= len(devices):
                    selected = devices[choice - 1]
                    print_status("INFO", f"Mouse selecionado: {selected[0]} [VID: {selected[1]}, PID: {selected[2]}]")
                    return selected[1], selected[2]
                else:
                    print_status("AVISO", f"Por favor, escolha um número entre 1 e {len(devices)}")
            except ValueError:
                print_status("AVISO", "Por favor, digite um número válido")
            except Exception as e:
                print_status("ERRO", f"Erro ao selecionar mouse: {e}")
    
    def update_boards_txt(self, vid, pid):
        """
        Atualiza o arquivo boards.txt para usar o VID e PID do mouse selecionado.
        
        Args:
            vid (str): VID do mouse
            pid (str): PID do mouse
        """
        print_status("INFO", "Atualizando configuração do Arduino Leonardo...")
        
        try:
            # Verificar se o arquivo boards.txt existe
            if not os.path.exists(self.BOARDS_TXT_PATH):
                print_status("ERRO", f"Arquivo boards.txt não encontrado em {self.BOARDS_TXT_PATH}")
                print_status("INFO", "Tente executar o comando 'arduino-cli core install arduino:avr@1.8.6' manualmente")
                sys.exit(1)
            
            # Ler o arquivo boards.txt
            with open(self.BOARDS_TXT_PATH, 'r') as file:
                content = file.readlines()
            
            # Gerar um nome aleatório para o dispositivo
            random_name = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))
            
            # Modificar as linhas relevantes
            modified = False
            for i, line in enumerate(content):
                # Modificar o nome do Leonardo
                if line.startswith("leonardo.name="):
                    content[i] = f"leonardo.name={random_name}\n"
                    modified = True
                
                # Modificar o VID
                elif line.startswith("leonardo.vid."):
                    suffix = line.split("leonardo.vid.")[1].split("=")[0]
                    content[i] = f"leonardo.vid.{suffix}=0x{vid}\n"
                    modified = True
                
                # Modificar o PID
                elif line.startswith("leonardo.pid."):
                    suffix = line.split("leonardo.pid.")[1].split("=")[0]
                    content[i] = f"leonardo.pid.{suffix}=0x{pid}\n"
                    modified = True
                
                # Modificar o VID de compilação
                elif line.startswith("leonardo.build.vid="):
                    content[i] = f"leonardo.build.vid=0x{vid}\n"
                    modified = True
                
                # Modificar o PID de compilação
                elif line.startswith("leonardo.build.pid="):
                    content[i] = f"leonardo.build.pid=0x{pid}\n"
                    modified = True
                
                # Modificar o nome do produto USB
                elif line.startswith("leonardo.build.usb_product="):
                    content[i] = f"leonardo.build.usb_product=\"{random_name}\"\n"
                    modified = True
            
            if not modified:
                print_status("AVISO", "Não foi possível encontrar as linhas necessárias no arquivo boards.txt")
                print_status("INFO", "Verifique se o core arduino:avr está instalado corretamente")
                return False
            
            # Salvar as alterações no arquivo
            with open(self.BOARDS_TXT_PATH, 'w') as file:
                file.writelines(content)
            
            print_status("SUCESSO", "Arquivo boards.txt atualizado com sucesso!")
            return True
            
        except Exception as e:
            print_status("ERRO", f"Falha ao atualizar boards.txt: {e}")
            return False
    
    def create_arduino_sketch(self):
        """
        Cria o sketch Arduino com o código que queremos usar.
        """
        # Verifique se o diretório existe, se não, crie-o
        sketch_dir = os.path.dirname(self.SKETCH_PATH)
        if not os.path.exists(sketch_dir):
            os.makedirs(sketch_dir)
        
        # Código Arduino para o nosso propósito
        sketch_code = """#include <Mouse.h>

// Variáveis globais para armazenar o comando e valores de movimento
String command = "";         // Comando recebido do buffer serial
int deltaX = 0, deltaY = 0;  // Valores de movimento para os eixos X e Y

// Gerenciamento de estado de clique
bool isClicking = false;         // Rastreia se um clique do mouse está acontecendo
unsigned long clickStartTime = 0; // Marca o momento em que o clique começa
unsigned long clickDuration;     // Especifica quanto tempo o clique durará em milissegundos

void setup() {
    // Inicializar comunicação serial com uma taxa de transmissão de 115200
    Serial.begin(115200);
    Serial.setTimeout(1);  // Definir um timeout curto para leituras seriais
    Mouse.begin();         // Inicializar controle do mouse
    
    // Alimentar o gerador de números aleatórios para durações de clique variáveis
    randomSeed(analogRead(0));  // Usar um pino analógico desconectado para melhor aleatoriedade
}

void loop() {
    // Verificar se há algum comando aguardando no buffer serial
    if (Serial.available() > 0) {
        // Ler o comando de entrada até um caractere de nova linha
        command = Serial.readStringUntil('\\n');
        command.trim();  // Limpar quaisquer espaços no início ou fim
        
        // Se o comando começa com 'M', é um comando de movimento do mouse
        if (command.startsWith("M")) {
            int commaIndex = command.indexOf(',');  // Encontrar a posição da vírgula
            // Certificar-se de que o comando está formatado corretamente
            if (commaIndex != -1) {
                // Extrair os valores de movimento para os eixos X e Y
                deltaX = command.substring(1, commaIndex).toInt();  // Obter movimento do eixo X
                deltaY = command.substring(commaIndex + 1).toInt();  // Obter movimento do eixo Y
                
                // Mover o mouse incrementalmente para evitar saltos repentinos
                // Isso divide movimentos grandes em etapas menores
                while (deltaX != 0 || deltaY != 0) {
                    int moveX = constrain(deltaX, -127, 127);  // Limitar o movimento X para evitar overflow
                    int moveY = constrain(deltaY, -127, 127);  // Limitar o movimento Y de forma semelhante
                    Mouse.move(moveX, moveY);  // Realizar o movimento do mouse
                    deltaX -= moveX;  // Diminuir o movimento restante para o eixo X
                    deltaY -= moveY;  // Diminuir o movimento restante para o eixo Y
                    
                    // Pequena pausa para tornar o movimento mais suave
                    delayMicroseconds(500);
                }
            }
        }
        // Se o comando começa com 'C', é um comando de clique do mouse
        else if (command.startsWith("C")) {
            // Iniciar o processo de clique se ainda não estamos clicando
            if (!isClicking) {
                Mouse.press(MOUSE_LEFT);  // Pressionar o botão esquerdo do mouse
                clickStartTime = millis();  // Registrar o tempo atual como o início do clique
                clickDuration = random(40, 80);  // Escolher uma duração aleatória entre 40ms e 80ms
                isClicking = true;  // Marcar que estamos em um estado de clique
            }
        }
    }
    
    // Se um clique estiver em andamento, verificar se é hora de soltar o botão
    if (isClicking) {
        // Se a duração especificada do clique tiver passado, soltar o botão
        if (millis() - clickStartTime >= clickDuration) {
            Mouse.release(MOUSE_LEFT);  // Soltar o botão esquerdo do mouse
            isClicking = false;  // Redefinir o estado de clique
        }
    }
}"""
        
        # Escrever o código no arquivo
        try:
            with open(self.SKETCH_PATH, 'w') as f:
                f.write(sketch_code)
            print_status("SUCESSO", f"Sketch Arduino criado em {self.SKETCH_PATH}")
            return True
        except Exception as e:
            print_status("ERRO", f"Falha ao criar sketch Arduino: {e}")
            return False
    
    def compile_upload_sketch(self):
        """
        Compila e faz upload do sketch para o Arduino Leonardo.
        """
        # Solicitar a porta COM
        com_port = input("\nDigite a porta COM do seu Arduino Leonardo (ex: COM5): ")
        
        # Verificar se o sketch existe
        if not os.path.exists(self.SKETCH_PATH):
            if not self.create_arduino_sketch():
                return False
        
        # Compilar o sketch
        print_status("INFO", "Compilando sketch...")
        try:
            compile_cmd = [
                self.ARDUINO_CLI_PATH,
                "compile",
                "--fqbn", "arduino:avr:leonardo",
                self.SKETCH_PATH
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print_status("ERRO", f"Falha ao compilar sketch: {result.stderr}")
                return False
            
            print_status("SUCESSO", "Sketch compilado com sucesso!")
            
        except Exception as e:
            print_status("ERRO", f"Falha ao compilar sketch: {e}")
            return False
        
        # Fazer upload do sketch
        print_status("INFO", f"Fazendo upload para o Arduino na porta {com_port}...")
        try:
            upload_cmd = [
                self.ARDUINO_CLI_PATH,
                "upload",
                "-p", com_port,
                "--fqbn", "arduino:avr:leonardo",
                self.SKETCH_PATH
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print_status("ERRO", f"Falha ao fazer upload: {result.stderr}")
                return False
            
            print_status("SUCESSO", "Sketch enviado com sucesso para o Arduino!")
            return True
            
        except Exception as e:
            print_status("ERRO", f"Falha ao fazer upload: {e}")
            return False
    
    def run(self):
        """
        Executa o processo completo de clonagem.
        """
        # Detectar mouses
        mice = self.detect_mouse_devices()
        
        if not mice:
            print_status("ERRO", "Nenhum mouse detectado! Conecte pelo menos um mouse USB.")
            return
        
        # Selecionar mouse para clonar
        vid, pid = self.select_mouse_device(mice)
        
        # Atualizar boards.txt
        if not self.update_boards_txt(vid, pid):
            print_status("ERRO", "Falha ao atualizar o arquivo boards.txt.")
            return
        
        # Compilar e fazer upload do sketch
        if not self.compile_upload_sketch():
            print_status("ERRO", "Falha ao compilar e enviar o sketch.")
            return
        
        # Atualizar settings.ini com a porta COM
        try:
            from config_manager import ConfigManager
            config = ConfigManager('settings.ini')
            
            # Obter a porta COM usada
            com_port = input("\nConfirme a porta COM do seu Arduino após a clonagem: ")
            config.set('Connection', 'com_port', com_port)
            
            print_status("SUCESSO", "Arquivo settings.ini atualizado com a nova porta COM!")
            
        except Exception as e:
            print_status("AVISO", f"Não foi possível atualizar settings.ini: {e}")
            print_status("INFO", "Você precisará atualizar manualmente a porta COM no arquivo settings.ini")
        
        print("\n=======================================")
        print("CLONE DE MOUSE CONCLUÍDO COM SUCESSO!")
        print("=======================================")
        print("\nO Arduino Leonardo agora está configurado para aparecer como seu mouse.")
        print("Desconecte e reconecte o Arduino para que as alterações tenham efeito.")
        print("\nEm seguida, execute o main.py para iniciar o aim assist.")


if __name__ == "__main__":
    spoofer = MouseSpoofer()
    spoofer.run()
