import pygame
import sys
import math

# ──────────────────────────────────────────────
#  CONSTANTES
# ──────────────────────────────────────────────
WIDTH, HEIGHT = 540, 660
ROWS, COLS = 3, 3
CELL = WIDTH // COLS

# Paleta de colores
BG        = (18,  18,  30)
LINE_CLR  = (50,  50,  80)
X_CLR     = (80,  160, 255)   # azul
O_CLR     = (255,  80,  80)   # rojo
WIN_CLR   = (50,  220, 140)   # verde
TEXT_CLR  = (220, 220, 240)
DIM_CLR   = (100, 100, 130)
BTN_CLR   = (40,  40,  65)
BTN_HOV   = (60,  60,  95)

X = "X"
O = "O"
E = None

# ──────────────────────────────────────────────
#  LÓGICA DEL JUEGO  (métodos requeridos)
# ──────────────────────────────────────────────

def player(board):
    """Devuelve a quién le toca mover: X o O."""
    xs = sum(1 for c in board if c == X)
    os = sum(1 for c in board if c == O)
    return X if xs <= os else O


def actions(board):
    """Devuelve el conjunto de movimientos válidos (índices vacíos)."""
    return [i for i, c in enumerate(board) if c == E]


def result(board, action):
    """Retorna el tablero resultante de aplicar 'action' al estado 'board'."""
    new_board = board[:]
    new_board[action] = player(board)
    return new_board


def terminal(board):
    """Retorna True si el juego ha terminado."""
    return _winner(board) is not None or len(actions(board)) == 0


def utility(board):
    """Retorna +1 si gana X, -1 si gana O, 0 si empate."""
    w = _winner(board)
    if w == X:
        return 1
    if w == O:
        return -1
    return 0


# ──────────────────────────────────────────────
#  MINIMAX  con poda Alpha-Beta
# ──────────────────────────────────────────────

def minimax(board, alpha, beta, is_maximizing):

    if terminal(board):          # caso base
        return utility(board)

    moves = actions(board)

    if is_maximizing:            # turno de X → maximiza
        best = -math.inf
        for m in moves:
            score = minimax(result(board, m), alpha, beta, False)
            best  = max(best, score)
            alpha = max(alpha, best)
            if alpha >= beta:    # ✂ poda beta
                break
        return best

    else:                        # turno de O → minimiza
        best = math.inf
        for m in moves:
            score = minimax(result(board, m), alpha, beta, True)
            best  = min(best, score)
            beta  = min(beta, best)
            if alpha >= beta:    # ✂ poda alpha
                break
        return best


def best_move(board, difficulty):
    
    import random
    moves = actions(board)
    if not moves:
        return None

    if difficulty == "easy":
        return random.choice(moves)

    if difficulty == "medium" and random.random() < 0.4:
        return random.choice(moves)

    # HARD → Minimax completo
    best_score = math.inf
    best_act   = moves[0]
    for m in moves:
        score = minimax(result(board, m), -math.inf, math.inf, True)
        if score < best_score:
            best_score = score
            best_act   = m
    return best_act


# funciones de ayuda
WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def _winner(board):
    for a, b, c in WINS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def winning_line(board):
    for a, b, c in WINS:
        if board[a] and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None

