import math
import random
import sys

import pygame

# ----------------------------- Configurações -----------------------------
LARGURA, ALTURA = 640, 760
FPS = 60

COLUNAS, LINHAS = 4, 4          # 16 cartas = 8 pares
TAM_CARTA = 120
ESPACO = 15
TOPO = 150

TEMPO_MEMORIZACAO = 4000        # ms que as cartas ficam à mostra no início
TEMPO_ERRO = 900                # ms que um par errado fica visível

FUNDO = (24, 28, 44)
COR_VERSO = (60, 90, 160)
COR_VERSO_BORDA = (110, 140, 210)
COR_FRENTE = (240, 240, 245)
COR_ACERTO = (80, 200, 120)
BRANCO = (255, 255, 255)
CINZA = (170, 175, 190)

# Cada par tem um símbolo (forma + cor)
SIMBOLOS = [
    ("circulo", (231, 76, 60)),
    ("quadrado", (52, 152, 219)),
    ("triangulo", (46, 204, 113)),
    ("losango", (241, 196, 15)),
    ("estrela", (155, 89, 182)),
    ("cruz", (230, 126, 34)),
    ("hexagono", (26, 188, 156)),
    ("anel", (232, 90, 160)),
]


# ----------------------------- Desenho dos símbolos -----------------------------
def desenhar_simbolo(tela, forma, cor, rect):
    cx, cy = rect.center
    r = TAM_CARTA // 2 - 24

    if forma == "circulo":
        pygame.draw.circle(tela, cor, (cx, cy), r)
    elif forma == "quadrado":
        pygame.draw.rect(tela, cor, (cx - r, cy - r, 2 * r, 2 * r), border_radius=6)
    elif forma == "triangulo":
        pygame.draw.polygon(tela, cor, [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)])
    elif forma == "losango":
        pygame.draw.polygon(tela, cor, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)])
    elif forma == "estrela":
        pontos = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            raio = r + 4 if i % 2 == 0 else (r + 4) * 0.45
            pontos.append((cx + raio * math.cos(ang), cy + raio * math.sin(ang)))
        pygame.draw.polygon(tela, cor, pontos)
    elif forma == "cruz":
        espessura = r * 0.8
        pygame.draw.rect(tela, cor, (cx - espessura / 2, cy - r, espessura, 2 * r))
        pygame.draw.rect(tela, cor, (cx - r, cy - espessura / 2, 2 * r, espessura))
    elif forma == "hexagono":
        pontos = [
            (cx + r * math.cos(math.pi / 3 * i), cy + r * math.sin(math.pi / 3 * i))
            for i in range(6)
        ]
        pygame.draw.polygon(tela, cor, pontos)
    elif forma == "anel":
        pygame.draw.circle(tela, cor, (cx, cy), r, 10)


# ----------------------------- Carta -----------------------------
class Carta:
    def _init_(self, id_simbolo, x, y):
        self.id = id_simbolo
        self.rect = pygame.Rect(x, y, TAM_CARTA, TAM_CARTA)
        self.virada = False       # mostrando a frente?
        self.encontrada = False   # par já descoberto?

    def desenhar(self, tela):
        if self.virada or self.encontrada:
            borda = COR_ACERTO if self.encontrada else CINZA
            pygame.draw.rect(tela, COR_FRENTE, self.rect, border_radius=14)
            pygame.draw.rect(tela, borda, self.rect, 4, border_radius=14)
            forma, cor = SIMBOLOS[self.id]
            desenhar_simbolo(tela, forma, cor, self.rect)
        else:
            pygame.draw.rect(tela, COR_VERSO, self.rect, border_radius=14)
            pygame.draw.rect(tela, COR_VERSO_BORDA, self.rect, 4, border_radius=14)
            # pequeno desenho no verso
            pygame.draw.circle(tela, COR_VERSO_BORDA, self.rect.center, 14, 3)


