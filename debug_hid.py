import usb.core
import usb.util
import struct
import time
import sys

def find_and_test_arduino():
    """
    Encontra e testa o dispositivo Arduino diretamente
    """
    print("🔍 Procurando Arduino (VID: 046D, PID: C547)...")
    
    device = usb.core.find(idVendor=0x046D, idProduct=0xC547)
    if device is None:
        print("❌ Arduino não encontrado!")
        print("💡 Verifique:")
        print("   - Arduino está conectado")
        print("   - Firmware LUFA carregado")
        print("   - Aparece como 'Logitech USB Receiver' no Gerenciador de Dispositivos")
        return None
    
    print("✅ Arduino encontrado!")
    print(f"   Produto: {device.manufacturer} {device.product}")
    print(f"   Configurações: {device.bNumConfigurations}")
    
    return device

def test_driver_access(device):
    """
    Testa se conseguimos acessar a Interface 2 com WinUSB
    """
    print("\n🔧 Testando acesso à Interface 2...")
    
    # Primeiro, vamos verificar se o dispositivo está configurado
    try:
        # Verificar se há driver kernel ativo na interface 2
        if device.is_kernel_driver_active(2):
            print("📌 Driver kernel detectado na Interface 2, tentando desanexar...")
            try:
                device.detach_kernel_driver(2)
                print("✅ Driver kernel desanexado")
            except Exception as e:
                print(f"⚠️  Não foi possível desanexar driver kernel: {e}")
    except NotImplementedError:
        # Em Windows, is_kernel_driver_active pode não estar implementado
        print("📌 Checagem de driver kernel não suportada no Windows")
    except Exception as e:
        print(f"📌 Verificação de driver: {e}")
    
    # Tentar configurar o dispositivo
    try:
        device.set_configuration()
        print("✅ Dispositivo configurado com sucesso")
    except usb.core.USBError as e:
        if "busy" in str(e).lower() or "access" in str(e).lower():
            print("❌ ERRO: Driver HID ainda está interceptando!")
            print("💡 SOLUÇÃO:")
            print("   1. Desconecte e reconecte o Arduino")
            print("   2. Execute este script novamente")
            print("   3. Se persistir, reinstale o driver WinUSB no Zadig")
            return False
        else:
            print(f"❌ Erro de configuração: {e}")
            return False
    
    # Tentar fazer claim da interface 2
    try:
        usb.util.claim_interface(device, 2)
        print("✅ Interface 2 claimed com sucesso!")
        print("🎉 Driver WinUSB está funcionando corretamente!")
        return True
    except usb.core.USBError as e:
        if "busy" in str(e).lower() or "resource" in str(e).lower():
            print("❌ Interface 2 está sendo usada por outro driver!")
            print("💡 Execute: reconecte o Arduino e tente novamente")
            return False
        else:
            print(f"❌ Erro ao fazer claim da interface: {e}")
            return False

def find_endpoints(device):
    """
    Encontra endpoints IN e OUT da Interface 2
    """
    print("\n🔍 Localizando endpoints...")
    
    try:
        cfg = device.get_active_configuration()
        interface = cfg[(2, 0)]  # Interface 2, alternate setting 0
        
        ep_out = None
        ep_in = None
        
        for endpoint in interface:
            addr = endpoint.bEndpointAddress
            direction = usb.util.endpoint_direction(addr)
            
            if direction == usb.util.ENDPOINT_OUT:
                ep_out = endpoint
                print(f"✅ Endpoint OUT encontrado: 0x{addr:02X}")
            elif direction == usb.util.ENDPOINT_IN:
                ep_in = endpoint
                print(f"✅ Endpoint IN encontrado: 0x{addr:02X}")
        
        if ep_out is None:
            print("❌ Endpoint OUT não encontrado!")
            print("💡 Verifique o firmware - deve ter Interface 2 com endpoints IN/OUT")
            return None, None
        
        if ep_in is None:
            print("⚠️  Endpoint IN não encontrado (opcional)")
        
        return ep_in, ep_out
    
    except Exception as e:
        print(f"❌ Erro ao encontrar endpoints: {e}")
        return None, None

