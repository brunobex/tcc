import pygame  # Biblioteca para criação de jogos
import os  # Biblioteca para interagir com o sistema operacional
import random  # Biblioteca para gerar números aleatórios
import logging  # Biblioteca para registro de logs

# Configurações de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Variáveis para controlar o estado do jogo e a velocidade
VEL_NORMAL = 30  # Velocidade normal do jogo
VEL_ACELERADA = 120  # Velocidade acelerada do jogo
velocidade_jogo = VEL_NORMAL  # Velocidade inicial do jogo
bug_ativo = False  # Variável para controlar se o bug está ativo
mostrar_bug = False  # Variável para controlar a visibilidade do retângulo de bug
mostrar_colisoes = False  # Variável para controlar a visibilidade das colisões

# Dimensões da tela
TELA_LARGURA = 500
TELA_ALTURA = 800

# Carregar e escalar imagens para o jogo
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

# Inicializar fontes
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)  # Fonte para pontos
FONTE_BOTAO = pygame.font.SysFont('arial', 30)  # Fonte para botão

# Função para desenhar um botão na tela
def desenhar_botao(tela, texto, pos, cor_fundo, cor_texto):
    botao_rect = pygame.Rect(pos)  # Criar retângulo do botão
    pygame.draw.rect(tela, cor_fundo, botao_rect)  # Desenhar retângulo do botão
    texto_surface = FONTE_BOTAO.render(texto, True, cor_texto)  # Renderizar texto do botão
    texto_rect = texto_surface.get_rect(center=botao_rect.center)  # Centralizar texto no botão
    tela.blit(texto_surface, texto_rect)  # Desenhar texto na tela
    return botao_rect  # Retornar retângulo do botão para detecção de clique

# Função para verificar se um botão foi clicado
def verificar_clique_botao(pos_mouse, botao_rect):
    return botao_rect.collidepoint(pos_mouse)  # Verificar se a posição do mouse está dentro do retângulo do botão

# Função para escrever logs em um arquivo
def escrever_log(mensagem):
    with open("log.txt", "a") as log_file:
        log_file.write(mensagem + "\n")

# Classe que representa o agente no jogo
class Agente:
    IMGS = IMAGENS_PASSARO  # Imagens do pássaro para animação
    # Constantes de animação de rotação
    ROTACAO_MAXIMA = 25  # Ângulo máximo de rotação
    VELOCIDADE_ROTACAO = 20  # Velocidade de rotação
    TEMPO_ANIMACAO = 5  # Tempo para cada quadro de animação

    def __init__(self):
        self.x = 230  # Posição X inicial do agente
        self.y = 350  # Posição Y inicial do agente
        self.angulo = 0  # Ângulo inicial do agente
        self.velocidade = 0  # Velocidade inicial do agente
        self.altura = self.y  # Altura inicial do agente
        self.tempo = 0  # Contador de tempo para cálculos de movimento
        self.contagem_imagem = 0  # Contador de imagem para animação
        self.imagem = self.IMGS[0]  # Imagem inicial do agente
        self.reward = 0  # Recompensa inicial do agente
        self.bug_detectado = False  # Indicador de bug detectado
        self.bug_timer = 0  # Temporizador de bug

    def pular(self):
        self.velocidade = -10.5  # Velocidade negativa para pular
        self.tempo = 0  # Reiniciar contador de tempo
        self.altura = self.y  # Definir altura atual

    def mover(self):
        # Calcular deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # Restringir deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento  # Atualizar posição Y

        # Manter o agente dentro da tela
        if self.y + self.imagem.get_height() > TELA_ALTURA - IMAGEM_CHAO.get_height():
            self.y = TELA_ALTURA - IMAGEM_CHAO.get_height() - self.imagem.get_height()
            self.velocidade = 0
        elif self.y < 0:
            self.y = 0
            self.velocidade = 0

        # Ajustar ângulo do agente
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    # Função para detectar bugs
    def detectar_bug(self, canos, chao, bug_rect):
        global bug_ativo
        if bug_ativo and bug_rect.collidepoint(self.x, self.y):
            mensagem = f"Bug detectado pelo agente na posição: ({self.x}, {self.y})"
            logging.warning(mensagem)
            escrever_log(mensagem)
            self.reward -= 1
            self.bug_detectado = True
            self.bug_timer = 30  # Duração do efeito de piscamento
            return True
        for cano in canos:
            if cano.colidir(self):
                logging.warning(f"Colisão detectada pelo agente na posição: ({self.x}, {self.y})")
                self.reward -= 1
                return True
        if self.y + self.imagem.get_height() > chao.y or self.y < 0:
            logging.warning(f"Colisão com o chão ou fora da tela detectada pelo agente na posição: ({self.x}, {self.y})")
            self.reward -= 1
            return True
        return False

    # Função para explorar o ambiente
    def explorar(self):
        # Probabilidade de pular
        if random.random() < 0.1:  # 10% de chance de pular a cada frame
            self.pular()

    def desenhar(self, tela):
        # Definir qual imagem do agente vai usar
        self.contagem_imagem += 1

        if self.bug_timer > 0:
            self.bug_timer -= 1
            if self.bug_timer % 5 < 2:
                return  # Pula o desenho para criar efeito de piscamento

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # Desenhar imagem rotacionada do agente
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

        # Desenhar máscara de colisão
        if mostrar_colisoes:
            mask = self.get_mask()
            mask_surf = mask.to_surface(unsetcolor=None, setcolor=(255, 0, 0, 100))
            tela.blit(mask_surf, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)  # Obter máscara para detecção de colisão

