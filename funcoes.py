

import math
import random
import sys

import pygame

# =============================== CONFIGURAÇÕES ===============================
LARGURA, ALTURA = 720, 820
FPS = 60

ESPACO = 12               # espaço (px) entre as cartas
AREA_TOPO = 175           # onde a grade de cartas começa (y)
AREA_BASE = 55            # margem livre embaixo da grade
VELOCIDADE_GIRO = 6       # velocidade da animação de virar (maior = mais rápido)

# Cores (R, G, B)
COR_FRENTE = (22, 26, 58)        # fundo da frente da carta (azul-noite)
COR_FRENTE_BORDA = (120, 130, 200)
COR_VERSO_1 = (120, 70, 200)     # verso: degradê do roxo...
COR_VERSO_2 = (50, 30, 120)      # ...para o azul escuro
COR_VERSO_BORDA = (190, 160, 255)
COR_ACERTO = (90, 230, 140)
COR_ERRO = (255, 100, 110)
COR_PAINEL = (30, 30, 70)
AMARELO = (255, 215, 90)
BRANCO = (255, 255, 255)
CINZA = (175, 180, 210)

# Os 3 níveis. colunas x linhas = quantidade de cartas.
NIVEIS = [
    {"nome": "Fácil",   "patente": "Cadete",     "colunas": 4, "linhas": 3,
     "memorizar": 5000, "erro": 1000, "cor": (60, 170, 120)},
    {"nome": "Médio",   "patente": "Piloto",     "colunas": 4, "linhas": 4,
     "memorizar": 4000, "erro": 800,  "cor": (210, 140, 40)},
    {"nome": "Difícil", "patente": "Comandante", "colunas": 6, "linhas": 4,
     "memorizar": 3000, "erro": 600,  "cor": (200, 60, 90)},
]

# 12 figuras: (nome, cor principal). A cor também é usada nas partículas.
FIGURAS = [
    ("foguete",    (240, 80, 80)),
    ("saturno",    (235, 180, 90)),
    ("terra",      (70, 150, 240)),
    ("lua",        (240, 230, 170)),
    ("sol",        (255, 190, 50)),
    ("ovni",       (150, 230, 255)),
    ("alien",      (120, 230, 120)),
    ("astronauta", (230, 230, 245)),
    ("cometa",     (130, 210, 255)),
    ("satelite",   (225, 185, 80)),
    ("galaxia",    (210, 120, 255)),
    ("brilho",     (255, 240, 120)),
]


# =============================== FUNÇÕES AUXILIARES ===============================
def texto(tela, msg, fonte, cor, centro):
    """Escreve um texto centralizado no ponto `centro`."""
    surf = fonte.render(msg, True, cor)
    tela.blit(surf, surf.get_rect(center=centro))


def degrade(tamanho, cor_cima, cor_baixo):
    """Cria uma imagem com degradê vertical, desenhando uma linha de cada cor."""
    larg, alt = tamanho
    img = pygame.Surface(tamanho)
    for y in range(alt):
        t = y / max(1, alt - 1)                                   # 0 em cima, 1 embaixo
        cor = [int(a + (b - a) * t) for a, b in zip(cor_cima, cor_baixo)]
        pygame.draw.line(img, cor, (0, y), (larg, y))
    return img


def poligono_transparente(sup, cor_rgba, pontos):
    """Desenha um polígono semitransparente (ex.: rastro do cometa).
    O pygame só mistura transparência ao colar (blit) uma imagem,
    então desenhamos numa imagem temporária e colamos."""
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    x0, y0 = int(min(xs)), int(min(ys))
    temp = pygame.Surface((int(max(xs)) - x0 + 1, int(max(ys)) - y0 + 1), pygame.SRCALPHA)
    pygame.draw.polygon(temp, cor_rgba, [(x - x0, y - y0) for x, y in pontos])
    sup.blit(temp, (x0, y0))


def pontos_estrela(cx, cy, raio_ext, raio_int, pontas=5):
    """Vértices de uma estrela: alterna entre o raio externo e o interno."""
    pontos = []
    for i in range(pontas * 2):
        ang = -math.pi / 2 + i * math.pi / pontas
        raio = raio_ext if i % 2 == 0 else raio_int
        pontos.append((cx + raio * math.cos(ang), cy + raio * math.sin(ang)))
    return pontos


