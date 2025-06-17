"""
Mouse Controller Ultra-Otimizado para Aimbot
Substitui completamente a comunicação serial por Raw HID ultra-rápido
"""

import usb.core
import usb.util
import time
import threading
from collections import deque
import statistics
import queue
import random

class MouseController:
    """
    Controlador de Mouse Ultra-Otimizado para Aimbot
    
    Características:
    - Latência sub-milissegundo (1ms)
    - Threading assíncrono com prioridades
    - Raw HID direto (sem drivers)
    - Polling rate 1000Hz
    - Performance profissional para gaming
    """
    
    def __init__(self, com_port=None, baudrate=115200, vid=0x046D, pid=0xC547):
        """
        Inicializa o controlador Raw HID
        
        Args:
            com_port: Ignorado (mantido para compatibilidade)
            baudrate: Ignorado (mantido para compatibilidade)
            vid: Vendor ID do dispositivo (padrão: Logitech)
            pid: Product ID do dispositivo (padrão: USB Receiver)
        """
        if com_port:
            print(f"⚠️ Porta COM {com_port} ignorada - usando Raw HID ultra-rápido!")
        
        # Configuração do dispositivo
        self.device = None
        self.interface = 2
        self.endpoint_out = None
        self.vid = vid
        self.pid = pid
        
        # Humanização
        self.humanization_enabled = True
        self.jitter_enabled = True
        self.timing_variance_enabled = True
        self.last_move_time = 0
        
        # Configuração de timeouts otimizada
        self.timeout_levels = {
            'ultra': 1,    # 1ms - máxima performance
            'turbo': 2,    # 2ms - alta performance
            'fast': 3,     # 3ms - performance padrão
            'safe': 5      # 5ms - modo seguro
        }
        self.current_timeout = 'ultra'
        
        # Sistema de filas assíncronas
        self.mouse_queue = queue.Queue(maxsize=1000)
        self.priority_queue = queue.PriorityQueue(maxsize=200)
        self.mouse_thread = None
        self.running = False
        
        # Otimizações para aimbot
        self.batch_enabled = False      # Desabilitado para aimbot
        self.delta_compression = False  # Desabilitado para responsividade máxima
        
        # Cache de comandos
        self.command_cache = {}
        self.cache_enabled = True
        
        # Estatísticas de performance
        self.stats = {
            'commands_sent': 0,
            'commands_failed': 0,
            'avg_latency_ms': 0.0,
            'min_latency_ms': float('inf'),
            'max_latency_ms': 0.0,
            'aimbot_commands': 0,
            'success_rate': 0.0
        }
        
        # Histórico de performance
        self.performance_history = deque(maxlen=200)
        
        # Tracking de movimento fracionário
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Lock para threading
        self.send_lock = threading.RLock()
        
        # Conectar e inicializar
        self._connect()
        self._calibrate_performance()
        self._start_async_thread()
        
        print(f"✅ MouseController inicializado com sucesso!")
        print(f"   Dispositivo: {self.device.manufacturer} {self.device.product}")
        print(f"   Modo: {self.current_timeout} ({self.timeout_levels[self.current_timeout]}ms)")
        print(f"   Polling Rate: 1000Hz (1ms)")
    
    def _connect(self):
        """Conecta ao dispositivo USB"""
        print("🔍 Conectando ao Arduino via Raw HID...")
        
        self.device = usb.core.find(idVendor=self.vid, idProduct=self.pid)
        if self.device is None:
            raise Exception(f"Arduino não encontrado (VID: {self.vid:04X}, PID: {self.pid:04X})")
        
        try:
            # Configurar dispositivo
            try:
                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)
            except:
                pass
            
            self.device.set_configuration()
            usb.util.claim_interface(self.device, self.interface)
            
            # Encontrar endpoint OUT
            cfg = self.device.get_active_configuration()
            interface_cfg = cfg[(self.interface, 0)]
            
            for endpoint in interface_cfg:
                if endpoint.bEndpointAddress == 0x04:
                    self.endpoint_out = endpoint
                    break
            
            if not self.endpoint_out:
                raise Exception("Endpoint OUT não encontrado!")
            
            print(f"✅ Conectado com sucesso!")
            
        except Exception as e:
            raise Exception(f"Erro na conexão: {e}")
    
    def _calibrate_performance(self):
        """Calibra a performance do sistema"""
        print("⚡ Calibrando performance...")
        
        test_timeouts = [1, 2, 3, 5]
        calibration_data = {}
        
        test_command = self._build_command(1, 1, 0)
        
        for timeout in test_timeouts:
            successes = 0
            latencies = []
            
            for _ in range(20):
                start = time.perf_counter()
                try:
                    bytes_sent = self.endpoint_out.write(test_command, timeout=timeout)
                    end = time.perf_counter()
                    
                    if bytes_sent == len(test_command):
                        successes += 1
                        latencies.append((end - start) * 1000)
                
                except:
                    pass
                
                time.sleep(0.0001)
            
            success_rate = successes / 20
            avg_latency = statistics.mean(latencies) if latencies else float('inf')
            
            calibration_data[timeout] = {
                'success_rate': success_rate,
                'avg_latency': avg_latency
            }
        
        # Escolher o timeout mais rápido com >90% de sucesso
        best_timeout = None
        for timeout in sorted(test_timeouts):
            if calibration_data[timeout]['success_rate'] >= 0.9:
                best_timeout = timeout
                break
        
        if best_timeout:
            if best_timeout <= 1:
                self.current_timeout = 'ultra'
            elif best_timeout <= 2:
                self.current_timeout = 'turbo'
            elif best_timeout <= 3:
                self.current_timeout = 'fast'
            else:
                self.current_timeout = 'safe'
        
        print(f"✅ Calibração concluída: modo {self.current_timeout}")
    
    def _start_async_thread(self):
        """Inicia thread assíncrona para processamento"""
        self.running = True
        
        def async_sender():
            """Thread dedicada para envio de comandos"""
            while self.running:
                commands_processed = 0
                
                # Processar comandos prioritários (aimbot)
                while not self.priority_queue.empty() and commands_processed < 20:
                    try:
                        priority, command = self.priority_queue.get_nowait()
                        self._send_raw_command(command, is_priority=True)
                        commands_processed += 1
                    except queue.Empty:
                        break
                
                # Processar comandos normais
                while not self.mouse_queue.empty() and commands_processed < 50:
                    try:
                        command = self.mouse_queue.get_nowait()
                        self._send_raw_command(command, is_priority=False)
                        commands_processed += 1
                    except queue.Empty:
                        break
                
                # Pausa mínima se não processou nada
                if commands_processed == 0:
                    time.sleep(0.00001)  # 10µs
        
        self.mouse_thread = threading.Thread(target=async_sender, daemon=True)
        self.mouse_thread.start()
    
    def _build_command(self, x, y, buttons=0):
        """Constrói comando otimizado"""
        if self.cache_enabled:
            cache_key = (x, y, buttons)
            if cache_key in self.command_cache:
                return self.command_cache[cache_key]
        
        # Limitar valores
        x = max(-127, min(127, x))
        y = max(-127, min(127, y))
        
        # Construir comando de 8 bytes
        command = bytearray(8)
        command[0] = 0x01  # Tipo: movimento
        command[1] = x if x >= 0 else (256 + x)
        command[2] = y if y >= 0 else (256 + y)
        command[3] = buttons
        # Bytes 4-7: padding
        
        result = bytes(command)
        
        # Cache se habilitado
        if self.cache_enabled and len(self.command_cache) < 50:
            self.command_cache[cache_key] = result
        
        return result
    
    def _send_raw_command(self, command, is_priority=False):
        """Envia comando raw otimizado"""
        timeout = self.timeout_levels[self.current_timeout]
        start_time = time.perf_counter()
        
        try:
            if is_priority:
                # Comandos prioritários sem lock
                bytes_sent = self.endpoint_out.write(command, timeout=timeout)
            else:
                with self.send_lock:
                    bytes_sent = self.endpoint_out.write(command, timeout=timeout)
            
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000
            
            success = bytes_sent == len(command)
            
            # Atualizar estatísticas
            if success:
                self.stats['commands_sent'] += 1
                if is_priority:
                    self.stats['aimbot_commands'] += 1
                
                self.stats['min_latency_ms'] = min(self.stats['min_latency_ms'], latency)
                self.stats['max_latency_ms'] = max(self.stats['max_latency_ms'], latency)
                
                self.performance_history.append({
                    'success': True,
                    'latency': latency,
                    'priority': is_priority
                })
            else:
                self.stats['commands_failed'] += 1
            
            return success
            
        except Exception:
            self.stats['commands_failed'] += 1
            return False
    
    def move(self, x, y, priority=False):
        """
        Move o mouse
        
        Args:
            x (float): Movimento X
            y (float): Movimento Y
            priority (bool): True para comandos de aimbot (alta prioridade)
        """
        if not self.device:
            return False
        
        # Acumular movimento fracionário
        x += self.remainder_x
        y += self.remainder_y
        
        move_x = int(x)
        move_y = int(y)
        
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y
        
        # Ignorar movimentos muito pequenos
        if abs(move_x) == 0 and abs(move_y) == 0:
            return True
        
        # Construir comando
        command = self._build_command(move_x, move_y, 0)
        
        # Enviar com prioridade apropriada
        if priority:
            try:
                self.priority_queue.put_nowait((0, command))
                return True
            except queue.Full:
                return self._send_raw_command(command, is_priority=True)
        else:
            try:
                self.mouse_queue.put_nowait(command)
                return True
            except queue.Full:
                return False
    
    def click(self, button=1, priority=False):
        """
        Executa clique do mouse
        
        Args:
            button (int): Botão (1=esquerdo, 2=direito, 4=meio)
            priority (bool): True para alta prioridade
        """
        command = self._build_command(0, 0, button)
        
        if priority:
            try:
                self.priority_queue.put_nowait((0, command))
                return True
            except queue.Full:
                return self._send_raw_command(command, is_priority=True)
        else:
            try:
                self.mouse_queue.put_nowait(command)
                return True
            except queue.Full:
                return False
    
    def reset(self):
        """Reseta o estado do mouse"""
        command = bytearray(8)
        command[0] = 0x04  # Tipo: reset
        
        try:
            self.endpoint_out.write(command, timeout=100)
            self.remainder_x = 0.0
            self.remainder_y = 0.0
            return True
        except:
            return False
    
    def get_performance_stats(self):
        """Retorna estatísticas de performance"""
        total_commands = self.stats['commands_sent'] + self.stats['commands_failed']
        success_rate = self.stats['commands_sent'] / total_commands if total_commands > 0 else 0
        
        # Calcular latência média recente
        recent_latencies = [p['latency'] for p in list(self.performance_history)[-50:] if p['success']]
        avg_latency = statistics.mean(recent_latencies) if recent_latencies else 0
        
        return {
            'commands_sent': self.stats['commands_sent'],
            'commands_failed': self.stats['commands_failed'],
            'success_rate': success_rate,
            'avg_latency_ms': avg_latency,
            'min_latency_ms': self.stats['min_latency_ms'],
            'max_latency_ms': self.stats['max_latency_ms'],
            'aimbot_commands': self.stats['aimbot_commands'],
            'current_timeout': self.current_timeout,
            'queue_sizes': {
                'normal': self.mouse_queue.qsize(),
                'priority': self.priority_queue.qsize()
            }
        }
    
    def is_connected(self):
        """Verifica se ainda está conectado"""
        try:
            return self.device is not None and self.endpoint_out is not None
        except:
            return False
    
    def close(self):
        """Fecha a conexão"""
        print("🔌 Fechando MouseController...")
        
        self.running = False
        
        # Flush filas
        flushed = 0
        while not self.priority_queue.empty():
            try:
                priority, command = self.priority_queue.get_nowait()
                self._send_raw_command(command, is_priority=True)
                flushed += 1
            except:
                break
        
        while not self.mouse_queue.empty():
            try:
                command = self.mouse_queue.get_nowait()
                self._send_raw_command(command, is_priority=False)
                flushed += 1
            except:
                break
        
        if flushed > 0:
            print(f"💾 Flush final: {flushed} comandos")
        
        # Reset dispositivo
        if self.device and self.endpoint_out:
            try:
                reset_cmd = bytearray(8)
                reset_cmd[0] = 0x04
                self.endpoint_out.write(reset_cmd, timeout=100)
            except:
                pass
        
        # Cleanup USB
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
            except:
                pass
            finally:
                self.device = None
        
        print("✅ MouseController fechado com sucesso!")
    
    def __del__(self):
        """Destructor"""
        self.close()


# Função para compatibilidade com código antigo
def create_mouse_controller(com_port=None, baudrate=115200):
    """
    Cria um controlador de mouse (compatibilidade)
    
    Args:
        com_port: Ignorado (mantido para compatibilidade)
        baudrate: Ignorado (mantido para compatibilidade)
    
    Returns:
        MouseController: Instância do controlador
    """
    return MouseController(com_port=com_port, baudrate=baudrate)
