import usb.core
import usb.util
import struct
import time
import sys

def find_arduino():
    """Encontra o Arduino"""
    print("🔍 Procurando Arduino...")
    device = usb.core.find(idVendor=0x046D, idProduct=0xC547)
    if device is None:
        print("❌ Arduino não encontrado!")
        return None
    print("✅ Arduino encontrado!")
    return device

def setup_raw_hid(device):
    """Configura Raw HID"""
    print("🔧 Configurando Raw HID...")
    
    try:
        # Desanexar driver se necessário
        try:
            if device.is_kernel_driver_active(2):
                device.detach_kernel_driver(2)
        except:
            pass
        
        # Configurar
        device.set_configuration()
        usb.util.claim_interface(device, 2)
        
        # Encontrar endpoints
        cfg = device.get_active_configuration()
        interface_cfg = cfg[(2, 0)]
        
        ep_out = None
        ep_in = None
        
        for endpoint in interface_cfg:
            addr = endpoint.bEndpointAddress
            if usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_OUT:
                ep_out = endpoint
                print(f"✅ Endpoint OUT: 0x{addr:02X}")
            elif usb.util.endpoint_direction(addr) == usb.util.ENDPOINT_IN:
                ep_in = endpoint
                print(f"✅ Endpoint IN: 0x{addr:02X}")
        
        return ep_in, ep_out
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def create_movement_command_CORRIGIDO(x, y):
    """
    COMANDO CORRIGIDO - Formato exato que o Arduino espera
    
    Baseado no firmware: [cmd][x_low][x_high][y_low][y_high][btn][wheel][padding...]
    """
    # DEBUG: Mostrar o que estamos enviando
    print(f"🔧 Criando movimento: X={x}, Y={y}")
    
    command = bytearray(64)
    
    # Byte 0: Tipo de comando
    command[0] = 0x01  # Comando de movimento
    
    # Bytes 1-2: X (16-bit little endian)
    if x < 0:
        x_unsigned = (1 << 16) + x  # Complemento de 2
    else:
        x_unsigned = x
    command[1] = x_unsigned & 0xFF       # X low byte
    command[2] = (x_unsigned >> 8) & 0xFF # X high byte
    
    # Bytes 3-4: Y (16-bit little endian)  
    if y < 0:
        y_unsigned = (1 << 16) + y  # Complemento de 2
    else:
        y_unsigned = y
    command[3] = y_unsigned & 0xFF       # Y low byte
    command[4] = (y_unsigned >> 8) & 0xFF # Y high byte
    
    # Byte 5: Botões (0 = nenhum botão)
    command[5] = 0
    
    # Byte 6: Wheel (0 = sem scroll)
    command[6] = 0
    
    # Bytes 7-63: Padding (zeros)
    # Já são zero por padrão no bytearray
    
    # DEBUG: Mostrar primeiros 8 bytes
    print(f"📦 Comando: {[hex(b) for b in command[:8]]}")
    
    return bytes(command)

def test_MOVIMENTO_SIMPLES(ep_out):
    """
    Teste focado APENAS no movimento do cursor
    """
    print("\n🎯 TESTE FOCADO - MOVIMENTO DO CURSOR")
    print("="*50)
    print("👀 OBSERVE O CURSOR NA TELA!")
    
    movements = [
        (50, 0, "→ DIREITA"),
        (-50, 0, "← ESQUERDA"),
        (0, 50, "↓ BAIXO"),
        (0, -50, "↑ CIMA"),
        (30, 30, "↘ DIAGONAL"),
    ]
    
    for x, y, desc in movements:
        print(f"\n📤 {desc}: ({x:+3d}, {y:+3d})")
        
        # Criar comando corrigido
        cmd = create_movement_command_CORRIGIDO(x, y)
        
        try:
            # Enviar com timeout baixo
            bytes_sent = ep_out.write(cmd, timeout=100)
            print(f"✅ Enviado: {bytes_sent} bytes")
            
            # PAUSA MAIOR para ver o movimento
            print("⏳ Aguardando movimento...")
            time.sleep(1.0)
            
            # Perguntar ao usuário
            moved = input("❓ O cursor se moveu? (s/n): ").lower().strip()
            if moved == 's':
                print("🎉 SUCESSO! Movimento detectado!")
            else:
                print("❌ Movimento não detectado")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        time.sleep(0.5)

