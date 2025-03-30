import board as board
import chess
import pygame
import self as self
import random
import math

import sys
import os

from constants import *

pygame.init()

#experimental

board = chess.Board()
legal_moves = list(board.legal_moves)
is_checkmate = board.is_checkmate()
board.push(chess.Move.from_uci("e2e4"))
board.pop()
is_check = board.is_check()
is_pinned = board.is_pinned(chess.WHITE, chess.A2)
is_legal = board.is_legal(chess.Move.from_uci("e2e4"))
is_game_over = board.is_game_over()
is_repetition = board.is_repetition()

def resource_path(relative_path):
    try:
        # If the script is run in a PyInstaller bundle
        base_path = sys._MEIPASS
    except Exception:
        # If the script is run as a normal Python script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def play_move_sound():
    asset_sound_move = resource_path('assets/audio/move.mp3')
    pygame.mixer.music.load(asset_sound_move)
    pygame.mixer_music.play()
def play_bg_music():
    asset_bg_music = resource_path('assets/audio/idea22.mp3')
    pygame.mixer.music.load(asset_bg_music)
    pygame.mixer.music.play(-1)
play_bg_music()

def draw_board():
    for i in range(64):
        column = i % 8
        row = i // 8
        if (row + column) % 2 == 0:
            pygame.draw.rect(screen, 'forest green', [100 * column, 100 * row, 100, 100])
        else:
            pygame.draw.rect(screen, 'powder blue', [100 * column, 100 * row, 100, 100])

        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
        status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                       'Black: Select a Piece to Move!', 'Black: Select a Destination!']

        screen.blit(big_font.render(status_text[turn_step], True, 'black'), (15, 800))
        for i in range(9):
            pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        screen.blit(medium_font.render('RESIGN', True, 'black'), (820, 800))
        if white_promote or black_promote:
            pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100])
            pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
            screen.blit(big_font.render('Select Piece to Promote Pawn', True, 'black'), (20, 820))


def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (white_locations[i][0] * 100 + 22, white_locations[i][1] * 100 + 30))
        else:
            screen.blit(white_images[index], (white_locations[i][0] * 100 + 10, white_locations[i][1] * 100 + 10))
        if turn_step < 2:
            if selection == i:
                pygame.draw.rect(screen, 'red', [white_locations[i][0] * 100 + 1, white_locations[i][1] * 100 + 1,
                                                 100, 100], 2)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (black_locations[i][0] * 100 + 22, black_locations[i][1] * 100 + 30))
        else:
            screen.blit(black_images[index], (black_locations[i][0] * 100 + 10, black_locations[i][1] * 100 + 10))
        if turn_step >= 2:
            if selection == i:
                pygame.draw.rect(screen, 'blue', [black_locations[i][0] * 100 + 1, black_locations[i][1] * 100 + 1,
                                                  100, 100], 2)


def check_options(pieces, locations, turn):
    global castling_moves
    moves_list = []
    all_moves_list = []
    castling_moves = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list, castling_moves = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list


def check_king(position, color):

    moves_list = []
    castle_moves = check_castling()
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list, castle_moves


def check_queen(position, color):
    moves_list = check_bishop(position, color)
    second_list = check_rook(position, color)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


