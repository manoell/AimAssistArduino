import os
import sys
from datetime import datetime
import colorama
from colorama import Fore, Style

colorama.init()

def clear_console():
    """Limpa o console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Imprime o banner do programa."""
    banner = """
█████╗ ██╗███╗   ███╗      █████╗ ███████╗███████╗██╗███████╗████████╗
██╔══██╗██║████╗ ████║     ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝
███████║██║██╔████╔██║     ███████║███████╗███████╗██║███████╗   ██║   
██╔══██║██║██║╚██╔╝██║     ██╔══██║╚════██║╚════██║██║╚════██║   ██║   
██║  ██║██║██║ ╚═╝ ██║     ██║  ██║███████║███████║██║███████║   ██║   
╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   
"""
    print(banner)

def print_status(status_type, message, end="\n"):
    """
    Imprime uma mensagem de status formatada.
    
    Args:
        status_type: Tipo de status (INFO, SUCESSO, AVISO, ERRO)
        message: Mensagem a ser exibida
        end: Caractere final da linha (padrão: nova linha)
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    
    if status_type == "INFO":
        color = Fore.BLUE
    elif status_type == "SUCESSO":
        color = Fore.GREEN
    elif status_type == "AVISO":
        color = Fore.YELLOW
    elif status_type == "ERRO":
        color = Fore.RED
    else:
        color = Fore.WHITE
    
    print(f"[{current_time}] [{color}{status_type}{Style.RESET_ALL}] {message}", end=end)
    sys.stdout.flush()

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
