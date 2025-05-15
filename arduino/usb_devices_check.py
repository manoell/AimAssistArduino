import subprocess
import re
import sys
import os

def run_powershell_command(command):
    """Executa um comando PowerShell e retorna a saída"""
    process = subprocess.Popen(
        ["powershell", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Erro ao executar comando: {stderr}")
    return stdout

def get_usb_devices():
    """Obtém informações sobre todos os dispositivos USB usando PowerShell"""
    command = """
    Get-PnpDevice -Class USB -PresentOnly | ForEach-Object {
        $device = $_
        $instanceId = $device.InstanceId
        $vendorIdMatch = [regex]::Match($instanceId, 'VID_([0-9A-F]{4})')
        $productIdMatch = [regex]::Match($instanceId, 'PID_([0-9A-F]{4})')
        
        if ($vendorIdMatch.Success -and $productIdMatch.Success) {
            $vendorId = $vendorIdMatch.Groups[1].Value
            $productId = $productIdMatch.Groups[1].Value
            
            $deviceDetail = Get-PnpDeviceProperty -InstanceId $device.InstanceId
            $description = ($deviceDetail | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_FriendlyName' }).Data
            $manufacturer = ($deviceDetail | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Manufacturer' }).Data
            
            [PSCustomObject]@{
                Name = $device.FriendlyName
                Description = $description
                Manufacturer = $manufacturer
                VendorID = $vendorId
                ProductID = $productId
                Status = $device.Status
                InstanceId = $device.InstanceId
            }
        }
    } | ConvertTo-Json
    """
    
    result = run_powershell_command(command)
    return result

def main():
    """Função principal para verificar dispositivos USB"""
    print("Procurando dispositivos USB usando PowerShell...\n")
    
    # Gera um arquivo temporário com o resultado JSON
    output_file = "usb_devices.txt"
    
    # Obtém as informações dos dispositivos USB
    devices_json = get_usb_devices()
    
    # Salva o resultado bruto para análise
    with open(output_file, 'w') as f:
        f.write(devices_json)
    
    print(f"Dados dos dispositivos USB foram salvos em '{output_file}'")
    
    # Busca específica pelo Logitech G502 X PLUS
    logitech_pattern = r'VID_046D.*PID_C095'
    if re.search(logitech_pattern, devices_json, re.IGNORECASE):
        print("\n" + "=" * 80)
        print("ENCONTRADO: Logitech G502 X PLUS (VID: 046D, PID: C095)")
        
        # Extrai a linha que contém as informações do G502
        matches = re.findall(r'({[^{}]*"VendorID": "046D"[^{}]*"ProductID": "C095"[^{}]*})', devices_json, re.IGNORECASE | re.DOTALL)
        if matches:
            for match in matches:
                print("\nDetalhes do dispositivo:")
                print(match)
        print("=" * 80)
    else:
        print("\nAVISO: Logitech G502 X PLUS (VID: 046D, PID: C095) NÃO foi encontrado!")
    
    # Agora vamos também verificar usando o comando 'usbdeview' se disponível
    try:
        # Verifica se o USBDeview está no mesmo diretório
        if os.path.exists("USBDeview.exe"):
            print("\nExecutando USBDeview para análise adicional...")
            usbdeview_output = "usbdeview_output.txt"
            subprocess.run(["USBDeview.exe", "/shtml", usbdeview_output], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Relatório do USBDeview salvo em '{usbdeview_output}'")
    except Exception as e:
        print(f"Erro ao executar USBDeview: {e}")
    
    print("\nAnalise os arquivos gerados para verificar os detalhes dos dispositivos USB.")

if __name__ == "__main__":
    try:
        main()
        print("\nPressione Enter para sair...")
        input()
    except Exception as e:
        print(f"Erro: {e}")
        print("\nPressione Enter para sair...")
        input()