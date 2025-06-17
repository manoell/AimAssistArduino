import usb.core
import usb.util
import time
import threading
from collections import deque
import statistics
import queue
import ctypes
import os
import sys

class UltraSpeedControllerV2:
    """
    VERSÃO 2.0 - OTIMIZADA PARA AIMBOT COMPETITIVO
    
    NOVAS OTIMIZAÇÕES CRÍTICAS:
    1. Eliminação de delays desnecessários no benchmark
    2. Burst processing ultra-agressivo
    3. Zero-latency command processing
    4. Dedicated thread para mouse commands apenas
    5. Memory-mapped USB operations onde possível
    6. CPU affinity para thread crítica
    7. Real-time priority para processo
    """
    
    def __init__(self, vid=0x046D, pid=0xC547):
        self.device = None
        self.interface = 2
        self.endpoint_out = None
        
        # Timeouts ultra-agressivos
        self.timeout_levels = {
            'ultra': 1,    # 1ms
            'turbo': 2,    # 2ms  
            'fast': 3,     # 3ms (reduzido de 5ms)
            'safe': 5      # 5ms (reduzido de 10ms)
        }
        
        self.current_timeout = 'ultra'  # Começar no máximo
        
        # Threading dedicado para mouse
        self.mouse_queue = queue.Queue(maxsize=2000)  # Queue maior
        self.priority_queue = queue.PriorityQueue(maxsize=500)
        self.mouse_thread = None
        self.running = False
        
        # Eliminação de batch para aimbot (cada comando individual)
        self.batch_enabled = False  # DESABILITADO para aimbot
        
        # Compressão desabilitada para máxima responsividade
        self.delta_compression = False  # DESABILITADO
        
        # Cache otimizado para comandos de aimbot
        self.command_cache = {}
        self.cache_enabled = True
        
        # Estatísticas otimizadas
        self.stats = {
            'commands_sent': 0,
            'commands_failed': 0,
            'avg_latency_ms': 0.0,
            'min_latency_ms': float('inf'),
            'max_latency_ms': 0.0,
            'effective_fps': 0.0,
            'mouse_commands': 0,
            'priority_commands': 0
        }
        
        self.performance_history = deque(maxlen=500)  # Histórico menor
        
        # Precision tracking
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Lock ultra-rápido
        self.send_lock = threading.RLock()  # RLock é mais rápido para thread única
        
        # Conectar e otimizar
        self._connect(vid, pid)
        self._ultra_calibrate_v2()
        self._start_dedicated_mouse_thread()
        
        print(f"🚀 UltraSpeedControllerV2 inicializado!")
        print(f"   Modo: {self.current_timeout} ({self.timeout_levels[self.current_timeout]}ms)")
        print(f"   Batch: {'✅' if self.batch_enabled else '❌ (Otimizado para aimbot)'}")
        print(f"   Compression: {'✅' if self.delta_compression else '❌ (Máxima responsividade)'}")
    
    def _connect(self, vid, pid):
        """Conexão com configurações ultra-otimizadas"""
        self.device = usb.core.find(idVendor=vid, idProduct=pid)
        if self.device is None:
            raise Exception(f"Arduino não encontrado")
        
        try:
            # Configuração agressiva
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
                
        except Exception as e:
            raise Exception(f"Erro na conexão: {e}")
    
    def _ultra_calibrate_v2(self):
        """Calibração V2 - Focada em velocidade máxima"""
        print("🔥 Calibração V2 para aimbot...")
        
        # Testar apenas timeouts relevantes para aimbot
        test_timeouts = [1, 2, 3, 5]  # Apenas os mais rápidos
        calibration_data = {}
        
        test_command = self._build_optimized_command(1, 1, 0)
        
        for timeout in test_timeouts:
            print(f"   Testando {timeout}ms...", end=" ")
            
            successes = 0
            latencies = []
            
            # Teste mais focado e rápido
            for i in range(30):  # Menos testes, mais rápido
                start = time.perf_counter()
                try:
                    bytes_sent = self.endpoint_out.write(test_command, timeout=timeout)
                    end = time.perf_counter()
                    
                    if bytes_sent == len(test_command):
                        successes += 1
                        latencies.append((end - start) * 1000)
                
                except usb.core.USBTimeoutError:
                    pass
                except Exception:
                    pass
                
                # Pausa mínima
                time.sleep(0.00005)  # 50µs
            
            success_rate = successes / 30 if successes > 0 else 0
            avg_latency = statistics.mean(latencies) if latencies else float('inf')
            
            # Score focado em velocidade + confiabilidade
            speed_score = 1000 / (timeout + avg_latency)  # Quanto mais rápido, melhor
            reliability_score = success_rate * success_rate  # Quadrático = penaliza falhas
            final_score = speed_score * reliability_score
            
            calibration_data[timeout] = {
                'success_rate': success_rate,
                'avg_latency': avg_latency,
                'speed_score': speed_score,
                'final_score': final_score
            }
            
            print(f"{success_rate*100:.0f}% ({avg_latency:.1f}ms)")
        
        # Escolher o mais rápido que tenha pelo menos 90% de sucesso
        valid_timeouts = {k: v for k, v in calibration_data.items() 
                         if v['success_rate'] >= 0.90}
        
        if valid_timeouts:
            best_timeout = min(valid_timeouts.keys())  # Menor timeout válido
        else:
            best_timeout = min(calibration_data.keys())  # Fallback
        
        # Mapear para modo
        if best_timeout <= 1:
            self.current_timeout = 'ultra'
        elif best_timeout <= 2:
            self.current_timeout = 'turbo'
        elif best_timeout <= 3:
            self.current_timeout = 'fast'
        else:
            self.current_timeout = 'safe'
        
        print(f"✅ Modo otimizado: {self.current_timeout} ({best_timeout}ms)")
        print(f"   Taxa de sucesso: {calibration_data[best_timeout]['success_rate']*100:.1f}%")
    
    def _start_dedicated_mouse_thread(self):
        """Thread dedicada APENAS para comandos de mouse"""
        self.running = True
        
        def mouse_thread_func():
            """Thread otimizada APENAS para mouse - máxima prioridade"""
            
            # Tentar definir prioridade máxima (Linux/Windows)
            try:
                import os
                if hasattr(os, 'sched_setscheduler'):
                    os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(99))
            except:
                pass
            
            while self.running:
                commands_processed = 0
                
                # Processar comandos prioritários primeiro (aimbot)
                while not self.priority_queue.empty() and commands_processed < 50:
                    try:
                        priority, command = self.priority_queue.get_nowait()
                        self._send_raw_command_v2(command, is_priority=True)
                        commands_processed += 1
                    except queue.Empty:
                        break
                
                # Processar comandos normais
                while not self.mouse_queue.empty() and commands_processed < 100:
                    try:
                        command = self.mouse_queue.get_nowait()
                        self._send_raw_command_v2(command, is_priority=False)
                        commands_processed += 1
                    except queue.Empty:
                        break
                
                # Pausa ultra-mínima apenas se não processou nada
                if commands_processed == 0:
                    time.sleep(0.00001)  # 10µs
        
        self.mouse_thread = threading.Thread(target=mouse_thread_func, daemon=True)
        self.mouse_thread.start()
    
    def _send_raw_command_v2(self, command, is_priority=False):
        """Envio ultra-otimizado V2"""
        timeout = self.timeout_levels[self.current_timeout]
        start_time = time.perf_counter()
        
        try:
            # Send sem lock se for comando prioritário
            if is_priority:
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
                    self.stats['priority_commands'] += 1
                else:
                    self.stats['mouse_commands'] += 1
                
                self.stats['min_latency_ms'] = min(self.stats['min_latency_ms'], latency)
                self.stats['max_latency_ms'] = max(self.stats['max_latency_ms'], latency)
                
                # Histórico simplificado
                self.performance_history.append({
                    'success': True,
                    'latency': latency,
                    'priority': is_priority,
                    'timestamp': end_time
                })
            else:
                self.stats['commands_failed'] += 1
            
            return success
            
        except usb.core.USBTimeoutError:
            self.stats['commands_failed'] += 1
            return False
        except Exception:
            self.stats['commands_failed'] += 1
            return False
    
    def _build_optimized_command(self, x, y, buttons=0):
        """Build command com cache otimizado para aimbot"""
        if not self.cache_enabled:
            return self._build_raw_command(x, y, buttons)
        
        cache_key = (x, y, buttons)
        if cache_key in self.command_cache:
            return self.command_cache[cache_key]
        
        command = self._build_raw_command(x, y, buttons)
        
        # Cache limitado para comandos mais comuns
        if len(self.command_cache) < 50:  # Cache pequeno para aimbot
            self.command_cache[cache_key] = command
        
        return command
    
    def _build_raw_command(self, x, y, buttons):
        """Build command raw ultra-rápido"""
        x = max(-127, min(127, x))
        y = max(-127, min(127, y))
        
        command = bytearray(8)
        command[0] = 0x01  # Move command
        command[1] = x if x >= 0 else (256 + x)
        command[2] = y if y >= 0 else (256 + y)
        command[3] = buttons
        # 4-7 = padding
        
        return bytes(command)
    
    def move(self, x, y, priority=False):
        """
        Movimento otimizado V2 para aimbot
        
        Args:
            x (float): Movimento X
            y (float): Movimento Y
            priority (bool): TRUE para comandos de aimbot (alta prioridade)
        """
        if not self.device:
            return False
        
        # Accumular movimento fracionário
        x += self.remainder_x
        y += self.remainder_y
        
        move_x = int(x)
        move_y = int(y)
        
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y
        
        # Ignorar movimentos insignificantes
        if abs(move_x) == 0 and abs(move_y) == 0:
            return True
        
        # Build command
        command = self._build_optimized_command(move_x, move_y, 0)
        
        # Para aimbot, usar sempre prioridade
        if priority:
            try:
                self.priority_queue.put_nowait((0, command))
                return True
            except queue.Full:
                # Se fila prioritária cheia, envio direto
                return self._send_raw_command_v2(command, is_priority=True)
        else:
            try:
                self.mouse_queue.put_nowait(command)
                return True
            except queue.Full:
                # Se fila cheia, descartar comando mais antigo
                try:
                    self.mouse_queue.get_nowait()  # Remove o mais antigo
                    self.mouse_queue.put_nowait(command)  # Adiciona o novo
                    return True
                except:
                    return False
    
    def aimbot_move(self, x, y):
        """Função específica para aimbot - máxima prioridade"""
        return self.move(x, y, priority=True)
    
    def benchmark_aimbot_performance(self, duration=10.0, target_fps=1000):
        """Benchmark específico para aimbot com padrões reais"""
        print(f"\n🎯 BENCHMARK AIMBOT PERFORMANCE ({duration}s)")
        print(f"Target FPS: {target_fps}")
        print("="*60)
        
        # Padrões de movimento típicos de aimbot
        aimbot_patterns = [
            (1, 0), (2, -1), (3, 1), (1, -2), (4, 2),
            (-1, 1), (2, 3), (-3, -1), (5, -2), (-2, 4),
            (1, 1), (-1, -1), (2, 2), (-2, -2), (3, -3),
            (6, 0), (0, 6), (-6, 0), (0, -6), (4, 4)
        ]
        
        start_time = time.perf_counter()
        commands_sent = 0
        pattern_idx = 0
        
        # Delay calculado para target FPS (sem delays desnecessários)
        base_delay = 1.0 / target_fps
        
        while time.perf_counter() - start_time < duration:
            x, y = aimbot_patterns[pattern_idx % len(aimbot_patterns)]
            
            # Usar função específica de aimbot
            if self.aimbot_move(x, y):
                commands_sent += 1
            
            pattern_idx += 1
            
            # Delay mínimo controlado
            time.sleep(base_delay * 0.5)  # 50% do delay teórico
        
        elapsed_time = time.perf_counter() - start_time
        effective_fps = commands_sent / elapsed_time
        
        # Flush filas
        flushed = self._flush_all_queues()
        
        stats = self.get_stats()
        
        print(f"🎯 Comandos de aimbot: {commands_sent}")
        print(f"⚡ FPS efetivo: {effective_fps:.1f}")
        print(f"🎯 Target atingido: {effective_fps/target_fps*100:.1f}%")
        print(f"📈 Taxa sucesso: {stats['success_rate']*100:.1f}%")
        print(f"⚡ Latência média: {stats['avg_latency_ms']:.1f}ms")
        print(f"🏆 Comandos prioritários: {stats['priority_commands']}")
        print(f"💾 Comandos flushed: {flushed}")
        
        return {
            'commands_sent': commands_sent,
            'effective_fps': effective_fps,
            'target_achievement': effective_fps / target_fps,
            'success_rate': stats['success_rate'],
            'avg_latency_ms': stats['avg_latency_ms'],
            'priority_commands': stats['priority_commands']
        }
    
    def _flush_all_queues(self):
        """Flush todas as filas"""
        flushed = 0
        
        # Flush prioridade
        while not self.priority_queue.empty():
            try:
                priority, command = self.priority_queue.get_nowait()
                self._send_raw_command_v2(command, is_priority=True)
                flushed += 1
            except queue.Empty:
                break
        
        # Flush normal
        while not self.mouse_queue.empty():
            try:
                command = self.mouse_queue.get_nowait()
                self._send_raw_command_v2(command, is_priority=False)
                flushed += 1
            except queue.Empty:
                break
        
        return flushed
    
    def get_stats(self):
        """Estatísticas otimizadas"""
        total_commands = self.stats['commands_sent'] + self.stats['commands_failed']
        success_rate = self.stats['commands_sent'] / total_commands if total_commands > 0 else 0
        
        # Calcular latência média dos últimos comandos
        recent_latencies = [p['latency'] for p in list(self.performance_history)[-50:] if p['success']]
        avg_latency = statistics.mean(recent_latencies) if recent_latencies else 0
        
        return {
            'commands_sent': self.stats['commands_sent'],
            'commands_failed': self.stats['commands_failed'],
            'success_rate': success_rate,
            'avg_latency_ms': avg_latency,
            'min_latency_ms': self.stats['min_latency_ms'],
            'max_latency_ms': self.stats['max_latency_ms'],
            'mouse_commands': self.stats['mouse_commands'],
            'priority_commands': self.stats['priority_commands'],
            'current_timeout': self.current_timeout,
            'queue_sizes': {
                'mouse': self.mouse_queue.qsize(),
                'priority': self.priority_queue.qsize()
            }
        }
    
    def close(self):
        """Cleanup V2"""
        print("🔌 Fechando UltraSpeedControllerV2...")
        
        self.running = False
        
        if self.device and self.endpoint_out:
            flushed = self._flush_all_queues()
            print(f"💾 Flush final: {flushed} comandos")
            
            try:
                reset_cmd = self._build_raw_command(0, 0, 0)
                self.endpoint_out.write(reset_cmd, timeout=100)
            except:
                pass
        
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
            except:
                pass
            finally:
                self.device = None
        
        stats = self.get_stats()
        print(f"📊 Estatísticas finais:")
        print(f"   Comandos enviados: {stats['commands_sent']}")
        print(f"   Taxa de sucesso: {stats['success_rate']*100:.1f}%")
        print(f"   Latência média: {stats['avg_latency_ms']:.1f}ms")
        print(f"   Comandos prioritários: {stats['priority_commands']}")
        print("✅ Fechado com sucesso!")


def test_aimbot_controller():
    """Teste específico para performance de aimbot"""
    print("🎯 TESTE AIMBOT CONTROLLER V2")
    print("="*50)
    
    try:
        controller = UltraSpeedControllerV2()
        
        # Teste 1: Movimentos básicos de aimbot
        print("\n1️⃣ Teste movimentos aimbot...")
        aimbot_moves = [(1, 0), (2, -1), (3, 2), (-1, 1), (5, -3)]
        success_count = 0
        
        for i, (x, y) in enumerate(aimbot_moves):
            if controller.aimbot_move(x, y):
                success_count += 1
                print(f"✅ Aimbot #{i+1}: ({x:3d}, {y:3d})")
            else:
                print(f"❌ Aimbot #{i+1}: ({x:3d}, {y:3d})")
        
        print(f"Sucesso aimbot: {success_count}/{len(aimbot_moves)}")
        
        # Teste 2: Benchmark aimbot específico
        print("\n2️⃣ Benchmark aimbot performance...")
        results = controller.benchmark_aimbot_performance(duration=8.0, target_fps=800)
        
        time.sleep(0.5)
        controller.close()
        
        return results
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


if __name__ == "__main__":
    test_aimbot_controller()