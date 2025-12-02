import pygame

class Texto:
    def __init__(self, texto, tamanho, cor, x, y):
        self.fonte = pygame.font.SysFont(None, tamanho)
        self.texto = texto
        self.cor = cor
        self.x = x
        self.y = y
        self.renderizar()
    
    def renderizar(self):
        self.surface = self.fonte.render(self.texto, True, self.cor)
        self.rect = self.surface.get_rect(center=(self.x, self.y))
    
    def desenhar(self, tela):
        tela.blit(self.surface, self.rect)

class Botao:
    def __init__(self, texto, x, y, largura, altura, cor_normal, cor_hover):
        self.texto = Texto(texto, 32, (255, 255, 255), x, y)
        self.rect = pygame.Rect(x - largura/2, y - altura/2, largura, altura)
        self.cor_normal = cor_normal  # Cor normal
        self.cor_hover = cor_hover    # Cor quando mouse está em cima
        self.cor_atual = cor_normal   # Começa com cor normal
        self.clicado = False
    
    def atualizar(self, eventos):
        mouse_pos = pygame.mouse.get_pos()
        
        # Verifica se o mouse está sobre o botão
        if self.rect.collidepoint(mouse_pos):
            # Muda para cor de hover
            self.cor_atual = self.cor_hover  # CORRIGIDO: usa self.cor_hover
            
            # Verifica se houve clique
            for evento in eventos:
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.clicado = True
                    return True
        else:
            # Volta para cor normal
            self.cor_atual = self.cor_normal  # CORRIGIDO: usa self.cor_normal
        
        # Se chegou aqui, não foi clicado neste frame
        self.clicado = False
        return False
    
    def desenhar(self, tela):
        # Desenha o retângulo do botão
        pygame.draw.rect(tela, self.cor_atual, self.rect, border_radius=10)
        pygame.draw.rect(tela, (0, 0, 0), self.rect, 3, border_radius=10)  # Borda
        
        # Desenha o texto
        self.texto.desenhar(tela)