def cell_center(idx):
    r, c = divmod(idx, 3)
    return (c * CELL + CELL // 2, r * CELL + CELL // 2)


# dibujos

def draw_grid(surface):
    for i in range(1, 3):
        pygame.draw.line(surface, LINE_CLR, (i * CELL, 0), (i * CELL, WIDTH), 3)
        pygame.draw.line(surface, LINE_CLR, (0, i * CELL), (WIDTH, i * CELL), 3)


def draw_x(surface, cx, cy, size=54):
    offset = size // 2
    pygame.draw.line(surface, X_CLR, (cx-offset, cy-offset), (cx+offset, cy+offset), 8)
    pygame.draw.line(surface, X_CLR, (cx+offset, cy-offset), (cx-offset, cy+offset), 8)


def draw_o(surface, cx, cy, size=54):
    pygame.draw.circle(surface, O_CLR, (cx, cy), size // 2, 7)


def draw_board(surface, board):
    for i, cell in enumerate(board):
        cx, cy = cell_center(i)
        if cell == X:
            draw_x(surface, cx, cy)
        elif cell == O:
            draw_o(surface, cx, cy)


def draw_win_line(surface, line):
    if line is None:
        return
    a, _, c = line
    x1, y1 = cell_center(a)
    x2, y2 = cell_center(c)
    pygame.draw.line(surface, WIN_CLR, (x1, y1), (x2, y2), 6)


def draw_ui(surface, font_big, font_sm, status_msg, score, difficulty, hover_btn):
    """Dibuja el panel inferior con estado, puntaje y botones."""
    panel_y = WIDTH         # 540
    panel_h = HEIGHT - WIDTH  # 120

    # fondo panel
    pygame.draw.rect(surface, (12, 12, 22), (0, panel_y, WIDTH, panel_h))
    pygame.draw.line(surface, LINE_CLR, (0, panel_y), (WIDTH, panel_y), 2)

    # mensaje de estado
    msg_surf = font_big.render(status_msg, True, TEXT_CLR)
    surface.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, panel_y + 10))

    # puntaje
    score_txt = f"Tú {score['human']}  —  IA {score['ai']}  —  Empate {score['draw']}"
    sc_surf = font_sm.render(score_txt, True, DIM_CLR)
    surface.blit(sc_surf, (WIDTH // 2 - sc_surf.get_width() // 2, panel_y + 46))

    # botones
    buttons = {}
    diffs = ["easy", "medium", "hard"]
    labels = {"easy": "Fácil", "medium": "Media", "hard": "Difícil"}
    bw, bh = 100, 30
    total = len(diffs) * bw + (len(diffs)-1) * 10
    bx_start = (WIDTH - total) // 2
    by = panel_y + 80

    for j, d in enumerate(diffs):
        bx = bx_start + j * (bw + 10)
        rect = pygame.Rect(bx, by, bw, bh)
        is_active = (d == difficulty)
        is_hover  = (hover_btn == d)
        color = WIN_CLR if is_active else (BTN_HOV if is_hover else BTN_CLR)
        pygame.draw.rect(surface, color, rect, border_radius=6)
        txt_clr = (20, 20, 30) if is_active else TEXT_CLR
        lbl = font_sm.render(labels[d], True, txt_clr)
        surface.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by + bh//2 - lbl.get_height()//2))
        buttons[d] = rect

    # botón reiniciar
    reset_rect = pygame.Rect(WIDTH - 110, panel_y + 80, 100, 30)
    r_color = BTN_HOV if hover_btn == "reset" else BTN_CLR
    pygame.draw.rect(surface, r_color, reset_rect, border_radius=6)
    r_lbl = font_sm.render("↺ Nueva", True, TEXT_CLR)
    surface.blit(r_lbl, (reset_rect.x + 50 - r_lbl.get_width()//2,
                          reset_rect.y + 15 - r_lbl.get_height()//2))
    buttons["reset"] = reset_rect

    return buttons


# ──────────────────────────────────────────────
#  BUCLE PRINCIPAL
# ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tres en Raya — Minimax IA")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("segoeui", 22, bold=False)
    font_sm  = pygame.font.SysFont("segoeui", 16)

    board      = [E] * 9
    difficulty = "hard"
    game_over  = False
    player_turn= True        # True = humano (X), False = IA (O)
    status_msg = "Tu turno"
    win_line   = None
    ai_delay   = 0           # frames de espera antes de que la IA mueva
    score      = {"human": 0, "ai": 0, "draw": 0}
    hover_btn  = None
    buttons    = {}

    def reset():
        nonlocal board, game_over, player_turn, status_msg, win_line, ai_delay
        board       = [E] * 9
        game_over   = False
        player_turn = True
        status_msg  = "Tu turno"
        win_line    = None
        ai_delay    = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # detectar hover sobre botones del panel
        hover_btn = None
        for name, rect in buttons.items():
            if rect.collidepoint(mouse_pos):
                hover_btn = name
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # clic en botones del panel
                for name, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        if name == "reset":
                            reset()
                        elif name in ("easy", "medium", "hard"):
                            difficulty = name
                            reset()

                # clic en tablero
                if not game_over and player_turn and my < WIDTH:
                    col = mx // CELL
                    row = my // CELL
                    idx = row * 3 + col
                    if board[idx] == E:
                        board[idx] = X
                        player_turn = False
                        status_msg  = "IA pensando…"

                        # verificar fin
                        w = _winner(board)
                        if w == X:
                            status_msg = "¡Ganaste! 🎉"
                            win_line   = winning_line(board)
                            game_over  = True
                            score["human"] += 1
                        elif not actions(board):
                            status_msg = "Empate 🤝"
                            game_over  = True
                            score["draw"] += 1
                        else:
                            ai_delay = 30   # ~0.5 s a 60 fps

        # turno de la IA con pequeño retraso visual
        if not game_over and not player_turn and ai_delay > 0:
            ai_delay -= 1
            if ai_delay == 0:
                move = best_move(board, difficulty)
                if move is not None:
                    board[move] = O
                w = _winner(board)
                if w == O:
                    status_msg  = "La IA gana 🤖"
                    win_line    = winning_line(board)
                    game_over   = True
                    score["ai"] += 1
                elif not actions(board):
                    status_msg = "Empate 🤝"
                    game_over  = True
                    score["draw"] += 1
                else:
                    player_turn = True
                    status_msg  = "Tu turno"

        # ── DIBUJO ──────────────────────────────
        screen.fill(BG)
        draw_grid(screen)
        draw_board(screen, board)

        if game_over and win_line:
            draw_win_line(screen, win_line)

        buttons = draw_ui(screen, font_big, font_sm, status_msg, score, difficulty, hover_btn)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()