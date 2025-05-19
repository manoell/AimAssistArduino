import hid
import struct
import time

# Teste básico de comunicação HID
def test_hid_communication():
    try:
        # Conectar ao dispositivo
        device = None
        for device_info in hid.enumerate(0x046D, 0xC547):
            if device_info.get('interface_number') == 2:
                device = hid.device()
                device.open_path(device_info['path'])
                device.set_nonblocking(1)
                break
        
        if not device:
            print("❌ Dispositivo não encontrado!")
            return
        
        print("✅ Dispositivo encontrado e conectado!")
        
        # Teste 1: Envio direto via write (Output Report)
        print("\n🧪 TESTE 1: Output Report via write()...")
        packet = struct.pack('<BhhBbBB55x', 
                           0x01,  # command_type = move
                           50,    # delta_x = 50 pixels
                           0,     # delta_y = 0
                           0,     # buttons = 0
                           0,     # wheel = 0
                           5,     # speed_factor = 5
                           5      # smooth_factor = 5
                           )
        
        try:
            result = device.write(packet)
            print(f"   Resultado write: {result} bytes enviados")
            time.sleep(1)
        except Exception as e:
            print(f"   Erro ao enviar via write: {e}")
        
        # Teste 2: Usando Set_Output_Report
        print("\n🧪 TESTE 2: Set Output Report...")
        try:
            # Adicionar Report ID 0x00
            report = b'\x00' + packet
            result = device.send_feature_report(report)
            print(f"   Resultado send_feature_report: {result}")
            time.sleep(1)
        except Exception as e:
            print(f"   Erro ao enviar feature report: {e}")
        
        # Teste 3: Múltiplos comandos pequenos
        print("\n🧪 TESTE 3: Comandos múltiplos...")
        
        # Mover direita
        packet_right = struct.pack('<BhhBbBB55x', 0x01, 30, 0, 0, 0, 5, 5)
        try:
            device.write(packet_right)
            print("   ✅ Comando direita enviado")
            time.sleep(0.5)
        except Exception as e:
            print(f"   ❌ Erro comando direita: {e}")
        
        # Mover esquerda
        packet_left = struct.pack('<BhhBbBB55x', 0x01, -30, 0, 0, 0, 5, 5)
        try:
            device.write(packet_left)
            print("   ✅ Comando esquerda enviado")
            time.sleep(0.5)
        except Exception as e:
            print(f"   ❌ Erro comando esquerda: {e}")
        
        # Reset
        packet_reset = struct.pack('<BhhBbBB55x', 0x04, 0, 0, 0, 0, 0, 0)
        try:
            device.write(packet_reset)
            print("   ✅ Comando reset enviado")
            time.sleep(0.5)
        except Exception as e:
            print(f"   ❌ Erro comando reset: {e}")
        
        # Teste 4: Verificar se dispositivo responde
        print("\n🧪 TESTE 4: Lendo resposta...")
        try:
            # Tentar ler dados do dispositivo
            response = device.read(64, timeout_ms=1000)
            if response:
                print(f"   ✅ Resposta recebida: {[hex(b) for b in response[:10]]}")
            else:
                print("   ℹ️ Nenhuma resposta (normal para este tipo de dispositivo)")
        except Exception as e:
            print(f"   ℹ️ Erro ao ler (esperado): {e}")
        
        device.close()
        print("\n✅ Testes concluídos!")
        print("\n💡 Se não houve movimentos visíveis do cursor:")
        print("   1. Verifique se o Arduino está processando os comandos")
        print("   2. O problema pode estar no firmware LUFA")
        print("   3. Comandos podem estar sendo enviados mas não processados")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_hid_communication()