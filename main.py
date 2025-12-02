import pygame
import sys
import os
import random
import math
from enum import Enum

# Inicializa
pygame.init()

# Configurações
LARGURA = 400
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Flappy Bird - Coletáveis")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonte
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 64)
fonte_pequena = pygame.font.SysFont(None, 24)

# ====== ENUMS ======

class TipoColetavel(Enum):
    MOEDA = 1
    VIDA = 2
    IMÃ = 3
    ESCUDO = 4
    VELOCIDADE = 5
    GRAVIDADE = 6
    PONTOS_DOBRO = 7
    TAMANHO = 8

class TipoPowerUp(Enum):
    VELOCIDADE = 1
    GRAVIDADE = 2
    PONTOS_DOBRO = 3
    TAMANHO = 4
    IMÃ = 5

# ====== FUNÇÃO PARA CARREGAR IMAGENS ======

def carregar_imagem(nome, tamanho=None):
    """Carrega uma imagem da pasta assets"""
    caminhos = [
        f'assets/{nome}',
        f'./assets/{nome}',
        nome
    ]
    
    for caminho in caminhos:
        if os.path.exists(caminho):
            try:
                img = pygame.image.load(caminho)
                if img.get_alpha() is None:
                    img = img.convert()
                else:
                    img = img.convert_alpha()
                print(f"✓ Carregado: {caminho}")
                
                if tamanho:
                    img = pygame.transform.scale(img, tamanho)
                return img
            except Exception as e:
                print(f"✗ Erro ao carregar {caminho}: {e}")
    
    print(f"✗ Imagem não encontrada: {nome}")
    return None

# ====== CARREGA IMAGENS ======

print("=== Carregando imagens ===")

