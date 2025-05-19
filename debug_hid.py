import usb.core
import usb.util
import struct
import time

def test_with_driver_check():
    """
    Teste com verificação de driver e debug detalhado
    """
    print("🚀 TESTE COM DEBUG AVANÇADO")
    print("=" * 50)
    
    # Encontrar dispositivo
    device = usb.core.find(idVendor=0x046D, idProduct=0xC547)
    if device is None:
        print("❌ Arduino não encontrado!")
        return False
    
    print(f"✅ Arduino encontrado!")
    
    # VERIFICAR DRIVER ATUAL
    print("\n🔍 Verificando driver atual...")
    try:
        # Tenta acessar directamente
        device.set_configuration()
        print("✅ Driver WinUSB/libusb funcionando")
    except usb.core.USBTimeoutError:
        print("⚠️ Timeout - pode ser driver HID padrão")
    except usb.core.USBError as e:
        if "busy" in str(e).lower() or "access" in str(e).lower():
            print("❌ Driver HID padrão está interceptando!")
            print("💡 SOLUÇÃO: Use Zadig para instalar driver WinUSB:")
            print("   1. Baixe Zadig: https://zadig.akeo.ie/")
            print("   2. Execute como Administrador")
            print("   3. Em Options > List All Devices")
            print("   4. Selecione 'Logitech USB Receiver (Interface 2)'")
            print("   5. Instale driver 'WinUSB'")
            print("   6. Execute este teste novamente")
            return False
        else:
            print(f"❌ Erro driver: {e}")
            return False
    
    # Claim interface
    try:
        usb.util.claim_interface(device, 2)
        print("✅ Interface 2 claimed com sucesso")
    except Exception as e:
        print(f"❌ Erro ao claim interface: {e}")
        return False
    
    # Encontrar endpoint OUT
    cfg = device.get_active_configuration()
    interface = cfg[(2, 0)]
    
    ep_out = None
    for endpoint in interface:
        if usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_OUT:
            ep_out = endpoint
            break
    
    if ep_out is None:
        print("❌ Endpoint OUT não encontrado!")
        return False
    
    print(f"✅ Endpoint OUT: 0x{ep_out.bEndpointAddress:02X}")
    
    # TESTE COM VERIFICAÇÃO DE LED
    def send_and_check(x, y, test_name):
        """Envia comando e verifica se LED pisca"""
        def int16_to_bytes(value):
            if value < 0:
                value = 65536 + value
            return [value & 0xFF, (value >> 8) & 0xFF]
        
        x_bytes = int16_to_bytes(x)
        y_bytes = int16_to_bytes(y)
        
        command = struct.pack('<BBBBBBB57x', 
                            0x01, x_bytes[0], x_bytes[1], 
                            y_bytes[0], y_bytes[1], 0, 0)
        
        print(f"\n📤 {test_name}")
        print(f"   Enviando: X={x}, Y={y}")
        print(f"   👀 OBSERVE O LED DO ARDUINO PISCAR!")
        
        try:
            result = ep_out.write(command, timeout=2000)
            print(f"   ✅ {result} bytes enviados via endpoint OUT")
            print(f"   ❓ LED piscou? (Resposta visual)")
            time.sleep(1.5)
            return True
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    
    # BATERIA DE TESTES
    tests = [
        (50, 0, "Direita pequena"),
        (0, 50, "Baixo pequeno"),
        (200, 0, "Direita grande"),
        (0, 200, "Baixo grande"),
    ]
    
    success_count = 0
    for x, y, name in tests:
        if send_and_check(x, y, name):
            success_count += 1
    
    # RESULTADO
    print(f"\n📊 ANÁLISE FINAL:")
    print(f"   Comandos enviados: {success_count}/{len(tests)}")
    
    if success_count == len(tests):
        print(f"\n🔍 DIAGNÓSTICO:")
        print(f"   ✅ Endpoint OUT está recebendo dados")
        print(f"   ❓ LED piscou? Se SIM: firmware OK, problema no processamento")
        print(f"   ❓ LED piscou? Se NÃO: firmware não está recebendo dados")
        print(f"   ❓ Cursor se moveu? Se SIM: tudo funcionando!")
        print(f"   ❓ Cursor se moveu? Se NÃO: problema no HID_Task()")
        
        input("\n🤔 O LED piscou durante os testes? (s/n): ")
        response = input().lower()
        
        if response == 's':
            print("\n✅ FIRMWARE RECEBENDO DADOS!")
            print("❌ Problema está no processamento dos dados")
            print("💡 Aplique a correção do HID_Task() fornecida acima")
        else:
            print("\n❌ FIRMWARE NÃO ESTÁ RECEBENDO!")
            print("💡 Possíveis causas:")
            print("   1. Driver HID interceptando (use Zadig)")
            print("   2. Endpoint OUT não configurado corretamente")
            print("   3. Firmware não compilado com correção")
    else:
        print(f"\n❌ PROBLEMA NA COMUNICAÇÃO USB")
        print(f"💡 Verifique driver com Zadig")
    
    # Cleanup
    try:
        usb.util.release_interface(device, 2)
        usb.util.dispose_resources(device)
    except:
        pass
    
    return success_count == len(tests)

if __name__ == "__main__":
    try:
        test_with_driver_check()
        input("\nPressione Enter para sair...")
    except Exception as e:
        print(f"❌ Erro: {e}")
        input("Pressione Enter para sair...")