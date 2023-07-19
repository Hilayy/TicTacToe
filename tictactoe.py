import random
from datetime import datetime
import sqlite3


def print_board():  # print game board
    print('-------')
    print('|' + board['top-L'] + '|' + board['top-M'] + '|' + board['top-R'] + '|')
    print('-------')
    print('|' + board['mid-L'] + '|' + board['mid-M'] + '|' + board['mid-R'] + '|')
    print('-------')
    print('|' + board['low-L'] + '|' + board['low-M'] + '|' + board['low-R'] + '|')
    print('-------')  #


def take_turn(board, turn):  # take 1 player turn
    placement = input('where to place {}?\n'.format(turns[turn]))
    keys = board.keys()

    # placing the shape in the desired square, if it is on the board and is clear.
    if placement in keys:
        if board[placement] == ' ':  # register the placement request only if the spot has not been taken
            board[placement] = turns[turn]
            return
    print('invalid placement, try again')
    take_turn(board, turn)  # repeat until a valid square has been chosen


def choose_mode():
    mode = input("Choose a mode: \n1- player vs player\n2-player vs computer\n3-view saves\n")
    while mode != "1" and mode != "2" and mode != "3":
        mode = input("Invalid choice. Please choose a mode (1, 2, or 3): \n")
    return int(mode)


def check_win(board, names):
    # check if any of the win patterns have 3 shapes of the same kind
    for winning_key in winning_keys:
        if board[winning_key[0]] == board[winning_key[1]] == board[winning_key[2]] and board[winning_key[0]] != ' ':
            print("{} wins!".format(names[turn]))
            return True
    if ' ' not in board.values():  # checks for a draw, if the board is full and there is no winner, its a draw
        print("Draw!")
        return True
    return False


def player_vs_player(board, turn):  # player vs player game logic
    end = False
    names = [input("please enter player X and player O names:\nplayer X:"), input("\nplayer O:")]
    print_board()
    while not end:
        take_turn(board, turn)
        print_board()

        # if someone wins the game stops and game data is returned
        if check_win(board, names):
            return names[0], names[1], names[turn]  # returns the names of the player and the winner

        turn = not turn
    return


def is_first():  # let the player choose if they want to be X or O
    x_or_o = input("do you want to be X or O? (X starts first)\n")
    while x_or_o != "X" and x_or_o != "O":
        x_or_o = input("Invalid choice. Please choose A shape(X or O): \n")
    player_name = input("please enter your name:")
    # return False if the computer starts first and false otherwise
    if x_or_o == "X":
        names = ['Computer', player_name]
        return True, names
    names = [player_name, 'Computer']
    return False, names


def configure_moves(board, turn,
                    win_key):  # this function finds all the rational moves to make in the current board status
    rational_moves = []
    block_move = []
    keys = winning_keys

    # if the move does not win the game ignore diagonal patterns
    if not win_key:
        keys = keys[:-2]

    # check all the patterns
    for key in keys:
        empty_count = 0
        shape_count = 0
        for square in key:
            if board[square] == ' ':
                empty_count += 1
            elif board[square] == turns[turn]:
                shape_count += 1

        # if there is at least 1 computer-side shapes and no player-side shape
        if shape_count > 0 and shape_count + empty_count == 3:

            #  if the computer is 1 move from completing this pattern place its shape in the empty square of the pattern
            if shape_count == 2:
                for square in key:
                    if board[square] == ' ':
                        board[square] = turns[turn]
                        return

            # if there is 1 computer-side shape and 2 empty spaces add the pattern to the list of rational moves to make
            rational_moves.append(key)

        # if the opponent is 1 move away from completing this pattern place computer's shape in the empty square of the
        # pattern
        elif empty_count == 1 and shape_count == 0:
            block_move = key
    if block_move is not None:
        for square in block_move:
            if board[square] == ' ':
                board[square] = turns[turn]
                return

    # if at least 1 ideal pattern was found choose randomly 1 pattern and place the computer's shape on one of the
    # pattern's ends, if they are both taken, place in the middle of the pattern
    if len(rational_moves) != 0:
        move_to_make = random.choice(rational_moves)
        if board[move_to_make[0]] == ' ':
            board[move_to_make[0]] = turns[turn]
        elif board[move_to_make[2]] == ' ':
            board[move_to_make[2]] = turns[turn]
        else:
            board[move_to_make[1]] = turns[turn]
    # if no ideal moves were found place the computer's shape in one of the edge squares.
    else:
        for square in (['top-R', 'top-L', 'low-R', 'low-L']):
            if board[square] == ' ':
                board[square] = turns[turn]
                return

    return


