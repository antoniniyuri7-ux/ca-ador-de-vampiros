"""Caçador de Vampiros — jogo Pygame."""

import random
import sys
import os

import pygame
from Recursos.trabalho import ler_recorde, salvar_partida

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


def pedir_nome_antes_de_abrir_jogo():
    """Lê o nome no terminal antes de inicializar o Pygame e abrir a janela."""
    while True:
        try:
            nome = input("Informe o nome do jogador: ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if nome:
            return nome
        print("Digite um nome para continuar.")


# O jogo só cria sua janela depois que o competidor informa o nome.
NOME_JOGADOR = pedir_nome_antes_de_abrir_jogo()


BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
LARGURA, ALTURA = 1000, 700
# O cenário original tem 563 px de altura; o espaço inferior será o HUD.
AREA_JOGO = 563
FPS = 60
BRANCO = (248, 238, 228)
VERMELHO = (220, 25, 35)
PRETO = (8, 6, 12)
LOG = os.path.join(BASE, "log.dat")

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Caçador de Vampiros")
try:
    pygame.display.set_icon(pygame.image.load(os.path.join(ASSETS, "icone.png")))
except (pygame.error, FileNotFoundError):
    pass
relogio = pygame.time.Clock()


def imagem(nome, tamanho=None):
    img = pygame.image.load(os.path.join(ASSETS, nome)).convert_alpha()
    return pygame.transform.smoothscale(img, tamanho) if tamanho else img


def imagem_capa(nome):
    """Preserva a proporção da arte original e centraliza na tela 1000×700."""
    img = pygame.image.load(os.path.join(ASSETS, nome)).convert()
    largura = LARGURA
    altura = round(img.get_height() * largura / img.get_width())
    img = pygame.transform.smoothscale(img, (largura, altura))
    return img, (0, (ALTURA - altura) // 2)


FUNDO, _ = imagem_capa("fundo_jogo.png")
CAPA_INICIO, POS_INICIO = imagem_capa("tela_inicio.png")
CAPA_MORTE, POS_MORTE = imagem_capa("tela_morte.png")
CACADOR = imagem("cacador.png", (220, 160))
VAMPIRO = imagem("vampiro.png", (220, 155))
FLECHA = imagem("flecha.png", (82, 21))
FONT_MENU = pygame.font.SysFont("comicsans", 23)
FONT_MED = pygame.font.SysFont("comicsans", 28, bold=True)
FONT_BIG = pygame.font.SysFont("comicsans", 54, bold=True)
FONT_SMALL = pygame.font.SysFont("comicsans", 15)


def carregar_som(nome):
    try:
        return pygame.mixer.Sound(os.path.join(ASSETS, nome))
    except (pygame.error, FileNotFoundError):
        return None


SOM_TIRO = carregar_som("tiro_crossbow.mp3")
SOM_RECARREGAR = carregar_som("recarregar_crossbow.mp3")
SOM_MORTE = carregar_som("morte_cacador.mp3")
try:
    pygame.mixer.music.load(os.path.join(ASSETS, "som_vampiro.mp3"))
except (pygame.error, FileNotFoundError):
    pass


def tocar(som):
    if som:
        som.play()


def falar_boas_vindas(nome):
    """Fala o nome do competidor usando a biblioteca pyttsx3."""
    if pyttsx3 is None:
        return
    try:
        voz = pyttsx3.init()
        voz.say("Bem-vindo, " + nome + ". Sobreviva aos vampiros e marque pontos.")
        voz.runAndWait()
        voz.stop()
    except Exception:
        pass


def encerrar():
    pygame.quit()
    sys.exit()


def desenhar_capa(capa, pos):
    tela.fill(PRETO)
    tela.blit(capa, pos)


def texto(texto_, fonte, cor=BRANCO):
    return fonte.render(texto_, True, cor)


def caixas_menu_inicio():
    # Coordenadas dos três botões já desenhados na capa original (arte 1000×562).
    y0 = POS_INICIO[1]
    return (pygame.Rect(350, y0 + 325, 300, 66),
            pygame.Rect(350, y0 + 392, 300, 55),
            pygame.Rect(350, y0 + 447, 300, 60))


def caixas_morte():
    y0 = POS_MORTE[1]
    # As áreas acompanham os botões ilustrados na capa de morte após a escala.
    return (pygame.Rect(320, y0 + 150, 360, 70),
            pygame.Rect(320, y0 + 220, 360, 65))


def tela_instrucoes(nome):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                encerrar()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                encerrar()
            if evento.type == pygame.MOUSEBUTTONUP or (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_BACKSPACE)):
                return

        desenhar_capa(CAPA_INICIO, POS_INICIO)
        painel = pygame.Surface((590, 300), pygame.SRCALPHA)
        painel.fill((8, 5, 10, 228))
        tela.blit(painel, (205, 185))
        tela.blit(texto("Bem-vindo, " + nome, FONT_MED, VERMELHO), (245, 205))
        linhas = ["Use as setas para mover o caçador (um eixo por vez).",
                 "Pressione ESPAÇO para pausar ou continuar.",
                 "Use CTRL para disparar; R recarrega até 5 flechas.",
                 "Acerte os vampiros antes que alcancem você.",
                 "Recorde: " + ler_recorde(LOG),
                 "Clique ou pressione ENTER para voltar à capa inicial."]
        for i, linha in enumerate(linhas):
            tela.blit(texto(linha, FONT_MENU), (245, 250 + i * 35))
        pygame.display.flip()
        relogio.tick(FPS)


def tela_inicial(nome):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                encerrar()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                encerrar()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_x:
                return
            if evento.type == pygame.MOUSEBUTTONUP:
                iniciar, instrucoes, sair = caixas_menu_inicio()
                if iniciar.collidepoint(evento.pos):
                    return
                if instrucoes.collidepoint(evento.pos):
                    tela_instrucoes(nome)
                elif sair.collidepoint(evento.pos):
                    encerrar()

        desenhar_capa(CAPA_INICIO, POS_INICIO)
        # Informações solicitadas ficam numa faixa discreta, sem alterar a arte/botões.
        faixa = pygame.Surface((260, 108), pygame.SRCALPHA)
        faixa.fill((8, 5, 10, 205))
        tela.blit(faixa, (720, 430))
        tela.blit(texto("Olá, " + nome[:22], FONT_SMALL), (734, 442))
        tela.blit(texto("Acerte vampiros; sobreviva!", FONT_SMALL), (734, 465))
        recorde = ler_recorde(LOG)
        tela.blit(texto("Recorde: " + recorde[:25], FONT_SMALL), (734, 488))
        tela.blit(texto("Pressione X para começar", FONT_SMALL), (24, 652))
        pygame.display.flip()
        relogio.tick(FPS)


def criar_decoracao():
    decoracaoX = []
    decoracaoY = []
    movimentoX = []
    movimentoY = []
    tamanho = []
    for i in range(12):
        decoracaoX.append(random.randint(0, LARGURA))
        decoracaoY.append(random.randint(70, AREA_JOGO - 35))
        movimentoX.append(random.choice([-1, 1]))
        movimentoY.append(random.choice([-1, 1]))
        tamanho.append(random.randint(2, 4))
    return decoracaoX, decoracaoY, movimentoX, movimentoY, tamanho


def jogar(nome):
    pontos = 0
    posicaoXCacador, posicaoYCacador = 35, 290
    posicaoXVampiro, posicaoYVampiro = 1010, random.randint(45, AREA_JOGO - VAMPIRO.get_height() - 10)
    velocidadeVampiro = 2.4
    vx = vy = 0
    eixo = None
    flechas = 5
    projeteis = []
    pausado = False
    decoracaoX, decoracaoY, movimentoX, movimentoY, tamanhoDecoracao = criar_decoracao()
    tamanhoBola = 30
    aumentarBola = True
    try:
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    while True:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                encerrar()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    encerrar()
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
                    if pausado:
                        vx = vy = 0
                    continue
                if pausado:
                    continue
                if evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    eixo, vy = "x", 0
                    vx = -5 if evento.key == pygame.K_LEFT else 5
                elif evento.key in (pygame.K_UP, pygame.K_DOWN):
                    eixo, vx = "y", 0
                    vy = -5 if evento.key == pygame.K_UP else 5
                elif evento.key == pygame.K_LCTRL or evento.key == pygame.K_RCTRL:
                    if flechas > 0:
                        projeteis.append(pygame.Rect(posicaoXCacador + 170, posicaoYCacador + 72, 82, 21))
                        flechas -= 1
                        tocar(SOM_TIRO)
                elif evento.key == pygame.K_r and flechas < 5:
                    flechas = 5
                    tocar(SOM_RECARREGAR)
            if evento.type == pygame.KEYUP and not pausado:
                if eixo == "x" and evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    vx = 0
                if eixo == "y" and evento.key in (pygame.K_UP, pygame.K_DOWN):
                    vy = 0

        if not pausado:
            # A bola vermelha pulsa no canto superior direito durante a partida.
            if aumentarBola:
                tamanhoBola = tamanhoBola + 0.08
                if tamanhoBola >= 36:
                    aumentarBola = False
            else:
                tamanhoBola = tamanhoBola - 0.08
                if tamanhoBola <= 30:
                    aumentarBola = True

            posicaoXCacador = max(0, min(LARGURA - CACADOR.get_width(), posicaoXCacador + vx))
            posicaoYCacador = max(34, min(AREA_JOGO - CACADOR.get_height() - 10, posicaoYCacador + vy))
            posicaoXVampiro -= velocidadeVampiro
            for i in range(len(decoracaoX)):
                decoracaoX[i] = decoracaoX[i] + movimentoX[i]
                decoracaoY[i] = decoracaoY[i] + movimentoY[i]
                if decoracaoX[i] < 0 or decoracaoX[i] > LARGURA:
                    movimentoX[i] = movimentoX[i] * -1
                if decoracaoY[i] < 40 or decoracaoY[i] > AREA_JOGO - 20:
                    movimentoY[i] = movimentoY[i] * -1

            vampiro_corpo = pygame.Rect(posicaoXVampiro + 63, posicaoYVampiro + 39, 110, 89)
            hunter_corpo = pygame.Rect(posicaoXCacador + 65, posicaoYCacador + 47, 112, 82)
            flecha_acertou = False
            for seta in projeteis[:]:
                seta.x += 11
                if seta.left > LARGURA:
                    projeteis.remove(seta)
                elif seta.colliderect(vampiro_corpo):
                    projeteis.remove(seta)
                    pontos += 1
                    velocidadeVampiro = min(6.5, velocidadeVampiro + 0.25)
                    posicaoXVampiro, posicaoYVampiro = LARGURA + 10, random.randint(45, AREA_JOGO - VAMPIRO.get_height() - 10)
                    flecha_acertou = True
                    break

            if posicaoXVampiro < -VAMPIRO.get_width():
                posicaoXVampiro, posicaoYVampiro = LARGURA + 10, random.randint(45, AREA_JOGO - VAMPIRO.get_height() - 10)
            if not flecha_acertou and vampiro_corpo.colliderect(hunter_corpo):
                pygame.mixer.music.stop()
                salvar_partida(LOG, nome, pontos)
                tocar(SOM_MORTE)
                return pontos

        tela.fill((12, 7, 17))
        tela.blit(FUNDO, (0, 0))
        # Esconde a lua parada que já vinha desenhada no fundo do mapa.
        pygame.draw.circle(tela, (20, 9, 27), (800, 145), 112)
        pygame.draw.rect(tela, (18, 8, 16), (0, AREA_JOGO, LARGURA, ALTURA - AREA_JOGO))
        pygame.draw.line(tela, (113, 25, 34), (0, AREA_JOGO), (LARGURA, AREA_JOGO), 2)
        # Esta bola é independente do fundo e continua pulsando.
        pygame.draw.circle(tela, (90, 0, 12), (950, 55), int(tamanhoBola) + 7)
        pygame.draw.circle(tela, (225, 31, 42), (950, 55), int(tamanhoBola))
        pygame.draw.circle(tela, (255, 113, 91), (941, 47), 8)
        for i in range(len(decoracaoX)):
            pygame.draw.circle(tela, (160, 70, 83),
                               (decoracaoX[i], decoracaoY[i]), tamanhoDecoracao[i])
        tela.blit(CACADOR, (posicaoXCacador, posicaoYCacador))
        tela.blit(VAMPIRO, (posicaoXVampiro, posicaoYVampiro))
        for seta in projeteis:
            tela.blit(FLECHA, seta)

        tela.blit(texto(f"Jogador: {nome[:24]}", FONT_MENU), (24, AREA_JOGO + 16))
        tela.blit(texto(f"Pontos: {pontos}", FONT_MENU), (300, AREA_JOGO + 16))
        tela.blit(texto(f"Flechas: {flechas}/5", FONT_MENU), (465, AREA_JOGO + 16))
        tela.blit(texto("Setas: mover  |  CTRL: atirar  |  R: recarregar", FONT_SMALL), (24, AREA_JOGO + 58))
        tela.blit(texto("Press Space to Pause Game", FONT_SMALL), (720, AREA_JOGO + 58))
        if pausado:
            sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 145))
            tela.blit(sombra, (0, 0))
            aviso = texto("PAUSE", FONT_BIG, (255, 215, 190))
            tela.blit(aviso, aviso.get_rect(center=(LARGURA // 2, ALTURA // 2)))
        pygame.display.flip()


def tela_morte(nome, pontos):
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                encerrar()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                encerrar()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_x:
                return True
            if evento.type == pygame.MOUSEBUTTONUP:
                tentar, sair = caixas_morte()
                if tentar.collidepoint(evento.pos):
                    return True
                if sair.collidepoint(evento.pos):
                    encerrar()

        desenhar_capa(CAPA_MORTE, POS_MORTE)
        recorde = ler_recorde(LOG)
        linha1 = texto(f"{nome}  |  Pontuação: {pontos}", FONT_MENU)
        linha2 = texto("Recordista: " + recorde[:45], FONT_SMALL)
        tela.blit(linha1, linha1.get_rect(center=(500, 535)))
        tela.blit(linha2, linha2.get_rect(center=(500, 568)))
        tela.blit(texto("Pressione X para tentar novamente", FONT_SMALL), (24, 652))
        pygame.display.flip()
        relogio.tick(FPS)


def main():
    nome = NOME_JOGADOR
    falar_boas_vindas(nome)
    while True:
        tela_inicial(nome)
        while True:
            resultado = jogar(nome)
            if not tela_morte(nome, resultado):
                break


if __name__ == "__main__":
    main()