def create_movement_command(x, y):
    """
    Cria comando de movimento no formato correto para o firmware
    
    Formato: [0x01][x_low][x_high][y_low][y_high][buttons][wheel][...padding...]
    Total: 64 bytes
    """
    def int16_to_bytes(value):
        # Converter int16 para dois bytes (little endian)
        # Garantir que está no range -32768 a 32767
        if value > 32767:
            value = 32767
        elif value < -32768:
            value = -32768
        
        if value < 0:
            value = 65536 + value  # Complemento de 2 para unsigned
        
        return [value & 0xFF, (value >> 8) & 0xFF]
    
    x_bytes = int16_to_bytes(x)
    y_bytes = int16_to_bytes(y)
    
    # Criar comando completo de 64 bytes
    command = bytearray(64)
    command[0] = 0x01           # Tipo: movimento do mouse
    command[1] = x_bytes[0]     # X low byte
    command[2] = x_bytes[1]     # X high byte  
    command[3] = y_bytes[0]     # Y low byte
    command[4] = y_bytes[1]     # Y high byte
    command[5] = 0              # Buttons (não usado neste teste)
    command[6] = 0              # Wheel (não usado neste teste)
    # bytes 7-63 ficam em zero (padding)
    
    return bytes(command)

def read_status(ep_in):
    """
    Tenta ler status do endpoint IN
    """
    if ep_in is None:
        return None
    
    try:
        status_data = ep_in.read(64, timeout=500)
        if len(status_data) >= 8 and status_data[0] == 0xAA:
            return {
                'signature': status_data[0],
                'comm_status': status_data[1],
                'last_command': status_data[2],
                'commands_received': status_data[3] | (status_data[4] << 8),
                'mouse_x': status_data[5],
                'mouse_y': status_data[6],
                'mouse_buttons': status_data[7]
            }
    except Exception as e:
        print(f"⚠️  Não foi possível ler status: {e}")
    
    return None

def test_movements(ep_in, ep_out):
    """
    Executa bateria de testes de movimento
    """
    print("\n🧪 EXECUTANDO TESTES DE MOVIMENTO")
    print("="*50)
    print("👀 OBSERVE:")
    print("   • LED do Arduino deve piscar 3 vezes a cada comando")
    print("   • Cursor do mouse deve se mover na tela")
    print("="*50)
    
    movements = [
        (50, 0, "→ Direita pequena"),
        (-50, 0, "← Esquerda pequena"),
        (0, 50, "↓ Baixo pequeno"),
        (0, -50, "↑ Cima pequeno"),
        (100, 50, "↘ Diagonal direita-baixo"),
        (-100, -50, "↖ Diagonal esquerda-cima"),
        (200, 0, "→ Direita grande"),
        (0, 200, "↓ Baixo grande"),
    ]
    
    success_count = 0
    
    for i, (x, y, description) in enumerate(movements, 1):
        print(f"\n📤 Teste {i}/{len(movements)}: {description}")
        print(f"   Comando: X={x:+4d}, Y={y:+4d}")
        
        try:
            # Criar e enviar comando
            command = create_movement_command(x, y)
            bytes_sent = ep_out.write(command, timeout=2000)
            
            if bytes_sent == 64:
                print(f"   ✅ Comando enviado ({bytes_sent} bytes)")
                success_count += 1
                
                # Aguardar processamento
                time.sleep(0.5)
                
                # Tentar ler status se possível
                status = read_status(ep_in)
                if status:
                    print(f"   📊 Status: comandos={status['commands_received']}, last={status['last_command']:02X}")
                
                # Pausa entre comandos
                time.sleep(0.3)
            else:
                print(f"   ⚠️  Bytes enviados incorretos: {bytes_sent}")
        
        except usb.core.USBTimeoutError:
            print("   ❌ TIMEOUT - comando não foi aceito")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n📊 RESULTADO FINAL: {success_count}/{len(movements)} comandos enviados")
    
    if success_count == len(movements):
        print("🎉 TODOS OS COMANDOS FORAM ENVIADOS COM SUCESSO!")
        print("\n❓ O cursor se moveu na tela?")
        response = input("   Resposta (s/n): ").lower().strip()
        
        if response == 's':
            print("✅ COMUNICAÇÃO FUNCIONANDO PERFEITAMENTE!")
            return True
        else:
            print("❌ Comandos enviados mas cursor não se moveu")
            print("💡 Possível problema no firmware (processamento dos dados)")
            return False
    else:
        print("❌ FALHAS NA COMUNICAÇÃO")
        return False