def check_bishop(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


def check_rook(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    for i in range(4):
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        if (position[0], position[1] + 1) not in white_locations and \
                (position[0], position[1] + 1) not in black_locations and position[1] < 7:
            moves_list.append((position[0], position[1] + 1))
            # Check if pawn can move two steps
            if position[1] == 1 and (position[0], position[1] + 2) not in white_locations and \
                    (position[0], position[1] + 2) not in black_locations:
                moves_list.append((position[0], position[1] + 2))
        # Check for captures
        if (position[0] + 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in black_locations:
            moves_list.append((position[0] - 1, position[1] + 1))
        # En passant
        if (position[0] + 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) == black_ep:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        # Similar logic for black pawns
            if (position[0], position[1] - 1) not in black_locations and \
                    (position[0], position[1] - 1) not in white_locations and position[1] > 0:
                moves_list.append((position[0], position[1] - 1))
                if position[1] == 6 and (position[0], position[1] - 2) not in black_locations and \
                        (position[0], position[1] - 2) not in white_locations:
                    moves_list.append((position[0], position[1] - 2))
            if (position[0] + 1, position[1] - 1) in white_locations:
                moves_list.append((position[0] + 1, position[1] - 1))
            if (position[0] - 1, position[1] - 1) in white_locations:
                moves_list.append((position[0] - 1, position[1] - 1))
            if (position[0] + 1, position[1] - 1) == white_ep:
                moves_list.append((position[0] + 1, position[1] - 1))
            if (position[0] - 1, position[1] - 1) == white_ep:
                moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list

def check_knight(position, color):
    moves_list = []
    if color == 'white':
        enemies_list = black_locations
        friends_list = white_locations
    else:
        friends_list = black_locations
        enemies_list = white_locations
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list

#v3
def is_move_valid(piece, start_pos, end_pos, color):
    # Simulate the move and check if the king is in check
    # Make temporary copies of the game state
    temp_white_locations = white_locations.copy()
    temp_black_locations = black_locations.copy()
    temp_white_pieces = white_pieces.copy()
    temp_black_pieces = black_pieces.copy()
    
    if color == 'white':
        index = temp_white_locations.index(start_pos)
        temp_white_locations[index] = end_pos
        if end_pos in temp_black_locations:
            captured_index = temp_black_locations.index(end_pos)
            temp_black_pieces.pop(captured_index)
            temp_black_locations.pop(captured_index)
    else:
        index = temp_black_locations.index(start_pos)
        temp_black_locations[index] = end_pos
        if end_pos in temp_white_locations:
            captured_index = temp_white_locations.index(end_pos)
            temp_white_pieces.pop(captured_index)
            temp_white_locations.pop(captured_index)
    
    # Check if the king is in check after the move
    king_pos = None
    if color == 'white':
        if 'king' in temp_white_pieces:
            king_index = temp_white_pieces.index('king')
            king_pos = temp_white_locations[king_index]
        # Check if any black moves attack the king
        temp_black_options = check_options(temp_black_pieces, temp_black_locations, 'black')
        for moves in temp_black_options:
            if king_pos in moves:
                return False
    else:
        if 'king' in temp_black_pieces:
            king_index = temp_black_pieces.index('king')
            king_pos = temp_black_locations[king_index]
        temp_white_options = check_options(temp_white_pieces, temp_white_locations, 'white')
        for moves in temp_white_options:
            if king_pos in moves:
                return False
    return True

def draw_check():
    global check
    check = False
    king_pos = None
    if turn_step < 2 and 'king' in white_pieces:
        king_index = white_pieces.index('king')
        king_pos = white_locations[king_index]
        attacker_color = 'black'
    elif 'king' in black_pieces:
        king_index = black_pieces.index('king')
        king_pos = black_locations[king_index]
        attacker_color = 'white'
    
    if king_pos:
        # Create surface with alpha channel
        check_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        check_surface.fill(CHECK_RED)
        
        attacker_options = black_options if attacker_color == 'black' else white_options
        for moves in attacker_options:
            if king_pos in moves:
                check = True
                screen.blit(check_surface, (king_pos[0]*100, king_pos[1]*100))
                break


def draw_valid(moves):
    if turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)


def draw_captured():
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


def draw_check():
    global check
    check = False
    if turn_step < 2:
        if 'king' in white_pieces:
            king_index = white_pieces.index('king')
            king_location = white_locations[king_index]
            for i in range(len(black_options)):
                if king_location in black_options[i]:
                    check = True
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * 100 + 1,
                                                              white_locations[king_index][1] * 100 + 1, 100, 100], 5)
    else:
        if 'king' in black_pieces:
            king_index = black_pieces.index('king')
            king_location = black_locations[king_index]
            for i in range(len(white_options)):
                if king_location in white_options[i]:
                    check = True
                    if counter < 15:
                        pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * 100 + 1,
                                                               black_locations[king_index][1] * 100 + 1, 100, 100], 5)


