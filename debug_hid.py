import usb.core
import usb.util
import time
import threading
from collections import deque
import statistics
import queue

class UltraOptimizedController:
    """
    Ultra-optimized controller explorando TODO o potencial identificado:
    
    Baseado nos resultados:
    - Ping: 0.8ms (conexão muito rápida!)
    - Comandos mais rápidos: 0.6ms (potencial enorme!)
    - Latência atual: 26ms (muito conservador)
    - Oportunidade: 40x mais rápido é possível!
    """
    
    def __init__(self, vid=0x046D, pid=0xC547):
        self.device = None
        self.interface = 2
        self.endpoint_out = None
        
        # Timeouts ultra-agressivos baseados nos dados
        self.ultra_timeout = 2    # 2ms (vs 0.8ms ping)
        self.turbo_timeout = 5    # 5ms (fallback)
        self.safe_timeout = 20    # 20ms (emergência)
        
        # Sistema de múltiplas velocidades
        self.current_mode = 'turbo'  # Começar mais agressivo
        self.mode_config = {
            'ultra': {'timeout': self.ultra_timeout, 'delay': 0.0005},   # 2000 FPS target
            'turbo': {'timeout': self.turbo_timeout, 'delay': 0.001},    # 1000 FPS target  
            'fast': {'timeout': 10, 'delay': 0.002},                     # 500 FPS target
            'safe': {'timeout': self.safe_timeout, 'delay': 0.005}       # 200 FPS target
        }
        
        # Threading para comando assíncrono
        self.command_queue = queue.Queue(maxsize=100)
        self.async_mode = False
        self.command_thread = None
        
        # Batch processing
        self.batch_size = 3
        self.batch_buffer = []
        self.batch_enabled = True
        
        # Métricas avançadas
        self.mode_stats = {mode: {'sent': 0, 'failed': 0, 'latencies': deque(maxlen=50)} 
                          for mode in self.mode_config.keys()}
        self.recent_performance = deque(maxlen=200)
        self.adaptive_cooldown = 0
        
        # Precisão fracionada
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        
        # Lock para threading
        self.lock = threading.Lock()
        
        # Conectar e otimizar
        self._connect(vid, pid)
        self._ultra_calibrate()
        self._start_adaptive_system()
        
        print(f"🔥 UltraOptimizedController inicializado!")
        print(f"   Modo inicial: {self.current_mode}")
        print(f"   Timeout: {self.mode_config[self.current_mode]['timeout']}ms")
        print(f"   Target FPS: {1000/self.mode_config[self.current_mode]['delay']:.0f}")
    
    def _connect(self, vid, pid):
        """Conecta com configurações ultra-otimizadas"""
        self.device = usb.core.find(idVendor=vid, idProduct=pid)
        if self.device is None:
            raise Exception("Arduino não encontrado")
        
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
            
        except Exception as e:
            raise Exception(f"Erro na conexão: {e}")
    
    def _ultra_calibrate(self):
        """Calibração ultra-agressiva explorando os limites"""
        print("🔥 Calibração ultra-agressiva...")
        
        # Testar timeouts extremamente baixos
        ultra_timeouts = [1, 2, 3, 5, 8, 10]  # ms
        test_command = bytearray([0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        calibration_results = {}
        
        for timeout in ultra_timeouts:
            print(f"   Testando {timeout}ms...", end=" ")
            
            successes = 0
            latencies = []
            
            for _ in range(30):  # Mais testes para precisão
                start = time.perf_counter()
                try:
                    bytes_sent = self.endpoint_out.write(test_command, timeout=timeout)
                    end = time.perf_counter()
                    
                    if bytes_sent == len(test_command):
                        successes += 1
                        latencies.append((end - start) * 1000)  # ms
                except:
                    pass
                
                time.sleep(0.0005)  # Pausa mínima
            
            success_rate = successes / 30
            avg_latency = statistics.mean(latencies) if latencies else float('inf')
            
            calibration_results[timeout] = {
                'success_rate': success_rate,
                'avg_latency': avg_latency,
                'samples': len(latencies)
            }
            
            print(f"{success_rate*100:.0f}% ({avg_latency:.1f}ms)")
        
        # Encontrar configurações ótimas
        ultra_timeout = None
        turbo_timeout = None
        
        for timeout, results in calibration_results.items():
            if results['success_rate'] >= 0.95 and not ultra_timeout:
                ultra_timeout = timeout
            if results['success_rate'] >= 0.80 and not turbo_timeout:
                turbo_timeout = timeout
        
        # Atualizar configurações
        if ultra_timeout:
            self.ultra_timeout = ultra_timeout
            self.mode_config['ultra']['timeout'] = ultra_timeout
            print(f"✅ Modo ultra otimizado: {ultra_timeout}ms")
        
        if turbo_timeout:
            self.turbo_timeout = turbo_timeout
            self.mode_config['turbo']['timeout'] = turbo_timeout
            print(f"✅ Modo turbo otimizado: {turbo_timeout}ms")
        
        # Ajustar modo inicial baseado na calibração
        if ultra_timeout and calibration_results[ultra_timeout]['success_rate'] >= 0.95:
            self.current_mode = 'ultra'
            print("🚀 Iniciando em modo ULTRA!")
        elif turbo_timeout:
            self.current_mode = 'turbo'
            print("⚡ Iniciando em modo TURBO!")
    
    def _start_adaptive_system(self):
        """Sistema adaptativo ultra-responsivo"""
        def adaptive_monitor():
            while hasattr(self, 'device') and self.device:
                time.sleep(0.5)  # Verificar a cada 500ms (muito mais frequente)
                self._ultra_adaptive_update()
        
        self.adaptive_thread = threading.Thread(target=adaptive_monitor, daemon=True)
        self.adaptive_thread.start()
    
    def _ultra_adaptive_update(self):
        """Sistema adaptativo ultra-responsivo"""
        if time.time() < self.adaptive_cooldown:
            return
        
        if len(self.recent_performance) < 20:
            return
        
        # Analisar performance recente
        recent_success = sum(1 for p in list(self.recent_performance)[-20:] if p['success'])
        success_rate = recent_success / 20
        
        # Mais agressivo na escalada
        if success_rate >= 0.98:  # 98% sucesso
            if self.current_mode == 'safe':
                self._switch_mode('fast')
            elif self.current_mode == 'fast':
                self._switch_mode('turbo')
            elif self.current_mode == 'turbo':
                self._switch_mode('ultra')
        
        # Mais conservador na descida
        elif success_rate < 0.85:  # 85% sucesso
            if self.current_mode == 'ultra':
                self._switch_mode('turbo')
            elif self.current_mode == 'turbo':
                self._switch_mode('fast')
            elif self.current_mode == 'fast':
                self._switch_mode('safe')
    
    def _switch_mode(self, new_mode):
        """Mudança de modo com cooldown"""
        if new_mode != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = new_mode
            self.adaptive_cooldown = time.time() + 2.0  # 2s cooldown
            
            print(f"🔄 Modo: {old_mode} → {new_mode} "
                  f"({self.mode_config[new_mode]['timeout']}ms)")
    
    def _build_command(self, x, y, buttons=0):
        """Comando no formato otimizado de 8 bytes"""
        command = bytearray(8)
        
        x = max(-127, min(127, int(x)))
        y = max(-127, min(127, int(y)))
        
        x_byte = x if x >= 0 else (256 + x)
        y_byte = y if y >= 0 else (256 + y)
        
        command[0] = 0x01
        command[1] = x_byte
        command[2] = y_byte
        command[3] = buttons
        # Bytes 4-7 ficam zerados
        
        return bytes(command)
    
    def _send_ultra_command(self, command):
        """Envio ultra-otimizado com fallback inteligente"""
        mode_config = self.mode_config[self.current_mode]
        timeout = mode_config['timeout']
        
        start_time = time.perf_counter()
        success = False
        attempts = 0
        
        # Tentar modo atual
        try:
            with self.lock:
                bytes_sent = self.endpoint_out.write(command, timeout=timeout)
            
            if bytes_sent == len(command):
                success = True
                attempts = 1
        except usb.core.USBTimeoutError:
            attempts = 1
        except Exception:
            attempts = 1
        
        # Fallback para modo mais lento se falhou
        if not success and self.current_mode != 'safe':
            fallback_modes = ['turbo', 'fast', 'safe']
            current_idx = list(self.mode_config.keys()).index(self.current_mode)
            
            for mode in fallback_modes[current_idx:]:
                try:
                    fallback_timeout = self.mode_config[mode]['timeout']
                    with self.lock:
                        bytes_sent = self.endpoint_out.write(command, timeout=fallback_timeout)
                    
                    if bytes_sent == len(command):
                        success = True
                        break
                    
                    attempts += 1
                except:
                    attempts += 1
        
        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000
        
        # Registrar estatísticas
        if success:
            self.mode_stats[self.current_mode]['sent'] += 1
            self.mode_stats[self.current_mode]['latencies'].append(latency)
        else:
            self.mode_stats[self.current_mode]['failed'] += 1
        
        # Registrar para sistema adaptativo
        self.recent_performance.append({
            'success': success,
            'latency': latency,
            'mode': self.current_mode,
            'attempts': attempts
        })
        
        return success
    
    def _process_batch(self):
        """Processa comandos em batch para maior throughput"""
        if not self.batch_enabled or len(self.batch_buffer) == 0:
            return []
        
        batch = self.batch_buffer[:self.batch_size]
        self.batch_buffer = self.batch_buffer[self.batch_size:]
        
        results = []
        for command in batch:
            result = self._send_ultra_command(command)
            results.append(result)
            
            # Delay mínimo entre comandos do batch
            time.sleep(0.0001)  # 0.1ms
        
        return results
    
    def move(self, x, y, use_batch=True):
        """
        Movimento ultra-otimizado
        
        Args:
            x (float): Movimento X
            y (float): Movimento Y
            use_batch (bool): Usar sistema de batch
        """
        if not self.device or not self.endpoint_out:
            return False
        
        # Acumular movimento fracionário
        x += self.remainder_x
        y += self.remainder_y
        
        move_x = int(x)
        move_y = int(y)
        
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y
        
        if move_x == 0 and move_y == 0:
            return True
        
        command = self._build_command(move_x, move_y)
        
        # Usar batch se habilitado
        if use_batch and self.batch_enabled:
            self.batch_buffer.append(command)
            
            if len(self.batch_buffer) >= self.batch_size:
                results = self._process_batch()
                return all(results)
            else:
                return True  # Aguardando batch
        else:
            return self._send_ultra_command(command)
    
    def flush_batch(self):
        """Força envio de comandos em batch pendentes"""
        if self.batch_buffer:
            results = []
            while self.batch_buffer:
                batch_results = self._process_batch()
                results.extend(batch_results)
            return results
        return []
    
    def click(self, button=1):
        """Clique ultra-otimizado"""
        if not self.device:
            return False
        
        command = self._build_command(0, 0, button)
        return self._send_ultra_command(command)
    
    def burst_move(self, movements, optimize_speed=True):
        """Movimento em rajada ultra-otimizado"""
        if not movements:
            return []
        
        # Temporariamente desabilitar batch para controle preciso
        original_batch = self.batch_enabled
        self.batch_enabled = False
        
        results = []
        
        try:
            for x, y in movements:
                result = self.move(x, y, use_batch=False)
                results.append(result)
                
                # Delay baseado no modo atual
                mode_config = self.mode_config[self.current_mode]
                delay = mode_config['delay'] if optimize_speed else 0.005
                time.sleep(delay)
        
        finally:
            self.batch_enabled = original_batch
        
        return results
    
    def get_ultra_stats(self):
        """Estatísticas ultra-detalhadas"""
        stats = {
            'current_mode': self.current_mode,
            'mode_stats': {}
        }
        
        total_sent = 0
        total_failed = 0
        
        for mode, data in self.mode_stats.items():
            sent = data['sent']
            failed = data['failed']
            total_sent += sent
            total_failed += failed
            
            mode_stats = {
                'sent': sent,
                'failed': failed,
                'success_rate': sent / (sent + failed) if (sent + failed) > 0 else 0
            }
            
            if data['latencies']:
                mode_stats.update({
                    'avg_latency_ms': statistics.mean(data['latencies']),
                    'min_latency_ms': min(data['latencies']),
                    'max_latency_ms': max(data['latencies'])
                })
            
            stats['mode_stats'][mode] = mode_stats
        
        stats['total_sent'] = total_sent
        stats['total_failed'] = total_failed
        stats['overall_success_rate'] = total_sent / (total_sent + total_failed) if (total_sent + total_failed) > 0 else 0
        
        # Performance recente
        if self.recent_performance:
            recent_20 = list(self.recent_performance)[-20:]
            recent_successes = sum(1 for p in recent_20 if p['success'])
            stats['recent_success_rate'] = recent_successes / len(recent_20)
            
            recent_latencies = [p['latency'] for p in recent_20 if p['success']]
            if recent_latencies:
                stats['recent_avg_latency_ms'] = statistics.mean(recent_latencies)
        
        return stats
    
    def print_ultra_summary(self):
        """Resumo ultra-detalhado"""
        stats = self.get_ultra_stats()
        
        print(f"\n🔥 ULTRA-PERFORMANCE SUMMARY")
        print("="*40)
        print(f"Modo atual: {stats['current_mode'].upper()}")
        print(f"Sucesso geral: {stats['overall_success_rate']:.1%}")
        print(f"Total enviados: {stats['total_sent']}")
        
        if 'recent_success_rate' in stats:
            print(f"Sucesso recente: {stats['recent_success_rate']:.1%}")
        
        if 'recent_avg_latency_ms' in stats:
            print(f"Latência recente: {stats['recent_avg_latency_ms']:.1f}ms")
        
        print("\n📊 Por modo:")
        for mode, mode_stats in stats['mode_stats'].items():
            if mode_stats['sent'] > 0:
                print(f"  {mode.upper()}: {mode_stats['sent']} enviados, "
                      f"{mode_stats['success_rate']:.1%} sucesso")
                if 'avg_latency_ms' in mode_stats:
                    print(f"    Latência: {mode_stats['avg_latency_ms']:.1f}ms")
    
    def benchmark_ultra_performance(self, duration=10.0, target_fps=500):
        """Benchmark ultra-performance"""
        print(f"\n🔥 BENCHMARK ULTRA-PERFORMANCE ({duration}s)")
        print(f"Target FPS: {target_fps}")
        print("="*50)
        
        start_time = time.time()
        movements = [(1, 0), (0, 1), (-1, 0), (0, -1), (2, -1), (-1, 2), (3, 2), (-2, -3)]
        movement_idx = 0
        commands_sent = 0
        
        initial_stats = self.get_ultra_stats()
        
        target_delay = 1.0 / target_fps
        
        while time.time() - start_time < duration:
            x, y = movements[movement_idx % len(movements)]
            
            if self.move(x, y):
                commands_sent += 1
            
            movement_idx += 1
            
            # Delay para target FPS
            time.sleep(target_delay)
        
        # Flush comandos pendentes
        self.flush_batch()
        
        final_stats = self.get_ultra_stats()
        
        elapsed_time = time.time() - start_time
        effective_fps = commands_sent / elapsed_time
        
        print(f"⚡ Comandos enviados: {commands_sent}")
        print(f"🏃 FPS efetivo: {effective_fps:.1f}")
        print(f"🎯 Target atingido: {effective_fps/target_fps*100:.1f}%")
        print(f"📈 Sucesso final: {final_stats['overall_success_rate']:.1%}")
        print(f"🔥 Modo final: {final_stats['current_mode'].upper()}")
        
        if 'recent_avg_latency_ms' in final_stats:
            print(f"⚡ Latência: {final_stats['recent_avg_latency_ms']:.1f}ms")
        
        return {
            'commands_sent': commands_sent,
            'effective_fps': effective_fps,
            'target_achievement': effective_fps / target_fps,
            'final_success_rate': final_stats['overall_success_rate'],
            'final_mode': final_stats['current_mode']
        }
    
    def close(self):
        """Cleanup ultra-completo"""
        if self.device:
            try:
                # Flush final
                self.flush_batch()
                
                # Reset
                reset_cmd = self._build_command(0, 0, 0)
                self.endpoint_out.write(reset_cmd, timeout=100)
                
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
                
                print("🔌 UltraOptimizedController fechado")
                
            except:
                pass
            finally:
                self.device = None


# Wrapper de compatibilidade
class MouseController(UltraOptimizedController):
    def __init__(self, com_port=None, baudrate=115200):
        if com_port:
            print(f"⚠️ Ignorando {com_port} - usando Ultra-Optimized Raw HID")
        super().__init__()


# Teste ultra-avançado
def test_ultra_controller():
    print("🔥 TESTE ULTRA-PERFORMANCE")
    print("="*40)
    
    try:
        controller = UltraOptimizedController()
        
        # Teste básico
        print("\n1️⃣ Teste básico...")
        basic_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (5, -3), (10, 8), (-7, 12)]
        success_count = 0
        
        for i, (x, y) in enumerate(basic_moves):
            if controller.move(x, y, use_batch=False):
                success_count += 1
                print(f"✅ #{i+1}: ({x:3d}, {y:3d})")
            else:
                print(f"❌ #{i+1}: ({x:3d}, {y:3d})")
        
        print(f"Básico: {success_count}/{len(basic_moves)} sucessos")
        
        # Teste de rajada ultra-rápida
        print("\n2️⃣ Teste de rajada ultra-rápida...")
        burst_moves = [(i, -i) for i in range(1, 11)]  # 10 movimentos
        burst_results = controller.burst_move(burst_moves, optimize_speed=True)
        burst_success = sum(burst_results)
        
        print(f"Rajada: {burst_success}/{len(burst_moves)} sucessos")
        
        # Benchmark ultra-performance
        print("\n3️⃣ Benchmark ultra-performance...")
        benchmark_results = controller.benchmark_ultra_performance(duration=8.0, target_fps=200)
        
        # Estatísticas finais
        controller.print_ultra_summary()
        
        controller.close()
        
        return {
            'basic_success_rate': success_count / len(basic_moves),
            'burst_success_rate': burst_success / len(burst_moves),
            'benchmark_results': benchmark_results
        }
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


if __name__ == "__main__":
    test_ultra_controller()