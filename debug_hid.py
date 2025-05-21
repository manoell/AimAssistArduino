import usb.core
import usb.util
import time
import sys

class CommunicationTester:
    def __init__(self, vid=0x046D, pid=0xC547):
        self.device = None
        self.interface = 2
        self.endpoint_out = None
        self.endpoint_in = None
        
    def connect(self):
        """Conecta ao Arduino"""
        print("🔍 Procurando Arduino...")
        self.device = usb.core.find(idVendor=0x046D, idProduct=0xC547)
        if self.device is None:
            print("❌ Arduino não encontrado!")
            return False
        
        print(f"✅ Arduino encontrado: {self.device.manufacturer} {self.device.product}")
        
        try:
            # Desanexar driver se necessário
            try:
                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)
                    print("📤 Driver kernel desanexado")
            except:
                pass
            
            # Configurar
            self.device.set_configuration()
            usb.util.claim_interface(self.device, self.interface)
            
            # Encontrar endpoints
            cfg = self.device.get_active_configuration()
            interface_cfg = cfg[(self.interface, 0)]
            
            for endpoint in interface_cfg:
                addr = endpoint.bEndpointAddress
                if usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_OUT:
                    self.endpoint_out = endpoint
                    print(f"✅ Endpoint OUT: 0x{addr:02X}")
                elif usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_IN:
                    self.endpoint_in = endpoint
                    print(f"✅ Endpoint IN: 0x{addr:02X}")
            
            if not self.endpoint_out:
                print("❌ Endpoint OUT não encontrado!")
                return False
                
            print("🚀 Conexão estabelecida!")
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def send_command(self, command):
        """Envia comando e retorna sucesso/falha"""
        try:
            bytes_sent = self.endpoint_out.write(command, timeout=100)
            return bytes_sent == len(command)
        except Exception as e:
            print(f"❌ Erro no envio: {e}")
            return False
    
    def test_communication_basic(self):
        """Teste básico de comunicação - FOCO NO LED"""
        print("\n🔥 TESTE DE COMUNICAÇÃO COM LED")
        print("="*50)
        print("👀 OBSERVE O LED LARANJA DO ARDUINO!")
        print("   Deve piscar a cada comando enviado")
        
        commands = [
            (0x05, "PING", "Piscar curto"),
            (0x04, "RESET", "Piscar duplo"),
            (0x01, "MOVIMENTO", "Piscar curto"),
            (0x02, "CLIQUE", "Piscar curto"),
            (0xFF, "DESCONHECIDO", "Piscar duplo (erro)")
        ]
        
        for cmd_type, name, expected in commands:
            command = bytearray(64)
            command[0] = cmd_type
            
            print(f"\n📤 Enviando {name} (0x{cmd_type:02X})")
            print(f"   Esperado: {expected}")
            
            if self.send_command(command):
                print("✅ Comando enviado com sucesso")
                
                # Pausa para observar o LED
                time.sleep(1.0)
                
                led_blinked = input("❓ O LED piscou? (s/n): ").lower().strip()
                if led_blinked == 's':
                    print("🎉 COMUNICAÇÃO OK!")
                else:
                    print("❌ LED não piscou - problema na comunicação")
                    return False
            else:
                print("❌ Falha no envio")
                return False
        
        return True
    
    def test_specific_commands(self):
        """Teste comandos específicos"""
        print("\n🎯 TESTE DE COMANDOS ESPECÍFICOS")
        print("="*40)
        
        # Teste 1: Reset (deve piscar LED duplo)
        print("\n1️⃣ Testando RESET...")
        reset_cmd = bytearray(64)
        reset_cmd[0] = 0x04  # Reset
        
        if self.send_command(reset_cmd):
            print("✅ Reset enviado")
            time.sleep(0.5)
            led_ok = input("❓ LED piscou DUPLO para reset? (s/n): ").lower() == 's'
            if not led_ok:
                print("❌ Reset não foi processado corretamente")
                return False
        
        # Teste 2: Movimento (deve piscar LED simples)
        print("\n2️⃣ Testando MOVIMENTO...")
        move_cmd = bytearray(64)
        move_cmd[0] = 0x01  # Movement
        move_cmd[1] = 50    # X low byte
        move_cmd[2] = 0     # X high byte
        move_cmd[3] = 0     # Y low byte
        move_cmd[4] = 0     # Y high byte
        move_cmd[5] = 0     # Buttons
        move_cmd[6] = 0     # Wheel
        
        if self.send_command(move_cmd):
            print("✅ Movimento enviado")
            time.sleep(0.5)
            led_ok = input("❓ LED piscou SIMPLES para movimento? (s/n): ").lower() == 's'
            if not led_ok:
                print("❌ Movimento não foi processado corretamente")
                return False
        
        # Teste 3: Comando desconhecido (deve piscar LED duplo de erro)
        print("\n3️⃣ Testando COMANDO DESCONHECIDO...")
        unknown_cmd = bytearray(64)
        unknown_cmd[0] = 0xFF  # Unknown command
        
        if self.send_command(unknown_cmd):
            print("✅ Comando desconhecido enviado")
            time.sleep(0.5)
            led_ok = input("❓ LED piscou DUPLO para erro? (s/n): ").lower() == 's'
            if not led_ok:
                print("❌ Comando desconhecido não foi tratado corretamente")
                return False
        
        return True
    
    def test_mouse_movement_intensive(self):
        """Teste intensivo para movimento do cursor"""
        print("\n🚨 TESTE INTENSIVO - MOVIMENTO DO CURSOR")
        print("="*50)
        print("📊 Enviando muitos comandos para garantir resposta")
        print("👀 OBSERVE O CURSOR COM ATENÇÃO!")
        
        # Valores grandes para movimento mais visível
        moves = [
            ("direita", 30, 0),
            ("esquerda", 226, 0),  # -30 em complemento de 2
            ("baixo", 0, 30),
            ("cima", 0, 226),     # -30 em complemento de 2
            ("diagonal", 20, 20)
        ]
        
        for direction, x, y in moves:
            print(f"\n🔄 Teste: {direction} (X={x}, Y={y})")
            
            # Comando de movimento
            cmd = bytearray(64)
            cmd[0] = 0x01  # Movement
            cmd[1] = x     # X
            cmd[3] = y     # Y
            
            # Enviar MUITOS comandos para garantir que algum funcione
            for i in range(10):
                if self.send_command(cmd):
                    print(f"  ✅ #{i+1}", end=" ", flush=True)
                else:
                    print(f"  ❌ #{i+1}", end=" ", flush=True)
                time.sleep(0.05)  # Pequena pausa
            
            print("\n")
            moved = input(f"❓ O cursor se moveu para {direction}? (s/n): ").lower() == 's'
            if moved:
                print("🎉 MOVIMENTO FUNCIONANDO!")
                return True
        
        return False
    
    def test_rapid_fire(self):
        """Teste de comandos em rajada"""
        print("\n⚡ TESTE DE RAJADA")
        print("="*30)
        print("👀 OBSERVE: LED deve piscar rapidamente!")
        
        print("Enviando 10 comandos em sequência...")
        
        success_count = 0
        for i in range(10):
            cmd = bytearray(64)
            cmd[0] = 0x05  # Ping
            
            if self.send_command(cmd):
                success_count += 1
                print(f"  {i+1}/10 ✅", end=" ", flush=True)
            else:
                print(f"  {i+1}/10 ❌", end=" ", flush=True)
            
            time.sleep(0.1)  # 100ms entre comandos
        
        print(f"\n\n📊 Resultado: {success_count}/10 comandos enviados")
        
        if success_count >= 8:
            rapid_ok = input("❓ LED piscou rapidamente? (s/n): ").lower() == 's'
            return rapid_ok
        else:
            print("❌ Muitas falhas no envio")
            return False
    
    def run_communication_tests(self):
        """Executa todos os testes de comunicação"""
        print("🚀 TESTADOR DE COMUNICAÇÃO RAW HID")
        print("="*60)
        print("OBJETIVO: Verificar se a comunicação está funcionando")
        print("INDICADOR: LED laranja do Arduino deve piscar")
        print("="*60)
        
        tests = [
            ("Comunicação Básica", self.test_communication_basic),
            ("Comandos Específicos", self.test_specific_commands),
            ("Movimento Intensivo", self.test_mouse_movement_intensive),
            ("Teste de Rajada", self.test_rapid_fire),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🧪 Executando: {test_name}")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"💥 Erro no teste: {e}")
                results[test_name] = False
        
        # Resultado final
        print("\n" + "="*60)
        print("🎯 RELATÓRIO FINAL")
        print("="*60)
        
        passed = 0
        for test_name, success in results.items():
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"   {test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n📊 Total: {passed}/{len(tests)} testes passaram")
        
        if passed == len(tests):
            print("🏆 COMUNICAÇÃO FUNCIONANDO PERFEITAMENTE!")
            print("✅ Arduino está recebendo e processando comandos")
            print("✅ Cursor respondendo aos comandos")
        elif passed >= 1:
            print("⚠️ COMUNICAÇÃO PARCIAL")
            print("💡 Verifique o firmware e tente novamente")
        else:
            print("❌ COMUNICAÇÃO FALHANDO")
            print("💡 Verifique:")
            print("   1. Firmware foi uploadado corretamente?")
            print("   2. Arduino está conectado?")
            print("   3. LED pisca durante setup (3 vezes)?")
    
    def disconnect(self):
        """Desconecta do Arduino"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
                print("🔌 Desconectado")
            except:
                pass

def main():
    """Função principal"""
    tester = CommunicationTester()
    
    try:
        if not tester.connect():
            print("❌ Falha na conexão. Saindo...")
            return
        
        tester.run_communication_tests()
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n💥 Erro: {e}")
    finally:
        tester.disconnect()
    
    input("\n📌 Pressione Enter para sair...")

if __name__ == "__main__":
    main()