# Classe que representa os canos no jogo
class Cano:
    DISTANCIA = 200  # Distância entre os canos
    VELOCIDADE = 5  # Velocidade de movimento dos canos

    def __init__(self, x):
        self.x = x  # Posição X do cano
        self.altura = 0  # Altura do cano
        self.pos_topo = 0  # Posição do cano superior
        self.pos_base = 0  # Posição do cano inferior
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)  # Inverter imagem para cano superior
        self.CANO_BASE = IMAGEM_CANO  # Imagem para cano inferior
        self.passou = False  # Boolean para verificar se o cano foi passado
        self.definir_altura()  # Definir altura do cano

    def definir_altura(self):
        # Definir altura aleatória para os canos
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE  # Mover cano para a esquerda

    def desenhar(self, tela):
        # Desenhar canos na tela
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

        # Desenhar máscara de colisão
        if mostrar_colisoes:
            topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
            base_mask = pygame.mask.from_surface(self.CANO_BASE)
            topo_surf = topo_mask.to_surface(unsetcolor=None, setcolor=(255, 0, 0, 100))
            base_surf = base_mask.to_surface(unsetcolor=None, setcolor=(255, 0, 0, 100))
            tela.blit(topo_surf, (self.x, self.pos_topo))
            tela.blit(base_surf, (self.x, self.pos_base))

    def colidir(self, passaro):
        # Verificar colisão com o pássaro
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False

# Classe que representa o chão do jogo
class Chao:
    VELOCIDADE = 5  # Velocidade de movimento do chão
    LARGURA = IMAGEM_CHAO.get_width()  # Largura da imagem do chão
    IMAGEM = IMAGEM_CHAO  # Imagem do chão

    def __init__(self, y):
        self.y = y  # Posição Y do chão
        self.x1 = 0  # Primeira posição X do chão
        self.x2 = self.LARGURA  # Segunda posição X do chão

    def mover(self):
        # Mover chão para a esquerda
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        # Repetir posições do chão
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        # Desenhar chão na tela
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

        # Desenhar máscara de colisão
        if mostrar_colisoes:
            chao_mask = pygame.mask.from_surface(self.IMAGEM)
            chao_surf = chao_mask.to_surface(unsetcolor=None, setcolor=(255, 0, 0, 100))
            tela.blit(chao_surf, (self.x1, self.y))
            tela.blit(chao_surf, (self.x2, self.y))

