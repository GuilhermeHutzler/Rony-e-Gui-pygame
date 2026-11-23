

import os
import random
from array import array
import pygame

# ------------------------- CONFIGURAÇÕES -------------------------
LARGURA = 720
ALTURA = 820
FPS = 60
ESPACO = 12                 # espaço entre as cartas (em pixels)
TEMPO_ERRO = 800            # quanto tempo (ms) um par errado fica aparecendo
TAM_RANKING = 5             # quantas pessoas aparecem no ranking de cada nível
TAM_NOME = 12               # máximo de letras do nome
ARQUIVO_RANKING = "ranking.txt"

# Cores (R, G, B)
FUNDO = (15, 12, 40)
BRANCO = (255, 255, 255)
CINZA = (175, 180, 210)
AMARELO = (255, 215, 90)
VERDE = (90, 230, 140)
VERMELHO = (255, 100, 110)
AZUL_ESCURO = (30, 30, 70)
COR_FRENTE = (240, 240, 245)
COR_VERSO = (100, 60, 180)

# Os 3 níveis: quantidade de cartas, tamanho da carta e tempo para memorizar (ms)
NIVEIS = {
    "Fácil":   {"colunas": 4, "linhas": 3, "tamanho": 140, "memorizar": 5000, "cor": (60, 170, 120)},
    "Médio":   {"colunas": 4, "linhas": 4, "tamanho": 130, "memorizar": 4000, "cor": (210, 140, 40)},
    "Difícil": {"colunas": 6, "linhas": 4, "tamanho": 96,  "memorizar": 3000, "cor": (200, 60, 90)},
}

# 12 figuras. Cada figura = (forma, cor). As formas se repetem com cores diferentes.
FIGURAS = [
    ("circulo", (231, 76, 60)),     ("circulo", (52, 152, 219)),
    ("quadrado", (46, 204, 113)),   ("quadrado", (155, 89, 182)),
    ("triangulo", (241, 196, 15)),  ("triangulo", (230, 126, 34)),
    ("losango", (26, 188, 156)),    ("losango", (232, 90, 160)),
    ("cruz", (52, 73, 94)),         ("cruz", (192, 57, 43)),
    ("anel", (41, 128, 185)),       ("anel", (39, 174, 96)),
]

# Cores das partículas que aparecem quando acerta um par
CORES_PARTICULAS = [AMARELO, VERDE, (130, 210, 255), (240, 120, 255), BRANCO]

# Estrelas do fundo: lista de posições (x, y) sorteadas uma vez só
ESTRELAS = []
for i in range(120):
    ESTRELAS.append((random.randint(0, LARGURA), random.randint(0, ALTURA)))


