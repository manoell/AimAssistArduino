# Enhanced Arduino Aim Assist

Um sistema avançado de assistência de mira para jogos FPS, combinando técnicas de visão computacional e controle de hardware via Arduino Leonardo.

## Características Principais

- **Sistema Multi-modo**: Alterne entre Híbrido (Cor+YOLO), YOLO puro ou Cor pura
- **Detecção Híbrida**: Detecção por cor para velocidade + YOLO para precisão
- **Zero Falsos Positivos**: Filtragem inteligente de plantas e outros elementos visuais
- **Detecção Precisa**: Modelo YOLO treinado especificamente para jogos FPS
- **Movimentos Naturais**: Suavização avançada para movimentos realistas
- **Clonagem de Dispositivo**: O Arduino aparece para o sistema como seu próprio mouse

## Requisitos

### Hardware
- Arduino Leonardo (ou compatível com HID)
- Cabo USB
- PC com GPU (recomendável para melhor desempenho do YOLO)

### Software
- Python 3.8+ (recomendado Python 3.8.10)
- Bibliotecas Python:
  ```
  opencv-python
  numpy
  pyserial
  mss
  pyautogui
  keyboard
  pywin32
  ultralytics
  ```

## Instalação

1. Clone ou baixe este repositório:

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Baixe o arquivo do modelo YOLO (`my_yolo_model.pt`) e coloque-o na pasta raiz do projeto.

4. Configure seu Arduino:
   - **Método Simples**: Carregue o arquivo `arduino_code.ino` usando o Arduino IDE
   - **Método Avançado**: Execute `python spoofer.py` para clonar seu mouse

5. Configure o arquivo `settings.ini` para:
   - Definir a porta COM correta para seu Arduino
   - Ajustar velocidades, FOV e outras preferências

6. Execute o programa:
```
python main.py
```

## Modos de Detecção

O sistema oferece três modos diferentes que podem ser alternados durante o uso:

### 1. Modo HÍBRIDO (Cor + YOLO)
- **Como Funciona**: Usa detecção de cor para encontrar candidatos e YOLO para confirmar
- **Vantagens**: Combina velocidade da detecção por cor com precisão do YOLO
- **Melhor Para**: Uso geral, equilíbrio entre desempenho e precisão
- **Falsos Positivos**: Praticamente zero (YOLO filtra plantas e outros elementos)

### 2. Modo YOLO
- **Como Funciona**: Usa apenas o modelo YOLO para detectar alvos diretamente
- **Vantagens**: Máxima precisão, independente da cor dos contornos
- **Melhor Para**: Ambientes com muitos elementos visuais semelhantes
- **Falsos Positivos**: Mínimos, mas usa mais recursos computacionais

### 3. Modo COR
- **Como Funciona**: Usa apenas detecção por cor HSV para encontrar contornos roxos
- **Vantagens**: Baixo uso de recursos, resposta mais rápida
- **Melhor Para**: Sistemas com recursos limitados ou quando YOLO não está disponível
- **Falsos Positivos**: Alguns (plantas, efeitos visuais com cores similares)

## Teclas de Controle

| Tecla | Função |
|-------|--------|
| F2 | Ativar/desativar o aim assist |
| RMB (botão direito do mouse) | Ativar a assistência de mira (quando habilitada) |
| F3 | Ativar/desativar modo de depuração |
| F4 | Recarregar configurações |
| F5 | Alternar entre modos de detecção (Híbrido → YOLO → Cor) |
| F12 | Sair do programa |

## Configuração

O arquivo `settings.ini` controla todas as configurações do sistema:

### Aimbot
- `fov`: Tamanho do campo de visão para captura (padrão: 100)
- `x_speed`/`y_speed`: Velocidade de movimento nos eixos X/Y (padrão: 0.4)
- `target_offset`: Ajuste vertical para mira (valores maiores = mais baixo)
- `smoothing`: Fator de suavização para movimentos naturais (0-1)

### Color
- `lower_color`/`upper_color`: Limites HSV para detecção de cor

### Hotkeys
Teclas personalizáveis para todas as funções

### YOLO
- `model_path`: Caminho para o modelo YOLO treinado
- `confidence`: Limiar de confiança para detecções (0-1)
- `default_mode`: Modo de detecção padrão (0: Híbrido, 1: YOLO, 2: Cor)

## Modo de Depuração

Ative o modo de depuração (F3) para:
- Salvar imagens de detecção na pasta `debug/`
- Ver estatísticas no console sobre detecções e falsos positivos
- Analisar a eficácia dos diferentes modos

## Clonagem de Mouse

O utilitário de clonagem (`spoofer.py`) permite que seu Arduino Leonardo seja reconhecido pelo sistema como uma cópia exata do seu mouse atual:

1. Execute `python spoofer.py`
2. Selecione seu mouse atual na lista exibida
3. Siga as instruções para clonar sua identificação USB
4. Reconecte o Arduino para que as alterações tenham efeito

Isso evita qualquer referência a "Arduino" nos dispositivos conectados, tornando a detecção praticamente impossível.

## Uso em Valorant

Para uso ótimo em Valorant:

1. Configure a cor de destaque de inimigos para roxo/púrpura nas opções do jogo
2. Ajuste `target_offset` em `settings.ini` para acertar a cabeça
3. Use o modo depuração para verificar se as detecções estão precisas
4. Experimente diferentes modos para encontrar o melhor para seu sistema

O modelo YOLO incluído foi treinado especificamente com imagens de Valorant, garantindo máxima eficácia.

## Solução de Problemas

- **Arduino não detectado**: Verifique a porta COM em `settings.ini`
- **Detecção imprecisa**: Ajuste os valores HSV nas configurações
- **Movimento instável**: Aumente o valor de `smoothing`
- **Baixo desempenho**: Experimente o modo COR para reduzir o uso de recursos

## Aviso Legal

Este software é fornecido apenas para fins educacionais. O uso deste software para obter vantagens injustas em jogos competitivos pode violar os termos de serviço dos jogos. Use por sua própria conta e risco.

## Créditos

Este projeto integra tecnologias e conceitos de várias fontes, incluindo o modelo YOLO treinado especificamente para detecção em jogos FPS.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.