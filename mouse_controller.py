import usb.core
import usb.util
import time
import threading
import struct

class MouseController:
    """
    Controlador Raw HID para comunicação de ultra-baixa latência.
    Usa endpoint OUT dedicado para bypass completo do driver HID do sistema.
    
    Esta versão substitui completamente a comunicação serial COM,
    oferecendo latência sub-millisegundo para aimassist.
    """
    
    def __init__(self, vid=0x046D, pid=0xC547):
        """
        Inicializa conexão Raw HID direta.
        
        Args:
            vid (int): Vendor ID (padrão 0x046D = Logitech)
            pid (int): Product ID (padrão 0xC547 = USB Receiver)
        
        Raises:
            Exception: Se não conseguir conectar ao Arduino
        """
        self.device = None
        self.interface = 2  # Interface Generic HID
        self.endpoint_out = None
        self.endpoint_in = None
        self.lock = threading.Lock()
        
        # Variáveis para movimento fracionado
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Estatísticas de performance
        self.commands_sent = 0
        self.last_command_time = 0
        
        # Conectar ao dispositivo
        self._connect(vid, pid)
        
        print(f"🚀 MouseController Raw HID inicializado com sucesso!")
    
    def _connect(self, vid, pid):
        """
        Conecta ao dispositivo USB usando Raw HID
        
        Args:
            vid (int): Vendor ID
            pid (int): Product ID
            
        Raises:
            Exception: Se não conseguir conectar
        """
        print("🔍 Conectando via Raw HID...")
        
        # Encontrar dispositivo
        self.device = usb.core.find(idVendor=vid, idProduct=pid)
        if self.device is None:
            raise Exception(f"Arduino não encontrado (VID: {vid:04X}, PID: {pid:04X})")
        
        print(f"✅ Arduino encontrado: {self.device.manufacturer} {self.device.product}")
        
        # Configurar dispositivo
        try:
            # Desanexar driver kernel se estiver ativo
            try:
                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)
                    print("📤 Driver kernel desanexado")
            except NotImplementedError:
                # Windows não implementa isso
                pass
            except Exception:
                pass  # Ignorar erros de desanexar
            
            # Configurar dispositivo
            self.device.set_configuration()
            
            # Fazer claim da interface 2 (Generic HID)
            usb.util.claim_interface(self.device, self.interface)
            print(f"🎯 Interface {self.interface} configured")
            
            # Encontrar endpoints
            cfg = self.device.get_active_configuration()
            interface_cfg = cfg[(self.interface, 0)]
            
            # Encontrar endpoints IN e OUT
            for endpoint in interface_cfg:
                addr = endpoint.bEndpointAddress
                if usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_OUT:
                    self.endpoint_out = endpoint
                    print(f"📥 Endpoint OUT: 0x{addr:02X}")
                elif usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_IN:
                    self.endpoint_in = endpoint
                    print(f"📤 Endpoint IN: 0x{addr:02X}")
            
            if not self.endpoint_out:
                raise Exception("Endpoint OUT não encontrado na Interface 2!")
            
            print("🚀 Raw HID configurado com sucesso!")
            
        except usb.core.USBError as e:
            if "busy" in str(e).lower() or "access" in str(e).lower():
                raise Exception(
                    "Interface ocupada por outro driver! "
                    "Desconecte e reconecte o Arduino, depois tente novamente."
                )
            else:
                raise Exception(f"Erro USB: {e}")
        except Exception as e:
            raise Exception(f"Erro ao configurar Raw HID: {e}")
    
    def move(self, x, y):
        """
        Move o mouse com latência ultra-baixa.
        
        Args:
            x (float): Movimento X (pode ser fracionário)
            y (float): Movimento Y (pode ser fracionário)
        """
        if not self.device:
            return
        
        # Adicionar resto do movimento anterior para preservar precisão
        x += self.remainder_x
        y += self.remainder_y
        
        # Converter para inteiros
        move_x = int(x)
        move_y = int(y)
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y
        
        # Se não há movimento efetivo, não enviar comando
        if move_x == 0 and move_y == 0:
            return
        
        # Construir comando otimizado
        command = self._build_movement_command(move_x, move_y)
        
        # Enviar com Thread Lock para máxima velocidade
        with self.lock:
            try:
                # Timeout ultra-baixo para evitar bloqueios em alta velocidade
                bytes_sent = self.endpoint_out.write(command, timeout=50)
                
                if bytes_sent == len(command):
                    self.commands_sent += 1
                    self.last_command_time = time.time()
                else:
                    print(f"⚠️ Apenas {bytes_sent}/{len(command)} bytes enviados")
                    
            except usb.core.USBTimeoutError:
                # Timeout é aceitável em operações de alta velocidade
                # O importante é não bloquear o sistema
                pass
            except Exception as e:
                print(f"❌ Erro ao enviar movimento: {e}")
    
    def _build_movement_command(self, x, y, buttons=0, wheel=0):
        """
        Constrói comando binário otimizado para movimento.
        
        Formato do protocolo:
        [0x01][x_low][x_high][y_low][y_high][buttons][wheel][...padding...]
        
        Total: 64 bytes (tamanho do endpoint)
        
        Args:
            x (int): Movimento X (-32767 a 32767)
            y (int): Movimento Y (-32767 a 32767)
            buttons (int): Estado dos botões (opcional)
            wheel (int): Movimento da roda (opcional)
            
        Returns:
            bytes: Comando de 64 bytes pronto para envio
        """
        # Garantir que x e y estão no range válido
        x = max(-32767, min(32767, x))
        y = max(-32767, min(32767, y))
        
        # Converter para unsigned 16-bit (little endian)
        # Usar complemento de 2 para valores negativos
        if x < 0:
            x = 65536 + x
        if y < 0:
            y = 65536 + y
        
        # Construir comando de 64 bytes
        command = bytearray(64)
        command[0] = 0x01           # Tipo: movimento do mouse
        command[1] = x & 0xFF       # X low byte
        command[2] = (x >> 8) & 0xFF # X high byte  
        command[3] = y & 0xFF       # Y low byte
        command[4] = (y >> 8) & 0xFF # Y high byte
        command[5] = buttons        # Botões do mouse
        command[6] = wheel & 0xFF   # Roda do mouse
        # Bytes 7-63 ficam zerados (padding)
        
        return bytes(command)
    
    def click(self, button=1):
        """
        Envia comando de clique otimizado
        
        Args:
            button (int): Botão a clicar (1=esquerdo, 2=direito, 4=meio)
        """
        if not self.device:
            return
        
        # Comando de clique
        command = bytearray(64)
        command[0] = 0x02    # Tipo: clique
        command[1] = button  # Botão
        
        with self.lock:
            try:
                self.endpoint_out.write(command, timeout=100)
                self.commands_sent += 1
                self.last_command_time = time.time()
            except Exception as e:
                print(f"❌ Erro ao enviar clique: {e}")
    
    def reset(self):
        """
        Envia comando de reset para zerar estado do mouse
        """
        if not self.device:
            return
        
        # Comando de reset
        command = bytearray(64)
        command[0] = 0x04  # Tipo: reset
        
        with self.lock:
            try:
                self.endpoint_out.write(command, timeout=100)
                self.commands_sent += 1
                self.last_command_time = time.time()
                
                # Reset também das variáveis locais
                self.remainder_x = 0.0
                self.remainder_y = 0.0
                
            except Exception as e:
                print(f"❌ Erro ao enviar reset: {e}")
    
    def get_status(self):
        """
        Lê status do Arduino via endpoint IN (opcional)
        
        Returns:
            dict: Status do Arduino ou None se não disponível
        """
        if not self.endpoint_in:
            return None
        
        try:
            data = self.endpoint_in.read(64, timeout=100)
            if len(data) >= 8 and data[0] == 0xAA:
                return {
                    'signature': data[0],
                    'comm_status': data[1],
                    'last_command': data[2],
                    'commands_received': data[3] | (data[4] << 8),
                    'accumulated_x': int(data[5]) if data[5] < 128 else int(data[5]) - 256,
                    'accumulated_y': int(data[6]) if data[6] < 128 else int(data[6]) - 256,
                    'mouse_buttons': data[7]
                }
        except usb.core.USBTimeoutError:
            # Timeout é normal para leitura de status
            pass
        except Exception as e:
            print(f"⚠️ Erro ao ler status: {e}")
        
        return None
    
    def get_performance_stats(self):
        """
        Retorna estatísticas de performance
        
        Returns:
            dict: Estatísticas de uso
        """
        current_time = time.time()
        return {
            'commands_sent': self.commands_sent,
            'last_command_age': current_time - self.last_command_time if self.last_command_time > 0 else None,
            'connected': self.is_connected()
        }
    
    def is_connected(self):
        """
        Verifica se ainda está conectado ao Arduino
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        try:
            # Teste rápido de conectividade
            return self.device is not None and self.endpoint_out is not None
        except:
            return False
    
    def close(self):
        """
        Fecha conexão e libera recursos USB
        """
        if self.device:
            try:
                # Enviar reset antes de fechar
                if self.endpoint_out:
                    try:
                        reset_cmd = bytearray(64)
                        reset_cmd[0] = 0x04
                        self.endpoint_out.write(reset_cmd, timeout=100)
                    except:
                        pass
                
                # Liberar interface e recursos
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
                print("🔌 Conexão Raw HID fechada")
            except:
                pass  # Ignorar erros de cleanup
            finally:
                self.device = None
                self.endpoint_out = None
                self.endpoint_in = None
    
    def __del__(self):
        """
        Destructor - garante cleanup de recursos
        """
        self.close()


# Classe de compatibilidade para facilitar migração
class SerialMouseController(MouseController):
    """
    Wrapper de compatibilidade que mantém a interface da versão serial
    mas usa Raw HID internamente para máxima performance.
    """
    
    def __init__(self, com_port=None, baudrate=115200):
        """
        Inicializa usando Raw HID (ignora parâmetros de porta serial)
        
        Args:
            com_port: Ignorado (mantido para compatibilidade)
            baudrate: Ignorado (mantido para compatibilidade)
        """
        # Avisar sobre a mudança
        if com_port:
            print(f"⚠️ Nota: Ignorando COM port {com_port}")
            print("🚀 Usando Raw HID para máxima performance!")
        
        # Chamar construtor da classe base (Raw HID)
        super().__init__()


# Para compatibilidade total, exportar a classe serial como padrão
# Isso permite usar a nova versão Raw HID sem alterar o código principal
MouseController = SerialMouseController
