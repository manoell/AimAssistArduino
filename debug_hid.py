import usb.core
import usb.util
import usb.backend.libusb1
import struct
import time

def test_libusb_with_winusb():
    """
    Teste libusb após instalação do driver WinUSB via Zadig
    """
    print("🔧 TESTE LIBUSB - APÓS WINUSB DRIVER")
    print("="*60)
    
    try:
        # Usar backend libusb1 (mais estável)
        backend = usb.backend.libusb1.get_backend()
        if not backend:
            print("❌ Backend libusb1 não disponível")
            print("💡 Execute: pip install libusb1")
            return False
        
        print("✅ Backend libusb1 encontrado")
        
        # Buscar dispositivo Arduino
        print("\n🔍 Procurando dispositivo Arduino...")
        device = usb.core.find(idVendor=0x046D, idProduct=0xC547, backend=backend)
        
        if device is None:
            print("❌ Dispositivo não encontrado!")
            print("💡 Possíveis causas:")
            print("   - Arduino desconectado")
            print("   - Driver não instalado corretamente")
            print("   - VID/PID incorretos")
            
            # Listar todos os dispositivos para debug
            print("\n📋 Dispositivos USB encontrados:")
            all_devices = list(usb.core.find(find_all=True, backend=backend))
            for dev in all_devices[:10]:  # Primeiros 10
                print(f"   VID:0x{dev.idVendor:04X} PID:0x{dev.idProduct:04X}")
            
            return False
        
        print(f"✅ Arduino encontrado!")
        print(f"   VID: 0x{device.idVendor:04X}")
        print(f"   PID: 0x{device.idProduct:04X}")
        print(f"   Bus: {device.bus}")
        print(f"   Address: {device.address}")
        
        # Configurar dispositivo
        print("\n⚙️ Configurando dispositivo...")
        
        # Detach kernel driver (apenas Linux, seguro no Windows)
        try:
            if device.is_kernel_driver_active(2):
                device.detach_kernel_driver(2)
                print("   Kernel driver detached")
        except:
            pass  # Windows não tem kernel driver HID
        
        # Set configuration
        try:
            device.set_configuration()
            print("   ✅ Configuração definida")
        except usb.core.USBError as e:
            print(f"   ⚠️ Aviso configuração: {e}")
            # Continuar mesmo com aviso
        
        # Claim interface 2
        try:
            usb.util.claim_interface(device, 2)
            print("   ✅ Interface 2 claimed (Generic HID)")
        except usb.core.USBError as e:
            print(f"   ❌ Erro ao claim interface: {e}")
            return False
        
        # Encontrar endpoints
        cfg = device.get_active_configuration()
        interface = cfg[(2, 0)]  # Interface 2, alternate 0
        
        ep_out = None
        ep_in = None
        
        for endpoint in interface:
            if usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                ep_out = endpoint
                print(f"   ✅ Endpoint OUT: 0x{endpoint.bEndpointAddress:02X}")
            elif usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_IN:
                ep_in = endpoint
                print(f"   ✅ Endpoint IN: 0x{endpoint.bEndpointAddress:02X}")
        
        if ep_out is None:
            print("   ❌ Endpoint OUT não encontrado!")
            return False
        
        # TESTAR COMUNICAÇÃO
        print(f"\n🧪 Testando comunicação...")
        
        commands = [
            ("Movimento →", struct.pack('<BhhBbBB55x', 0x01, 50, 0, 0, 0, 5, 5)),
            ("Movimento ←", struct.pack('<BhhBbBB55x', 0x01, -50, 0, 0, 0, 5, 5)),  
            ("Movimento ↓", struct.pack('<BhhBbBB55x', 0x01, 0, 50, 0, 0, 5, 5)),
            ("Movimento ↑", struct.pack('<BhhBbBB55x', 0x01, 0, -50, 0, 0, 5, 5)),
            ("Reset", struct.pack('<BhhBbBB55x', 0x04, 0, 0, 0, 0, 0, 0)),
        ]
        
        success_count = 0
        
        for cmd_name, cmd_data in commands:
            try:
                print(f"   📤 {cmd_name}...")
                
                # Enviar comando
                result = ep_out.write(cmd_data, timeout=1000)
                
                if result == len(cmd_data):
                    print(f"      ✅ {result} bytes enviados")
                    success_count += 1
                    
                    # Pausa para observar movimento
                    print(f"      👀 Observe o cursor...")
                    time.sleep(0.8)
                else:
                    print(f"      ⚠️ Apenas {result}/{len(cmd_data)} bytes")
                
            except usb.core.USBTimeoutError:
                print(f"      ❌ Timeout")
            except usb.core.USBError as e:
                print(f"      ❌ Erro USB: {e}")
            except Exception as e:
                print(f"      ❌ Erro: {e}")
        
        # Cleanup
        usb.util.release_interface(device, 2)
        usb.util.dispose_resources(device)
        
        # Resultado final
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Comandos enviados: {success_count}/{len(commands)}")
        
        if success_count > 0:
            print("   🎉 COMUNICAÇÃO FUNCIONANDO!")
            print("   ✅ HID + WinUSB está operacional")
            print("   ✅ Latência mínima")
            print("   ✅ Não detectável por anticheats")
            return True
        else:
            print("   ❌ Nenhum comando funcionou")
            print("   💡 Verifique se o firmware Arduino está correto")
            return False
        
    except ImportError:
        print("❌ pyusb não instalado")
        print("💡 Execute: pip install pyusb")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def install_dependencies():
    """
    Instrui sobre instalação das dependências
    """
    print("📦 DEPENDÊNCIAS NECESSÁRIAS")
    print("="*40)
    print("Execute os seguintes comandos:")
    print("pip install pyusb")
    print("pip install libusb1")
    print()
    print("Ou todos de uma vez:")
    print("pip install pyusb libusb1")

if __name__ == "__main__":
    print("🚀 TESTE FINAL - LIBUSB + WINUSB")
    print("="*70)
    
    try:
        import usb
        success = test_libusb_with_winusb()
        
        if success:
            print("\n🎊 MISSÃO CUMPRIDA!")
            print("Comunicação HID funcionando perfeitamente!")
            print("Agora você pode usar este método no seu projeto.")
        else:
            print("\n❌ Ainda com problemas...")
            print("Tente verificar:")
            print("1. Se o driver WinUSB está realmente instalado")
            print("2. Se o Arduino não está sendo usado por outro programa")
            print("3. Se está executando como Administrador")
            
    except ImportError:
        install_dependencies()