# =============================== AS 12 FIGURAS ===============================
def desenhar_figura(sup, nome, rect):
    """Desenha a figura `nome` dentro de `rect`.
    Tudo é calculado a partir de `r` (proporcional ao tamanho da carta),
    por isso a mesma figura funciona em cartas grandes e pequenas."""
    cx, cy = rect.center
    r = rect.width * 0.32
    e = max(2, int(r / 8))   # espessura de linhas

    if nome == "foguete":
        # chama (laranja por fora, amarela por dentro)
        pygame.draw.polygon(sup, (255, 140, 40), [(cx - 0.25 * r, cy + 0.5 * r), (cx + 0.25 * r, cy + 0.5 * r), (cx, cy + 1.05 * r)])
        pygame.draw.polygon(sup, (255, 230, 90), [(cx - 0.12 * r, cy + 0.5 * r), (cx + 0.12 * r, cy + 0.5 * r), (cx, cy + 0.8 * r)])
        # aletas
        pygame.draw.polygon(sup, (220, 60, 70), [(cx - 0.35 * r, cy + 0.05 * r), (cx - 0.75 * r, cy + 0.6 * r), (cx - 0.35 * r, cy + 0.5 * r)])
        pygame.draw.polygon(sup, (220, 60, 70), [(cx + 0.35 * r, cy + 0.05 * r), (cx + 0.75 * r, cy + 0.6 * r), (cx + 0.35 * r, cy + 0.5 * r)])
        # corpo e bico
        pygame.draw.rect(sup, (235, 235, 245), (cx - 0.35 * r, cy - 0.45 * r, 0.7 * r, 0.95 * r))
        pygame.draw.polygon(sup, (240, 80, 80), [(cx, cy - 1.05 * r), (cx + 0.35 * r, cy - 0.45 * r), (cx - 0.35 * r, cy - 0.45 * r)])
        # janelinha
        pygame.draw.circle(sup, (90, 180, 255), (cx, cy - 0.1 * r), 0.19 * r)
        pygame.draw.circle(sup, (120, 130, 160), (cx, cy - 0.1 * r), 0.19 * r, max(1, e // 2))

    elif nome == "saturno":
        anel = pygame.Rect(0, 0, 2.3 * r, 0.75 * r)
        anel.center = (cx, cy)
        pygame.draw.ellipse(sup, (245, 225, 170), anel, e)                    # anel (parte de trás)
        pygame.draw.circle(sup, (235, 170, 80), (cx, cy), 0.62 * r)           # planeta
        pygame.draw.line(sup, (200, 130, 60), (cx - 0.55 * r, cy - 0.2 * r), (cx + 0.55 * r, cy - 0.2 * r), e)
        pygame.draw.arc(sup, (245, 225, 170), anel, math.pi, 2 * math.pi, e)  # anel (parte da frente)

    elif nome == "terra":
        pygame.draw.circle(sup, (60, 130, 230), (cx, cy), 0.85 * r)          # oceano
        pygame.draw.ellipse(sup, (80, 195, 100), (cx - 0.6 * r, cy - 0.55 * r, 0.55 * r, 0.45 * r))
        pygame.draw.ellipse(sup, (80, 195, 100), (cx + 0.0 * r, cy - 0.2 * r, 0.5 * r, 0.65 * r))
        pygame.draw.ellipse(sup, (80, 195, 100), (cx - 0.5 * r, cy + 0.2 * r, 0.35 * r, 0.3 * r))
        pygame.draw.circle(sup, (160, 220, 255), (cx, cy), 0.85 * r, max(1, e // 2))  # atmosfera

    elif nome == "lua":
        pygame.draw.circle(sup, (240, 230, 170), (cx, cy), 0.8 * r)
        pygame.draw.circle(sup, (200, 190, 140), (cx - 0.35 * r, cy + 0.25 * r), 0.14 * r)   # crateras
        pygame.draw.circle(sup, (200, 190, 140), (cx - 0.15 * r, cy - 0.4 * r), 0.1 * r)
        # um círculo da cor do fundo "morde" a lua e forma a meia-lua
        pygame.draw.circle(sup, COR_FRENTE, (cx + 0.4 * r, cy - 0.2 * r), 0.68 * r)

    elif nome == "sol":
        for i in range(12):                                                  # raios
            ang = i * math.pi / 6
            p1 = (cx + math.cos(ang) * 0.65 * r, cy + math.sin(ang) * 0.65 * r)
            p2 = (cx + math.cos(ang) * 1.0 * r, cy + math.sin(ang) * 1.0 * r)
            pygame.draw.line(sup, (255, 150, 40), p1, p2, e)
        pygame.draw.circle(sup, (255, 190, 50), (cx, cy), 0.58 * r)
        pygame.draw.circle(sup, (255, 230, 120), (cx, cy), 0.38 * r)

    elif nome == "ovni":
        # feixe de luz semitransparente
        poligono_transparente(sup, (255, 255, 150, 90),
                              [(cx - 0.3 * r, cy + 0.2 * r), (cx + 0.3 * r, cy + 0.2 * r),
                               (cx + 0.65 * r, cy + 1.0 * r), (cx - 0.65 * r, cy + 1.0 * r)])
        pygame.draw.circle(sup, (150, 230, 255), (cx, cy - 0.15 * r), 0.42 * r)        # cúpula
        pygame.draw.ellipse(sup, (175, 185, 205), (cx - r, cy - 0.25 * r, 2 * r, 0.6 * r))  # disco
        for i in range(5):                                                   # luzinhas
            x = cx - 0.6 * r + i * 0.3 * r
            pygame.draw.circle(sup, (255, 220, 60), (x, cy + 0.05 * r), max(2, 0.08 * r))

    elif nome == "alien":
        # antenas
        pygame.draw.line(sup, (120, 230, 120), (cx - 0.25 * r, cy - 0.7 * r), (cx - 0.5 * r, cy - 1.0 * r), e)
        pygame.draw.line(sup, (120, 230, 120), (cx + 0.25 * r, cy - 0.7 * r), (cx + 0.5 * r, cy - 1.0 * r), e)
        pygame.draw.circle(sup, (255, 120, 200), (cx - 0.5 * r, cy - 1.0 * r), 0.1 * r)
        pygame.draw.circle(sup, (255, 120, 200), (cx + 0.5 * r, cy - 1.0 * r), 0.1 * r)
        # cabeça
        pygame.draw.ellipse(sup, (120, 230, 120), (cx - 0.65 * r, cy - 0.8 * r, 1.3 * r, 1.65 * r))
        # olhos grandes com brilho
        for lado in (-1, 1):
            olho = pygame.Rect(0, 0, 0.42 * r, 0.55 * r)
            olho.center = (cx + lado * 0.27 * r, cy - 0.1 * r)
            pygame.draw.ellipse(sup, (20, 20, 30), olho)
            pygame.draw.circle(sup, BRANCO, (olho.centerx - 0.06 * r, olho.centery - 0.1 * r), max(1, 0.07 * r))
        # sorriso
        boca = pygame.Rect(0, 0, 0.4 * r, 0.25 * r)
        boca.center = (cx, cy + 0.45 * r)
        pygame.draw.arc(sup, (30, 80, 30), boca, math.pi, 2 * math.pi, max(1, e // 2))

    elif nome == "astronauta":
        pygame.draw.rect(sup, (170, 175, 195), (cx - 0.95 * r, cy - 0.2 * r, 0.3 * r, 0.4 * r), border_radius=3)
        pygame.draw.rect(sup, (170, 175, 195), (cx + 0.65 * r, cy - 0.2 * r, 0.3 * r, 0.4 * r), border_radius=3)
        pygame.draw.circle(sup, (235, 235, 245), (cx, cy), 0.8 * r)                    # capacete
        visor = pygame.Rect(0, 0, 1.1 * r, 0.75 * r)
        visor.center = (cx, cy)
        pygame.draw.ellipse(sup, (40, 60, 130), visor)                                  # visor
        pygame.draw.ellipse(sup, (120, 170, 255), (visor.x + 0.15 * r, visor.y + 0.1 * r, 0.35 * r, 0.18 * r))  # reflexo

    elif nome == "cometa":
        cabeca = (cx + 0.45 * r, cy - 0.45 * r)
        poligono_transparente(sup, (120, 200, 255, 110),     # cauda larga
                              [(cabeca[0] - 0.3 * r, cabeca[1] - 0.25 * r), (cx - 1.0 * r, cy + 1.0 * r),
                               (cabeca[0] + 0.25 * r, cabeca[1] + 0.3 * r)])
        poligono_transparente(sup, (200, 240, 255, 170),     # cauda fina
                              [(cabeca[0] - 0.15 * r, cabeca[1] - 0.1 * r), (cx - 0.7 * r, cy + 0.7 * r),
                               (cabeca[0] + 0.1 * r, cabeca[1] + 0.15 * r)])
        pygame.draw.circle(sup, (210, 245, 255), cabeca, 0.33 * r)

    elif nome == "satelite":
        for lado in (-1, 1):                                                # painéis solares
            painel = pygame.Rect(0, 0, 0.6 * r, 0.5 * r)
            painel.center = (cx + lado * 0.72 * r, cy)
            pygame.draw.line(sup, (180, 180, 190), (cx, cy), painel.center, e)
            pygame.draw.rect(sup, (50, 110, 220), painel)
            pygame.draw.line(sup, (140, 190, 255), painel.midtop, painel.midbottom, 1)
            pygame.draw.line(sup, (140, 190, 255), painel.midleft, painel.midright, 1)
        pygame.draw.rect(sup, (225, 185, 80), (cx - 0.25 * r, cy - 0.35 * r, 0.5 * r, 0.7 * r), border_radius=3)
        pygame.draw.line(sup, (200, 200, 210), (cx, cy - 0.35 * r), (cx, cy - 0.75 * r), max(1, e // 2))
        pygame.draw.circle(sup, (230, 230, 240), (cx, cy - 0.8 * r), 0.15 * r)

    elif nome == "galaxia":
        # dois braços em espiral: o ângulo e o raio crescem juntos
        for braco in range(2):
            for i in range(30):
                t = i / 30
                ang = braco * math.pi + t * 3 * math.pi
                raio = t * 0.95 * r
                x = cx + math.cos(ang) * raio
                y = cy + math.sin(ang) * raio * 0.7          # achatada = vista inclinada
                cor = (int(255 - 90 * t), int(150 - 60 * t), 255)
                pygame.draw.circle(sup, cor, (x, y), max(1, 0.12 * r * (1 - t) + 1))
        pygame.draw.circle(sup, (255, 230, 255), (cx, cy), 0.16 * r)

    elif nome == "brilho":
        pygame.draw.polygon(sup, (255, 240, 120), pontos_estrela(cx, cy, 0.95 * r, 0.25 * r, pontas=4))
        pygame.draw.polygon(sup, (255, 255, 220), pontos_estrela(cx, cy, 0.45 * r, 0.12 * r, pontas=4))
        pygame.draw.polygon(sup, (255, 240, 120), pontos_estrela(cx + 0.65 * r, cy - 0.6 * r, 0.25 * r, 0.07 * r, pontas=4))
        pygame.draw.polygon(sup, (255, 240, 120), pontos_estrela(cx - 0.6 * r, cy + 0.65 * r, 0.2 * r, 0.06 * r, pontas=4))


# =============================== CÉU ESTRELADO (fundo animado) ===============================
class CeuEstrelado:
    """Fundo das duas telas: degradê + nebulosas + estrelas que piscam e descem devagar."""

    def __init__(self, qtd=140):
        self.imagem = degrade((LARGURA, ALTURA), (8, 6, 28), (35, 18, 60))
        # nebulosas: círculos grandes bem transparentes
        for cor, pos, raio in [((120, 50, 200, 35), (150, 250), 220),
                               ((40, 120, 220, 30), (600, 600), 260),
                               ((220, 60, 150, 25), (500, 150), 160)]:
            nuvem = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            for k in range(6, 0, -1):     # vários círculos = borda suave
                pygame.draw.circle(nuvem, cor, (raio, raio), raio * k // 6)
            self.imagem.blit(nuvem, (pos[0] - raio, pos[1] - raio))

        # cada estrela = [x, y, velocidade, fase do piscar]
        self.estrelas = [[random.uniform(0, LARGURA), random.uniform(0, ALTURA),
                          random.uniform(4, 25), random.uniform(0, 6.28)] for _ in range(qtd)]
        self.tempo = 0

    def atualizar(self, dt):
        self.tempo += dt
        for estrela in self.estrelas:
            estrela[1] += estrela[2] * dt          # desce devagar
            if estrela[1] > ALTURA:                # saiu embaixo -> volta em cima
                estrela[1] = 0
                estrela[0] = random.uniform(0, LARGURA)

    def desenhar(self, tela):
        tela.blit(self.imagem, (0, 0))
        for x, y, vel, fase in self.estrelas:
            brilho = 150 + 105 * math.sin(self.tempo * 3 + fase)    # pisca com seno
            tamanho = 2 if vel > 18 else 1                          # as rápidas parecem mais perto
            pygame.draw.circle(tela, (brilho, brilho, 255), (x, y), tamanho)


# =============================== PARTÍCULAS ===============================
class Particula:
    """Pontinho que voa, cai com gravidade e some. Usado nos acertos e no confete."""

    def __init__(self, x, y, cor, vx=None, vy=None):
        if vx is None:                         # explosão: direção aleatória
            ang = random.uniform(0, 2 * math.pi)
            vel = random.uniform(80, 320)
            vx, vy = math.cos(ang) * vel, math.sin(ang) * vel - 80
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.cor = cor
        self.vida = self.vida_total = random.uniform(0.7, 1.4)
        self.tamanho = random.uniform(2, 5)

    def atualizar(self, dt):
        self.vy += 350 * dt          # gravidade
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vida -= dt

    def desenhar(self, tela):
        raio = self.tamanho * self.vida / self.vida_total   # encolhe até sumir
        if raio > 0.5:
            pygame.draw.circle(tela, self.cor, (self.x, self.y), raio)


# =============================== BOTÃO ===============================
class Botao:
    """Retângulo clicável. Brilha e cresce quando o mouse passa por cima.
    É usado nas duas telas (o menu.py importa esta classe)."""

    def __init__(self, rect, texto, cor, subtexto=""):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.subtexto = subtexto
        self.cor = cor

    def desenhar(self, tela, fonte, fonte_sub, mouse):
        rect, cor = self.rect, self.cor
        hover = self.rect.collidepoint(mouse)
        if hover:
            cor = tuple(min(255, c + 35) for c in cor)
            rect = self.rect.inflate(10, 8)
            # brilho em volta
            pygame.draw.rect(tela, cor, rect.inflate(10, 10), 2, border_radius=22)

        pygame.draw.rect(tela, cor, rect, border_radius=18)
        # faixa clara em cima = efeito de "vidro"
        brilho = pygame.Surface((rect.width - 16, rect.height // 2 - 4), pygame.SRCALPHA)
        pygame.draw.rect(brilho, (255, 255, 255, 40), brilho.get_rect(), border_radius=14)
        tela.blit(brilho, (rect.x + 8, rect.y + 5))
        pygame.draw.rect(tela, BRANCO, rect, 2, border_radius=18)

        if self.subtexto:
            texto(tela, self.texto, fonte, BRANCO, (rect.centerx, rect.centery - 14))
            texto(tela, self.subtexto, fonte_sub, BRANCO, (rect.centerx, rect.centery + 20))
        else:
            texto(tela, self.texto, fonte, BRANCO, rect.center)

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


# =============================== CARTA ===============================
class Carta:
    """Uma carta do jogo.

    Estados lógicos:  virada (frente para cima?) e encontrada (par já achado?).
    Animação: `progresso` vai de 0 (verso) até 1 (frente). A largura desenhada é
    |cos(progresso * pi)|: a carta afina até sumir e volta mostrando o outro lado.
    """

    def __init__(self, id_figura, x, y, tamanho):
        self.id = id_figura
        self.rect = pygame.Rect(x, y, tamanho, tamanho)
        self.virada = False
        self.encontrada = False
        self.progresso = 0.0

        # As imagens são desenhadas UMA vez e depois só redimensionadas.
        self.img_frente = self.criar_frente(COR_FRENTE_BORDA)
        self.img_acerto = self.criar_frente(COR_ACERTO)
        self.img_verso = self.criar_verso()

    def criar_frente(self, cor_borda):
        img = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        r = img.get_rect()
        pygame.draw.rect(img, COR_FRENTE, r, border_radius=14)
        for _ in range(6):   # estrelinhas no fundo da carta
            pygame.draw.circle(img, (90, 100, 160), (random.randint(8, r.w - 8), random.randint(8, r.h - 8)), 1)
        nome, _cor = FIGURAS[self.id]
        desenhar_figura(img, nome, r)
        pygame.draw.rect(img, cor_borda, r, 4, border_radius=14)
        return img

    def criar_verso(self):
        img = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        r = img.get_rect()
        # degradê recortado com cantos arredondados (máscara)
        img.blit(degrade(r.size, COR_VERSO_1, COR_VERSO_2), (0, 0))
        mascara = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), r, border_radius=14)
        img.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # órbitas e planetinha no centro
        orbita = r.inflate(-r.w * 0.3, -r.h * 0.55)
        pygame.draw.ellipse(img, (170, 140, 240), orbita, 2)
        pygame.draw.circle(img, AMARELO, r.center, r.w * 0.12)
        pygame.draw.circle(img, (255, 255, 255), (orbita.right - 2, r.centery), r.w * 0.04)
        pygame.draw.rect(img, COR_VERSO_BORDA, r, 3, border_radius=14)
        return img

    def atualizar(self, dt):
        """Move o `progresso` em direção ao alvo (1 = mostrar frente, 0 = verso)."""
        alvo = 1.0 if (self.virada or self.encontrada) else 0.0
        passo = VELOCIDADE_GIRO * dt
        if self.progresso < alvo:
            self.progresso = min(alvo, self.progresso + passo)
        elif self.progresso > alvo:
            self.progresso = max(alvo, self.progresso - passo)

    def desenhar(self, tela, dx=0, dy=0, destacar=False):
        """dx/dy deslocam a carta (usado para tremer no erro e levantar no hover)."""
        if self.progresso >= 0.5:
            img = self.img_acerto if self.encontrada else self.img_frente
        else:
            img = self.img_verso

        escala = abs(math.cos(self.progresso * math.pi))   # 1 -> 0 -> 1
        largura = max(1, int(self.rect.width * escala))
        img = pygame.transform.smoothscale(img, (largura, self.rect.height))
        centro = (self.rect.centerx + dx, self.rect.centery + dy)

        if destacar:   # sombra embaixo quando a carta "levanta"
            sombra = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(sombra, (0, 0, 0, 90), sombra.get_rect(), border_radius=14)
            tela.blit(sombra, sombra.get_rect(center=(self.rect.centerx + 4, self.rect.centery + 6)))

        tela.blit(img, img.get_rect(center=centro))

        if destacar:
            pygame.draw.rect(tela, AMARELO, img.get_rect(center=centro), 3, border_radius=14)


# =============================== TELA 2: JOGO ===============================
class TelaJogo:
    def __init__(self, tela, nivel, recordes, ceu):
        self.tela = tela
        self.nivel = nivel          # dicionário do nível escolhido no menu
        self.recordes = recordes    # MESMO dicionário do menu (compartilhado)
        self.ceu = ceu              # MESMO fundo animado do menu

        self.fonte_grande = pygame.font.SysFont("arial", 54, bold=True)
        self.fonte = pygame.font.SysFont("arial", 26, bold=True)
        self.fonte_media = pygame.font.SysFont("arial", 22)
        self.fonte_pequena = pygame.font.SysFont("arial", 18)

        self.botao_voltar = Botao((20, 18, 110, 44), "< Menu", (70, 60, 140))
        self.botao_de_novo = Botao((LARGURA // 2 - 215, 560, 205, 60), "Jogar de novo", (50, 160, 110))
        self.botao_ir_menu = Botao((LARGURA // 2 + 10, 560, 205, 60), "Menu", (70, 60, 140))

        self.reiniciar()

    # ------------------------- PREPARAR PARTIDA -------------------------
    def reiniciar(self):
        colunas, linhas = self.nivel["colunas"], self.nivel["linhas"]
        self.qtd_pares = colunas * linhas // 2

        # sorteia QUAIS figuras entram e depois duplica e embaralha
        ids = random.sample(range(len(FIGURAS)), self.qtd_pares) * 2
        random.shuffle(ids)

        # tamanho da carta para a grade caber na área disponível
        larg_disp = LARGURA - 80
        alt_disp = ALTURA - AREA_TOPO - AREA_BASE
        tam = min((larg_disp - (colunas - 1) * ESPACO) // colunas,
                  (alt_disp - (linhas - 1) * ESPACO) // linhas,
                  140)

        # centraliza a grade
        larg_grade = colunas * tam + (colunas - 1) * ESPACO
        alt_grade = linhas * tam + (linhas - 1) * ESPACO
        x0 = (LARGURA - larg_grade) // 2
        y0 = AREA_TOPO + (alt_disp - alt_grade) // 2

        self.cartas = []
        for i, id_figura in enumerate(ids):
            col, lin = i % colunas, i // colunas   # índice -> posição na grade
            carta = Carta(id_figura, x0 + col * (tam + ESPACO), y0 + lin * (tam + ESPACO), tam)
            carta.virada = True                    # todas à mostra no começo
            self.cartas.append(carta)

        self.particulas = []
        self.selecionadas = []
        self.tentativas = 0
        self.pares = 0
        self.estado = "memorizar"   # memorizar -> jogando <-> verificando -> vitoria
        self.inicio_estado = pygame.time.get_ticks()
        self.inicio_cronometro = None
        self.tempo_final = 0
        self.novo_recorde = False

    def tempo_de_jogo(self):
        """Segundos desde que as cartas viraram (o cronômetro para na vitória)."""
        if self.estado == "vitoria":
            return self.tempo_final
        if self.inicio_cronometro is None:
            return 0
        return (pygame.time.get_ticks() - self.inicio_cronometro) // 1000

    # ------------------------- EVENTOS -------------------------
    def tratar_evento(self, evento):
        """Devolve "menu" quando o jogador quer voltar para a tela 1."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
            if evento.key == pygame.K_r:
                self.reiniciar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.clicar(evento.pos)
        return None

    def clicar(self, pos):
        if self.botao_voltar.clicado(pos):
            return "menu"

        if self.estado == "vitoria":
            if self.botao_de_novo.clicado(pos):
                self.reiniciar()
            elif self.botao_ir_menu.clicado(pos):
                return "menu"
            return None

        if self.estado != "jogando":   # durante memorização/verificação não pode clicar
            return None

        for carta in self.cartas:
            if carta.rect.collidepoint(pos) and not carta.virada and not carta.encontrada:
                carta.virada = True
                self.selecionadas.append(carta)
                break

        if len(self.selecionadas) == 2:
            self.tentativas += 1
            a, b = self.selecionadas
            if a.id == b.id:                       # ACERTOU: marca e solta partículas
                a.encontrada = b.encontrada = True
                self.pares += 1
                self.explodir(a)
                self.explodir(b)
                self.selecionadas = []
                if self.pares == self.qtd_pares:
                    self.vencer()
            else:                                  # ERROU: espera, treme e desvira
                self.estado = "verificando"
                self.inicio_estado = pygame.time.get_ticks()
        return None

    def explodir(self, carta):
        """Cria partículas na cor da figura, saindo do centro da carta."""
        _nome, cor = FIGURAS[carta.id]
        for _ in range(28):
            self.particulas.append(Particula(*carta.rect.center, cor))

    def vencer(self):
        self.tempo_final = self.tempo_de_jogo()
        self.estado = "vitoria"
        nome = self.nivel["nome"]
        if self.recordes[nome] is None or self.tentativas < self.recordes[nome]:
            self.recordes[nome] = self.tentativas   # o menu "vê" esse recorde
            self.novo_recorde = True
        # confete caindo do topo
        for _ in range(160):
            cor = random.choice(FIGURAS)[1]
            p = Particula(random.uniform(0, LARGURA), random.uniform(-200, 0), cor,
                          vx=random.uniform(-60, 60), vy=random.uniform(50, 200))
            p.vida = p.vida_total = random.uniform(2.0, 3.5)
            self.particulas.append(p)

    def calcular_estrelas(self):
        """3 estrelas = quase perfeito; 2 = bom; 1 = completou."""
        if self.tentativas <= self.qtd_pares * 1.3:
            return 3
        if self.tentativas <= self.qtd_pares * 2:
            return 2
        return 1

    # ------------------------- ATUALIZAÇÃO -------------------------
    def atualizar(self, dt):
        agora = pygame.time.get_ticks()
        self.ceu.atualizar(dt)

        if self.estado == "memorizar":
            if agora - self.inicio_estado >= self.nivel["memorizar"]:
                for carta in self.cartas:
                    carta.virada = False
                self.estado = "jogando"
                self.inicio_cronometro = agora     # cronômetro começa aqui

        elif self.estado == "verificando":
            if agora - self.inicio_estado >= self.nivel["erro"]:
                for carta in self.selecionadas:
                    carta.virada = False
                self.selecionadas = []
                self.estado = "jogando"

        for carta in self.cartas:
            carta.atualizar(dt)

        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]   # remove as que morreram

    # ------------------------- DESENHO -------------------------
    def desenhar(self):
        mouse = pygame.mouse.get_pos()
        agora = pygame.time.get_ticks()
        tela = self.tela
        self.ceu.desenhar(tela)

        # Cabeçalho
        self.botao_voltar.desenhar(tela, self.fonte_media, self.fonte_pequena, mouse)
        texto(tela, f"{self.nivel['nome']}  •  {self.nivel['patente']}", self.fonte,
              self.nivel["cor"], (LARGURA // 2 + 40, 40))

        # Painel de informações (semitransparente)
        painel = pygame.Surface((LARGURA - 40, 50), pygame.SRCALPHA)
        pygame.draw.rect(painel, (30, 30, 80, 180), painel.get_rect(), border_radius=14)
        tela.blit(painel, (20, 78))
        minutos, segundos = divmod(self.tempo_de_jogo(), 60)
        texto(tela, f"Tentativas: {self.tentativas}", self.fonte_media, BRANCO, (130, 103))
        texto(tela, f"Pares: {self.pares}/{self.qtd_pares}", self.fonte_media, BRANCO, (LARGURA // 2, 103))
        texto(tela, f"Tempo: {minutos:02d}:{segundos:02d}", self.fonte_media, BRANCO, (LARGURA - 130, 103))

        # Mensagem de status
        if self.estado == "memorizar":
            restante = self.nivel["memorizar"] - (agora - self.inicio_estado)
            seg = max(0, math.ceil(restante / 1000))
            texto(tela, f"Memorize as cartas! Elas viram em {seg}s", self.fonte_media, AMARELO,
                  (LARGURA // 2, 150))
            fracao = max(0, restante) / self.nivel["memorizar"]          # barra diminuindo
            pygame.draw.rect(tela, AMARELO, (40, 165, int((LARGURA - 80) * fracao), 4), border_radius=2)
        elif self.estado == "verificando":
            texto(tela, "Não é par!", self.fonte, COR_ERRO, (LARGURA // 2, 150))
        elif self.estado == "jogando":
            texto(tela, "Encontre os pares com o menor número de tentativas",
                  self.fonte_pequena, CINZA, (LARGURA // 2, 150))

        # Cartas
        for carta in self.cartas:
            dx = dy = 0
            pode_clicar = (self.estado == "jogando" and not carta.virada
                           and not carta.encontrada and carta.rect.collidepoint(mouse))
            if pode_clicar:
                dy = -5                                   # "levanta" a carta
            if self.estado == "verificando" and carta in self.selecionadas:
                decorrido = agora - self.inicio_estado
                if 200 < decorrido < 550:                 # treme depois de terminar de virar
                    dx = math.sin(decorrido * 0.07) * 7
            carta.desenhar(tela, dx, dy, destacar=pode_clicar)

        for p in self.particulas:
            p.desenhar(tela)

        texto(tela, "R = reiniciar   |   ESC = menu", self.fonte_pequena, CINZA, (LARGURA // 2, ALTURA - 25))

        if self.estado == "vitoria":
            self.desenhar_vitoria(mouse)

    def desenhar_vitoria(self, mouse):
        tela = self.tela
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((5, 0, 20, 170))
        tela.blit(overlay, (0, 0))

        painel = pygame.Rect(LARGURA // 2 - 255, 190, 510, 460)
        pygame.draw.rect(tela, COR_PAINEL, painel, border_radius=24)
        pygame.draw.rect(tela, (150, 120, 255), painel, 3, border_radius=24)

        texto(tela, "Missão cumprida!", self.fonte_grande, AMARELO, (LARGURA // 2, 250))

        # estrelas (as conquistadas "pulsam" com seno)
        qtd = self.calcular_estrelas()
        pulso = 1 + 0.08 * math.sin(pygame.time.get_ticks() / 150)
        for i in range(3):
            cx = LARGURA // 2 + (i - 1) * 85
            if i < qtd:
                pygame.draw.polygon(tela, AMARELO, pontos_estrela(cx, 335, 34 * pulso, 15 * pulso))
            else:
                pygame.draw.polygon(tela, (70, 70, 110), pontos_estrela(cx, 335, 34, 15))

        minutos, segundos = divmod(self.tempo_final, 60)
        texto(tela, f"{self.tentativas} tentativas  •  {minutos:02d}:{segundos:02d}",
              self.fonte, BRANCO, (LARGURA // 2, 420))
        if self.novo_recorde:
            texto(tela, "Novo recorde!", self.fonte, COR_ACERTO, (LARGURA // 2, 475))
        else:
            rec = self.recordes[self.nivel["nome"]]
            texto(tela, f"Recorde: {rec} tentativas", self.fonte_media, CINZA, (LARGURA // 2, 475))

        self.botao_de_novo.desenhar(tela, self.fonte_media, self.fonte_pequena, mouse)
        self.botao_ir_menu.desenhar(tela, self.fonte_media, self.fonte_pequena, mouse)

        for p in self.particulas:       # confete por cima de tudo
            p.desenhar(tela)


# =============================== TELA 1: MENU ===============================
class Menu:
    def __init__(self, tela, recordes, ceu):
        self.tela = tela
        self.recordes = recordes
        self.ceu = ceu

        self.fonte_titulo = pygame.font.SysFont("arial", 56, bold=True)
        self.fonte = pygame.font.SysFont("arial", 26, bold=True)
        self.fonte_media = pygame.font.SysFont("arial", 22)
        self.fonte_pequena = pygame.font.SysFont("arial", 18)

        # Um botão para cada nível, um embaixo do outro
        self.botoes = []
        for i, nivel in enumerate(NIVEIS):
            qtd = nivel["colunas"] * nivel["linhas"]
            titulo = f"{nivel['nome']}  •  {nivel['patente']}"
            sub = f"{qtd} cartas  •  {qtd // 2} pares  •  {nivel['memorizar'] // 1000}s para memorizar"
            rect = (LARGURA // 2 - 260, 300 + i * 135, 520, 100)
            self.botoes.append(Botao(rect, titulo, nivel["cor"], sub))

    def tratar_evento(self, evento):
        """Devolve o NÍVEL escolhido (dicionário), "sair", ou None."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "sair"
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for botao, nivel in zip(self.botoes, NIVEIS):
                if botao.clicado(evento.pos):
                    return nivel
        return None

    def atualizar(self, dt):
        self.ceu.atualizar(dt)

    def desenhar_orbita(self):
        """Cartinhas girando numa órbita (elipse) no topo.
        sin(ângulo) diz se a carta está "na frente" ou "atrás":
        as da frente ficam maiores e são desenhadas por último."""
        t = self.ceu.tempo
        cx, cy = LARGURA // 2, 100
        cartinhas = []
        for i in range(8):
            ang = t * 0.6 + i * 2 * math.pi / 8
            profundidade = math.sin(ang)                 # -1 = atrás, 1 = na frente
            x = cx + math.cos(ang) * 270
            y = cy + profundidade * 38
            tam = int(46 + 16 * profundidade)
            cartinhas.append((profundidade, x, y, tam, FIGURAS[i][0]))

        for _prof, x, y, tam, nome in sorted(cartinhas):   # de trás para frente
            r = pygame.Rect(0, 0, tam, tam)
            r.center = (x, y)
            pygame.draw.rect(self.tela, COR_FRENTE, r, border_radius=8)
            desenhar_figura(self.tela, nome, r)
            pygame.draw.rect(self.tela, COR_FRENTE_BORDA, r, 2, border_radius=8)

    def desenhar(self):
        mouse = pygame.mouse.get_pos()
        tela = self.tela
        self.ceu.desenhar(tela)
        self.desenhar_orbita()

        # Título com "brilho": o mesmo texto em roxo deslocado, por trás
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            texto(tela, "Memória Espacial", self.fonte_titulo, (140, 80, 255), (LARGURA // 2 + dx, 205 + dy))
        texto(tela, "Memória Espacial", self.fonte_titulo, BRANCO, (LARGURA // 2, 205))
        texto(tela, "Escolha sua missão", self.fonte_media, CINZA, (LARGURA // 2, 255))

        for botao, nivel in zip(self.botoes, NIVEIS):
            botao.desenhar(tela, self.fonte, self.fonte_pequena, mouse)
            rec = self.recordes[nivel["nome"]]
            if rec is not None:
                texto(tela, f"Recorde: {rec} tentativas", self.fonte_pequena, AMARELO,
                      (LARGURA // 2, botao.rect.bottom + 15))

        texto(tela, "ESC = sair", self.fonte_pequena, CINZA, (LARGURA // 2, ALTURA - 30))


# =============================== PROGRAMA PRINCIPAL ===============================
def sair():
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Memória Espacial")
    clock = pygame.time.Clock()

    # Compartilhados entre as duas telas
    recordes = {nivel["nome"]: None for nivel in NIVEIS}   # menor nº de tentativas por nível
    ceu = CeuEstrelado()                                    # fundo animado

    menu = Menu(tela, recordes, ceu)
    tela_ativa = menu            # começa no menu

    while True:
        dt = clock.tick(FPS) / 1000   # segundos desde o último quadro

        # 1) EVENTOS: cada tela trata os seus e diz se quer trocar de tela
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sair()

            resultado = tela_ativa.tratar_evento(evento)

            if tela_ativa is menu:
                if resultado == "sair":
                    sair()
                elif resultado is not None:              # escolheu um nível
                    tela_ativa = TelaJogo(tela, resultado, recordes, ceu)
            else:
                if resultado == "menu":                  # jogo pediu para voltar
                    tela_ativa = menu

        # 2) LÓGICA  e  3) DESENHO da tela ativa
        tela_ativa.atualizar(dt)
        tela_ativa.desenhar()
        pygame.display.flip()


if __name__ == "__main__":
    main()
