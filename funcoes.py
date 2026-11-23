import os
import math
import random
import pygame

# =====================================================================
# 1) CONFIGURAÇÕES
# =====================================================================
LARGURA = 720
ALTURA = 820
FPS = 60                      # quadros por segundo

ESPACO = 12                   # espaço entre as cartas (pixels)
TEMPO_ERRO = 800              # tempo (ms) que um par errado fica aparecendo
TAM_NOME = 12                 # máximo de letras do nome
# O ranking fica na MESMA pasta deste arquivo .py (funciona mesmo rodando pelo VS Code,
# que às vezes executa o programa a partir de outra pasta)
PASTA_DO_JOGO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_RANKING = os.path.join(PASTA_DO_JOGO, "ranking.txt")

# Cores no formato (vermelho, verde, azul), cada um de 0 a 255
FUNDO = (15, 12, 40)
BRANCO = (255, 255, 255)
CINZA = (175, 180, 210)
AMARELO = (255, 215, 90)
VERDE = (90, 230, 140)
VERMELHO = (255, 100, 110)
AZUL_ESCURO = (30, 30, 70)
ROXO = (100, 60, 180)

# Os 3 níveis. Cada nível é um dicionário com suas configurações.
NIVEIS = {
    "Fácil":   {"colunas": 4, "linhas": 3, "tamanho": 140, "memorizar": 5000, "cor": (60, 170, 120)},
    "Médio":   {"colunas": 4, "linhas": 4, "tamanho": 130, "memorizar": 4000, "cor": (210, 140, 40)},
    "Difícil": {"colunas": 6, "linhas": 4, "tamanho": 96,  "memorizar": 3000, "cor": (200, 60, 90)},
}

# 12 figuras = 3 formas x 4 cores. Cada figura é uma tupla (forma, cor).
# O nível Difícil tem 24 cartas = 12 pares, por isso precisamos de 12 figuras.
FIGURAS = [
    ("circulo", (231, 76, 60)),    ("circulo", (52, 152, 219)),
    ("circulo", (46, 204, 113)),   ("circulo", (241, 196, 15)),
    ("quadrado", (231, 76, 60)),   ("quadrado", (52, 152, 219)),
    ("quadrado", (46, 204, 113)),  ("quadrado", (241, 196, 15)),
    ("triangulo", (231, 76, 60)),  ("triangulo", (52, 152, 219)),
    ("triangulo", (46, 204, 113)), ("triangulo", (241, 196, 15)),
]


# =====================================================================
# 2) INICIAR O PYGAME (janela, fontes)
# =====================================================================
pygame.mixer.pre_init(22050, 8, 1)     # som: 22050 pontos por segundo, 8 bits, mono
pygame.init()
janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória")
relogio = pygame.time.Clock()

FONTE_TITULO = pygame.font.SysFont("arial", 56, bold=True)
FONTE_GRANDE = pygame.font.SysFont("arial", 44, bold=True)
FONTE_NORMAL = pygame.font.SysFont("arial", 26, bold=True)
FONTE_PEQUENA = pygame.font.SysFont("arial", 20)

# Estrelas do fundo: sorteadas UMA vez só (senão elas ficariam piscando)
estrelas = []
for i in range(120):
    x = random.randint(0, LARGURA)
    y = random.randint(0, ALTURA)
    estrelas.append((x, y))