# ------------------------- SONS -------------------------
def criar_som(notas):
    """Cria um som a partir de uma lista de notas: [(frequência, duração), ...].
    O som é uma onda que fica alternando entre "alto" (+3000) e "baixo" (-3000).
    Quanto mais vezes por segundo ela alterna (frequência), mais agudo é o som."""
    taxa = 22050                                # pontos do som por segundo
    pontos = array("h")                         # lista de números inteiros (formato de áudio)
    for frequencia, duracao in notas:
        meia_onda = taxa // frequencia // 2     # quantos pontos fica em cima (ou embaixo)
        for i in range(int(taxa * duracao)):
            if (i // meia_onda) % 2 == 0:
                pontos.append(3000)
            else:
                pontos.append(-3000)
    return pygame.mixer.Sound(buffer=pontos)


def carregar_sons():
    sons = {}
    sons["virar"] = criar_som([(900, 0.04)])
    sons["acerto"] = criar_som([(660, 0.08), (990, 0.15)])
    sons["erro"] = criar_som([(220, 0.12), (160, 0.2)])
    sons["vitoria"] = criar_som([(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.4)])
    sons["clique"] = criar_som([(600, 0.05)])

    # Música de fundo: uma melodia curta (cerca de 8 segundos) que vai repetir
    # Notas usadas: Dó=262, Ré=294, Mi=330, Fá=349, Sol=392, Lá=440
    melodia = [
        (262, 0.25), (330, 0.25), (392, 0.25), (330, 0.25),
        (294, 0.25), (349, 0.25), (440, 0.25), (349, 0.25),
        (330, 0.25), (392, 0.25), (262, 0.25), (392, 0.25),
        (294, 0.25), (392, 0.25), (349, 0.25), (294, 0.25),
        (262, 0.25), (330, 0.25), (392, 0.25), (440, 0.25),
        (392, 0.25), (349, 0.25), (330, 0.25), (294, 0.25),
        (262, 0.5), (392, 0.5), (262, 1.0),
    ]
    sons["musica"] = criar_som(melodia)
    sons["musica"].set_volume(0.25)       # mais baixa que os efeitos (0 a 1)
    return sons


# ------------------------- FUNÇÕES DE DESENHO -------------------------
def escrever(janela, texto, fonte, cor, x, y):
    """Escreve um texto com o CENTRO no ponto (x, y)."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()
    retangulo.center = (x, y)
    janela.blit(imagem, retangulo)


def desenhar_fundo(janela):
    janela.fill(FUNDO)
    for estrela in ESTRELAS:
        pygame.draw.circle(janela, BRANCO, estrela, 1)


def desenhar_botao(janela, fonte, retangulo, texto, cor):
    """Desenha um botão. Se o mouse estiver em cima, a borda fica amarela."""
    pygame.draw.rect(janela, cor, retangulo, border_radius=16)
    if retangulo.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(janela, AMARELO, retangulo, 4, border_radius=16)
    else:
        pygame.draw.rect(janela, BRANCO, retangulo, 2, border_radius=16)
    escrever(janela, texto, fonte, BRANCO, retangulo.centerx, retangulo.centery)


def desenhar_forma(superficie, forma, cor, tamanho):
    """Desenha a forma no centro de uma superfície quadrada de lado `tamanho`."""
    c = tamanho // 2            # centro
    r = tamanho // 3            # "raio" da forma
    if forma == "circulo":
        pygame.draw.circle(superficie, cor, (c, c), r)
    elif forma == "quadrado":
        pygame.draw.rect(superficie, cor, (c - r, c - r, 2 * r, 2 * r))
    elif forma == "triangulo":
        pygame.draw.polygon(superficie, cor, [(c, c - r), (c - r, c + r), (c + r, c + r)])
    elif forma == "losango":
        pygame.draw.polygon(superficie, cor, [(c, c - r), (c + r, c), (c, c + r), (c - r, c)])
    elif forma == "cruz":
        pygame.draw.rect(superficie, cor, (c - r // 3, c - r, 2 * r // 3, 2 * r))
        pygame.draw.rect(superficie, cor, (c - r, c - r // 3, 2 * r, 2 * r // 3))
    elif forma == "anel":
        pygame.draw.circle(superficie, cor, (c, c), r, r // 3)


def criar_frente(forma, cor, tamanho):
    """Cria a imagem da frente da carta: fundo claro + forma colorida."""
    imagem = pygame.Surface((tamanho, tamanho))
    imagem.fill(FUNDO)
    pygame.draw.rect(imagem, COR_FRENTE, (0, 0, tamanho, tamanho), border_radius=14)
    desenhar_forma(imagem, forma, cor, tamanho)
    return imagem


def criar_verso(tamanho):
    """Cria a imagem do verso da carta: roxo com um círculo no meio."""
    imagem = pygame.Surface((tamanho, tamanho))
    imagem.fill(FUNDO)
    pygame.draw.rect(imagem, COR_VERSO, (0, 0, tamanho, tamanho), border_radius=14)
    pygame.draw.rect(imagem, (180, 150, 255), (0, 0, tamanho, tamanho), 3, border_radius=14)
    pygame.draw.circle(imagem, AMARELO, (tamanho // 2, tamanho // 2), tamanho // 8)
    return imagem


# ------------------------- RANKING (arquivo de texto) -------------------------
# Cada linha do arquivo ranking.txt tem o formato:   nivel;nome;tentativas
# Exemplo:   Fácil;Rony;7

def carregar_ranking():
    """Lê o arquivo e monta um dicionário: nível -> lista de jogadores."""
    ranking = {"Fácil": [], "Médio": [], "Difícil": []}

    if not os.path.exists(ARQUIVO_RANKING):     # 1ª vez: o arquivo ainda não existe
        return ranking

    with open(ARQUIVO_RANKING, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(";")
            if len(partes) == 3 and partes[0] in ranking:
                nivel = partes[0]
                jogador = {"nome": partes[1], "tentativas": int(partes[2])}
                ranking[nivel].append(jogador)
    return ranking


def salvar_ranking(ranking):
    """Escreve o ranking inteiro no arquivo (uma linha por jogador)."""
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as arquivo:
        for nivel in ranking:
            for jogador in ranking[nivel]:
                arquivo.write(nivel + ";" + jogador["nome"] + ";" + str(jogador["tentativas"]) + "\n")


def adicionar_no_ranking(ranking, nivel, nome, tentativas):
    """Coloca o jogador na posição certa (menos tentativas = melhor).
    Devolve a colocação (1 a 5) ou 0 se ele não entrou no top 5."""
    lista = ranking[nivel]

    # anda pela lista até achar alguém com MAIS tentativas que o jogador
    posicao = 0
    while posicao < len(lista) and lista[posicao]["tentativas"] <= tentativas:
        posicao += 1

    lista.insert(posicao, {"nome": nome, "tentativas": tentativas})
    ranking[nivel] = lista[:TAM_RANKING]          # guarda só os 5 primeiros
    salvar_ranking(ranking)

    if posicao < TAM_RANKING:
        return posicao + 1      # +1 porque a lista começa no 0
    return 0


# ------------------------- SPRITES -------------------------
class Carta(pygame.sprite.Sprite):
    """Uma carta. Todo Sprite precisa de self.image (o desenho) e self.rect (a posição)."""

    def __init__(self, numero, img_frente, img_verso, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.numero = numero            # número da figura (cartas do mesmo par têm o mesmo número)
        self.img_frente = img_frente
        self.img_verso = img_verso
        self.image = img_frente         # começa virada para cima (fase de memorizar)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.virada = True              # True = mostrando a figura
        self.encontrada = False         # True = o par já foi achado

    def virar_para_cima(self):
        self.virada = True
        self.image = self.img_frente

    def virar_para_baixo(self):
        self.virada = False
        self.image = self.img_verso


class Particula(pygame.sprite.Sprite):
    """Quadradinho colorido que pula, cai e some (aparece quando acerta um par)."""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((7, 7))
        self.image.fill(random.choice(CORES_PARTICULAS))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocidade_x = random.randint(-6, 6)
        self.velocidade_y = random.randint(-12, -3)     # negativo = sobe
        self.vida = 45                                   # quantos quadros ela dura

    def update(self):
        self.velocidade_y = self.velocidade_y + 0.5     # gravidade puxa para baixo
        self.rect.x = self.rect.x + self.velocidade_x
        self.rect.y = self.rect.y + self.velocidade_y
        self.vida = self.vida - 1
        if self.vida <= 0:
            self.kill()                                  # remove a partícula do grupo


# ------------------------- TELA 1: MENU -------------------------
def tela_menu(janela, fontes, sons, ranking, nome):
    """Devolve 3 coisas: a próxima tela, o nível escolhido e o nome digitado."""
    relogio = pygame.time.Clock()

    # Um retângulo (botão) para cada nível
    botoes = {}
    y = 310
    for nivel in NIVEIS:
        botoes[nivel] = pygame.Rect(LARGURA // 2 - 250, y, 500, 85)
        y = y + 115
    botao_ranking = pygame.Rect(LARGURA // 2 - 130, 670, 260, 60)
    caixa_nome = pygame.Rect(LARGURA // 2 - 170, 220, 340, 50)

    mostrar_ranking = False

    while True:
        relogio.tick(FPS)

        # ----- EVENTOS -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair", None, nome

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "sair", None, nome
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]                     # apaga a última letra
                elif evento.unicode.isalnum() and len(nome) < TAM_NOME:
                    nome = nome + evento.unicode         # só letras e números

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if mostrar_ranking:                      # clique fecha o ranking
                    mostrar_ranking = False
                elif botao_ranking.collidepoint(evento.pos):
                    sons["clique"].play()
                    mostrar_ranking = True
                else:
                    for nivel in botoes:
                        if botoes[nivel].collidepoint(evento.pos):
                            sons["clique"].play()
                            return "jogo", nivel, nome

        # ----- DESENHO -----
        desenhar_fundo(janela)

        # 6 cartinhas no topo, só de enfeite
        x = 105
        for i in range(6):
            forma, cor = FIGURAS[i * 2]
            janela.blit(criar_frente(forma, cor, 70), (x, 30))
            x = x + 85

        escrever(janela, "Jogo da Memória", fontes["titulo"], BRANCO, LARGURA // 2, 155)

        # Caixa do nome
        pygame.draw.rect(janela, AZUL_ESCURO, caixa_nome, border_radius=12)
        pygame.draw.rect(janela, CINZA, caixa_nome, 2, border_radius=12)
        if nome == "":
            escrever(janela, "Digite seu nome...", fontes["pequena"], CINZA, caixa_nome.centerx, caixa_nome.centery)
        else:
            escrever(janela, nome, fontes["normal"], BRANCO, caixa_nome.centerx, caixa_nome.centery)

        # Botões dos níveis
        for nivel in botoes:
            config = NIVEIS[nivel]
            qtd_cartas = config["colunas"] * config["linhas"]
            texto = nivel + "  -  " + str(qtd_cartas) + " cartas"
            desenhar_botao(janela, fontes["normal"], botoes[nivel], texto, config["cor"])

        desenhar_botao(janela, fontes["normal"], botao_ranking, "Ranking", (90, 70, 170))
        escrever(janela, "ESC = sair", fontes["pequena"], CINZA, LARGURA // 2, ALTURA - 30)

        if mostrar_ranking:
            desenhar_ranking(janela, fontes, ranking)

        pygame.display.update()


def desenhar_ranking(janela, fontes, ranking):
    """Janela por cima do menu com o top 5 de cada nível (3 colunas)."""
    painel = pygame.Rect(30, 120, LARGURA - 60, 560)
    pygame.draw.rect(janela, AZUL_ESCURO, painel, border_radius=20)
    pygame.draw.rect(janela, AMARELO, painel, 3, border_radius=20)
    escrever(janela, "Ranking - Top 5", fontes["grande"], AMARELO, LARGURA // 2, 175)

    x = 145                                         # centro da 1ª coluna
    for nivel in ranking:
        escrever(janela, nivel, fontes["normal"], NIVEIS[nivel]["cor"], x, 250)

        if len(ranking[nivel]) == 0:
            escrever(janela, "ninguém ainda", fontes["pequena"], CINZA, x, 300)

        y = 300
        colocacao = 1
        for jogador in ranking[nivel]:
            escrever(janela, str(colocacao) + ". " + jogador["nome"], fontes["pequena"], BRANCO, x, y)
            escrever(janela, str(jogador["tentativas"]) + " tentativas", fontes["pequena"], CINZA, x, y + 24)
            y = y + 65
            colocacao = colocacao + 1

        x = x + 215                                 # vai para a próxima coluna

    escrever(janela, "Clique para fechar", fontes["pequena"], CINZA, LARGURA // 2, 650)


# ------------------------- TELA 2: JOGO -------------------------
def tela_jogo(janela, fontes, sons, nivel, nome, ranking):
    """Devolve a próxima tela: "menu", "jogo" (jogar de novo) ou "sair"."""
    relogio = pygame.time.Clock()
    config = NIVEIS[nivel]
    colunas = config["colunas"]
    linhas = config["linhas"]
    tamanho = config["tamanho"]
    qtd_pares = colunas * linhas // 2

    # 1) Sorteia quais figuras entram na partida e duplica (cada uma vira um par)
    numeros = list(range(len(FIGURAS)))     # [0, 1, 2, ..., 11]
    random.shuffle(numeros)
    numeros = numeros[:qtd_pares]
    baralho = numeros + numeros
    random.shuffle(baralho)

    # 2) Cria as cartas na grade, centralizada na tela
    largura_grade = colunas * tamanho + (colunas - 1) * ESPACO
    x_inicial = (LARGURA - largura_grade) // 2
    y_inicial = 190
    img_verso = criar_verso(tamanho)

    cartas = pygame.sprite.Group()          # grupo com todas as cartas
    particulas = pygame.sprite.Group()      # grupo com as partículas

    for i in range(len(baralho)):
        coluna = i % colunas                # resto da divisão -> coluna
        linha = i // colunas                # divisão inteira  -> linha
        x = x_inicial + coluna * (tamanho + ESPACO)
        y = y_inicial + linha * (tamanho + ESPACO)
        forma, cor = FIGURAS[baralho[i]]
        img_frente = criar_frente(forma, cor, tamanho)
        cartas.add(Carta(baralho[i], img_frente, img_verso, x, y))

    # 3) Variáveis da partida
    estado = "memorizar"      # "memorizar" -> "jogando" <-> "errou" -> "vitoria"
    inicio = pygame.time.get_ticks()        # quando a partida começou
    inicio_jogo = 0                         # quando as cartas viraram (começa o cronômetro)
    momento_erro = 0
    tempo_final = 0
    selecionadas = []
    tentativas = 0
    pares = 0
    posicao = 0

    while True:
        relogio.tick(FPS)
        agora = pygame.time.get_ticks()

        # ----- EVENTOS -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"
                if evento.key == pygame.K_r:
                    return "jogo"                   # recomeça o mesmo nível

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado == "vitoria":
                    return "menu"                   # clique na vitória volta ao menu

                if estado == "jogando":
                    for carta in cartas:
                        if carta.rect.collidepoint(evento.pos) and not carta.virada:
                            carta.virar_para_cima()
                            sons["virar"].play()
                            selecionadas.append(carta)
                            break

                    if len(selecionadas) == 2:
                        tentativas = tentativas + 1
                        carta1 = selecionadas[0]
                        carta2 = selecionadas[1]

                        if carta1.numero == carta2.numero:        # ACERTOU
                            carta1.encontrada = True
                            carta2.encontrada = True
                            pares = pares + 1
                            sons["acerto"].play()
                            for k in range(20):                   # explosão de partículas
                                particulas.add(Particula(carta1.rect.centerx, carta1.rect.centery))
                                particulas.add(Particula(carta2.rect.centerx, carta2.rect.centery))
                            selecionadas = []

                            if pares == qtd_pares:                # achou todos: VITÓRIA
                                estado = "vitoria"
                                tempo_final = (agora - inicio_jogo) // 1000
                                posicao = adicionar_no_ranking(ranking, nivel, nome, tentativas)
                                sons["vitoria"].play()
                        else:                                     # ERROU
                            estado = "errou"
                            momento_erro = agora
                            sons["erro"].play()

        # ----- LÓGICA QUE DEPENDE DO TEMPO -----
        if estado == "memorizar" and agora - inicio >= config["memorizar"]:
            for carta in cartas:
                carta.virar_para_baixo()
            estado = "jogando"
            inicio_jogo = agora

        if estado == "errou" and agora - momento_erro >= TEMPO_ERRO:
            for carta in selecionadas:
                carta.virar_para_baixo()
            selecionadas = []
            estado = "jogando"

        particulas.update()            # chama o update() de cada partícula

        # ----- DESENHO -----
        desenhar_fundo(janela)

        escrever(janela, "Nível " + nivel + "  -  " + nome, fontes["normal"], config["cor"], LARGURA // 2, 40)

        # Cronômetro
        if estado == "memorizar":
            segundos = 0
        elif estado == "vitoria":
            segundos = tempo_final
        else:
            segundos = (agora - inicio_jogo) // 1000

        pygame.draw.rect(janela, AZUL_ESCURO, (20, 75, LARGURA - 40, 50), border_radius=12)
        escrever(janela, "Tentativas: " + str(tentativas), fontes["pequena"], BRANCO, 130, 100)
        escrever(janela, "Pares: " + str(pares) + "/" + str(qtd_pares), fontes["pequena"], BRANCO, LARGURA // 2, 100)
        escrever(janela, "Tempo: " + str(segundos) + "s", fontes["pequena"], BRANCO, LARGURA - 130, 100)

        # Mensagem do momento
        if estado == "memorizar":
            falta = (config["memorizar"] - (agora - inicio)) // 1000 + 1
            escrever(janela, "Memorize! As cartas viram em " + str(falta) + "s", fontes["normal"], AMARELO, LARGURA // 2, 155)
        elif estado == "errou":
            escrever(janela, "Não é par!", fontes["normal"], VERMELHO, LARGURA // 2, 155)
        elif estado == "jogando":
            escrever(janela, "Encontre os pares!", fontes["pequena"], CINZA, LARGURA // 2, 155)

        cartas.draw(janela)            # desenha todas as cartas do grupo

        # Borda verde nas cartas encontradas e amarela na carta sob o mouse
        for carta in cartas:
            if carta.encontrada:
                pygame.draw.rect(janela, VERDE, carta.rect, 4, border_radius=14)
            elif estado == "jogando" and not carta.virada and carta.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(janela, AMARELO, carta.rect, 4, border_radius=14)

        particulas.draw(janela)        # desenha todas as partículas do grupo

        escrever(janela, "R = reiniciar   |   ESC = menu", fontes["pequena"], CINZA, LARGURA // 2, ALTURA - 25)

        if estado == "vitoria":
            desenhar_vitoria(janela, fontes, tentativas, tempo_final, posicao)

        pygame.display.update()


def desenhar_vitoria(janela, fontes, tentativas, tempo, posicao):
    """Escurece a tela e mostra o resultado da partida."""
    escuro = pygame.Surface((LARGURA, ALTURA))
    escuro.set_alpha(170)                           # 0 = invisível, 255 = opaco
    escuro.fill((0, 0, 0))
    janela.blit(escuro, (0, 0))

    painel = pygame.Rect(LARGURA // 2 - 250, 230, 500, 360)
    pygame.draw.rect(janela, AZUL_ESCURO, painel, border_radius=20)
    pygame.draw.rect(janela, AMARELO, painel, 3, border_radius=20)

    escrever(janela, "Parabéns!", fontes["grande"], AMARELO, LARGURA // 2, 290)
    escrever(janela, str(tentativas) + " tentativas em " + str(tempo) + " segundos",
             fontes["normal"], BRANCO, LARGURA // 2, 370)

    if posicao == 1:
        escrever(janela, "NOVO RECORDE! 1º lugar", fontes["normal"], VERDE, LARGURA // 2, 430)
    elif posicao > 1:
        escrever(janela, "Você ficou em " + str(posicao) + "º no ranking!", fontes["normal"], VERDE, LARGURA // 2, 430)
    else:
        escrever(janela, "Não entrou no top 5. Tente de novo!", fontes["normal"], CINZA, LARGURA // 2, 430)

    escrever(janela, "R = jogar de novo   |   clique = menu", fontes["pequena"], CINZA, LARGURA // 2, 530)


# ------------------------- PROGRAMA PRINCIPAL -------------------------
pygame.mixer.pre_init(22050, -16, 1)      # som: 22050 pontos/s, 16 bits, 1 canal (mono)
pygame.init()
janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória")

fontes = {
    "titulo": pygame.font.SysFont("arial", 56, bold=True),
    "grande": pygame.font.SysFont("arial", 44, bold=True),
    "normal": pygame.font.SysFont("arial", 26, bold=True),
    "pequena": pygame.font.SysFont("arial", 20),
}
sons = carregar_sons()
sons["musica"].play(-1)         # -1 = repetir para sempre (música de fundo)
ranking = carregar_ranking()

tela = "menu"
nivel = None
nome = ""

# Cada função de tela devolve qual é a próxima tela
while tela != "sair":
    if tela == "menu":
        tela, nivel, nome = tela_menu(janela, fontes, sons, ranking, nome)
    elif tela == "jogo":
        if nome == "":
            nome = "Anônimo"
        tela = tela_jogo(janela, fontes, sons, nivel, nome, ranking)

pygame.quit())
