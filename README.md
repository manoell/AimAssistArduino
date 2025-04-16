# Arduino Aim Assist - Versão Simplificada

Um sistema eficiente de assistência de mira para jogos FPS, usando técnicas de detecção por cor e controle de hardware via Arduino Leonardo.

## Características Principais

- **Detecção por Cor**: Sistema otimizado para identificar contornos de inimigos com base em cores HSV
- **Zero Falsos Positivos**: Filtragem inteligente com parâmetros ajustáveis para minimizar detecções incorretas
- **Movimentos Naturais**: Suavização avançada para movimentos realistas
- **Clonagem de Dispositivo**: O Arduino aparece para o sistema como seu próprio mouse

## Requisitos

### Hardware
- Arduino Leonardo (ou compatível com HID)
- Cabo USB

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
  ```

## Instalação

1. Clone ou baixe este repositório:

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure seu Arduino:
   - **Método Simples**: Carregue o arquivo `arduino/arduino.ino` usando o Arduino IDE
   - **Método Avançado**: Execute `python spoofer.py` para clonar seu mouse

4. Configure o arquivo `settings.ini` para:
   - Definir a porta COM correta para seu Arduino
   - Ajustar velocidades, FOV e outras preferências
   - Configurar os valores HSV para a cor dos inimigos

5. Execute o programa:
```
python main.py
```

## Modo de Detecção

O sistema usa exclusivamente detecção por cor HSV para identificar alvos, proporcionando excelente desempenho:

### Detecção por COR
- **Como Funciona**: Usa detecção por cor HSV para encontrar contornos de cor específica (geralmente roxo/púrpura)
- **Vantagens**: Baixo uso de recursos, resposta rápida, eficiente
- **Melhor Para**: Todos os sistemas, especialmente aqueles com recursos limitados
- **Configuração Ideal**: Usar com cores de contorno de inimigo bem definidas nos jogos

## Teclas de Controle

| Tecla | Função |
|-------|--------|
| F2 | Ativar/desativar o aim assist |
| RMB (botão direito do mouse) | Ativar a assistência de mira (quando habilitada) |
| F3 | Ativar/desativar modo de depuração |
| F4 | Recarregar configurações |
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

## Modo de Depuração

Ative o modo de depuração (F3) para:
- Salvar imagens de detecção na pasta `debug/`
- Ver estatísticas no console sobre detecções e FPS
- Analisar a eficácia da detecção

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
4. Refine os valores HSV para detecção perfeita

## Solução de Problemas

- **Arduino não detectado**: Verifique a porta COM em `settings.ini`
- **Detecção imprecisa**: Ajuste os valores HSV nas configurações
- **Movimento instável**: Aumente o valor de `smoothing`
- **Sem detecção**: Verifique se a cor de destaque dos inimigos no jogo corresponde aos valores HSV configurados

## Dicas para Ajustes de Cores HSV

Para obter o melhor desempenho de detecção:

1. Ative o modo de depuração (F3)
2. Verifique as imagens salvas na pasta `debug/`
3. Se estiver detectando objetos errados:
   - Diminua o intervalo entre `lower_color` e `upper_color`
   - Aumente o valor mínimo em `lower_color` (segundo número)
4. Se estiver perdendo alvos:
   - Aumente o intervalo entre `lower_color` e `upper_color`
   - Diminua o valor mínimo em `lower_color` (segundo número)

## Aviso Legal

Este software é fornecido apenas para fins educacionais. O uso deste software para obter vantagens injustas em jogos competitivos pode violar os termos de serviço dos jogos. Use por sua própria conta e risco.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.