# Função para desenhar a tela do jogo
def desenhar_tela(tela, agentes, canos, chao, pontos, bug_rect):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))  # Desenhar fundo
    for agente in agentes:
        agente.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))  # Renderizar pontos
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))  # Desenhar pontos na tela

    chao.desenhar(tela)  # Desenhar chão

    # Desenhar botão para alternar velocidade
    botao_rect = desenhar_botao(tela, "Acelerar", (350, 70, 130, 50), (0, 255, 0), (255, 255, 255))

    # Desenhar área de bug
    if mostrar_bug:
        pygame.draw.rect(tela, (255, 0, 0), bug_rect, 2)

    pygame.display.update()  # Atualizar tela
    return botao_rect  # Retornar retângulo do botão para detecção de clique

# Função principal do jogo
def main():
    global velocidade_jogo, bug_ativo, mostrar_bug, mostrar_colisoes  # Declarar como global para usar as variáveis globais
    chao = Chao(730)  # Criar objeto Chao
    canos = [Cano(700)]  # Criar lista de objetos Cano
    agentes = [Agente() for _ in range(5)]  # Criar agentes
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))  # Definir modo de exibição da tela
    pontos = 0  # Inicializar pontos
    relogio = pygame.time.Clock()  # Inicializar relógio do Pygame
    bug_rect_x = 600  # Posição inicial do retângulo de bug, sincronizado com a posição inicial dos canos
    bug_rect = pygame.Rect(bug_rect_x, 100, 100, 100)  # Define o retângulo de bug

    rodando = True  # Variável para controlar o loop do jogo
    while rodando:
        relogio.tick(velocidade_jogo)  # Controlar a velocidade do jogo

        # Interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for agente in agentes:
                        agente.pular()
                if evento.key == pygame.K_b:  # Tecla 'b' para ativar/desativar o bug
                    bug_ativo = not bug_ativo
                    logging.info(f"Bug {'ativado' if bug_ativo else 'desativado'}")
                if evento.key == pygame.K_v:  # Tecla 'v' para mostrar/esconder o retângulo de bug
                    mostrar_bug = not mostrar_bug
                    logging.info(f"Visibilidade do retângulo de bug {'ativada' if mostrar_bug else 'desativada'}")
                if evento.key == pygame.K_c:  # Tecla 'c' para mostrar/esconder as colisões
                    mostrar_colisoes = not mostrar_colisoes
                    logging.info(f"Visibilidade das colisões {'ativada' if mostrar_colisoes else 'desativada'}")
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()
                if verificar_clique_botao(pos_mouse, botao_rect):
                    if velocidade_jogo == VEL_NORMAL:
                        velocidade_jogo = VEL_ACELERADA
                    else:
                        velocidade_jogo = VEL_NORMAL

        # Mover as coisas
        for agente in agentes:
            agente.explorar()  # Agente explora o ambiente
            agente.mover()  # Agente se move

        chao.mover()  # Chão se move

        adicionar_cano = False  # Flag para adicionar um novo cano
        remover_canos = []  # Lista de canos a serem removidos
        for cano in canos:
            for agente in agentes:
                if cano.colidir(agente):
                    logging.warning(f"Colisão detectada pelo agente na posição: ({agente.x}, {agente.y})")
                if not cano.passou and agente.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()  # Cano se move
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1  # Incrementar pontos
            canos.append(Cano(600))  # Adicionar novo cano
            # Adicionar retângulo de bug a cada 5 pontos
            if pontos % 5 == 0:
                bug_ativo = True

        for cano in remover_canos:
            canos.remove(cano)  # Remover canos

        # Atualizar a posição do retângulo de bug para que acompanhe a movimentação do cenário
        bug_rect.x -= Cano.VELOCIDADE
        if bug_rect.x + bug_rect.width < 0:
            bug_rect.x = 600  # Reset a posição do retângulo de bug quando ele sair da tela

        for agente in agentes:
            agente.detectar_bug(canos, chao, bug_rect)  # Detectar bug

        botao_rect = desenhar_tela(tela, agentes, canos, chao, pontos, bug_rect)  # Desenhar tela do jogo

if __name__ == '__main__':
    main()  # Chamar função principal do jogo
