import os
import platform
import time
from datetime import datetime

def clear_console():
    """
    Limpa o console de acordo com o sistema operacional.
    """
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def print_banner():
    """
    Imprime o banner do programa.
    """
    banner = """
    █████╗ ██╗███╗   ███╗      █████╗ ███████╗███████╗██╗███████╗████████╗
    ██╔══██╗██║████╗ ████║     ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝
    ███████║██║██╔████╔██║     ███████║███████╗███████╗██║███████╗   ██║   
    ██╔══██║██║██║╚██╔╝██║     ██╔══██║╚════██║╚════██║██║╚════██║   ██║   
    ██║  ██║██║██║ ╚═╝ ██║     ██║  ██║███████║███████║██║███████║   ██║   
    ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   
    """
    print(banner)
    print()

def print_status(status, message, end="\n"):
    """
    Imprime uma mensagem de status formatada.
    
    Args:
        status (str): Tipo de status (INFO, ERRO, SUCESSO)
        message (str): Mensagem a ser exibida
        end (str, optional): Caractere de término da linha. Padrão: "\n"
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    if status.upper() == "INFO":
        prefix = f"[{timestamp}] [INFO] "
    elif status.upper() == "ERRO":
        prefix = f"[{timestamp}] [ERRO] "
    elif status.upper() == "SUCESSO":
        prefix = f"[{timestamp}] [SUCESSO] "
    elif status.upper() == "AVISO":
        prefix = f"[{timestamp}] [AVISO] "
    else:
        prefix = f"[{timestamp}] [{status}] "
    
    print(f"{prefix}{message}", end=end)

def get_time_str():
    """
    Retorna uma string formatada com o tempo atual.
    
    Returns:
        str: Tempo atual formatado (HH:MM:SS)
    """
    return datetime.now().strftime('%H:%M:%S')

def create_debug_dir():
    """
    Cria um diretório para arquivos de debug.
    
    Returns:
        str: Caminho para o diretório de debug
    """
    debug_dir = "debug"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    return debug_dir

def log_to_file(message, log_file="debug/log.txt"):
    """
    Adiciona uma mensagem ao arquivo de log.
    
    Args:
        message (str): Mensagem a ser registrada
        log_file (str, optional): Caminho para o arquivo de log. Padrão: "debug/log.txt"
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Criar diretório de debug se necessário
    debug_dir = os.path.dirname(log_file)
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    # Adicionar a mensagem ao arquivo
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def measure_execution_time(func):
    """
    Decorator para medir o tempo de execução de uma função.
    
    Args:
        func: Função a ser medida
        
    Returns:
        function: Função decorada
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Função {func.__name__} executada em {execution_time:.4f} segundos")
        return result
    return wrapper