def interactive_test(ep_in, ep_out):
    """
    Teste interativo para controle manual
    """
    print("\n🎮 TESTE INTERATIVO DE MOVIMENTO")
    print("="*50)
    print("Controles:")
    print("  W = Cima    A = Esquerda")
    print("  S = Baixo   D = Direita")
    print("  Q = Sair")
    print("\nPressione uma tecla...")
    
    try:
        import msvcrt
        
        step = 30  # Pixels por movimento
        
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                
                x, y = 0, 0
                description = ""
                
                if key == 'w':
                    y = -step
                    description = "⬆️ Cima"
                elif key == 's':
                    y = step
                    description = "⬇️ Baixo"
                elif key == 'a':
                    x = -step
                    description = "⬅️ Esquerda"
                elif key == 'd':
                    x = step
                    description = "➡️ Direita"
                elif key == 'q':
                    print("🏁 Saindo do teste interativo...")
                    break
                else:
                    print(f"❓ Tecla '{key}' não reconhecida")
                    continue
                
                # Enviar comando
                print(f"{description} (X:{x:+3d}, Y:{y:+3d})", end=" ")
                try:
                    command = create_movement_command(x, y)
                    ep_out.write(command, timeout=1000)
                    print("✅")
                except Exception as e:
                    print(f"❌ {e}")
            
            time.sleep(0.01)
    
    except ImportError:
        print("⚠️  Módulo msvcrt não disponível - teste interativo não suportado")
    except KeyboardInterrupt:
        print("\n🛑 Teste interativo cancelado")

def cleanup(device):
    """
    Limpa recursos USB
    """
    try:
        usb.util.release_interface(device, 2)
        usb.util.dispose_resources(device)
        print("🧹 Recursos USB liberados")
    except:
        pass

def main():
    """
    Função principal
    """
    print("🚀 TESTE DEFINITIVO - COMUNICAÇÃO HID")
    print("="*60)
    print("Verificando se comunicação está funcionando após instalação do WinUSB...")
    
    # 1. Encontrar dispositivo
    device = find_and_test_arduino()
    if device is None:
        return False
    
    # 2. Testar acesso do driver
    if not test_driver_access(device):
        cleanup(device)
        return False
    
    # 3. Encontrar endpoints
    ep_in, ep_out = find_endpoints(device)
    if ep_out is None:
        cleanup(device)
        return False
    
    # 4. Testar movimentos
    success = test_movements(ep_in, ep_out)
    
    if success:
        # 5. Teste interativo (opcional)
        response = input("\n🎮 Executar teste interativo? (s/n): ").lower().strip()
        if response == 's':
            interactive_test(ep_in, ep_out)
    
    # 6. Cleanup
    cleanup(device)
    
    if success:
        print("\n🎉 SUCESSO TOTAL!")
        print("✅ Comunicação HID funcionando perfeitamente")
        print("✅ Cursor respondendo aos comandos")
        print("✅ Pronto para integrar no projeto principal")
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        print("💡 Verifique:")
        print("   1. Firmware carregado corretamente")
        print("   2. LED pisca durante os comandos")
        print("   3. Interfaces corretas no Gerenciador de Dispositivos")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🔥 COMUNICAÇÃO CONFIRMADA! 🔥")
            print("Agora podemos integrar no projeto principal.")
        else:
            print("\n🔧 Ainda há problemas a resolver...")
            
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro crítico: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n📌 Pressione Enter para sair...")