# =====================================================================
# 3) SONS (criados pelo próprio código, sem precisar de arquivo .wav)
# =====================================================================
def criar_som(notas):
    """Recebe uma lista de notas [(frequência, duração em segundos), ...]
    e devolve um som do pygame.

    Um som digital é uma lista de números. Com 8 bits, cada número vai de 0 a 255
    e o 128 é o silêncio. A onda fica pulando entre "128 + forca" (alto) e
    "128 - forca" (baixo). Quanto mais rápido ela pula (maior a frequência),
    mais agudo é o som. A forca diminui até 0 durante a nota, então cada nota
    começa forte e vai sumindo (parecido com uma caixinha de música)."""
    valores = []
    for frequencia, duracao in notas:
        total_pontos = int(22050 * duracao)          # quantos números essa nota tem
        meia_onda = 22050 // frequencia // 2         # quantos números seguidos em cima (ou embaixo)
        for i in range(total_pontos):
            forca = 32 * (total_pontos - i) // total_pontos    # vai de 32 até 0
            if (i // meia_onda) % 2 == 0:
                valores.append(128 + forca)
            else:
                valores.append(128 - forca)
    return pygame.mixer.Sound(buffer=bytes(valores))   # bytes() transforma a lista no formato de áudio


SOM_VIRAR = criar_som([(900, 0.04)])
SOM_CLIQUE = criar_som([(600, 0.05)])
SOM_ACERTO = criar_som([(660, 0.08), (990, 0.15)])
SOM_ERRO = criar_som([(220, 0.12), (160, 0.2)])
SOM_VITORIA = criar_som([(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.4)])

def criar_musica(acordes):
    """Recebe uma lista de acordes [(lista de frequências, duração), ...].
    Um acorde = várias notas tocando AO MESMO TEMPO.

    Aqui usamos a onda SENO (math.sin), que é bem mais suave que a onda
    quadrada dos efeitos: parece um piano elétrico de lobby de hotel.
    Para tocar várias notas juntas, é só SOMAR as ondas de cada nota."""
    valores = []
    for frequencias, duracao in acordes:
        total_pontos = int(22050 * duracao)
        for i in range(total_pontos):
            t = i / 22050                                  # tempo em segundos
            soma = 0
            for f in frequencias:
                soma = soma + math.sin(2 * math.pi * f * t)  # seno vai de -1 a 1
            media = soma / len(frequencias)                # continua entre -1 e 1
            forca = 50 * (total_pontos - i) / total_pontos # o acorde vai sumindo
            valores.append(128 + int(forca * media))
    return pygame.mixer.Sound(buffer=bytes(valores))


# Música de fundo estilo jazz de lobby: acordes com 7ª, cada um com 1 nota grave (baixo).
# Sequência: Dó7M - Lám7 - Rém7 - Sol7 - Fá7M - Mim7 - Rém7 - Sol7
MUSICA = criar_musica([
    ([131, 330, 392, 494], 2.4),     # Dó com 7ª maior
    ([110, 262, 330, 392], 2.4),     # Lá menor com 7ª
    ([147, 349, 440, 523], 2.4),     # Ré menor com 7ª
    ([98, 349, 494, 587], 2.4),      # Sol com 7ª
    ([87, 440, 523, 659], 2.4),      # Fá com 7ª maior
    ([165, 392, 494, 587], 2.4),     # Mi menor com 7ª
    ([147, 349, 440, 523], 2.4),     # Ré menor com 7ª
    ([98, 349, 494, 587], 2.4),      # Sol com 7ª
])
MUSICA.set_volume(0.3)         # volume de 0 a 1 (baixinho, só de fundo)


# =====================================================================
# 4) FUNÇÕES DE DESENHO
# =====================================================================
def escrever(texto, fonte, cor, x, y):
    """Escreve um texto com o CENTRO no ponto (x, y)."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()
    retangulo.center = (x, y)
    janela.blit(imagem, retangulo)


def desenhar_fundo():
    janela.fill(FUNDO)
    for estrela in estrelas:
        pygame.draw.circle(janela, BRANCO, estrela, 1)


def desenhar_botao(retangulo, texto, cor):
    """Botão colorido. Se o mouse estiver em cima, a borda fica amarela."""
    pygame.draw.rect(janela, cor, retangulo, border_radius=16)
    if retangulo.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(janela, AMARELO, retangulo, 4, border_radius=16)
    else:
        pygame.draw.rect(janela, BRANCO, retangulo, 2, border_radius=16)
    escrever(texto, FONTE_NORMAL, BRANCO, retangulo.centerx, retangulo.centery)


def criar_frente(forma, cor, tamanho):
    """Cria a imagem da FRENTE da carta: quadrado claro com uma forma no meio."""
    imagem = pygame.Surface((tamanho, tamanho))
    imagem.fill(FUNDO)
    pygame.draw.rect(imagem, (240, 240, 245), (0, 0, tamanho, tamanho), border_radius=14)

    meio = tamanho // 2
    r = tamanho // 3           # "raio" da forma
    if forma == "circulo":
        pygame.draw.circle(imagem, cor, (meio, meio), r)
    elif forma == "quadrado":
        pygame.draw.rect(imagem, cor, (meio - r, meio - r, 2 * r, 2 * r))
    elif forma == "triangulo":
        pontas = [(meio, meio - r), (meio - r, meio + r), (meio + r, meio + r)]
        pygame.draw.polygon(imagem, cor, pontas)
    return imagem


def criar_verso(tamanho):
    """Cria a imagem do VERSO da carta: roxo com uma bolinha amarela."""
    imagem = pygame.Surface((tamanho, tamanho))
    imagem.fill(FUNDO)
    pygame.draw.rect(imagem, ROXO, (0, 0, tamanho, tamanho), border_radius=14)
    pygame.draw.circle(imagem, AMARELO, (tamanho // 2, tamanho // 2), tamanho // 8)
    return imagem


# =====================================================================
# 5) RANKING (salvo no arquivo ranking.txt)
# =====================================================================
# Cada linha do arquivo:  nivel;nome;tentativas      Exemplo:  Fácil;Rony;7
# Na memória, cada jogador é uma lista [tentativas, nome].
# As tentativas vêm PRIMEIRO de propósito: assim o .sort() ordena por elas.

def carregar_ranking():
    ranking = {"Fácil": [], "Médio": [], "Difícil": []}

    if not os.path.exists(ARQUIVO_RANKING):      # 1ª vez jogando: arquivo não existe
        return ranking

    with open(ARQUIVO_RANKING, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(";")    # "Fácil;Rony;7" -> ["Fácil", "Rony", "7"]
            if len(partes) == 3 and partes[0] in ranking:
                nivel = partes[0]
                nome = partes[1]
                tentativas = int(partes[2])
                ranking[nivel].append([tentativas, nome])
    return ranking


def salvar_ranking(ranking):
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as arquivo:
        for nivel in ranking:
            for jogador in ranking[nivel]:
                tentativas = jogador[0]
                nome = jogador[1]
                arquivo.write(nivel + ";" + nome + ";" + str(tentativas) + "\n")


def adicionar_no_ranking(ranking, nivel, nome, tentativas):
    """Coloca o jogador no ranking e devolve a colocação dele (1 a 5),
    ou 0 se ele não entrou no top 5."""
    novo = [tentativas, nome]
    lista = ranking[nivel]
    lista.append(novo)
    lista.sort()                    # menos tentativas fica na frente
    ranking[nivel] = lista[:5]      # guarda só os 5 primeiros
    salvar_ranking(ranking)

    if novo in ranking[nivel]:
        return ranking[nivel].index(novo) + 1     # +1 porque a lista começa no 0
    return 0


# =====================================================================
# 6) SPRITES
# =====================================================================
# Todo Sprite precisa de self.image (o desenho) e self.rect (a posição).
# Colocando os sprites num Group, dá para desenhar todos com grupo.draw(janela).

class Carta(pygame.sprite.Sprite):
    def __init__(self, numero, img_frente, img_verso, x, y):
        super().__init__()
        self.numero = numero            # as 2 cartas de um par têm o mesmo número
        self.img_frente = img_frente
        self.img_verso = img_verso
        self.image = img_frente         # começa virada para cima (para memorizar)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.virada = True              # True = mostrando a figura
        self.encontrada = False         # True = o par dela já foi achado

    def virar_para_cima(self):
        self.virada = True
        self.image = self.img_frente

    def virar_para_baixo(self):
        self.virada = False
        self.image = self.img_verso


class Particula(pygame.sprite.Sprite):
    """Quadradinho colorido que pula, cai e some (quando acerta um par)."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((7, 7))
        self.image.fill(random.choice([AMARELO, VERDE, BRANCO]))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = random.randint(-6, 6)
        self.vel_y = random.randint(-12, -3)     # negativo = sobe
        self.vida = 45                            # quantos quadros ela dura

    def update(self):                             # chamado a cada quadro pelo grupo
        self.vel_y = self.vel_y + 0.5             # gravidade
        self.rect.x = self.rect.x + self.vel_x
        self.rect.y = self.rect.y + self.vel_y
        self.vida = self.vida - 1
        if self.vida <= 0:
            self.kill()                           # tira a partícula do grupo


# =====================================================================
# 7) TELA 1: MENU
# =====================================================================
def tela_menu(nome, ranking):
    """Devolve 3 coisas: a próxima tela ("jogo" ou "sair"), o nível e o nome."""

    # Um botão (retângulo) para cada nível, um embaixo do outro
    botoes = {}
    y = 310
    for nivel in NIVEIS:
        botoes[nivel] = pygame.Rect(110, y, 500, 85)
        y = y + 115
    botao_ranking = pygame.Rect(230, 670, 260, 60)
    caixa_nome = pygame.Rect(190, 220, 340, 50)
    mostrar_ranking = False

    while True:
        relogio.tick(FPS)

        # ---------- EVENTOS ----------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair", None, nome

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "sair", None, nome
                elif evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]                          # apaga a última letra
                elif evento.unicode.isalnum() and len(nome) < TAM_NOME:
                    nome = nome + evento.unicode              # só aceita letras e números

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if mostrar_ranking:                           # se o ranking está aberto, clique fecha
                    mostrar_ranking = False
                elif botao_ranking.collidepoint(evento.pos):
                    SOM_CLIQUE.play()
                    mostrar_ranking = True
                else:
                    for nivel in botoes:
                        if botoes[nivel].collidepoint(evento.pos):
                            SOM_CLIQUE.play()
                            return "jogo", nivel, nome

        # ---------- DESENHO ----------
        desenhar_fundo()

        # 6 cartinhas de enfeite no topo
        for i in range(6):
            forma, cor = FIGURAS[i * 2]
            janela.blit(criar_frente(forma, cor, 70), (105 + i * 85, 30))

        escrever("Jogo da Memória", FONTE_TITULO, BRANCO, LARGURA // 2, 155)

        # Caixa do nome
        pygame.draw.rect(janela, AZUL_ESCURO, caixa_nome, border_radius=12)
        pygame.draw.rect(janela, CINZA, caixa_nome, 2, border_radius=12)
        if nome == "":
            escrever("Digite seu nome...", FONTE_PEQUENA, CINZA, caixa_nome.centerx, caixa_nome.centery)
        else:
            escrever(nome, FONTE_NORMAL, BRANCO, caixa_nome.centerx, caixa_nome.centery)

        # Botões dos níveis
        for nivel in botoes:
            config = NIVEIS[nivel]
            qtd_cartas = config["colunas"] * config["linhas"]
            desenhar_botao(botoes[nivel], nivel + "  -  " + str(qtd_cartas) + " cartas", config["cor"])

        desenhar_botao(botao_ranking, "Ranking", (90, 70, 170))
        escrever("ESC = sair", FONTE_PEQUENA, CINZA, LARGURA // 2, ALTURA - 30)

        if mostrar_ranking:
            desenhar_ranking(ranking)

        pygame.display.update()


def desenhar_ranking(ranking):
    """Painel por cima do menu com o top 5 de cada nível (3 colunas)."""
    pygame.draw.rect(janela, AZUL_ESCURO, (30, 120, 660, 560), border_radius=20)
    pygame.draw.rect(janela, AMARELO, (30, 120, 660, 560), 3, border_radius=20)
    escrever("Ranking - Top 5", FONTE_GRANDE, AMARELO, LARGURA // 2, 175)

    x = 145                                   # centro da 1ª coluna
    for nivel in ranking:
        escrever(nivel, FONTE_NORMAL, NIVEIS[nivel]["cor"], x, 250)

        if len(ranking[nivel]) == 0:
            escrever("ninguém ainda", FONTE_PEQUENA, CINZA, x, 300)

        y = 300
        colocacao = 1
        for jogador in ranking[nivel]:
            tentativas = jogador[0]
            nome = jogador[1]
            escrever(str(colocacao) + ". " + nome, FONTE_PEQUENA, BRANCO, x, y)
            escrever(str(tentativas) + " tentativas", FONTE_PEQUENA, CINZA, x, y + 24)
            y = y + 65
            colocacao = colocacao + 1

        x = x + 215                           # próxima coluna

    escrever("Clique para fechar", FONTE_PEQUENA, CINZA, LARGURA // 2, 650)


# =====================================================================
# 8) TELA 2: JOGO
# =====================================================================
def tela_jogo(nivel, nome, ranking):
    """Devolve a próxima tela: "menu", "jogo" (jogar de novo) ou "sair"."""
    config = NIVEIS[nivel]
    colunas = config["colunas"]
    linhas = config["linhas"]
    tamanho = config["tamanho"]
    qtd_pares = colunas * linhas // 2

    # --- Sorteia as figuras da partida ---
    numeros = list(range(len(FIGURAS)))      # [0, 1, 2, ..., 11]
    random.shuffle(numeros)                  # embaralha
    escolhidos = numeros[:qtd_pares]         # pega só as que precisa
    baralho = escolhidos + escolhidos        # duplica: cada figura vira um par
    random.shuffle(baralho)                  # embaralha de novo

    # --- Cria as cartas em grade, centralizada na tela ---
    largura_grade = colunas * tamanho + (colunas - 1) * ESPACO
    x_inicial = (LARGURA - largura_grade) // 2
    y_inicial = 190
    img_verso = criar_verso(tamanho)         # o verso é igual para todas

    cartas = pygame.sprite.Group()
    particulas = pygame.sprite.Group()

    indice = 0
    for linha in range(linhas):
        for coluna in range(colunas):
            x = x_inicial + coluna * (tamanho + ESPACO)
            y = y_inicial + linha * (tamanho + ESPACO)
            numero = baralho[indice]
            forma, cor = FIGURAS[numero]
            img_frente = criar_frente(forma, cor, tamanho)
            cartas.add(Carta(numero, img_frente, img_verso, x, y))
            indice = indice + 1

    # --- Variáveis da partida ---
    # O "estado" diz em que momento a partida está:
    #   "memorizar" -> "jogando" <-> "errou"  ...  "vitoria"
    estado = "memorizar"
    inicio = pygame.time.get_ticks()         # get_ticks() = milissegundos desde que o jogo abriu
    inicio_jogo = 0                          # quando as cartas viraram para baixo
    momento_erro = 0
    tempo_final = 0
    selecionadas = []                        # cartas viradas nesta jogada (0, 1 ou 2)
    tentativas = 0
    pares = 0
    posicao = 0                              # colocação no ranking

    while True:
        relogio.tick(FPS)
        agora = pygame.time.get_ticks()

        # ---------- EVENTOS ----------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"
                if evento.key == pygame.K_r:
                    return "jogo"                     # recomeça o mesmo nível

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado == "vitoria":
                    return "menu"

                if estado == "jogando":
                    # Procura a carta clicada (só vale se ela estiver virada para baixo)
                    for carta in cartas:
                        if carta.rect.collidepoint(evento.pos) and not carta.virada:
                            carta.virar_para_cima()
                            SOM_VIRAR.play()
                            selecionadas.append(carta)

                    # Virou 2 cartas: confere se é par
                    if len(selecionadas) == 2:
                        tentativas = tentativas + 1
                        carta1 = selecionadas[0]
                        carta2 = selecionadas[1]

                        if carta1.numero == carta2.numero:          # ACERTOU
                            carta1.encontrada = True
                            carta2.encontrada = True
                            pares = pares + 1
                            selecionadas = []
                            SOM_ACERTO.play()
                            for i in range(20):
                                particulas.add(Particula(carta1.rect.centerx, carta1.rect.centery))
                                particulas.add(Particula(carta2.rect.centerx, carta2.rect.centery))

                            if pares == qtd_pares:                  # achou todos: VENCEU
                                estado = "vitoria"
                                tempo_final = (agora - inicio_jogo) // 1000
                                posicao = adicionar_no_ranking(ranking, nivel, nome, tentativas)
                                SOM_VITORIA.play()
                        else:                                       # ERROU
                            estado = "errou"
                            momento_erro = agora
                            SOM_ERRO.play()

        # ---------- COISAS QUE DEPENDEM DO TEMPO ----------
        # Acabou o tempo de memorizar: vira todas para baixo
        if estado == "memorizar" and agora - inicio >= config["memorizar"]:
            for carta in cartas:
                carta.virar_para_baixo()
            estado = "jogando"
            inicio_jogo = agora

        # Já mostrou o par errado por tempo suficiente: desvira as duas
        if estado == "errou" and agora - momento_erro >= TEMPO_ERRO:
            for carta in selecionadas:
                carta.virar_para_baixo()
            selecionadas = []
            estado = "jogando"

        particulas.update()          # chama o update() de cada partícula

        # ---------- DESENHO ----------
        desenhar_fundo()
        escrever("Nível " + nivel + "  -  " + nome, FONTE_NORMAL, config["cor"], LARGURA // 2, 40)

        # Cronômetro
        if estado == "memorizar":
            segundos = 0
        elif estado == "vitoria":
            segundos = tempo_final
        else:
            segundos = (agora - inicio_jogo) // 1000

        # Barra de informações
        pygame.draw.rect(janela, AZUL_ESCURO, (20, 75, LARGURA - 40, 50), border_radius=12)
        escrever("Tentativas: " + str(tentativas), FONTE_PEQUENA, BRANCO, 130, 100)
        escrever("Pares: " + str(pares) + "/" + str(qtd_pares), FONTE_PEQUENA, BRANCO, LARGURA // 2, 100)
        escrever("Tempo: " + str(segundos) + "s", FONTE_PEQUENA, BRANCO, LARGURA - 130, 100)

        # Mensagem de cada estado
        if estado == "memorizar":
            falta = (config["memorizar"] - (agora - inicio)) // 1000 + 1
            escrever("Memorize! As cartas viram em " + str(falta) + "s", FONTE_NORMAL, AMARELO, LARGURA // 2, 155)
        elif estado == "errou":
            escrever("Não é par!", FONTE_NORMAL, VERMELHO, LARGURA // 2, 155)
        elif estado == "jogando":
            escrever("Encontre os pares!", FONTE_PEQUENA, CINZA, LARGURA // 2, 155)

        cartas.draw(janela)          # desenha todas as cartas do grupo

        # Borda verde nas cartas encontradas; amarela na carta embaixo do mouse
        for carta in cartas:
            if carta.encontrada:
                pygame.draw.rect(janela, VERDE, carta.rect, 4, border_radius=14)
            elif estado == "jogando" and not carta.virada and carta.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(janela, AMARELO, carta.rect, 4, border_radius=14)

        particulas.draw(janela)

        escrever("R = reiniciar   |   ESC = menu", FONTE_PEQUENA, CINZA, LARGURA // 2, ALTURA - 25)

        if estado == "vitoria":
            desenhar_vitoria(tentativas, tempo_final, posicao)

        pygame.display.update()


def desenhar_vitoria(tentativas, tempo, posicao):
    """Escurece a tela e mostra o resultado."""
    escuro = pygame.Surface((LARGURA, ALTURA))
    escuro.fill((0, 0, 0))
    escuro.set_alpha(170)                     # transparência: 0 = invisível, 255 = opaco
    janela.blit(escuro, (0, 0))

    pygame.draw.rect(janela, AZUL_ESCURO, (110, 230, 500, 360), border_radius=20)
    pygame.draw.rect(janela, AMARELO, (110, 230, 500, 360), 3, border_radius=20)

    escrever("Parabéns!", FONTE_GRANDE, AMARELO, LARGURA // 2, 290)
    escrever(str(tentativas) + " tentativas em " + str(tempo) + " segundos", FONTE_NORMAL, BRANCO, LARGURA // 2, 370)

    if posicao == 1:
        escrever("NOVO RECORDE! 1º lugar", FONTE_NORMAL, VERDE, LARGURA // 2, 430)
    elif posicao > 1:
        escrever("Você ficou em " + str(posicao) + "º no ranking!", FONTE_NORMAL, VERDE, LARGURA // 2, 430)
    else:
        escrever("Não entrou no top 5. Tente de novo!", FONTE_NORMAL, CINZA, LARGURA // 2, 430)

    escrever("R = jogar de novo   |   clique = menu", FONTE_PEQUENA, CINZA, LARGURA // 2, 530)


# =====================================================================
# 9) PROGRAMA PRINCIPAL
# =====================================================================
MUSICA.play(-1)                  # -1 = repete para sempre
ranking = carregar_ranking()

tela = "menu"
nivel = None
nome = ""

# Cada função de tela roda até o jogador sair dela e devolve qual é a próxima tela
while tela != "sair":
    if tela == "menu":
        tela, nivel, nome = tela_menu(nome, ranking)
    elif tela == "jogo":
        if nome == "":
            nome = "Anônimo"
        tela = tela_jogo(nivel, nome, ranking)

pygame.quit()
