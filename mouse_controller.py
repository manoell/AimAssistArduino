import serial
import serial.tools.list_ports
import time
import threading
import random
from utils import print_status, log_to_file

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
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Variáveis para gerenciar movimento fracionado
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Iniciar watchdog para monitorar a conexão
        self.watchdog_active = True
        self.watchdog_thread = threading.Thread(target=self._connection_watchdog, daemon=True)
        self.last_communication = time.time()
        
        # Se a porta COM não for especificada, tenta detectar automaticamente
        if not com_port:
            com_port = self._find_arduino_port()
        else:
            print_status("INFO", f"Usando porta COM fornecida: {com_port}")
        
        # Tenta estabelecer conexão
        self._connect(com_port)
        
        # Inicia o watchdog após conectar
        self.watchdog_thread.start()
    
    def _find_arduino_port(self):
        """
        Tenta encontrar automaticamente a porta COM do Arduino.
        
        Returns:
            str: Porta COM do Arduino se encontrado
            
        Raises:
            Exception: Se nenhum Arduino for encontrado
        """
        print_status("INFO", "Procurando Arduino nas portas COM disponíveis...")
        arduino_ports = []
        
        # Listar todas as portas disponíveis
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        print_status("INFO", f"Portas disponíveis: {', '.join(available_ports)}")
        
        # Buscar portas com "Arduino" ou "USB Serial" na descrição
        for port in serial.tools.list_ports.comports():
            description = port.description.lower()
            if any(identifier.lower() in description for identifier in 
                  ["arduino", "usb serial", "ch340", "leonardo", "usb-serial"]):
                arduino_ports.append(port.device)
                print_status("INFO", f"Possível Arduino encontrado: {port.device} ({port.description})")
        
        # Se encontrar múltiplas portas, tenta cada uma
        for port in arduino_ports:
            try:
                print_status("INFO", f"Tentando conectar ao Arduino na porta {port}...")
                # Tenta estabelecer conexão
                test_port = serial.Serial(port, self.baudrate, timeout=2)
                
                # Aguarda 2 segundos para o Leonardo inicializar completamente
                time.sleep(2)
                
                # Limpar buffer antes de enviar/receber
                test_port.reset_input_buffer()
                test_port.reset_output_buffer()
                
                # Tenta obter resposta do Arduino (handshake)
                # Lê qualquer mensagem de boas-vindas
                if test_port.in_waiting:
                    welcome_msg = test_port.readline().decode('ascii', errors='ignore').strip()
                    print_status("INFO", f"Mensagem recebida: {welcome_msg}")
                    if "ARDUINO_MOUSE_READY" in welcome_msg:
                        print_status("SUCESSO", f"Arduino detectado na porta {port}")
                        test_port.close()
                        return port
                
                # Se não recebeu resposta, envia PING e espera PONG
                test_port.write(b"PING\n")
                time.sleep(0.5)
                
                if test_port.in_waiting:
                    response = test_port.readline().decode('ascii', errors='ignore').strip()
                    if response == "PONG":
                        print_status("SUCESSO", f"Arduino respondeu na porta {port}")
                        test_port.close()
                        return port
                
                # Se chegou aqui, não recebeu resposta esperada
                test_port.close()
                
            except Exception as e:
                print_status("AVISO", f"Falha ao testar porta {port}: {e}")
                continue
        
        # Se não encontrar nenhuma porta compatível
        if not arduino_ports:
            # Tenta todas as portas disponíveis como último recurso
            for port in available_ports:
                if port not in arduino_ports:
                    try:
                        print_status("INFO", f"Tentando porta alternativa {port}...")
                        test_port = serial.Serial(port, self.baudrate, timeout=2)
                        time.sleep(2)
                        test_port.reset_input_buffer()
                        test_port.write(b"PING\n")
                        time.sleep(0.5)
                        
                        if test_port.in_waiting:
                            response = test_port.readline().decode('ascii', errors='ignore').strip()
                            if response == "PONG" or "ARDUINO" in response:
                                print_status("SUCESSO", f"Arduino encontrado na porta alternativa {port}")
                                test_port.close()
                                return port
                        
                        test_port.close()
                    except:
                        pass
            
            raise Exception("Nenhum Arduino detectado! Verifique se está conectado corretamente.")
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
            print_status("INFO", f"Conectando ao Arduino na porta {com_port}...")
            
            # Tentar abrir a porta serial
            self.serial_port = serial.Serial(com_port, self.baudrate, timeout=2)
            
            # Pausa mais longa para o Leonardo inicializar completamente
            time.sleep(2)
            
            # Limpar qualquer dado residual
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            # Verificar se o Arduino envia uma mensagem de boas-vindas
            message_received = False
            start_time = time.time()
            while time.time() - start_time < 2:  # Espera até 2 segundos pela mensagem
                if self.serial_port.in_waiting:
                    welcome_msg = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if "ARDUINO_MOUSE_READY" in welcome_msg:
                        print_status("SUCESSO", "Arduino está pronto para receber comandos!")
                        message_received = True
                        break
                time.sleep(0.1)
            
            # Se não recebeu mensagem de boas-vindas, tenta PING
            if not message_received:
                print_status("INFO", "Não recebeu mensagem de boas-vindas, tentando PING...")
                self.serial_port.write(b"PING\n")
                time.sleep(0.5)
                
                if self.serial_port.in_waiting:
                    response = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if response == "PONG":
                        print_status("SUCESSO", "Arduino respondeu ao PING!")
                        message_received = True
            
            # Se ainda não recebeu resposta, Arduino pode não estar com o sketch correto
            if not message_received:
                print_status("AVISO", "Arduino não respondeu como esperado. Verificando compatibilidade...")
                # Tenta enviar um comando de movimento para ver se há resposta
                self.serial_port.write(b"M0,0\n")
                time.sleep(0.5)
                
                # Verifica qualquer resposta
                if self.serial_port.in_waiting:
                    response = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    print_status("INFO", f"Resposta do Arduino: {response}")
                    print_status("AVISO", "Arduino respondeu, mas não com o formato esperado. Continuando...")
                    message_received = True
                else:
                    print_status("AVISO", "Arduino não respondeu ao comando de teste.")
            
            # Se conseguiu qualquer tipo de comunicação, considera conectado
            if message_received or self.serial_port.is_open:
                self.connected = True
                self.last_communication = time.time()
                print_status("SUCESSO", f"Conectado ao Arduino na porta {com_port}")
                self.reconnect_attempts = 0
            else:
                raise Exception("Arduino não está respondendo corretamente")
            
        except serial.SerialException as e:
            error_msg = f"Erro ao conectar na porta {com_port}: {e}"
            print_status("ERRO", error_msg)
            log_to_file(error_msg)
            self.connected = False
            raise Exception(error_msg)
    
    def _connection_watchdog(self):
        """
        Thread que monitora a conexão com o Arduino e tenta reconectar se necessário.
        """
        while self.watchdog_active:
            # Verifica se a conexão está ativa
            if self.connected and self.serial_port and self.serial_port.is_open:
                # Verifica se não houve comunicação recente
                if time.time() - self.last_communication > 10:  # 10 segundos sem comunicação
                    try:
                        # Envia PING para verificar conexão
                        with self.lock:
                            self.serial_port.write(b"PING\n")
                        time.sleep(0.5)
                        
                        if self.serial_port.in_waiting:
                            response = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                            if response == "PONG":
                                # Conexão ainda está ativa
                                self.last_communication = time.time()
                            else:
                                print_status("AVISO", f"Resposta inesperada ao PING: {response}")
                        else:
                            print_status("AVISO", "Arduino não respondeu ao PING. Tentando reconectar...")
                            self._try_reconnect()
                    except Exception as e:
                        print_status("ERRO", f"Erro durante watchdog: {e}")
                        self._try_reconnect()
            
            # Verifica se precisa tentar reconectar
            elif not self.connected and self.reconnect_attempts < self.max_reconnect_attempts:
                self._try_reconnect()
            
            # Pausa antes da próxima verificação
            time.sleep(2)
    
    def _try_reconnect(self):
        """
        Tenta reconectar ao Arduino.
        """
        self.reconnect_attempts += 1
        print_status("INFO", f"Tentativa de reconexão {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        try:
            # Fechar a porta se estiver aberta
            if self.serial_port and self.serial_port.is_open:
                with self.lock:
                    self.serial_port.close()
            
            # Detectar porta automaticamente
            com_port = self._find_arduino_port()
            
            # Tenta conectar novamente
            self._connect(com_port)
            
            if self.connected:
                print_status("SUCESSO", "Reconectado com sucesso!")
                self.reconnect_attempts = 0
            
        except Exception as e:
            print_status("ERRO", f"Falha ao reconectar: {e}")
            
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                print_status("ERRO", "Número máximo de tentativas de reconexão atingido.")
                self.watchdog_active = False
    
    def move(self, x, y):
        """
        Move o mouse relativamente à posição atual.
        Gerencia movimentos fracionados acumulando-os até que formem um pixel inteiro.
        
        Args:
            x (float): Movimento no eixo X (pode ser fracionário)
            y (float): Movimento no eixo Y (pode ser fracionário)
            
        Returns:
            bool: True se o comando foi enviado com sucesso, False caso contrário
        """
        if not self.serial_port or not self.serial_port.is_open or not self.connected:
            return False
        
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
            return True
        
        # Enviar comando para o Arduino
        with self.lock:
            try:
                command = f"M{move_x},{move_y}\n"
                self.serial_port.write(command.encode())
                
                # Atualiza timestamp da última comunicação
                self.last_communication = time.time()
                
                # Opcional: tentar ler resposta de confirmação
                time.sleep(0.001)  # Pequena pausa para resposta chegar
                
                if self.serial_port.in_waiting:
                    response = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if response != "OK" and "error" in response.lower():
                        print_status("AVISO", f"Erro do Arduino: {response}")
                
                # Pequena variação aleatória no tempo para parecer mais humano
                time.sleep(random.uniform(0.001, 0.003))
                return True
                
            except serial.SerialException as e:
                error_msg = f"Erro ao enviar comando para o Arduino: {e}"
                print_status("ERRO", error_msg)
                log_to_file(error_msg)
                self.connected = False
                return False
    
    def click(self):
        """
        Envia comando para o Arduino clicar com o botão esquerdo do mouse.
        
        Returns:
            bool: True se o comando foi enviado com sucesso, False caso contrário
        """
        if not self.serial_port or not self.serial_port.is_open or not self.connected:
            return False
        
        with self.lock:
            try:
                self.serial_port.write(b"C\n")
                self.last_communication = time.time()
                return True
            except serial.SerialException as e:
                print_status("ERRO", f"Erro ao enviar comando de clique para o Arduino: {e}")
                self.connected = False
                return False
    
    def is_connected(self):
        """
        Verifica se o Arduino está conectado.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        return self.connected and self.serial_port is not None and self.serial_port.is_open
    
    def test_connection(self):
        """
        Testa a conexão com o Arduino enviando um PING.
        
        Returns:
            bool: True se o Arduino responder corretamente, False caso contrário
        """
        if not self.serial_port or not self.serial_port.is_open:
            return False
        
        with self.lock:
            try:
                self.serial_port.write(b"PING\n")
                time.sleep(0.5)
                
                if self.serial_port.in_waiting:
                    response = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if response == "PONG":
                        self.last_communication = time.time()
                        return True
                return False
            except:
                return False
    
    def close(self):
        """
        Fecha a conexão com o Arduino.
        """
        self.watchdog_active = False
        if self.watchdog_thread.is_alive():
            self.watchdog_thread.join(timeout=1.0)
        
        if self.serial_port and self.serial_port.is_open:
            with self.lock:
                self.serial_port.close()
                self.connected = False
    
    def __del__(self):
        """
        Destrutor da classe - garante que a porta serial seja fechada.
        """
        self.close()