# Carrega imagens
img_fundo = carregar_imagem('background.png', (LARGURA, ALTURA))
if not img_fundo:
    img_fundo = pygame.Surface((LARGURA, ALTURA))
    for y in range(ALTURA):
        cor = (135 - y//10, 206 - y//10, 235)
        pygame.draw.line(img_fundo, cor, (0, y), (LARGURA, y))

img_chao = carregar_imagem('ground.png', (LARGURA, 100))
if not img_chao:
    img_chao = pygame.Surface((LARGURA, 100))
    img_chao.fill((222, 184, 135))
    for i in range(0, LARGURA, 40):
        pygame.draw.rect(img_chao, (139, 69, 19), (i, 0, 40, 20))

img_passaro = carregar_imagem('bird.png', (40, 40))
if not img_passaro:
    img_passaro = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(img_passaro, (255, 255, 0), (20, 20), 18)
    pygame.draw.circle(img_passaro, (0, 0, 0), (30, 15), 5)

img_cano = carregar_imagem('pipe.png')
if not img_cano:
    img_cano = carregar_imagem('cano.png')
if not img_cano:
    print("Criando cano gráfico...")
    img_cano = pygame.Surface((70, 400), pygame.SRCALPHA)
    pygame.draw.rect(img_cano, (0, 180, 0), (0, 0, 70, 400))
    pygame.draw.rect(img_cano, (0, 150, 0), (0, 0, 70, 15))
    pygame.draw.rect(img_cano, (0, 150, 0), (0, 385, 70, 15))

print("=== Todas as imagens carregadas ===\n")

# ====== SISTEMA DE COLETÁVEIS ======

class Coletavel:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.raio = 15
        self.vel_y = random.uniform(-0.5, 0.5)
        self.tempo_vida = 400  # Frames de vida (mais tempo)
        self.coletado = False
        self.angulo = 0
        self.vel_rotacao = random.uniform(-3, 3)
        
        # Efeitos visuais
        self.particulas = []
        self.efeito_brilho = 0
        self.efeito_direcao = 1
        
        # Cores por tipo
        self.cores = {
            TipoColetavel.MOEDA: (255, 215, 0),      # Ouro
            TipoColetavel.VIDA: (255, 50, 50),       # Vermelho
            TipoColetavel.IMÃ: (100, 200, 255),      # Azul
            TipoColetavel.ESCUDO: (100, 255, 100),   # Verde
            TipoColetavel.VELOCIDADE: (255, 165, 0), # Laranja
            TipoColetavel.GRAVIDADE: (200, 100, 255),# Roxo
            TipoColetavel.PONTOS_DOBRO: (255, 255, 100), # Amarelo claro
            TipoColetavel.TAMANHO: (100, 255, 255)   # Ciano
        }
        
        # Valores por tipo
        self.valores = {
            TipoColetavel.MOEDA: 10,
            TipoColetavel.VIDA: 1,
            TipoColetavel.IMÃ: 0,
            TipoColetavel.ESCUDO: 0,
            TipoColetavel.VELOCIDADE: 0,
            TipoColetavel.GRAVIDADE: 0,
            TipoColetavel.PONTOS_DOBRO: 0,
            TipoColetavel.TAMANHO: 0
        }
        
        # Tempo de duração dos power-ups (em frames)
        self.duracoes = {
            TipoColetavel.IMÃ: 300,          # 5 segundos
            TipoColetavel.ESCUDO: 400,       # ~6.5 segundos
            TipoColetavel.VELOCIDADE: 350,   # ~5.8 segundos
            TipoColetavel.GRAVIDADE: 300,    # 5 segundos
            TipoColetavel.PONTOS_DOBRO: 400, # ~6.5 segundos
            TipoColetavel.TAMANHO: 450       # 7.5 segundos
        }
        
        print(f"Coletável criado: {tipo} em ({x}, {y})")
    
    def atualizar(self, jogador_x, jogador_y, ima_ativo=False):
        self.tempo_vida -= 1
        self.angulo += self.vel_rotacao
        
        # Flutuação vertical
        self.y += self.vel_y
        if self.y < 50 or self.y > ALTURA - 150:
            self.vel_y *= -1
        
        # Efeito de brilho pulsante
        self.efeito_brilho += 0.1 * self.efeito_direcao
        if self.efeito_brilho > 1.0 or self.efeito_brilho < 0.3:
            self.efeito_direcao *= -1
        
        # Se ímã está ativo, atrai moedas para o jogador
        if ima_ativo and self.tipo == TipoColetavel.MOEDA:
            dx = jogador_x - self.x
            dy = jogador_y - self.y
            distancia = math.sqrt(dx*dx + dy*dy)
            
            if distancia > 0 and distancia < 200:  # Raio de atração
                forca = 3.0 / (distancia + 1)
                self.x += dx * forca * 0.1
                self.y += dy * forca * 0.1
        
        # Move coletável para a esquerda (como os canos)
        self.x -= 3  # Velocidade fixa para coletáveis
        
        # Adiciona partículas ocasionalmente
        if random.random() < 0.1:
            self.particulas.append({
                'x': self.x,
                'y': self.y,
                'vel_x': random.uniform(-1, 1),
                'vel_y': random.uniform(-1, 1),
                'tamanho': random.randint(1, 3),
                'cor': self.cores[self.tipo],
                'vida': 30
            })
        
        # Atualiza partículas
        for p in self.particulas[:]:
            p['x'] += p['vel_x']
            p['y'] += p['vel_y']
            p['vida'] -= 1
            if p['vida'] <= 0:
                self.particulas.remove(p)
        
        # Retorna True se saiu da tela ou tempo acabou
        return self.tempo_vida <= 0 or self.x < -50
    
    def desenhar(self, tela):
        # Desenha partículas
        for p in self.particulas:
            alpha = p['vida'] * 8
            pygame.draw.circle(tela, p['cor'], 
                             (int(p['x']), int(p['y'])), p['tamanho'])
        
        cor_base = self.cores[self.tipo]
        
        # Efeito de brilho
        brilho = int(255 * self.efeito_brilho)
        cor_brilhante = (
            min(255, cor_base[0] + brilho // 3),
            min(255, cor_base[1] + brilho // 3),
            min(255, cor_base[2] + brilho // 3)
        )
        
        # Desenha o coletável rotacionado
        superficie = pygame.Surface((self.raio * 3, self.raio * 3), pygame.SRCALPHA)
        
        if self.tipo == TipoColetavel.MOEDA:
            # Moeda dourada
            pygame.draw.circle(superficie, cor_brilhante, (self.raio * 1.5, self.raio * 1.5), self.raio)
            pygame.draw.circle(superficie, (200, 170, 0), (self.raio * 1.5, self.raio * 1.5), self.raio - 3)
            
            # Símbolo $
            fonte_moeda = pygame.font.SysFont(None, 24)
            texto = fonte_moeda.render("$", True, (255, 255, 200))
            superficie.blit(texto, (self.raio * 1.5 - 6, self.raio * 1.5 - 10))
            
        elif self.tipo == TipoColetavel.VIDA:
            # Coração
            pontos = [
                (self.raio * 1.5, self.raio * 0.8),
                (self.raio * 1.2, self.raio * 1.2),
                (self.raio * 1.5, self.raio * 2.0),
                (self.raio * 1.8, self.raio * 1.2)
            ]
            pygame.draw.polygon(superficie, cor_brilhante, pontos)
            
        elif self.tipo == TipoColetavel.IMÃ:
            # Ímã (forma de ferradura)
            pygame.draw.circle(superficie, cor_brilhante, (self.raio * 1.5, self.raio * 1.5), self.raio)
            pygame.draw.circle(superficie, (0, 0, 0), (self.raio * 1.5, self.raio * 1.5), self.raio - 5)
            
        elif self.tipo == TipoColetavel.ESCUDO:
            # Escudo circular
            pygame.draw.circle(superficie, cor_brilhante, (self.raio * 1.5, self.raio * 1.5), self.raio)
            for i in range(3):
                raio_interno = self.raio - 3 - i * 3
                if raio_interno > 0:
                    pygame.draw.circle(superficie, (200, 255, 200), 
                                     (self.raio * 1.5, self.raio * 1.5), 
                                     raio_interno, 2)
                    
        elif self.tipo == TipoColetavel.VELOCIDADE:
            # Raio (seta)
            pontos = [
                (self.raio * 1.5, self.raio * 0.5),
                (self.raio * 1.0, self.raio * 1.5),
                (self.raio * 1.3, self.raio * 1.5),
                (self.raio * 1.3, self.raio * 2.5),
                (self.raio * 1.7, self.raio * 2.5),
                (self.raio * 1.7, self.raio * 1.5),
                (self.raio * 2.0, self.raio * 1.5)
            ]
            pygame.draw.polygon(superficie, cor_brilhante, pontos)
            
        elif self.tipo == TipoColetavel.GRAVIDADE:
            # Planeta com anéis
            pygame.draw.circle(superficie, cor_brilhante, (self.raio * 1.5, self.raio * 1.5), self.raio)
            # Anéis
            pygame.draw.ellipse(superficie, (150, 150, 255), 
                              (self.raio * 0.5, self.raio * 0.8, self.raio * 2, self.raio * 0.5), 2)
            
        elif self.tipo == TipoColetavel.PONTOS_DOBRO:
            # "2X" em um diamante
            pygame.draw.polygon(superficie, cor_brilhante, [
                (self.raio * 1.5, self.raio * 0.5),
                (self.raio * 2.0, self.raio * 1.5),
                (self.raio * 1.5, self.raio * 2.5),
                (self.raio * 1.0, self.raio * 1.5)
            ])
            texto = fonte_pequena.render("2X", True, (255, 255, 255))
            superficie.blit(texto, (self.raio * 1.5 - 10, self.raio * 1.5 - 8))
            
        elif self.tipo == TipoColetavel.TAMANHO:
            # Setas para dentro/fora
            pygame.draw.circle(superficie, cor_brilhante, (self.raio * 1.5, self.raio * 1.5), self.raio)
            # Setas
            for i in range(4):
                ang = i * 90
                x1 = self.raio * 1.5 + math.cos(math.radians(ang)) * (self.raio - 5)
                y1 = self.raio * 1.5 + math.sin(math.radians(ang)) * (self.raio - 5)
                x2 = self.raio * 1.5 + math.cos(math.radians(ang)) * (self.raio - 10)
                y2 = self.raio * 1.5 + math.sin(math.radians(ang)) * (self.raio - 10)
                pygame.draw.line(superficie, (255, 255, 255), (x1, y1), (x2, y2), 3)
        
        # Rotaciona e desenha
        superficie_rot = pygame.transform.rotate(superficie, self.angulo)
        rect_rot = superficie_rot.get_rect(center=(self.x, self.y))
        tela.blit(superficie_rot, rect_rot)
        
        # Aura/brilho externo
        for i in range(2):
            raio_aura = self.raio + 3 + i * 2
            alpha = 100 - i * 30
            pygame.draw.circle(tela, (*cor_base[:3], alpha), (int(self.x), int(self.y)), 
                             raio_aura, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, 
                          self.raio * 2, self.raio * 2)
    
    def coletar(self):
        self.coletado = True
        print(f"Coletável {self.tipo} coletado!")
        return self.valores.get(self.tipo, 0), self.tipo, self.duracoes.get(self.tipo, 0)

# ====== SISTEMA DE POWER-UPS ATIVOS ======

class PowerUpAtivo:
    def __init__(self, tipo, duracao):
        self.tipo = tipo
        self.duracao = duracao
        self.tempo_restante = duracao
    
    def atualizar(self):
        self.tempo_restante -= 1
        return self.tempo_restante > 0
    
    def get_porcentagem(self):
        return self.tempo_restante / self.duracao

# ====== JOGADOR ======

class Passaro:
    def __init__(self):
        self.x = 100
        self.y = ALTURA // 2
        self.tamanho_base = 40
        self.tamanho_atual = self.tamanho_base
        self.imagem_original = img_passaro
        
        self.velocidade_base = 3
        self.velocidade_canos = self.velocidade_base
        self.gravidade_base = 0.5
        self.gravidade_atual = self.gravidade_base
        self.pulo_base = -7
        self.pulo_atual = self.pulo_base
        
        self.velocidade = 0
        self.angulo = 0
        self.rect = pygame.Rect(self.x, self.y, self.tamanho_atual, self.tamanho_atual)
        
        self.efeito_particulas = []
        self.power_ups_ativos = []
        self.vidas = 3
        self.escudo = False
        self.escudo_duracao = 0
        self.multiplier_pontos = 1
        
        # Efeitos visuais
        self.efeito_brilho = 0
        self.cor_efeito = (255, 255, 255)
    
    def aplicar_power_up(self, tipo, duracao):
        # Remove power-ups do mesmo tipo
        self.power_ups_ativos = [p for p in self.power_ups_ativos if p.tipo != tipo]
        
        # Adiciona novo power-up
        self.power_ups_ativos.append(PowerUpAtivo(tipo, duracao))
        print(f"Power-up aplicado: {tipo}")
        
        # Aplica efeitos imediatos
        if tipo == TipoPowerUp.VELOCIDADE:
            self.velocidade_canos = self.velocidade_base * 0.7
            self.cor_efeito = (255, 165, 0)
        elif tipo == TipoPowerUp.GRAVIDADE:
            self.gravidade_atual = self.gravidade_base * 0.6
            self.pulo_atual = self.pulo_base * 0.8
            self.cor_efeito = (200, 100, 255)
        elif tipo == TipoPowerUp.PONTOS_DOBRO:
            self.multiplier_pontos = 2
            self.cor_efeito = (255, 255, 100)
        elif tipo == TipoPowerUp.TAMANHO:
            self.tamanho_atual = self.tamanho_base * 0.7
            self.cor_efeito = (100, 255, 255)
        elif tipo == TipoPowerUp.IMÃ:
            self.cor_efeito = (100, 200, 255)
    
    def remover_power_up(self, tipo):
        print(f"Power-up removido: {tipo}")
        if tipo == TipoPowerUp.VELOCIDADE:
            self.velocidade_canos = self.velocidade_base
        elif tipo == TipoPowerUp.GRAVIDADE:
            self.gravidade_atual = self.gravidade_base
            self.pulo_atual = self.pulo_base
        elif tipo == TipoPowerUp.PONTOS_DOBRO:
            self.multiplier_pontos = 1
        elif tipo == TipoPowerUp.TAMANHO:
            self.tamanho_atual = self.tamanho_base
        elif tipo == TipoPowerUp.IMÃ:
            pass
    
    def atualizar_power_ups(self):
        # Atualiza power-ups ativos
        for power_up in self.power_ups_ativos[:]:
            if not power_up.atualizar():
                self.remover_power_up(power_up.tipo)
                self.power_ups_ativos.remove(power_up)
        
        # Atualiza escudo
        if self.escudo:
            self.escudo_duracao -= 1
            if self.escudo_duracao <= 0:
                self.escudo = False
                print("Escudo desativado")
        
        # Efeito de brilho se tem power-up
        if self.power_ups_ativos:
            self.efeito_brilho = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
        else:
            self.efeito_brilho = 0
    
    def pular(self):
        self.velocidade = self.pulo_atual
        self.angulo = 20
        
        # Efeito de partículas
        for _ in range(5):
            self.efeito_particulas.append({
                'x': self.x,
                'y': self.y + self.tamanho_atual//2,
                'vel_x': random.uniform(-2, 2),
                'vel_y': random.uniform(-3, -1),
                'tamanho': random.randint(2, 4),
                'cor': (255, 255, 200),
                'vida': 20
            })
    
    def atualizar(self):
        # Atualiza física
        self.velocidade += self.gravidade_atual
        self.y += self.velocidade
        
        # Rotação
        if self.velocidade > 0:
            self.angulo = max(-90, self.angulo - 3)
        else:
            self.angulo = min(20, self.angulo + 5)
        
        # Limites
        if self.y < 0:
            self.y = 0
            self.velocidade = 0
        elif self.y > ALTURA - 150:
            self.y = ALTURA - 150
            return True
        
        # Atualiza retângulo
        self.rect = pygame.Rect(self.x - self.tamanho_atual//2, 
                              self.y - self.tamanho_atual//2,
                              self.tamanho_atual, self.tamanho_atual)
        
        # Atualiza power-ups
        self.atualizar_power_ups()
        
        # Atualiza partículas
        for p in self.efeito_particulas[:]:
            p['x'] += p['vel_x']
            p['y'] += p['vel_y']
            p['vida'] -= 1
            if p['vida'] <= 0:
                self.efeito_particulas.remove(p)
        
        return False
    
    def desenhar(self, tela):
        # Desenha partículas
        for p in self.efeito_particulas:
            alpha = p['vida'] * 10
            pygame.draw.circle(tela, p['cor'], 
                             (int(p['x']), int(p['y'])), p['tamanho'])
        
        # Escudo visual
        if self.escudo:
            for i in range(3):
                raio = self.tamanho_atual//2 + 5 + i * 3
                alpha = 100 - i * 30
                cor_escudo = (100, 255, 100)
                
                pygame.draw.circle(tela, (*cor_escudo[:3], alpha), 
                                 (int(self.x), int(self.y)), 
                                 raio, 3)
        
        # Pássaro
        if self.imagem_original:
            # Redimensiona imagem se necessário
            img_redimensionada = pygame.transform.scale(self.imagem_original, 
                                                       (self.tamanho_atual, self.tamanho_atual))
            img_rot = pygame.transform.rotate(img_redimensionada, self.angulo)
        else:
            # Fallback gráfico
            img_rot = pygame.Surface((self.tamanho_atual, self.tamanho_atual), pygame.SRCALPHA)
            pygame.draw.circle(img_rot, (255, 255, 0), 
                             (self.tamanho_atual//2, self.tamanho_atual//2), 
                             self.tamanho_atual//2 - 3)
            img_rot = pygame.transform.rotate(img_rot, self.angulo)
        
        rect_rot = img_rot.get_rect(center=(self.x, self.y))
        tela.blit(img_rot, rect_rot)
        
        # Efeito de brilho com power-up
        if self.efeito_brilho > 0:
            brilho = int(255 * self.efeito_brilho)
            cor_brilho = (
                min(255, self.cor_efeito[0] + brilho),
                min(255, self.cor_efeito[1] + brilho),
                min(255, self.cor_efeito[2] + brilho)
            )
            
            pygame.draw.circle(tela, (*cor_brilho[:3], 100), 
                             (int(self.x), int(self.y)), 
                             self.tamanho_atual//2 + 8)
    
    def get_rect(self):
        return self.rect
    
    def tem_power_up(self, tipo):
        return any(p.tipo == tipo for p in self.power_ups_ativos)

# ====== CANO COM IMAGEM ======

class Cano:
    def __init__(self, x, velocidade):
        self.x = x
        self.largura = img_cano.get_width() if img_cano else 70
        self.velocidade = velocidade
        
        # Altura aleatória
        self.altura_superior = random.randint(100, 350)
        self.altura_inferior = self.altura_superior + 150
        self.passou = False
        
        # Prepara as imagens dos canos
        self.preparar_canos()
    
    def preparar_canos(self):
        """Prepara as imagens dos canos com a imagem carregada"""
        altura_sup = self.altura_superior
        altura_inf = ALTURA - self.altura_inferior
        
        if img_cano:
            # Cano superior (vira a imagem)
            self.cano_superior = pygame.Surface((self.largura, altura_sup), pygame.SRCALPHA)
            # Corta parte da imagem
            parte_sup = img_cano.subsurface((0, 0, self.largura, min(altura_sup, img_cano.get_height())))
            parte_sup = pygame.transform.scale(parte_sup, (self.largura, altura_sup))
            parte_sup = pygame.transform.flip(parte_sup, False, True)
            self.cano_superior.blit(parte_sup, (0, 0))
            
            # Cano inferior
            self.cano_inferior = pygame.Surface((self.largura, altura_inf), pygame.SRCALPHA)
            parte_inf = img_cano.subsurface((0, 0, self.largura, min(altura_inf, img_cano.get_height())))
            parte_inf = pygame.transform.scale(parte_inf, (self.largura, altura_inf))
            self.cano_inferior.blit(parte_inf, (0, 0))
        else:
            # Fallback gráfico
            self.cano_superior = pygame.Surface((self.largura, altura_sup), pygame.SRCALPHA)
            pygame.draw.rect(self.cano_superior, (0, 180, 0), (0, 0, self.largura, altura_sup))
            pygame.draw.rect(self.cano_superior, (0, 150, 0), (0, altura_sup - 20, self.largura, 20))
            
            self.cano_inferior = pygame.Surface((self.largura, altura_inf), pygame.SRCALPHA)
            pygame.draw.rect(self.cano_inferior, (0, 180, 0), (0, 0, self.largura, altura_inf))
            pygame.draw.rect(self.cano_inferior, (0, 150, 0), (0, 0, self.largura, 20))
    
    def atualizar(self):
        self.x -= self.velocidade
        return self.x < -self.largura
    
    def desenhar(self, tela):
        if hasattr(self, 'cano_superior'):
            tela.blit(self.cano_superior, (self.x, 0))
            tela.blit(self.cano_inferior, (self.x, self.altura_inferior))
        else:
            # Fallback
            pygame.draw.rect(tela, (0, 180, 0), 
                           (self.x, 0, self.largura, self.altura_superior))
            pygame.draw.rect(tela, (0, 180, 0),
                           (self.x, self.altura_inferior, self.largura, ALTURA - self.altura_inferior))
    
    def colidiu(self, rect):
        rect_sup = pygame.Rect(self.x, 0, self.largura, self.altura_superior)
        rect_inf = pygame.Rect(self.x, self.altura_inferior, 
                              self.largura, ALTURA - self.altura_inferior)
        return rect.colliderect(rect_sup) or rect.colliderect(rect_inf)

# ====== BOTÃO ======

class Botao:
    def __init__(self, texto, x, y, largura, altura, cor_normal, cor_hover):
        self.texto = texto
        self.rect = pygame.Rect(x - largura/2, y - altura/2, largura, altura)
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover
        self.cor_atual = cor_normal
    
    def atualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.cor_atual = self.cor_hover
            for evento in eventos:
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    return True
        else:
            self.cor_atual = self.cor_normal
        return False
    
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor_atual, self.rect, border_radius=15)
        pygame.draw.rect(tela, (255, 255, 255), self.rect, 3, border_radius=15)
        texto_surf = fonte.render(self.texto, True, (255, 255, 255))
        tela.blit(texto_surf, (self.rect.centerx - texto_surf.get_width()//2, 
                              self.rect.centery - texto_surf.get_height()//2))

# ====== FUNÇÕES AUXILIARES ======

def criar_coletavel():
    """Cria um coletavel aleatório"""
    # Probabilidades diferentes para cada tipo
    pesos = [
        (TipoColetavel.MOEDA, 50),        # 50% de chance
        (TipoColetavel.VIDA, 5),          # 5% de chance
        (TipoColetavel.IMÃ, 10),          # 10% de chance
        (TipoColetavel.ESCUDO, 8),        # 8% de chance
        (TipoColetavel.VELOCIDADE, 9),    # 9% de chance
        (TipoColetavel.GRAVIDADE, 7),     # 7% de chance
        (TipoColetavel.PONTOS_DOBRO, 6),  # 6% de chance
        (TipoColetavel.TAMANHO, 5)        # 5% de chance
    ]
    
    # Escolhe aleatoriamente baseado nos pesos
    total = sum(peso for _, peso in pesos)
    r = random.uniform(0, total)
    acumulado = 0
    
    for tipo, peso in pesos:
        acumulado += peso
        if r <= acumulado:
            x = LARGURA + 50
            y = random.randint(100, ALTURA - 200)
            print(f"Criando coletável do tipo: {tipo} em ({x}, {y})")
            return Coletavel(x, y, tipo)
    
    # Fallback: moeda
    x = LARGURA + 50
    y = random.randint(100, ALTURA - 200)
    return Coletavel(x, y, TipoColetavel.MOEDA)

def converter_para_powerup(tipo_coletavel):
    """Converte tipo de coletavel para tipo de power-up"""
    mapeamento = {
        TipoColetavel.IMÃ: TipoPowerUp.IMÃ,
        TipoColetavel.VELOCIDADE: TipoPowerUp.VELOCIDADE,
        TipoColetavel.GRAVIDADE: TipoPowerUp.GRAVIDADE,
        TipoColetavel.PONTOS_DOBRO: TipoPowerUp.PONTOS_DOBRO,
        TipoColetavel.TAMANHO: TipoPowerUp.TAMANHO
    }
    return mapeamento.get(tipo_coletavel)

# ====== INICIALIZAÇÃO ======

passaro = Passaro()
canos = []
coletaveis = []
botao_jogar = Botao("INICIAR", LARGURA//2, ALTURA//2, 180, 50, 
                    (30, 100, 200), (50, 150, 255))
botao_sair = Botao("SAIR", LARGURA//2, ALTURA//2 + 70, 180, 50,
                   (200, 50, 50), (255, 80, 80))

estado = "menu"
pontos = 0
record = 0
tempo_cano = 0
tempo_coletavel = 0
chao_x = 0

print("=== Jogo Inicializado ===")
print("Pressione ESPAÇO ou clique para pular")
print("Colete os itens para ganhar vantagens!\n")

# ====== LOOP PRINCIPAL ======

executando = True
while executando:
    eventos = pygame.event.get()
    
    for evento in eventos:
        if evento.type == pygame.QUIT:
            executando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if estado == "jogando":
                    passaro.pular()
                elif estado == "menu":
                    estado = "jogando"
                    passaro = Passaro()
                    canos = []
                    coletaveis = []
                    pontos = 0
                    tempo_cano = 0
                    tempo_coletavel = 0
                    print("=== Novo Jogo Iniciado ===")
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if estado == "jogando":
                passaro.pular()
    
    # ====== ATUALIZAÇÕES ======
    
    if estado == "jogando":
        # Atualiza pássaro
        colidiu_chao = passaro.atualizar()
        
        # Cria canos
        tempo_cano += 1
        if tempo_cano >= 90:  # A cada ~1.5 segundos
            canos.append(Cano(LARGURA, passaro.velocidade_canos))
            tempo_cano = 0
        
        # Remove canos que saíram da tela
        canos = [c for c in canos if not c.atualizar()]
        
        # Cria coletáveis
        tempo_coletavel += 1
        if tempo_coletavel >= 100:  # A cada ~1.7 segundos
            coletaveis.append(criar_coletavel())
            tempo_coletavel = 0
        
        # Atualiza coletáveis
        ima_ativo = passaro.tem_power_up(TipoPowerUp.IMÃ)
        for coletavel in coletaveis[:]:
            if coletavel.atualizar(passaro.x, passaro.y, ima_ativo):
                coletaveis.remove(coletavel)
                continue
            
            # Verifica colisão com pássaro
            if coletavel.get_rect().colliderect(passaro.get_rect()):
                valor, tipo, duracao = coletavel.coletar()
                
                if tipo == TipoColetavel.MOEDA:
                    pontos += valor * passaro.multiplier_pontos
                    print(f"Moeda coletada! +{valor} pontos (Total: {pontos})")
                elif tipo == TipoColetavel.VIDA:
                    passaro.vidas += valor
                    print(f"Vida extra! Total de vidas: {passaro.vidas}")
                elif tipo == TipoColetavel.ESCUDO:
                    passaro.escudo = True
                    passaro.escudo_duracao = duracao
                    print("Escudo ativado!")
                else:
                    # Power-up
                    power_up = converter_para_powerup(tipo)
                    if power_up:
                        passaro.aplicar_power_up(power_up, duracao)
                
                coletaveis.remove(coletavel)
        
        # Verifica colisões com canos
        game_over = False
        for cano in canos:
            if cano.colidiu(passaro.get_rect()):
                if passaro.escudo:
                    passaro.escudo = False
                    passaro.escudo_duracao = 0
                    print("Escudo quebrado ao colidir!")
                else:
                    game_over = True
                break
            
            # Pontuação ao passar pelo cano
            if not cano.passou and cano.x + cano.largura < passaro.x:
                cano.passou = True
                pontos += 1 * passaro.multiplier_pontos
                print(f"Passou pelo cano! +{1 * passaro.multiplier_pontos} pontos")
        
        if game_over or colidiu_chao:
            passaro.vidas -= 1
            if passaro.vidas > 0:
                print(f"Colisão! Vidas restantes: {passaro.vidas}")
                # Reseta posição
                passaro.x = 100
                passaro.y = ALTURA // 2
                passaro.velocidade = 0
                passaro.angulo = 0
            else:
                print("Game Over!")
                estado = "menu"
        
        # Atualiza recorde
        if pontos > record:
            record = pontos
        
        # Anima chão
        chao_x -= 5
        if chao_x <= -LARGURA:
            chao_x = 0
            
    elif estado == "menu":
        if botao_jogar.atualizar(eventos):
            estado = "jogando"
            passaro = Passaro()
            canos = []
            coletaveis = []
            pontos = 0
            tempo_cano = 0
            tempo_coletavel = 0
            print("=== Novo Jogo Iniciado ===")
        
        if botao_sair.atualizar(eventos):
            executando = False
    
    # ====== DESENHO ======
    
    # Fundo
    tela.blit(img_fundo, (0, 0))
    
    if estado == "jogando":
        # Desenha canos
        for cano in canos:
            cano.desenhar(tela)
        
        # Desenha coletáveis
        for coletavel in coletaveis:
            coletavel.desenhar(tela)
        
        # Desenha pássaro
        passaro.desenhar(tela)
        
        # ====== HUD (Interface) ======
        
        # Pontuação
        texto_pontos = fonte_grande.render(str(pontos), True, (255, 255, 255))
        sombra = fonte_grande.render(str(pontos), True, (0, 0, 0))
        tela.blit(sombra, (LARGURA//2 - texto_pontos.get_width()//2 + 2, 52))
        tela.blit(texto_pontos, (LARGURA//2 - texto_pontos.get_width()//2, 50))
        
        # Vidas
        for i in range(passaro.vidas):
            x = 20 + i * 35
            pygame.draw.polygon(tela, (255, 50, 50), [
                (x, 20), (x + 15, 30), (x + 30, 20),
                (x + 30, 45), (x + 15, 55), (x, 45)
            ])
        
        # Multiplicador de pontos
        if passaro.multiplier_pontos > 1:
            texto_mult = fonte_pequena.render(f"x{passaro.multiplier_pontos}", True, (255, 255, 100))
            tela.blit(texto_mult, (LARGURA - 50, 25))
        
        # Power-ups ativos (lado direito)
        y_powerup = 80
        for power_up in passaro.power_ups_ativos:
            porcentagem = power_up.get_porcentagem()
            
            # Barra de progresso
            largura_barra = 80
            pygame.draw.rect(tela, (50, 50, 50), (LARGURA - 90, y_powerup, largura_barra, 8))
            pygame.draw.rect(tela, (100, 200, 100), 
                           (LARGURA - 90, y_powerup, int(largura_barra * porcentagem), 8))
            
            # Nome do power-up
            nomes = {
                TipoPowerUp.VELOCIDADE: "VEL",
                TipoPowerUp.GRAVIDADE: "GRA",
                TipoPowerUp.PONTOS_DOBRO: "2X",
                TipoPowerUp.TAMANHO: "TAM",
                TipoPowerUp.IMÃ: "IMÃ"
            }
            
            texto = fonte_pequena.render(nomes.get(power_up.tipo, "???"), True, (255, 255, 255))
            tela.blit(texto, (LARGURA - 100 - texto.get_width(), y_powerup - 2))
            
            y_powerup += 15
    
    elif estado == "menu":
        # Título
        titulo = fonte_grande.render("FLAPPY BIRD+", True, (255, 255, 100))
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 100))
        
        # Instruções sobre coletáveis
        y_inst = 180
        instrucoes = [
            ("Moedas ($): +10 pontos", (255, 215, 0)),
            ("Vidas (❤): +1 vida", (255, 50, 50)),
            ("Velocidade (⚡): Mais rápido", (255, 165, 0)),
            ("Gravidade (🌍): Flutua mais", (200, 100, 255)),
            ("2X Pontos (2X): Dobra pontos", (255, 255, 100)),
            ("Tamanho (⬡): Fica menor", (100, 255, 255)),
            ("Ímã (🧲): Atrai moedas", (100, 200, 255)),
            ("Escudo (🛡️): Protege 1x", (100, 255, 100))
        ]
        
        for texto, cor in instrucoes:
            texto_surf = fonte_pequena.render(texto, True, cor)
            tela.blit(texto_surf, (LARGURA//2 - texto_surf.get_width()//2, y_inst))
            y_inst += 25
        
        botao_jogar.desenhar(tela)
        botao_sair.desenhar(tela)
        
        if record > 0:
            rec_text = fonte.render(f"Recorde: {record}", True, (255, 255, 255))
            tela.blit(rec_text, (LARGURA//2 - rec_text.get_width()//2, ALTURA - 120))
        
        inst_text = fonte.render("ESPACO ou CLIQUE = Pular", True, (200, 200, 255))
        tela.blit(inst_text, (LARGURA//2 - inst_text.get_width()//2, ALTURA - 80))
    
    # Chão
    tela.blit(img_chao, (chao_x, ALTURA - 100))
    tela.blit(img_chao, (chao_x + LARGURA, ALTURA - 100))
    
    # Linha do horizonte
    pygame.draw.line(tela, (100, 100, 100), (0, ALTURA - 100), 
                    (LARGURA, ALTURA - 100), 2)
    
    pygame.display.flip()
    clock.tick(FPS)

print("=== Jogo Encerrado ===")
pygame.quit()
sys.exit()