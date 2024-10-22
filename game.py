#pip install pygame

import pygame
import random
import time

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 15
WIN_LINE_WIDTH = 15
SQUARE_SIZE = WIDTH // 3
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Cores
RED = (255, 0, 0)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# Tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jogo da Velha - IA vs IA')
screen.fill(BG_COLOR)

# Funções de Desenho
def draw_lines():
    # Linhas horizontais
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    # Linhas verticais
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures(board):
    for row in range(3):
        for col in range(3):
            if board[row][col] == 1:
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 2:
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)

# Inicializa o tabuleiro
def init_board():
    return [[0 for _ in range(3)] for _ in range(3)]

# Verifica vitória
def check_win(board, player):
    for row in range(3):
        if board[row] == [player] * 3:
            return True
    for col in range(3):
        if [board[row][col] for row in range(3)] == [player] * 3:
            return True
    if [board[i][i] for i in range(3)] == [player] * 3:
        return True
    if [board[i][2-i] for i in range(3)] == [player] * 3:
        return True
    return False

# Verifica empate
def check_draw(board):
    return all(cell != 0 for row in board for cell in row)

# IA Simples (Joga aleatoriamente)
def ai_move(board, player):
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    move = random.choice(empty_cells)
    board[move[0]][move[1]] = player
    return move

# IA com bug proposital (não verifica vitórias)
def buggy_ai_move(board, player):
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    move = random.choice(empty_cells)
    board[move[0]][move[1]] = player
    return move

# Exemplo de bug: IA não verifica vitória adversária
def buggy_check_win(board, player):
    for row in range(3):
        if board[row] == [player] * 3:
            return True
    for col in range(3):
        if [board[row][col] for row in range(3)] == [player] * 3:
            return True
    if [board[i][i] for i in range(3)] == [player] * 3:
        return True
    # Bug proposital: Não verifica a segunda diagonal
    # if [board[i][2-i] for i in range(3)] == [player] * 3:
    #     return True
    return False

# Função principal para rodar o jogo
def main():
    board = init_board()
    draw_lines()
    
    player = 1
    game_over = False
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if player == 1:
            move = ai_move(board, player)
        else:
            move = buggy_ai_move(board, player)
        
        draw_figures(board)
        pygame.display.update()

        if check_win(board, player):
            game_over = True
            print(f'Player {player} wins!')
        
        if check_draw(board):
            game_over = True
            print('Draw!')

        player = 2 if player == 1 else 1
        time.sleep(1)  # Pausa para visualizar a jogada

main()
