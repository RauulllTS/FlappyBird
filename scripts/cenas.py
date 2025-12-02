import pygame
import random
from scripts.jogador import Jogador
from scripts.cano import Cano
from scripts.interfaces import Texto, Botao

class Partida:
    def __init__(self, tela):
        self.tela = tela
        self.jogador = Jogador(tela)
        self.canhos = []
        self.estado = 'partida'
        self.tempo_canos = 0
        self.intervalo_canos = 90
        self.pontos = 0
        self.fonte = pygame.font.SysFont(None, 48)
        
        # Carrega fonte para pontuação
        try:
            self.fonte_pontos = pygame.font.Font(None, 48)
        except:
            self.fonte_pontos = pygame.font.SysFont(None, 48)
    
    def processar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                self.jogador.pular()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.jogador.pular()
    
    def atualizar(self):
        # Atualiza jogador
        self.jogador.atualizar()
        
        # Atualiza canos
        self.tempo_canos += 1
        if self.tempo_canos >= self.intervalo_canos:
            self.canhos.append(Cano(self.tela, 400))
            self.tempo_canos = 0
        
        # Remove canos que saíram da tela
        self.canhos = [cano for cano in self.canhos if not cano.atualizar()]
        
        # Verifica colisões e pontos
        for cano in self.canhos:
            if cano.colidiu(self.jogador.get_rect()):
                return 'menu'
            
            # Pontuação
            if not cano.passou and cano.x + cano.largura < self.jogador.x:
                cano.passou = True
                self.pontos += 1
        
        # Verifica se bateu no chão
        if self.jogador.y >= 500:
            return 'menu'
        
        return self.estado
    
    def desenhar(self):
        # Desenha canos
        for cano in self.canhos:
            cano.desenhar()
        
        # Desenha jogador
        self.jogador.desenhar()
        
        # Desenha pontuação
        texto_pontos = self.fonte_pontos.render(f"{self.pontos}", True, (255, 255, 255))
        self.tela.blit(texto_pontos, (LARGURA // 2 - texto_pontos.get_width() // 2, 50))

class Menu:
    def __init__(self, tela):
        self.tela = tela
        self.estado = 'menu'
        
        # Título
        self.titulo = Texto("FLAPPY BIRD", 64, (255, 255, 0), 200, 150)
        
        # Botões
        self.botao_jogar = Botao("JOGAR", 200, 300, 200, 60, 
                                (0, 100, 0), (0, 200, 0))
        self.botao_sair = Botao("SAIR", 200, 380, 200, 60,
                               (200, 0, 0), (255, 0, 0))
        
        # Eventos
        self.eventos_frame = []
        
        # Animação
        self.bird_y = 250
        self.bird_dir = 1
        
        # Nuvens
        self.nuvens = []
        for _ in range(5):
            self.nuvens.append({
                'x': random.randint(0, 400),
                'y': random.randint(50, 200),
                'vel': random.uniform(0.5, 1.5)
            })
    
    def processar_evento(self, evento):
        self.eventos_frame.append(evento)
    
    def atualizar(self):
        # Animação do pássaro no menu
        self.bird_y += 0.3 * self.bird_dir
        if self.bird_y > 260 or self.bird_y < 240:
            self.bird_dir *= -1
        
        # Nuvens
        for nuvem in self.nuvens:
            nuvem['x'] -= nuvem['vel']
            if nuvem['x'] < -100:
                nuvem['x'] = 500
                nuvem['y'] = random.randint(50, 200)
        
        # Botões
        if self.botao_jogar.atualizar(self.eventos_frame):
            self.eventos_frame = []
            return 'partida'
        
        if self.botao_sair.atualizar(self.eventos_frame):
            pygame.quit()
            exit()
        
        self.eventos_frame = []
        return self.estado
    
    def desenhar(self):
        # Nuvens
        for nuvem in self.nuvens:
            pygame.draw.ellipse(self.tela, (255, 255, 255),
                               (nuvem['x'], nuvem['y'], 80, 40))
            pygame.draw.ellipse(self.tela, (255, 255, 255),
                               (nuvem['x'] + 20, nuvem['y'] - 20, 60, 40))
        
        # Pássaro decorativo
        pygame.draw.circle(self.tela, (255, 255, 0), (200, int(self.bird_y)), 20)
        pygame.draw.circle(self.tela, (255, 165, 0), (215, int(self.bird_y) - 5), 8)
        
        # Título
        self.titulo.desenhar(self.tela)
        
        # Botões
        self.botao_jogar.desenhar(self.tela)
        self.botao_sair.desenhar(self.tela)
        
        # Instruções
        texto_instrucao = Texto("Pressione ESPAÇO ou CLIQUE para pular", 
                               24, (255, 255, 255), 200, 480)
        texto_instrucao.desenhar(self.tela)
        
        # Créditos
        texto_creditos = Texto("Desenvolvido com Pygame", 
                              20, (200, 200, 200), 200, 520)
        texto_creditos.desenhar(self.tela)