# 🎯 Enhanced Arduino Aim Assist - Ultra Performance Edition

Sistema avançado de assistência de mira (aim assist) para jogos FPS, usando Arduino Leonardo com comunicação **Raw HID ultra-otimizada** para latência sub-milissegundo.

## ⚡ **PERFORMANCE ULTRA-OTIMIZADA**

- **Latência**: 1ms (vs 36ms da versão anterior)
- **Comunicação**: Raw HID direto (sem drivers COM)
- **Polling Rate**: 1000Hz (1ms)
- **Confiabilidade**: 99.6%+ taxa de sucesso
- **Responsividade**: Nível profissional para gaming competitivo

## 🔥 **CARACTERÍSTICAS PRINCIPAIS**

- **Detecção Precisa de Cores**: Sistema otimizado para detectar contornos roxos (Valorant)
- **Algoritmo de Suavização**: Movimentos naturais e humanos
- **Detecção de Cabeça**: Mira automática ajustada para zona superior dos contornos
- **Raw HID Ultra-Rápido**: Comunicação direta USB sem overhead de drivers
- **Threading Assíncrono**: Processamento em paralelo para máxima performance
- **Sistema Adaptativo**: Ajusta automaticamente para condições ótimas
- **Arquitetura Modular**: Código bem organizado e facilmente extensível

## 🛠 **REQUISITOS DE HARDWARE**

- **Arduino Leonardo** (ou compatível com ATmega32U4)
- **Cabo USB** (USB 2.0 ou superior)
- **Porta USB dedicada** (evitar hubs para máxima performance)

## 💻 **REQUISITOS DE SOFTWARE**

- **Python 3.7+**
- **Windows 10/11** (testado e otimizado)
- **Bibliotecas Python** (instaláveis via pip):
  - OpenCV (`opencv-python`)
  - NumPy (`numpy`)
  - PyUSB (`pyusb`) - **NOVO: substitui pyserial**
  - MSS (`mss`) - captura de tela rápida
  - PyAutoGUI (`pyautogui`)
  - Keyboard (`keyboard`)
  - PyWin32 (`pywin32`)

## 🚀 **INSTALAÇÃO**

### 1. **Clonar o Repositório**
```bash
git clone https://github.com/seu-usuario/arduino-aim-assist.git
cd arduino-aim-assist
```

### 2. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 3. **Configurar o Arduino**

#### **Carregar Firmware LUFA Otimizado:**
1. Abrir projeto `LUFALogiMouse` no Arduino IDE
2. Selecionar: **Arduino Leonardo** como placa
3. **Carregar os arquivos otimizados:**
   - `LUFAConfig.h` - Configurações ultra-otimizadas
   - `Descriptors.c` - Polling rate 1000Hz
   - `LogitechMouse.c` - Processamento otimizado
   - `LUFALogiMouse.ino` - Loop principal sem delays
4. **Compilar e carregar** no Arduino

#### **Verificar Instalação:**
Após carregar o firmware, o Arduino deve aparecer como:
- **Nome**: "Logitech USB Receiver"
- **VID**: 0x046D
- **PID**: 0xC547

### 4. **Executar o Sistema**
```bash
python main.py
```

## 🎮 **USO**

### **Controles Principais:**
- **F2**: Ativar/Desativar aim assist
- **Botão Direito do Mouse**: Usar aim assist (quando ativado)
- **F4**: Recarregar configurações
- **Ctrl+I**: Mostrar estatísticas de performance
- **F12**: Sair do programa

### **Configuração para Jogos:**

#### **Valorant:**
1. Configurar cor de destaque de inimigos para **roxo/púrpura**
2. Usar **modo janela sem bordas**
3. Ajustar `target_offset` no `settings.ini` para mira na cabeça

#### **Outros Jogos:**
1. Ajustar cores no `settings.ini` conforme necessário
2. Testar e otimizar configurações de velocidade e suavização

## ⚙️ **CONFIGURAÇÕES AVANÇADAS**

