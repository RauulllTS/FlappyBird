import pygame
import random
import os

class Cano:
    def __init__(self, tela, x):
        self.tela = tela
        self.x = x
        self.largura = 70
        self.velocidade = 3
        self.distancia = 150  # Distância entre os canos
        self.passou = False
        
        # Posições aleatórias
        self.altura_superior = random.randint(100, 350)
        self.altura_inferior = self.altura_superior + self.distancia
        
        # Tenta carregar imagem do cano
        self.imagem_original = None
        try:
            caminhos = [
                'assets/pipe.png',
                './assets/pipe.png',
                'pipe.png',
                'assets/cano.png',
                './assets/cano.png',
                'cano.png'
            ]
            
            for caminho in caminhos:
                if os.path.exists(caminho):
                    self.imagem_original = pygame.image.load(caminho).convert_alpha()
                    print(f"✓ Imagem do cano carregada: {caminho}")
                    
                    # Ajusta tamanho da imagem
                    largura_original = self.imagem_original.get_width()
                    if largura_original != self.largura:
                        self.imagem_original = pygame.transform.scale(
                            self.imagem_original, 
                            (self.largura, 400)  # Altura alta para recortar
                        )
                    break
                    
        except Exception as e:
            print(f"✗ Erro ao carregar imagem do cano: {e}")
            self.imagem_original = None
        
        # Cores para fallback
        self.cor_cano = (0, 180, 0)
        self.cor_borda = (0, 150, 0)
    
    def atualizar(self):
        self.x -= self.velocidade
        return self.x < -self.largura
    
    def desenhar(self):
        if self.imagem_original:
            # Cano superior (virado para baixo)
            # Pega apenas a parte necessária da imagem
            altura_cano_superior = self.altura_superior
            cano_superior = pygame.transform.flip(self.imagem_original, False, True)
            cano_superior = pygame.transform.scale(
                cano_superior, 
                (self.largura, altura_cano_superior)
            )
            self.tela.blit(cano_superior, (self.x, 0))
            
            # Cano inferior
            altura_cano_inferior = 600 - self.altura_inferior
            cano_inferior = pygame.transform.scale(
                self.imagem_original,
                (self.largura, altura_cano_inferior)
            )
            self.tela.blit(cano_inferior, (self.x, self.altura_inferior))
            
            # Desenha bordas/efeitos
            pygame.draw.rect(self.tela, self.cor_borda,
                           (self.x, self.altura_superior - 5, self.largura, 5))
            pygame.draw.rect(self.tela, self.cor_borda,
                           (self.x, self.altura_inferior, self.largura, 5))
        else:
            # Fallback gráfico
            # Cano superior
            pygame.draw.rect(self.tela, self.cor_cano,
                           (self.x, 0, self.largura, self.altura_superior))
            pygame.draw.rect(self.tela, self.cor_borda,
                           (self.x, self.altura_superior - 20, self.largura, 20))
            
            # Cano inferior
            pygame.draw.rect(self.tela, self.cor_cano,
                           (self.x, self.altura_inferior, self.largura, 600))
            pygame.draw.rect(self.tela, self.cor_borda,
                           (self.x, self.altura_inferior, self.largura, 20))
    
    def colidiu(self, jogador_rect):
        rect_superior = pygame.Rect(self.x, 0, self.largura, self.altura_superior)
        rect_inferior = pygame.Rect(self.x, self.altura_inferior,
                                   self.largura, 600 - self.altura_inferior)
        return jogador_rect.colliderect(rect_superior) or jogador_rect.colliderect(rect_inferior)