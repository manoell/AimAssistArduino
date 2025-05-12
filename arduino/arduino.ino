#include <Mouse.h>

// Variáveis globais para armazenar o comando e valores de movimento
String command = "";         // Comando recebido do buffer serial
int deltaX = 0, deltaY = 0;  // Valores de movimento para os eixos X e Y
// Gerenciamento de estado de clique
bool isClicking = false;         // Rastreia se um clique do mouse está acontecendo
unsigned long clickStartTime = 0; // Marca o momento em que o clique começa
unsigned long clickDuration;     // Especifica quanto tempo o clique durará em milissegundos
unsigned long lastPingTime = 0;  // Último momento que recebemos um ping

void setup() {
    // Inicializar comunicação serial com uma taxa de transmissão de 115200
    Serial.begin(115200);
    Serial.setTimeout(1);  // Definir um timeout curto para leituras seriais
    
    // Esperar a conexão serial ser estabelecida (importante para o Leonardo)
    while (!Serial) {
        ; // Aguardar conexão serial (Leonardo-específico)
    }
    
    Mouse.begin();         // Inicializar controle do mouse
    
    // Alimentar o gerador de números aleatórios para durações de clique variáveis
    randomSeed(analogRead(0));  // Usar um pino analógico desconectado para melhor aleatoriedade
    
    // Enviar mensagem de identificação para o handshake
    Serial.println("ARDUINO_MOUSE_READY");
}

void loop() {
    // Verificar se há algum comando aguardando no buffer serial
    if (Serial.available() > 0) {
        // Ler o comando de entrada até um caractere de nova linha
        command = Serial.readStringUntil('\n');
        command.trim();  // Limpar quaisquer espaços no início ou fim
        
        // Atualizar timestamp do último comando recebido
        lastPingTime = millis();
        
        // Se o comando é um ping, responder com pong
        if (command.equals("PING")) {
            Serial.println("PONG");
        }
        // Se o comando começa com 'M', é um comando de movimento do mouse
        else if (command.startsWith("M")) {
            int commaIndex = command.indexOf(',');  // Encontrar a posição da vírgula
            // Certificar-se de que o comando está formatado corretamente
            if (commaIndex != -1) {
                // Extrair os valores de movimento para os eixos X e Y
                deltaX = command.substring(1, commaIndex).toInt();  // Obter movimento do eixo X
                deltaY = command.substring(commaIndex + 1).toInt();  // Obter movimento do eixo Y
                
                // Mover o mouse incrementalmente para evitar saltos repentinos
                // Isso divide movimentos grandes em etapas menores
                while (deltaX != 0 || deltaY != 0) {
                    int moveX = constrain(deltaX, -127, 127);  // Limitar o movimento X para evitar overflow
                    int moveY = constrain(deltaY, -127, 127);  // Limitar o movimento Y de forma semelhante
                    Mouse.move(moveX, moveY);  // Realizar o movimento do mouse
                    deltaX -= moveX;  // Diminuir o movimento restante para o eixo X
                    deltaY -= moveY;  // Diminuir o movimento restante para o eixo Y
                    
                    // Pequena pausa para tornar o movimento mais suave
                    delayMicroseconds(500);
                }
                
                // Responder com confirmação opcional
                Serial.println("OK");
            }
        }
        // Se o comando começa com 'C', é um comando de clique do mouse
        else if (command.startsWith("C")) {
            // Iniciar o processo de clique se ainda não estamos clicando
            if (!isClicking) {
                Mouse.press(MOUSE_LEFT);  // Pressionar o botão esquerdo do mouse
                clickStartTime = millis();  // Registrar o tempo atual como o início do clique
                clickDuration = random(40, 80);  // Escolher uma duração aleatória entre 40ms e 80ms
                isClicking = true;  // Marcar que estamos em um estado de clique
                
                // Responder com confirmação
                Serial.println("CLICK_START");
            }
        }
    }
    
    // Se um clique estiver em andamento, verificar se é hora de soltar o botão
    if (isClicking) {
        // Se a duração especificada do clique tiver passado, soltar o botão
        if (millis() - clickStartTime >= clickDuration) {
            Mouse.release(MOUSE_LEFT);  // Soltar o botão esquerdo do mouse
            isClicking = false;  // Redefinir o estado de clique
            Serial.println("CLICK_END");
        }
    }
}