### **settings.ini:**
```ini
[Connection]
com_port = AUTO_RAW_HID  # Detecção automática via Raw HID

[Aimbot]
fov = 100              # Campo de visão
x_speed = 0.4          # Velocidade horizontal
y_speed = 0.4          # Velocidade vertical
target_offset = 2.0    # Offset para mira na cabeça
smoothing = 0.7        # Suavização (0.0-1.0)

[Color]
lower_color = 125,100,100  # HSV inferior (roxo)
upper_color = 155,255,255  # HSV superior (roxo)

[Performance]
preferred_timeout = ultra  # ultra, turbo, fast, safe
aimbot_priority = True     # Prioridade para comandos de aimbot
```

## 📊 **MONITORAMENTO DE PERFORMANCE**

### **Estatísticas em Tempo Real:**
- **Latência**: Tempo de resposta em milissegundos
- **Taxa de Sucesso**: Porcentagem de comandos bem-sucedidos
- **Comandos de Aimbot**: Contagem de movimentos prioritários
- **Modo de Operação**: ultra/turbo/fast/safe
- **Filas**: Status das filas de comando

### **Como Verificar:**
1. Pressionar **Ctrl+I** durante execução
2. Verificar output no console
3. Monitorar estatísticas finais ao sair

## 🔧 **OTIMIZAÇÕES IMPLEMENTADAS**

### **Lado Python:**
- **Raw HID**: Comunicação direta USB sem overhead de drivers
- **Threading Assíncrono**: Processamento paralelo
- **Filas Prioritárias**: Comandos de aimbot têm prioridade máxima
- **Sistema Adaptativo**: Ajusta automaticamente para condições ótimas
- **Cache de Comandos**: Melhora performance de comandos repetitivos

### **Lado Arduino:**
- **Polling Rate 1000Hz**: Máxima frequência de comunicação
- **Loop Otimizado**: Sem delays, processamento múltiplo por ciclo
- **Processamento Inline**: Comandos processados imediatamente
- **Configuração USB Agressiva**: Timeouts mínimos, máxima responsividade

## 🎯 **RESULTADOS DE PERFORMANCE**

### **Benchmarks Típicos:**
- **Latência**: 1.0ms (mín: 0.4ms, máx: 10.9ms)
- **FPS Efetivo**: 60-65 comandos/segundo
- **Taxa de Sucesso**: 99.6%+
- **Modo de Operação**: ULTRA (1ms timeout)

### **Comparação com Versão Anterior:**
- **Latência**: 97% de melhoria (36ms → 1ms)
- **FPS**: 280% de melhoria (17 → 65)
- **Confiabilidade**: 99.6% vs ~95%

## 🛡️ **RECURSOS DE SEGURANÇA**

- **Movimentos Naturais**: Algoritmo de suavização evita detecção
- **Offset de Mira**: Simula comportamento humano natural
- **Responsividade Variável**: Evita padrões mecânicos
- **Compatibilidade com Anti-Cheat**: Usa interfaces padrão do sistema

## 🔍 **SOLUÇÃO DE PROBLEMAS**

### **Arduino não detectado:**
1. Verificar conexão USB
2. Confirmar que firmware LUFA está carregado
3. Verificar se aparece como "Logitech USB Receiver"
4. Tentar porta USB diferente (evitar hubs)

### **Performance baixa:**
1. Verificar modo de operação (deve ser ULTRA)
2. Pressionar Ctrl+I para ver estatísticas
3. Verificar se taxa de sucesso > 95%
4. Considerar fechar outros programas USB

### **Detecção imprecisa:**
1. Ajustar cores HSV no `settings.ini`
2. Verificar iluminação do jogo
3. Testar diferentes valores de `target_offset`
4. Configurar cor de destaque no jogo

## 🤝 **CONTRIBUIÇÃO**

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Criar branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit das mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## ⚠️ **AVISO LEGAL**

Este software é fornecido apenas para fins **educacionais e de pesquisa**. O uso deste software para obter vantagens injustas em jogos competitivos pode violar os termos de serviço dos jogos. 

**Use por sua própria conta e risco.**

## 📄 **LICENÇA**

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 **AGRADECIMENTOS**

- **LUFA Library** - Framework USB para AVR
- **OpenCV** - Biblioteca de visão computacional
- **PyUSB** - Interface Python para USB
- **Comunidade Arduino** - Suporte e documentação

---

### 🎯 **Sistema otimizado para performance profissional de gaming!**

**Latência de 1ms • Polling Rate 1000Hz • Confiabilidade 99.6%**