def draw_game_over():

    pygame.draw.rect(screen, 'black', [250, 250, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (260, 260))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (260, 290))


def check_ep(old_coords, new_coords):
    if turn_step <= 1:
        index = white_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] - 1)
        piece = white_pieces[index]
        play_move_sound()

    else:
        index = black_locations.index(old_coords)
        ep_coords = (new_coords[0], new_coords[1] + 1)
        piece = black_pieces[index]
        play_move_sound()

    if piece == 'pawn' and abs(old_coords[1] - new_coords[1]) > 1:
        pass
    else:
        ep_coords = (100, 100)
    return ep_coords




def check_castling():
    castle_moves = []
    rook_indexes = []
    rook_locations = []
    king_index = 0
    king_pos = (0, 0)
    
    if turn_step > 1:
        for i in range(len(white_pieces)):
            if white_pieces[i] == 'rook':
                rook_indexes.append(white_moved[i])
                rook_locations.append(white_locations[i])
            if white_pieces[i] == 'king':
                king_index = i
                king_pos = white_locations[i]
                
        if not white_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                   (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                    
                castle = True
                # Check if any square is under attack
                for square in empty_squares:
                    if is_square_under_attack(square, 'white', black_pieces, black_locations):
                        castle = False
                        break
                        
                # Check if squares are empty and rook hasn't moved
                if castle:
                    for square in empty_squares:
                        if square in white_locations or square in black_locations or rook_indexes[i]:
                            castle = False
                            break
                            
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
    else:
        for i in range(len(black_pieces)):
            if black_pieces[i] == 'rook':
                rook_indexes.append(black_moved[i])
                rook_locations.append(black_locations[i])
            if black_pieces[i] == 'king':
                king_index = i
                king_pos = black_locations[i]
                
        if not black_moved[king_index] and False in rook_indexes and not check:
            for i in range(len(rook_indexes)):
                if rook_locations[i][0] > king_pos[0]:
                    empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                   (king_pos[0] + 3, king_pos[1])]
                else:
                    empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                    
                castle = True
                # Check if any square is under attack
                for square in empty_squares:
                    if is_square_under_attack(square, 'black', white_pieces, white_locations):
                        castle = False
                        break
                        
                # Check if squares are empty and rook hasn't moved
                if castle:
                    for square in empty_squares:
                        if square in white_locations or square in black_locations or rook_indexes[i]:
                            castle = False
                            break
                            
                if castle:
                    castle_moves.append((empty_squares[1], empty_squares[0]))
                    
    return castle_moves


