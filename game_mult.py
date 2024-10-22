import pygame
import random
import time

# Inicialização do Pygame
pygame.init()

# Configurações da tela
GRID_SIZE = 3  # Definindo uma grid 3x3 para 9 jogos simultâneos
WIDTH, HEIGHT = 900, 900
LINE_WIDTH = 15
WIN_LINE_WIDTH = 15
SQUARE_SIZE = WIDTH // (3 * GRID_SIZE)
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


def draw_lines():
    for row in range(GRID_SIZE * 3):
        pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (row * SQUARE_SIZE, 0), (row * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures(boards):
    for idx, board in enumerate(boards):
        for row in range(3):
            for col in range(3):
                cell_value = board[row][col]
                if cell_value != 0:
                    offset_x = (idx % GRID_SIZE) * 3 * SQUARE_SIZE
                    offset_y = (idx // GRID_SIZE) * 3 * SQUARE_SIZE
                    center = (col * SQUARE_SIZE + SQUARE_SIZE // 2 + offset_x, row * SQUARE_SIZE + SQUARE_SIZE // 2 + offset_y)
                    if cell_value == 1:
                        pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)
                    elif cell_value == 2:
                        pygame.draw.line(screen, CROSS_COLOR, (center[0] - SPACE, center[1] - SPACE), (center[0] + SPACE, center[1] + SPACE), CROSS_WIDTH)
                        pygame.draw.line(screen, CROSS_COLOR, (center[0] - SPACE, center[1] + SPACE), (center[0] + SPACE, center[1] - SPACE), CROSS_WIDTH)

def init_board():
    return [[0 for _ in range(3)] for _ in range(3)]

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

def check_draw(board):
    return all(cell != 0 for row in board for cell in row)

def ai_move(board, player):
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    move = random.choice(empty_cells)
    board[move[0]][move[1]] = player
    return move

def buggy_ai_move(board, player):
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    move = random.choice(empty_cells)
    board[move[0]][move[1]] = player
    return move


def main():
    num_games = GRID_SIZE * GRID_SIZE
    boards = [init_board() for _ in range(num_games)]
    players = [1] * num_games
    game_over = [False] * num_games

    draw_lines()
    
    while not all(game_over):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        for i in range(num_games):
            if not game_over[i]:
                if players[i] == 1:
                    move = ai_move(boards[i], players[i])
                else:
                    move = buggy_ai_move(boards[i], players[i])

                if check_win(boards[i], players[i]):
                    game_over[i] = True
                    print(f'Game {i + 1}: Player {players[i]} wins!')
                
                if check_draw(boards[i]):
                    game_over[i] = True
                    print(f'Game {i + 1}: Draw!')

                players[i] = 2 if players[i] == 1 else 1

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures(boards)
        pygame.display.update()
        time.sleep(0.5)

main()