# ----------------------------- Jogo -----------------------------
class Jogo:
    def _init_(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Jogo da Memória")
        self.clock = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("arial", 40, bold=True)
        self.fonte = pygame.font.SysFont("arial", 26)
        self.fonte_pequena = pygame.font.SysFont("arial", 20)
        self.fonte_grande = pygame.font.SysFont("arial", 64, bold=True)

        self.melhor = None  # menor número de tentativas na sessão
        self.novo_jogo()

    def novo_jogo(self):
        ids = list(range(len(SIMBOLOS))) * 2
        random.shuffle(ids)

        largura_grade = COLUNAS * TAM_CARTA + (COLUNAS - 1) * ESPACO
        x0 = (LARGURA - largura_grade) // 2

        self.cartas = []
        for i, id_simbolo in enumerate(ids):
            col, lin = i % COLUNAS, i // COLUNAS
            x = x0 + col * (TAM_CARTA + ESPACO)
            y = TOPO + lin * (TAM_CARTA + ESPACO)
            carta = Carta(id_simbolo, x, y)
            carta.virada = True  # todas à mostra no início
            self.cartas.append(carta)

        self.estado = "memorizar"   # memorizar -> jogando -> verificando -> vitoria
        self.inicio_estado = pygame.time.get_ticks()
        self.selecionadas = []
        self.tentativas = 0
        self.pares = 0

    # ---------- Lógica ----------
    def clicar(self, pos):
        if self.estado != "jogando":
            return
        for carta in self.cartas:
            if carta.rect.collidepoint(pos) and not carta.virada and not carta.encontrada:
                carta.virada = True
                self.selecionadas.append(carta)
                break

        if len(self.selecionadas) == 2:
            self.tentativas += 1
            a, b = self.selecionadas
            if a.id == b.id:
                a.encontrada = b.encontrada = True
                self.pares += 1
                self.selecionadas = []
                if self.pares == len(SIMBOLOS):
                    self.estado = "vitoria"
                    if self.melhor is None or self.tentativas < self.melhor:
                        self.melhor = self.tentativas
            else:
                self.estado = "verificando"
                self.inicio_estado = pygame.time.get_ticks()

    def atualizar(self):
        agora = pygame.time.get_ticks()

        if self.estado == "memorizar":
            if agora - self.inicio_estado >= TEMPO_MEMORIZACAO:
                for carta in self.cartas:
                    carta.virada = False
                self.estado = "jogando"

        elif self.estado == "verificando":
            if agora - self.inicio_estado >= TEMPO_ERRO:
                for carta in self.selecionadas:
                    carta.virada = False
                self.selecionadas = []
                self.estado = "jogando"

    # ---------- Desenho ----------
    def texto(self, msg, fonte, cor, centro):
        surf = fonte.render(msg, True, cor)
        self.tela.blit(surf, surf.get_rect(center=centro))

    def desenhar(self):
        self.tela.fill(FUNDO)

        self.texto("Jogo da Memória", self.fonte_titulo, BRANCO, (LARGURA // 2, 40))
        self.texto(f"Tentativas: {self.tentativas}", self.fonte, BRANCO, (150, 95))
        self.texto(f"Pares: {self.pares}/{len(SIMBOLOS)}", self.fonte, BRANCO, (LARGURA // 2 + 20, 95))
        melhor = "-" if self.melhor is None else str(self.melhor)
        self.texto(f"Melhor: {melhor}", self.fonte, CINZA, (LARGURA - 100, 95))

        # Mensagem de status
        if self.estado == "memorizar":
            restante = max(0, TEMPO_MEMORIZACAO - (pygame.time.get_ticks() - self.inicio_estado))
            segundos = math.ceil(restante / 1000)
            self.texto(f"Memorize as cartas! Elas viram em {segundos}s", self.fonte, (255, 215, 90),
                       (LARGURA // 2, 130))
        elif self.estado in ("jogando", "verificando"):
            self.texto("Encontre os pares com o menor número de tentativas",
                       self.fonte_pequena, CINZA, (LARGURA // 2, 130))

        for carta in self.cartas:
            carta.desenhar(self.tela)

        self.texto("R = reiniciar   |   ESC = sair", self.fonte_pequena, CINZA,
                   (LARGURA // 2, ALTURA - 25))

        if self.estado == "vitoria":
            self.tela_vitoria()

        pygame.display.flip()

    def tela_vitoria(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.tela.blit(overlay, (0, 0))

        minimo = len(SIMBOLOS)
        if self.tentativas <= minimo + 2:
            nota = "Memória incrível!"
        elif self.tentativas <= minimo * 2:
            nota = "Muito bom!"
        else:
            nota = "Continue treinando!"

        self.texto("Parabéns!", self.fonte_grande, (255, 215, 90), (LARGURA // 2, 280))
        self.texto(f"Você terminou em {self.tentativas} tentativas", self.fonte, BRANCO,
                   (LARGURA // 2, 360))
        self.texto(nota, self.fonte, COR_ACERTO, (LARGURA // 2, 410))
        self.texto("Pressione R para jogar de novo", self.fonte, CINZA, (LARGURA // 2, 480))

    # ---------- Loop principal ----------
    def rodar(self):
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif evento.key == pygame.K_r:
                        self.novo_jogo()
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.clicar(evento.pos)

            self.atualizar()
            self.desenhar()
            self.clock.tick(FPS)


if _name_ == "_main_":
    Jogo().rodar()