def draw_castling(moves):
    if turn_step < 2:
        color = 'red'
    else:
        color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70), 8)
        screen.blit(font.render('king', True, 'black'), (moves[i][0][0] * 100 + 30, moves[i][0][1] * 100 + 70))
        pygame.draw.circle(screen, color, (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 8)
        screen.blit(font.render('rook', True, 'black'),
                    (moves[i][1][0] * 100 + 30, moves[i][1][1] * 100 + 70))
        pygame.draw.line(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70),
                         (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 2)


def en_passant(start_pos, end_pos, color):
    if selected_piece == 'pawn':
        if abs(start_pos[1] - end_pos[1]) == 2:
            if color == 'white':
                return (end_pos[0], end_pos[1] - 1)
            else:
                return (end_pos[0], end_pos[1] + 1)
    # Reset en passant if not a two-step move
    return (100, 100)

def check_promotion():
    pawn_indexes = []
    white_promotion = False
    black_promotion = False
    promote_index = 100
    for i in range(len(white_pieces)):
        if white_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if white_locations[pawn_indexes[i]][1] == 7:
            white_promotion = True
            promote_index = pawn_indexes[i]
    pawn_indexes = []
    for i in range(len(black_pieces)):
        if black_pieces[i] == 'pawn':
            pawn_indexes.append(i)
    for i in range(len(pawn_indexes)):
        if black_locations[pawn_indexes[i]][1] == 0:
            black_promotion = True
            promote_index = pawn_indexes[i]
    return white_promotion, black_promotion, promote_index


def draw_promotion():
    promo_surface = pygame.Surface((200, 400), pygame.SRCALPHA)
    promo_surface.fill((50, 50, 50, 200))
    screen.blit(promo_surface, (800, 0))
    
    if white_promote:
        pieces = white_promotions
        images = white_images
    else:
        pieces = black_promotions
        images = black_images
    
    for i, piece in enumerate(pieces):
        index = piece_list.index(piece)
        screen.blit(images[index], (810, 10 + 100*i))
        text = medium_font.render(piece.capitalize(), True, 'white')
        screen.blit(text, (900, 40 + 100*i))

# Add this to mouse click handling in game loop
if white_promote or black_promote:
    x, y = pygame.mouse.get_pos()
    if 800 < x < 1000 and 0 < y < 400:
        promo_choice = (y - 10) // 100
        valid_choices = white_promotions if white_promote else black_promotions
        if promo_choice < len(valid_choices):
            # Handle promotion
            if white_promote:
                white_pieces[promo_index] = valid_choices[promo_choice]
            else:
                black_pieces[promo_index] = valid_choices[promo_choice]
            white_promote = False
            black_promote = False
            promo_index = 100

def get_moves(piece, position, color):
    if piece == 'pawn':
        return check_pawn(position, color)
    elif piece == 'rook':
        return check_rook(position, color)
    elif piece == 'knight':
        return check_knight(position, color)
    elif piece == 'bishop':
        return check_bishop(position, color)
    elif piece == 'queen':
        return check_queen(position, color)
    elif piece == 'king':
        moves_list, _ = check_king(position, color)
        return moves_list
    return []

def check_valid_moves():
    if selection == 100:
        return []
    if turn_step < 2:
        moves = get_moves(white_pieces[selection], white_locations[selection], 'white')
        return [mv for mv in moves if is_move_valid(white_pieces[selection], white_locations[selection], mv, 'white')]
    else:
        moves = get_moves(black_pieces[selection], black_locations[selection], 'black')
        return [mv for mv in moves if is_move_valid(black_pieces[selection], black_locations[selection], mv, 'black')]

def in_check(new_locations, pieces, color):
    king_index = pieces.index('king')
    king_pos = new_locations[king_index]
    attacker_color = 'black' if color == 'white' else 'white'
    attacker_pieces = black_pieces if attacker_color == 'black' else white_pieces
    attacker_locations = black_locations if attacker_color == 'black' else white_locations
    
    for i, piece in enumerate(attacker_pieces):
        piece_moves = get_moves(piece, attacker_locations[i], attacker_color)
        if king_pos in piece_moves:
            return True
    return False

def is_checkmate(color):
    king_index = None   
    king_pos = None
    if color == 'white':
        pieces = white_pieces
        locations = white_locations
        options = black_options
    else:
        pieces = black_pieces
        locations = black_locations
        options = white_options

    for i, piece_moves in enumerate(options):
        if len(piece_moves) > 0:
            for move in piece_moves:
                temp_locations = locations.copy()
                temp_locations[i] = move
                if not in_check(temp_locations, pieces, color):
                    return False     
    # In the main loop, after checking for check:
    if check:
        if turn_step < 2:
            current_pieces = white_pieces
            current_locations = white_locations
            current_options = white_options
        else:
            current_pieces = black_pieces
            current_locations = black_locations
            current_options = black_options
        has_valid_moves = False
        for i in range(len(current_pieces)):
            if current_options[i]:  # Check if any moves are available
                temp_selection = i
                temp_valid = current_options[i]
                for move in temp_valid:
                    if is_move_valid(current_pieces[i], current_locations[i], move, 'white' if turn_step < 2 else 'black'):
                        has_valid_moves = True
                        break
                if has_valid_moves:
                    break
        if not has_valid_moves:
            winner = 'black' if turn_step < 2 else 'white'
            game_over = True
        
    # Find king's position
    if 'king' in pieces:
        king_index = pieces.index('king')
        king_pos = locations[king_index]

    # Check if the king can move to any available square
    if king_pos:
        for move_list in options:
            if king_pos not in move_list:
                return False  # King can move, not checkmate

    # Check if any other piece can capture the threatening piece
    for move_list in options:
        for move in move_list:
            if color == 'white':
                if move in black_locations:
                    piece_index = black_locations.index(move)
                    piece = black_pieces[piece_index]
                    if piece != 'king':
                        return False  # Checkmate is avoided
            else:
                if move in white_locations:
                    piece_index = white_locations.index(move)
                    piece = white_pieces[piece_index]
                    if piece != 'king':
                        return False  # Checkmate is avoided

    return True  # Checkmate condition met

def is_square_under_attack(square, color, opponent_pieces, opponent_locations):
    """
    Check if a square is under attack by opponent's pieces.
    """
    for piece, loc in zip(opponent_pieces, opponent_locations):
        if piece != 'king' and loc != 'captured':
            if piece == 'pawn':
                if color == 'white':
                    if (loc[0] + 1, loc[1] + 1) == square or (loc[0] + 1, loc[1] - 1) == square:
                        return True
                else:
                    if (loc[0] - 1, loc[1] + 1) == square or (loc[0] - 1, loc[1] - 1) == square:
                        return True
            elif piece == 'knight':
                moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
                for move in moves:
                    if (loc[0] + move[0], loc[1] + move[1]) == square:
                        return True
            elif piece == 'bishop':
                if abs(loc[0] - square[0]) == abs(loc[1] - square[1]):
                    return True
            elif piece == 'rook':
                if loc[0] == square[0] or loc[1] == square[1]:
                    return True
            elif piece == 'queen':
                if abs(loc[0] - square[0]) == abs(loc[1] - square[1]) or loc[0] == square[0] or loc[1] == square[1]:
                    return True
    return False

def filter_moves_in_check(moves, color, opponent_pieces, opponent_locations):
    """
    Filter moves that lead to squares under attack by opponent's pieces.
    """
    safe_moves = []
    for move in moves:
        if not is_square_under_attack(move, color, opponent_pieces, opponent_locations):
            safe_moves.append(move)
    return safe_moves

def force_king_move(color, checked_squares, opponent_pieces, opponent_locations):
    """
    Generate possible king moves and filter out moves that lead to checked squares.
    """
    king_moves = []
    if color == 'white':
        king_loc = white_locations[white_pieces.index('king')]
    else:
        king_loc = black_locations[black_pieces.index('king')]

    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for target in targets:
        new_loc = (king_loc[0] + target[0], king_loc[1] + target[1])
        if 0 <= new_loc[0] <= 7 and 0 <= new_loc[1] <= 7:
            king_moves.append(new_loc)

    safe_moves = filter_moves_in_check(king_moves, color, opponent_pieces, opponent_locations)
    return safe_moves




def check_promo_select():
    mouse_pos = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]
    x_pos = mouse_pos[0] // 100
    y_pos = mouse_pos[1] // 100
    if white_promote and left_click and x_pos > 7 and y_pos < 4:
        white_pieces[promo_index] = white_promotions[y_pos]
    elif black_promote and left_click and x_pos > 7 and y_pos < 4:
        black_pieces[promo_index] = black_promotions[y_pos]


