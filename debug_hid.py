import usb.core
import usb.util
import time
import sys

class FinalTester:
    def __init__(self, vid=0x046D, pid=0xC547):
        self.device = None
        self.interface = 2
        self.endpoint_out = None
        
    def connect(self):
        """Conecta ao Arduino"""
        print("🔍 Procurando Arduino...")
        self.device = usb.core.find(idVendor=0x046D, idProduct=0xC547)
        if self.device is None:
            print("❌ Arduino não encontrado!")
            return False
        
        print(f"✅ Arduino encontrado: {self.device.manufacturer} {self.device.product}")
        
        try:
            try:
                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)
            except:
                pass
            
            self.device.set_configuration()
            usb.util.claim_interface(self.device, self.interface)
            
            cfg = self.device.get_active_configuration()
            interface_cfg = cfg[(self.interface, 0)]
            
            for endpoint in interface_cfg:
                addr = endpoint.bEndpointAddress
                if usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_OUT:
                    self.endpoint_out = endpoint
                    print(f"✅ Endpoint OUT: 0x{addr:02X}")
            
            if not self.endpoint_out:
                print("❌ Endpoint OUT não encontrado!")
                return False
                
            print("🚀 Conexão estabelecida!")
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def send_command(self, command):
        """Envia comando simples"""
        try:
            bytes_sent = self.endpoint_out.write(command, timeout=100)
            return bytes_sent == len(command)
        except Exception as e:
            print(f"❌ Erro no envio: {e}")
            return False
    
    def build_simple_movement(self, x, y, buttons=0):
        """
        Comando SIMPLES: [cmd][x][y][buttons][padding...]
        Boot Protocol: 3 bytes de report
        """
        command = bytearray(64)
        command[0] = 0x01  # Movimento
        command[1] = x & 0xFF  # X como byte direto
        command[2] = y & 0xFF  # Y como byte direto  
        command[3] = buttons   # Botões (opcional)
        return command
    
    def test_simple_movement(self):
        """Teste super simples de movimento"""
        print("\n🎯 TESTE FINAL - BOOT PROTOCOL CORRETO")
        print("="*50)
        print("⚡ Usando formato Boot Protocol padrão")
        print("📐 Report de 3 bytes: [buttons][x][y]")
        print("👀 CURSOR DEVE SE MOVER AGORA!")
        
        # Valores pequenos para teste
        moves = [
            ("DIREITA", 10, 0),
            ("BAIXO", 0, 10),
            ("ESQUERDA", -10, 0),  # 246 em complemento de 2
            ("CIMA", 0, -10),      # 246 em complemento de 2  
        ]
        
        print("\n🚨 Posicione cursor no centro da tela!")
        input("Pressione Enter quando pronto...")
        
        for direction, x, y in moves:
            # Converter negativo para byte
            x_byte = x if x >= 0 else (256 + x)
            y_byte = y if y >= 0 else (256 + y)
            
            print(f"\n➡️ {direction}: X={x} ({x_byte}), Y={y} ({y_byte})")
            
            cmd = self.build_simple_movement(x_byte, y_byte)
            
            # Enviar várias vezes
            for i in range(5):
                if self.send_command(cmd):
                    print(f"✅ #{i+1}", end=" ", flush=True)
                    time.sleep(0.05)
                else:
                    print(f"❌ #{i+1}", end=" ", flush=True)
            
            print()
            moved = input(f"❓ Cursor moveu para {direction}? (s/n): ").lower().strip()
            if moved == 's':
                print("🎉 MOVIMENTO FUNCIONANDO!")
                return True
            
            time.sleep(0.5)
        
        return False
    
    def test_click(self):
        """Teste de clique"""
        print("\n🖱️ TESTE DE CLIQUE")
        print("="*30)
        
        cmd = bytearray(64)
        cmd[0] = 0x02  # Clique
        cmd[1] = 0x01  # Botão esquerdo
        
        for i in range(3):
            if self.send_command(cmd):
                print(f"✅ Clique #{i+1} enviado")
                time.sleep(0.2)
            else:
                print(f"❌ Clique #{i+1} falhou")
        
        clicked = input("❓ Houve cliques? (s/n): ").lower().strip()
        return clicked == 's'
    
    def test_continuous(self):
        """Teste contínuo - cursor em círculo"""
        print("\n🔄 TESTE CONTÍNUO - CÍRCULO")
        print("="*35)
        print("Cursor deve se mover em movimento circular por 3 segundos")
        
        input("Pressione Enter para começar...")
        
        import math
        start_time = time.time()
        angle = 0
        
        while time.time() - start_time < 3.0:
            # Movimento circular pequeno
            x = int(5 * math.cos(angle))
            y = int(5 * math.sin(angle))
            
            # Converter para bytes
            x_byte = x if x >= 0 else (256 + x)
            y_byte = y if y >= 0 else (256 + y)
            
            cmd = self.build_simple_movement(x_byte, y_byte)
            self.send_command(cmd)
            
            angle += 0.3
            time.sleep(0.03)  # ~30 FPS
        
        moved = input("❓ Cursor fez movimento circular? (s/n): ").lower().strip()
        return moved == 's'
    
    def run_final_test(self):
        """Executa teste final definitivo"""
        print("🔥 TESTE FINAL - BOOT PROTOCOL LUFA")
        print("="*50)
        print("📋 Correções aplicadas:")
        print("   ✅ Boot Protocol de 3 bytes")
        print("   ✅ Descriptor HID correto")
        print("   ✅ Função sendMouseReportNow() otimizada")
        print("   ✅ Formato de comando simplificado")
        print("="*50)
        
        tests = [
            ("Movimento Básico", self.test_simple_movement),
            ("Cliques", self.test_click),
            ("Movimento Contínuo", self.test_continuous),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}")
            try:
                if test_func():
                    print(f"🏆 {test_name}: SUCESSO!")
                    print("✅ PROBLEMA RESOLVIDO!")
                    print("🎊 Seu Arduino LUFA está funcionando!")
                    return
                else:
                    print(f"❌ {test_name}: Falhou")
            except Exception as e:
                print(f"💥 {test_name}: Erro - {e}")
        
        print("\n😞 CURSOR AINDA NÃO MOVE")
        print("🔧 Possíveis causas restantes:")
        print("   1. Novo firmware não foi carregado")
        print("   2. Windows está interferindo")
        print("   3. Hardware do Arduino com problema")
        print("   4. Problema no bootloader LUFA")
        print("\n💡 Recomendação: Desconecte e reconecte o Arduino")
    
    def disconnect(self):
        """Desconecta"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
                print("🔌 Desconectado")
            except:
                pass

def main():
    """Função principal do teste final"""
    print("🎯 TESTE FINAL - LUFA BOOT PROTOCOL")
    print("="*40)
    print("Este é o teste definitivo!")
    print("Se não funcionar agora, o problema")
    print("é mais fundamental.")
    print("="*40)
    
    tester = FinalTester()
    
    try:
        if not tester.connect():
            print("❌ Falha na conexão. Saindo...")
            return
        
        tester.run_final_test()
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n💥 Erro: {e}")
    finally:
        tester.disconnect()
    
    input("\n📌 Pressione Enter para sair...")

if __name__ == "__main__":
    main()