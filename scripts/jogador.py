import pygame
import os

class Jogador:
    def __init__(self, tela):
        self.tela = tela
        
        # Tenta carregar a imagem do pássaro
        try:
            # Tenta diferentes caminhos
            caminhos = [
                'assets/bird.png',
                './assets/bird.png',
                'bird.png'
            ]
            
            for caminho in caminhos:
                if os.path.exists(caminho):
                    self.imagem = pygame.image.load(caminho).convert_alpha()
                    print(f"Imagem carregada: {caminho}")
                    break
            else:
                # Se não encontrar, cria um pássaro com gráficos
                raise FileNotFoundError
                
        except:
            # Cria uma superfície para o pássaro (fallback)
            print("Imagem não encontrada. Criando pássaro com gráficos...")
            self.imagem = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Corpo amarelo
            pygame.draw.circle(self.imagem, (255, 255, 0), (25, 25), 20)
            # Olho preto
            pygame.draw.circle(self.imagem, (0, 0, 0), (35, 20), 5)
            # Bico laranja
            pygame.draw.polygon(self.imagem, (255, 165, 0), [
                (45, 25), (55, 20), (55, 30)
            ])
            # Asa
            pygame.draw.ellipse(self.imagem, (255, 200, 0), (10, 30, 20, 10))
        
        # Redimensiona se necessário
        self.imagem = pygame.transform.scale(self.imagem, (40, 40))
        
        # Posição inicial
        self.x = 100
        self.y = 300
        self.largura = 40
        self.altura = 40
        
        # Física do jogador
        self.velocidade = 0
        self.gravidade = 0.5
        self.pulo = -10
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        
        # Ângulo para rotação
        self.angulo = 0
    
    def pular(self):
        self.velocidade = self.pulo
        self.angulo = 15  # Inclina para cima ao pular
    
    def atualizar(self):
        # Aplica gravidade
        self.velocidade += self.gravidade
        self.y += self.velocidade
        
        # Rotação baseada na velocidade
        if self.velocidade > 0:  # Caindo
            self.angulo = max(-90, self.angulo - 2)
        else:  # Subindo
            self.angulo = min(15, self.angulo + 5)
        
        # Limita a posição para não sair da tela
        if self.y < 0:
            self.y = 0
            self.velocidade = 0
        elif self.y > 500:  # Limite inferior (considerando chão)
            self.y = 500
            self.velocidade = 0
        
        # Atualiza o retângulo de colisão
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
    
    def desenhar(self):
        # Rotaciona a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        rect_rotacionado = imagem_rotacionada.get_rect(center=(self.x + self.largura//2, self.y + self.altura//2))
        
        # Desenha o pássaro
        self.tela.blit(imagem_rotacionada, rect_rotacionado)
    
    def get_rect(self):
        return self.rect