black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')
run = True
while run:
    timer.tick(fps)
    if counter < 30:
        counter += 1
    else:
        counter = 0
    screen.fill('grey')

    draw_board()
    draw_pieces()
    draw_captured()
    draw_check()
    if not game_over:
        white_promote, black_promote, promo_index = check_promotion()
        if white_promote or black_promote:
            draw_promotion()
            check_promo_select()
    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)
        if selected_piece == 'king':
            draw_castling(castling_moves)
        
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)
            if turn_step <= 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'black'
                if click_coords in white_locations:
                    selection = white_locations.index(click_coords)
                    selected_piece = white_pieces[selection]
                    if turn_step == 0:
                        turn_step = 1
                if click_coords in valid_moves and selection != 100:
                    white_ep = check_ep(white_locations[selection], click_coords)
                    white_locations[selection] = click_coords
                    white_moved[selection] = True
                    if click_coords in black_locations:
                        black_piece = black_locations.index(click_coords)
                        captured_pieces_white.append(black_pieces[black_piece])
                        if black_pieces[black_piece] == 'king':
                            winner = 'white'
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    # adding check if en passant pawn was captured
                    if click_coords == black_ep:
                        black_piece = black_locations.index((black_ep[0], black_ep[1] - 1))
                        captured_pieces_white.append(black_pieces[black_piece])
                        black_pieces.pop(black_piece)
                        black_locations.pop(black_piece)
                        black_moved.pop(black_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 2
                    selection = 100
                    valid_moves = []
                elif selection != 100 and selected_piece == 'king':
                    for q in range(len(castling_moves)):
                        if click_coords == castling_moves[q][0]:
                            white_locations[selection] = click_coords
                            white_moved[selection] = True
                            if click_coords == (1, 0):
                                rook_coords = (0, 0)
                            else:
                                rook_coords = (7, 0)
                            rook_index = white_locations.index(rook_coords)
                            white_locations[rook_index] = castling_moves[q][1]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 2
                            selection = 100
                            valid_moves = []
            if turn_step > 1:
                if click_coords == (8, 8) or click_coords == (9, 8):
                    winner = 'white'
                if click_coords in black_locations:
                    selection = black_locations.index(click_coords)
                    selected_piece = black_pieces[selection]
                    if turn_step == 2:
                        turn_step = 3
                if click_coords in valid_moves and selection != 100:
                    black_ep = check_ep(black_locations[selection], click_coords)
                    black_locations[selection] = click_coords
                    black_moved[selection] = True
                    if click_coords in white_locations:
                        white_piece = white_locations.index(click_coords)
                        captured_pieces_black.append(white_pieces[white_piece])
                        if white_pieces[white_piece] == 'king':
                            winner = 'black'
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    if click_coords == white_ep:
                        white_piece = white_locations.index((white_ep[0], white_ep[1] + 1))
                        captured_pieces_black.append(white_pieces[white_piece])
                        white_pieces.pop(white_piece)
                        white_locations.pop(white_piece)
                        white_moved.pop(white_piece)
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    turn_step = 0
                    selection = 100
                    valid_moves = []
                # add option to castle
                elif selection != 100 and selected_piece == 'king':
                    for q in range(len(castling_moves)):
                        if click_coords == castling_moves[q][0]:
                            black_locations[selection] = click_coords
                            black_moved[selection] = True
                            if click_coords == (1, 7):
                                rook_coords = (0, 7)
                            else:
                                rook_coords = (7, 7)
                            rook_index = black_locations.index(rook_coords)
                            black_locations[rook_index] = castling_moves[q][1]
                            black_options = check_options(black_pieces, black_locations, 'black')
                            white_options = check_options(white_pieces, white_locations, 'white')
                            turn_step = 0
                            selection = 100
                            valid_moves = []
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ''
                white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                white_moved = [False, False, False, False, False, False, False, False,
                               False, False, False, False, False, False, False, False]
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                black_moved = [False, False, False, False, False, False, False, False,
                               False, False, False, False, False, False, False, False]
                captured_pieces_white = []
                captured_pieces_black = []
                turn_step = 0
                selection = 100
                valid_moves = []
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if winner != '':

        game_over = True
        draw_game_over()



    pygame.display.flip()
pygame.quit()
