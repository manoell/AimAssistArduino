import os
import time
import random
import shutil
from utils import print_banner, clear_console, print_status

# Caminho padrão para o arquivo boards.txt
BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")
BOARDS_TXT_BACKUP_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt.backup")

# Faz backup do arquivo boards.txt se não existir
if not os.path.exists(BOARDS_TXT_BACKUP_PATH) and os.path.exists(BOARDS_TXT_PATH):
    try:
        shutil.copy2(BOARDS_TXT_PATH, BOARDS_TXT_BACKUP_PATH)
        print("Backup do arquivo boards.txt criado com sucesso.")
    except Exception as e:
        print(f"Falha ao criar backup do boards.txt: {e}")

# Modifica o arquivo boards.txt
if os.path.exists(BOARDS_TXT_PATH):
    try:
        # Ler o arquivo boards.txt
        with open(BOARDS_TXT_PATH, 'r') as file:
            content = file.readlines()
        
        # VID e PID desejados (Logitech G502 HERO)
        vid = "046D"
        pid = "C08B"
        
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
            
            # Modificar o nome do fabricante USB
            elif line.startswith("leonardo.build.usb_manufacturer="):
                content[i] = f"leonardo.build.usb_manufacturer=\"Logitech\"\n"
                modified = True
                
            # Assegurar que ambas interfaces HID e CDC estão habilitadas
            elif line.startswith("leonardo.build.usb_flags="):
                content[i] = f"leonardo.build.usb_flags=-DUSB_VID=0x{vid} -DUSB_PID=0x{pid} -DUSBCON -DUSB_HID -DUSB_SERIAL -DCDC_ENABLED\n"
                modified = True
        
        if modified:
            # Salvar as alterações no arquivo
            with open(BOARDS_TXT_PATH, 'w') as file:
                file.writelines(content)
            
            print("Arquivo boards.txt atualizado com sucesso!")
        else:
            print("Não foi possível encontrar as linhas necessárias no arquivo boards.txt")
    except Exception as e:
        print(f"Falha ao atualizar boards.txt: {e}")
else:
    print(f"Arquivo boards.txt não encontrado em {BOARDS_TXT_PATH}")