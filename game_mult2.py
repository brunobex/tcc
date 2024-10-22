import matplotlib.pyplot as plt
import random
import time
import threading

# Classe do jogo da velha
class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # Tabuleiro inicializado com espaços vazios
        self.current_winner = None  # Nenhum vencedor inicialmente

    def print_board(self):
        # Imprime o tabuleiro no console
        for row in [self.board[i * 3:(i + 1) * 3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    def available_moves(self):
        # Retorna uma lista de movimentos disponíveis
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def empty_squares(self):
        # Verifica se há quadrados vazios no tabuleiro
        return ' ' in self.board

    def num_empty_squares(self):
        # Retorna o número de quadrados vazios
        return self.board.count(' ')

    def make_move(self, square, letter):
        # Faz um movimento no tabuleiro
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter  # Atualiza o vencedor se houver
            return True
        return False

    def winner(self, square, letter):
        # Verifica se há um vencedor
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([s == letter for s in row]):
            return True

        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([s == letter for s in column]):
            return True

        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([s == letter for s in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([s == letter for s in diagonal2]):
                return True

        return False

# Classe para jogadores IA
class RandomComputerPlayer:
    def __init__(self, letter):
        self.letter = letter  # Define a letra do jogador (X ou O)

    def get_move(self, game):
        # Retorna um movimento aleatório disponível
        square = random.choice(game.available_moves())
        return square

# Função para desenhar o tabuleiro
def draw_board(ax, board):
    ax.clear()  # Limpa o eixo
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_xticks([])
    ax.set_yticks([])

    # Desenha linhas do tabuleiro
    for i in range(1, 3):
        ax.plot([0, 3], [i, i], color='black')
        ax.plot([i, i], [0, 3], color='black')

    # Desenha X e O no tabuleiro
    for i, spot in enumerate(board):
        row, col = divmod(i, 3)
        if spot == 'X':
            ax.text(col + 0.5, 2 - row + 0.5, 'X', ha='center', va='center', fontsize=32, color='red')
        elif spot == 'O':
            ax.text(col + 0.5, 2 - row + 0.5, 'O', ha='center', va='center', fontsize=32, color='blue')

# Função para jogar um jogo
def play_game(game, x_player, o_player, ax):
    while game.empty_squares():
        if game.num_empty_squares() % 2 == 0:
            square = x_player.get_move(game)
            if game.make_move(square, 'X'):
                draw_board(ax, game.board)
                plt.pause(0.5)  # Pausa para mostrar a jogada
                if game.current_winner:
                    return 'X'
        else:
            square = o_player.get_move(game)
            if game.make_move(square, 'O'):
                draw_board(ax, game.board)
                plt.pause(0.5)  # Pausa para mostrar a jogada
                if game.current_winner:
                    return 'O'
    return 'Tie'

# Função para rodar múltiplos jogos simultaneamente
def run_multiple_games(n):
    results = {'X': 0, 'O': 0, 'Tie': 0}
    fig, axes = plt.subplots(n // 2, 2, figsize=(10, n * 2.5))
    axes = axes.flatten()

    def run_game(i):
        game = TicTacToe()
        x_player = RandomComputerPlayer('X')
        o_player = RandomComputerPlayer('O')
        result = play_game(game, x_player, o_player, axes[i])
        results[result] += 1

    threads = []
    for i in range(n):
        t = threading.Thread(target=run_game, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    plt.tight_layout()
    plt.show()
    print(f'Results after {n} games: {results}')

# Rodar 4 jogos simultâneos como exemplo
run_multiple_games(4)