def take_comp_turn(board, turn, turn_count):
    if turns[turn] == 'X':
        if turn_count == 0:
            placement = random.choice(['top-R', 'top-L', 'low-R', 'low-L'])
            board[placement] = turns[turn]
        else:

            # after the first move start recognizing diagonal patterns
            if turn_count > 2:
                configure_moves(board, turn, True)
            else:
                configure_moves(board, turn, False)

    # if the middle square was not taken by the player when O take it.
    elif board['mid-M'] == ' ':
        board['mid-M'] = 'O'
    else:
        configure_moves(board, turn, False)
    print_board()
    return


def player_vs_computer(board, turn):
    turn_count = 0
    comp_turn, names = is_first()

    print_board()
    while True:
        if comp_turn == turn:
            take_comp_turn(board, turn, turn_count)
        else:
            take_turn(board, turn)
        if check_win(board, names):
            return names[0], names[1], names[turn]  # returns the names of the player and the winner
        turn = not turn
        turn_count += 1


def get_table_names():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in cur.fetchall()]
    return table_names


def game(mode):  # initializing the game and getting the required data from it
    table_names = get_table_names()
    current_datetime = datetime.now()  # gets the time
    game_time = current_datetime.strftime('%H:%M:%S - %Y-%m-%d')
    if mode == 1:
        player_x, player_o, result = player_vs_player(board, turn)
    else:
        player_x, player_o, result = player_vs_computer(board, turn)
    if result != 'Draw!':
        result += " won!"
    game_name = input("Please Name this game save(only use uppercase letters, underscores and numbers).\n")
    while not all(i.isupper() or i == "_" or i.isdigit() for i in game_name):
        if game_name in table_names:
            game_name = input("Name already in use, please choose another name.\n")
        else:
            game_name = input("Name structure is not valid, please choose another name.\n")
    save(player_x, player_o, result, game_time, game_name)
    return


def save(player_x, player_o, result, game_time, game_name):
    cur.execute("CREATE TABLE {} (X_player text, O_player text, Result text, Time text)".format(game_name))
    cur.execute("INSERT INTO {} (X_player, O_player, Result, Time) VALUES (?,?,?,?)".format(game_name),
                (player_x, player_o, result, game_time))
    conn.commit()


def view():
    table_names = get_table_names()

    # print the names of all the tables in the file
    for table_name in table_names:
        print(str(table_names.index(table_name) + 1) + ". {}".format(table_name))  # present the list of saves to view

    while True:
        try:
            view_num = int(input("type the number associated with the save you want to view, to go back type -999\n"))
            if view_num in range(1, len(table_names) + 1):
                break
            elif view_num != -999:
                print("The number is out of range, Please try again")
            else:
                return

        except ValueError:
            print("Invalid input, Please try again.")

    # take all the data from the table and write it in the console
    cur.execute("SELECT * FROM {}".format(table_names[view_num - 1]))
    view_data = cur.fetchall()
    view_data = view_data[0]
    print(table_names[view_num - 1] + " save data:\n\n player X: {}\n player O: {}\n Result: {}\n Time: {}\n\nPress "
                                      "enter to go back".format(view_data[0], view_data[1], view_data[2],
                                                                view_data[3]))

    press = None
    while press is None:
        press = input()
    view()


conn = sqlite3.connect('tictactoe.db')
cur = conn.cursor()
winning_keys = [["top-L", "top-M", "top-R"],
                ["mid-L", "mid-M", "mid-R"],
                ["low-L", "low-M", "low-R"],
                ["top-L", "mid-L", "low-L"],
                ["top-M", "mid-M", "low-M"],
                ["top-R", "mid-R", "low-R"],
                ["top-L", "mid-M", "low-R"],
                ["top-R", "mid-M", "low-L"]]
while True:
    board = {'top-L': ' ', 'top-R': ' ', 'top-M': ' ', 'low-L': ' ', 'low-R': ' ', 'low-M': ' ', 'mid-L': ' ',
             'mid-R': ' ', 'mid-M'
             : ' '}
    turns = ['X', 'O']
    turn = False  # indicates which side's turn it is, switches value after every turn
    mode = choose_mode()
    if mode != 3:
        game(mode)
    else:
        view()