def test_RESET_E_STATUS(ep_in, ep_out):
    """
    Testa reset e leitura de status
    """
    print("\n🔄 TESTE RESET E STATUS")
    print("="*30)
    
    # Enviar reset
    reset_cmd = bytearray(64)
    reset_cmd[0] = 0x04  # Comando de reset
    
    try:
        ep_out.write(reset_cmd, timeout=100)
        print("✅ Reset enviado")
        time.sleep(0.2)
    except Exception as e:
        print(f"❌ Erro no reset: {e}")
    
    # Tentar ler status
    try:
        data = ep_in.read(64, timeout=500)
        if len(data) >= 4:
            print(f"📊 Status recebido: {data[:8].hex()}")
            if data[0] == 0xAA:
                commands = data[3] | (data[4] << 8) if len(data) > 4 else data[3]
                print(f"📈 Comandos processados: {commands}")
            else:
                print("⚠️ Formato de status desconhecido")
        else:
            print("📊 Status vazio")
    except Exception as e:
        print(f"⚠️ Não foi possível ler status: {e}")

def test_MOVIMENTO_CONTINUO(ep_out):
    """
    Movimento contínuo para verificar responsividade
    """
    print("\n🌀 TESTE MOVIMENTO CONTÍNUO")
    print("="*40)
    print("🔥 Movimento contínuo por 3 segundos...")
    print("👀 OBSERVE se o cursor se move em círculo!")
    
    import math
    
    try:
        angle = 0
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < 3.0:
            # Movimento circular
            x = int(20 * math.cos(angle))
            y = int(20 * math.sin(angle))
            
            cmd = create_movement_command_CORRIGIDO(x, y)
            ep_out.write(cmd, timeout=50)
            
            angle += 0.3
            count += 1
            time.sleep(0.02)  # 50 Hz
        
        print(f"✅ Enviados {count} comandos")
        moved = input("❓ O cursor se moveu em círculo? (s/n): ").lower().strip()
        return moved == 's'
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Teste principal focado no movimento"""
    print("🚀 TESTE DIRECIONADO - MOVIMENTO DO CURSOR")
    print("="*60)
    
    # 1. Conectar
    device = find_arduino()
    if not device:
        return
    
    # 2. Configurar Raw HID
    ep_in, ep_out = setup_raw_hid(device)
    if not ep_out:
        return
    
    print("\n" + "="*60)
    
    try:
        # 3. Teste de reset/status
        test_RESET_E_STATUS(ep_in, ep_out)
        
        # 4. Teste de movimento simples (PRINCIPAL)
        test_MOVIMENTO_SIMPLES(ep_out)
        
        # 5. Teste contínuo
        continous_success = test_MOVIMENTO_CONTINUO(ep_out)
        
        # Resultado final
        print("\n" + "="*60)
        print("🎯 RESULTADO FINAL")
        print("="*60)
        
        if continous_success:
            print("🏆 SUCESSO! Comunicação Raw HID funcionando!")
            print("✅ Cursor respondendo aos comandos")
            print("✅ Pronto para integrar no projeto principal!")
        else:
            print("❌ PROBLEMA: Comandos enviados mas cursor não se move")
            print("💡 Possíveis causes:")
            print("   1. Firmware não processando comandos corretamente")
            print("   2. Formato de comando incorreto")
            print("   3. Arduino não enviando para interface HID")
        
    finally:
        # Cleanup
        try:
            usb.util.release_interface(device, 2)
            usb.util.dispose_resources(device)
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Teste cancelado")
    except Exception as e:
        print(f"\n💥 Erro: {e}")
    
    input("\n📌 Pressione Enter para sair...")
