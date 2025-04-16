# Enhanced Arduino Aim Assist

Este projeto implementa um sistema avançado de assistência de mira (aim assist) para jogos FPS, usando Arduino Leonardo para controle de mouse. O sistema foi projetado para ser modular, eficiente e facilmente configurável.

## Características Principais

- **Detecção Precisa de Cores**: Sistema otimizado para detectar contornos roxos (padrão de destaque de inimigos em Valorant)
- **Algoritmo de Suavização**: Movimentos mais naturais e humanos através de técnicas avançadas de suavização
- **Detecção de Cabeça**: Mira automática ajustada para zona superior dos contornos detectados
- **Arquitetura Modular**: Código bem organizado e facilmente extensível
- **Configuração Flexível**: Todas as configurações podem ser ajustadas através do arquivo settings.ini
- **Alta Performance**: Captura de tela assíncrona para máxima velocidade e eficiência

## Requisitos de Hardware

- Arduino Leonardo (ou compatível com HID)
- Cabo USB

## Requisitos de Software

- Python 3.7+
- Bibliotecas Python (instaláveis via pip):
  - OpenCV (`opencv-python`)
  - NumPy (`numpy`)
  - PySerial (`pyserial`)
  - MSS (`mss`) - captura de tela rápida
  - PyAutoGUI (`pyautogui`)
  - Keyboard (`keyboard`)
  - PyWin32 (`pywin32`)

## Clonagem de Mouse (Opcional, mas Recomendado)

Para maior segurança, o projeto inclui um utilitário para "clonar" seu mouse real, fazendo com que o Arduino Leonardo apareça para o sistema operacional exatamente como seu mouse legítimo:

1. Conecte seu Arduino Leonardo e seu mouse normal ao computador
2. Execute o utilitário de clonagem:
```
python spoofer.py
```
3. Siga as instruções na tela para selecionar qual mouse clonar
4. Após a conclusão, desconecte e reconecte o Arduino para que as alterações tenham efeito

Esta etapa é altamente recomendada para evitar detecção, pois remove qualquer referência a "Arduino" nos dispositivos conectados.

## Instalação

1. Clone este repositório:
```
git clone https://github.com/seu-usuario/arduino-aim-assist.git
cd arduino-aim-assist
```

2. Instale as dependências necessárias:
```
pip install -r requirements.txt
```

3. Configure o Arduino (duas opções):
   - **Opção 1 (Padrão):** Carregue o código `arduino_code.ino` no seu Arduino Leonardo usando o Arduino IDE.
   - **Opção 2 (Recomendada):** Use o utilitário de clonagem (instruções abaixo) para configurar o Arduino para imitar seu mouse real.

4. Configure o arquivo `settings.ini` com a porta COM correta e outras preferências.

5. Execute o programa principal:
```
python main.py
```

## Uso

1. Inicie o programa executando `python main.py`
2. Pressione a tecla definida em `aim_toggle` (padrão: F2) para ativar o aim assist
3. Segure a tecla definida em `aim_key` (padrão: botão direito do mouse) para usar o aim assist quando ativado
4. Outras teclas úteis:
   - `reload` (padrão: F4): Recarrega as configurações
   - `exit` (padrão: F12): Sai do programa

## Estrutura do Projeto

- `main.py`: Programa principal, coordena todos os componentes
- `screen_capture.py`: Gerencia a captura de tela de alta performance
- `target_detector.py`: Implementa algoritmos de detecção de alvo
- `mouse_controller.py`: Controla a comunicação com o Arduino
- `config_manager.py`: Gerencia configurações do sistema
- `utils.py`: Funções utilitárias
- `arduino_code.ino`: Código para o Arduino Leonardo

## Configuração para Jogos Específicos

### Valorant
- No jogo, configure a cor de destaque de inimigos para roxo/púrpura
- As configurações padrão são otimizadas para Valorant
- Ajuste `target_offset` para mira na cabeça conforme necessário

## Desenvolvimento

Para expandir ou modificar este projeto:

1. Clone o repositório
2. Instale as dependências de desenvolvimento
3. Modifique os módulos conforme necessário
4. Contribua com pull requests

## Solução de Problemas

- **Arduino não detectado**: Verifique a conexão USB e certifique-se de que a porta COM está correta
- **Detecção imprecisa**: Ajuste os valores de cor HSV nas configurações
- **Movimento instável**: Aumente o valor de `smoothing` para movimentos mais suaves
- **Problemas de captura de tela**: Verifique se o jogo está em modo de janela sem bordas ou tela cheia

## Aviso Legal

Este software é fornecido apenas para fins educacionais. O uso deste software para obter vantagens injustas em jogos competitivos pode violar os termos de serviço dos jogos. Use por sua própria conta e risco.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.