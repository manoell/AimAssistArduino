import serial
import serial.tools.list_ports
import time
import threading
import random

class MouseController:
    """
    Classe responsável por controlar o mouse via Arduino.
    Implementa comunicação serial otimizada e tratamento robusto de erros.
    """
    
    def __init__(self, com_port=None, baudrate=115200):
        """
        Inicializa o controlador de mouse.
        
        Args:
            com_port (str, optional): Porta COM para comunicação com Arduino.
                                     Se None, tenta detectar automaticamente.
            baudrate (int, optional): Taxa de transmissão. Padrão: 115200.
        
        Raises:
            Exception: Se não conseguir conectar ao Arduino.
        """
        self.baudrate = baudrate
        self.lock = threading.Lock()
        self.serial_port = None
        
        # Variáveis para gerenciar movimento fracionado
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Se a porta COM não for especificada, tenta detectar automaticamente
        if not com_port:
            com_port = self._find_arduino_port()
        
        # Tenta estabelecer conexão
        self._connect(com_port)
    
    def _find_arduino_port(self):
        """
        Tenta encontrar automaticamente a porta COM do Arduino.
        
        Returns:
            str: Porta COM do Arduino se encontrado
            
        Raises:
            Exception: Se nenhum Arduino for encontrado
        """
        arduino_ports = []
        
        # Buscar portas com "Arduino" ou "USB Serial" na descrição
        for port in serial.tools.list_ports.comports():
            if any(identifier in port.description for identifier in 
                  ["Arduino", "USB Serial", "CH340", "Leonardo", "USB-SERIAL"]):
                arduino_ports.append(port.device)
        
        # Se encontrar múltiplas portas, tenta cada uma
        for port in arduino_ports:
            try:
                # Teste rápido de conexão
                test_port = serial.Serial(port, self.baudrate, timeout=1)
                test_port.close()
                return port
            except:
                continue
        
        # Se não encontrar nenhuma porta compatível
        if not arduino_ports:
            raise Exception("Nenhum Arduino detectado!")
        else:
            raise Exception(f"Tentei conectar aos Arduinos nas portas {arduino_ports}, mas nenhum respondeu.")
    
    def _connect(self, com_port):
        """
        Estabelece conexão com o Arduino.
        
        Args:
            com_port (str): Porta COM para conexão
            
        Raises:
            Exception: Se não conseguir conectar
        """
        try:
            self.serial_port = serial.Serial(com_port, self.baudrate, timeout=1)
            
            # Pequena pausa para garantir que a conexão foi estabelecida
            time.sleep(0.5)
            
            # Limpar qualquer dado residual
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
        except serial.SerialException as e:
            raise Exception(f"Erro ao conectar na porta {com_port}: {e}")
    
    def move(self, x, y):
        """
        Move o mouse relativamente à posição atual.
        Gerencia movimentos fracionados acumulando-os até que formem um pixel inteiro.
        
        Args:
            x (float): Movimento no eixo X (pode ser fracionário)
            y (float): Movimento no eixo Y (pode ser fracionário)
        """
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        # Adicionar o resto do movimento anterior
        x += self.remainder_x
        y += self.remainder_y
        
        # Converter para inteiros e salvar o resto para o próximo movimento
        move_x = int(x)
        move_y = int(y)
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y
        
        # Se não houver movimento efetivo, não envia comando
        if move_x == 0 and move_y == 0:
            return
        
        # Enviar comando para o Arduino
        with self.lock:
            try:
                command = f"M{move_x},{move_y}\n"
                self.serial_port.write(command.encode())
                
                # Pequena variação aleatória no tempo para parecer mais humano
                time.sleep(random.uniform(0.001, 0.003))
                
            except serial.SerialException as e:
                print(f"Erro ao enviar comando para o Arduino: {e}")
                # Tentativa de reconexão automática poderia ser implementada aqui
    
    def click(self):
        """
        Envia comando para o Arduino clicar com o botão esquerdo do mouse.
        """
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        with self.lock:
            try:
                self.serial_port.write(b"C\n")
            except serial.SerialException as e:
                print(f"Erro ao enviar comando de clique para o Arduino: {e}")
    
    def is_connected(self):
        """
        Verifica se o Arduino está conectado.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        return self.serial_port is not None and self.serial_port.is_open
    
    def close(self):
        """
        Fecha a conexão com o Arduino.
        """
        if self.serial_port and self.serial_port.is_open:
            with self.lock:
                self.serial_port.close()
    
    def __del__(self):
        """
        Destrutor da classe - garante que a porta serial seja fechada.
        """
        self.close()
