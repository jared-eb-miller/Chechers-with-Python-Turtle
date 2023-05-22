import turtle as trtl
import math
import time
import random
import os

# set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ======== Setup Variables / Constants ========
board_side_len = 500
border_size = 150
tile_side_len = board_side_len / 8
half_tile_side_len = tile_side_len / 2
window_side = board_side_len + border_size*2
tile_colors = ((255,240,240),(130,100,100),(75,150,75), \
              None,(163,100,100),(234,175,175))
tile_shape = ((-half_tile_side_len, -half_tile_side_len), \
              (-half_tile_side_len, half_tile_side_len), \
              (half_tile_side_len, half_tile_side_len), \
              (half_tile_side_len, -half_tile_side_len))
border_width = 8
num_checkers = 12

# =========== Global Game Variables ===========
turn_is_red = True
possible_moves_list = []
selecting = False
last_two_tiles = []
selected_checker = None
route_list = []
global_to_tile = None
kinged_checkers = []

# =================== Setup ===================
wn = trtl.Screen()
wn.setup(width=window_side, height=window_side)
wn.title('Turtle Checkers')
wn.register_shape('checker tile', tile_shape)
black_image = 'Images/Black.gif'
black_king_image = 'Images/Black King.gif'
red_image = 'Images/Red.gif'
red_king_image = 'Images/Red King.gif'
start_btn_image = 'Images/Start Button.gif'
wn.addshape(black_image)
wn.addshape(black_king_image)
wn.addshape(red_image)
wn.addshape(red_king_image)
wn.addshape(start_btn_image)
wn.colormode(255)
wn.tracer(False) # make all setup happen instantly

# ------ Create Checkerboard Grid ------
xcor = -board_side_len/2 + half_tile_side_len
rows = []
row = 0
while row < 8:
  row += 1
  ycor = -board_side_len/2 + half_tile_side_len
  tiles = []
  column = 0
  while column < 8:
    column += 1
    board_tile = trtl.Turtle(shape='checker tile')
    board_tile.penup()
    board_tile.goto(xcor, ycor)
    color = 0 if (column % 2) == (row % 2) else 1
    board_tile.color(tile_colors[color])
    board_tile.stamp()
    board_tile.hideturtle()
    tiles.append(board_tile)
    ycor += tile_side_len
  rows.append(tiles)
  xcor += tile_side_len

# ------ Create Border ------
border = trtl.Turtle()
border.hideturtle()
border.color('black')
border.penup()
border.pensize(border_width)
border.goto(-board_side_len/2 - border_width, -board_side_len/2 - border_width)
border.pendown()
border.goto(border.xcor(), board_side_len/2 + border_width)
border.goto(board_side_len/2 + border_width, border.ycor())
border.goto(border.xcor(), -board_side_len/2 - border_width)
border.goto(-board_side_len/2 - border_width, border.ycor())

# ------ Create Both Lists of Checkers ------
red_checkers = []
black_checkers = []
spacing = 30
horizontal_pos = spacing * num_checkers / 2 # variable
vertical_pos = board_side_len/2 + border_width*2 + 45
while len(red_checkers) < num_checkers:
  r_checker = trtl.Turtle(shape=red_image)
  b_checker = trtl.Turtle(shape=black_image)

  r_checker.penup()
  b_checker.penup()
  r_checker.goto(-horizontal_pos, -vertical_pos)
  b_checker.goto(horizontal_pos, vertical_pos)
  r_checker.speed(0)
  b_checker.speed(0)

  red_checkers.append(r_checker)
  black_checkers.append(b_checker)

  horizontal_pos -= spacing

start_btn = trtl.Turtle(shape=start_btn_image)

wn.tracer(True) # show all previous code on the screen at once
wn.update()

# ============== Game Functions ==============
def black_computer_generated_move():
  """ 
  Selects and executes a random move.
  """
  global black_checkers, global_to_tile, selected_checker
  
  checkers_to_try = black_checkers.copy()
  got_move = False
  while (not got_move) and (len(checkers_to_try) > 0):
    try:
      selected_checker = random.choice(checkers_to_try)
      checkers_to_try.remove(selected_checker)
      global_to_tile = random.choice(possible_moves(selected_checker))
      got_move = True
    except:
      None
  if not got_move:
    black_checkers.clear()
    change_turn()
  else:
    move_selected_checker(selected_checker)

def is_ocupied(tile, check_team=False):
  """
  This function will return whether a space on the board is ocupied by a checker.
  If check_team is true, then the function will only check for checkers of the
  team who's turn it is not.
  The function returns a boolean of whether or not the tile is ocupied.
  """
  global red_checkers, black_checkers, turn_is_red, selected_checker

  checker_list = black_checkers + red_checkers if not check_team \
    else black_checkers if turn_is_red else red_checkers
  if not check_team:
    checker_list.remove(selected_checker)
  ocupied = False
  for checker in checker_list:
    if checker.position() == tile.position():
      ocupied = True
      break
  return ocupied

def get_moves(row_index, tile_index, on_secondary_move=False, direction=0):
  """
  Returns a list of board tiles, or moves, of a checker at the specified borad tile cordinates
  Args on_secondary_move, and direction are used for when the function calls itself to find
  the moves where a checher jumps another checker or for the function, move_selected_checker(),
  which calls this function through the functino, possible_moves().
  """
  global rows, selected_checker, kinged_checkers, turn_is_red

  original_tile = rows[row_index][tile_index]
  diagonals = [] # list of the immeadiate diagonals

  # --- construct the diagonals list ---
  # Exclude 'backwards' diagonals for non-kinged checkers as well as
  # exclude the starting position as a move when the function is called 
  # abaing to determine jumps which is determined by the direction argument.
  if tile_index != 0: 
    if not turn_is_red or selected_checker in kinged_checkers:
      if row_index != 0 and direction != 1:
        diagonals.append(rows[row_index-1][tile_index-1])
      if row_index != 7 and direction != 2:
        diagonals.append(rows[row_index+1][tile_index-1])
  if tile_index != 7:
    if turn_is_red or selected_checker in kinged_checkers:
      if row_index != 0 and direction != 4:
        diagonals.append(rows[row_index-1][tile_index+1])
      if row_index != 7 and direction != 3:
        diagonals.append(rows[row_index+1][tile_index+1])

  # Add ocupied diagonals to their own list for them to be checked for possible
  # jump moves and for them to be eventually exclued from the final moves list.
  ocupied_diagonals = []
  for diagonal in diagonals:
    if is_ocupied(diagonal):
      ocupied_diagonals.append(diagonal)
  
  special_moves = []
  for diagonal in ocupied_diagonals:
    # check each ocupied diagonal for jump moves that come off of that diagonal
    if is_ocupied(diagonal, check_team=True):
      # find the second diagonal in same direction the ocupied diagonal was to the original tile
      diagonal_is_left = original_tile.xcor() > diagonal.xcor()
      diagonal_is_down = original_tile.ycor() > diagonal.ycor()
      special_move_row_index = (row_index - 2) if diagonal_is_left else (row_index + 2)
      special_move_tile_index = (tile_index - 2) if diagonal_is_down else (tile_index + 2)
      if special_move_row_index >= 0 and special_move_row_index <= 7:
        if special_move_tile_index >= 0 and special_move_tile_index <= 7:
          new_diagonal = rows[special_move_row_index][special_move_tile_index]
          if not is_ocupied(new_diagonal):  # check if second diagonal is ocupied
            if new_diagonal.position() == selected_checker.position(): 
              # prevents an infinite loop when a move ends where it started
              return [new_diagonal]
            special_moves.append(new_diagonal)

            # --- Repeat to find double / triple jumps ---
            if diagonal_is_left:
              if diagonal_is_down:
                new_direction = 3
              else:
                new_direction = 2
            else:
              if diagonal_is_down:
                new_direction = 4
              else:
                new_direction = 1
            special_moves += get_moves(special_move_row_index, special_move_tile_index, \
              on_secondary_move=True, direction=new_direction)
    diagonals.remove(diagonal)  # exclude the actual ocupied diagonal form the final moves list

  return diagonals + special_moves if not on_secondary_move else special_moves

def possible_moves(turtle, only_jumps=False):
  """
  This function returns a list of moves for a given board tile or checker.
  """
  global rows

  for row in rows:  # get board cordinates for input turtle
    for tile in row:
      if tile.position() == turtle.position():
        row_index = rows.index(row)
        tile_index = row.index(tile)
        break
  # pass cordinates to the get_moves() function and store the returned list
  moves = get_moves(row_index, tile_index, on_secondary_move=only_jumps)
  # remove duplicate moves
  non_duplicate_moves = []
  for move in moves:
    if move not in non_duplicate_moves:
      non_duplicate_moves.append(move)
  return non_duplicate_moves

def move_selected_checker(selected_checker):
  """
  Move selected_checker to global_to_tile through the correct route.
  """
  global possible_moves_list, turn_is_red, tile_side_len, black_checkers, \
          red_checkers, route_list, tile_colors, global_to_tile

  to_tile = global_to_tile
  selected_checker.speed(4)
  if selected_checker.position() == to_tile.position(): # if the checker will end up where it started
    for move in possible_moves_list:
      if abs(selected_checker.xcor() - move.xcor()) > tile_side_len*2 or \
        abs(selected_checker.ycor() - move.ycor()) > tile_side_len*2:
        single_jump(selected_checker, possible_moves_list[possible_moves_list.index(move)-1])
        single_jump(selected_checker, move)
        single_jump(selected_checker, possible_moves_list[possible_moves_list.index(move)+1])
        single_jump(selected_checker, to_tile)
        break
  elif abs(selected_checker.xcor() - to_tile.xcor()) <= tile_side_len and \
    abs(selected_checker.ycor() - to_tile.ycor()) <= tile_side_len: # normal move
    selected_checker.goto(to_tile.position())
  elif abs(selected_checker.xcor() - to_tile.xcor()) <= tile_side_len*2 and \
    abs(selected_checker.ycor() - to_tile.ycor()) <= tile_side_len*2: # single jump
    single_jump(selected_checker, to_tile)
  elif abs(selected_checker.xcor() - to_tile.xcor()) <= tile_side_len*4 and \
    abs(selected_checker.ycor() - to_tile.ycor()) <= tile_side_len*4: # more than single jump
    # find all possible routes
    traceback_jump_list = possible_moves(selected_checker, only_jumps=True)
    routes = []
    for move in possible_moves_list:
      for traceback_jump in traceback_jump_list:
          if traceback_jump == move:
            if move != to_tile:
              if move.position() != selected_checker.position():
                routes.append(move)
    if len(routes) == 1:
      # execute full move if ther is only one route
      single_jump(selected_checker, routes[0])
      single_jump(selected_checker, to_tile)
    else:
      route_list = routes # global
      wn.tracer(False)
      for route in route_list:  # higlight different possible routes
        route.showturtle()
        route.color(tile_colors[2])
      wn.tracer(True)
      wn.update()
      wn.onclick(select_route) # the select_route() function will dicide which rout the user wants to go
  if selected_checker.position() == to_tile.position(): # if move is complete then change the turn
    change_turn()
      
def change_turn():
  """
  Resets all global variables that were manipulated during each turn, and starts the next turn.
  """
  global turn_is_red, possible_moves_list, last_two_tiles, selected_checker, route_list, \
    global_to_tile, kinged_checkers, red_king_image, black_king_image, red_checkers, black_checkers
  
  possible_moves_list = []
  last_two_tiles = []
  route_list = []
  global_to_tile = None
  # check if a checker was kinged. If so, king it.
  king_cor_threshold = tile_side_len*4 - half_tile_side_len
  if abs(selected_checker.ycor()) == king_cor_threshold:
    kinged_checkers.append(selected_checker)
    selected_checker.shape(red_king_image if turn_is_red else black_king_image)
  selected_checker = None

  time.sleep(0.2)

  turn_is_red = False if turn_is_red else True  # switch turn
  
  if len(red_checkers) != 0 and len(black_checkers) != 0: # continue game
    if turn_is_red:
      wn.onclick(find_checker_clicked)
    else:
      black_computer_generated_move()
  else: # game over
    # display winner
    wn.tracer(False)
    writer = trtl.Turtle()
    writer.ht()
    writer.penup()
    window_height = wn.window_height()
    writer.goto(0, (window_height)/-2 + 20)
    if len(red_checkers) == 0:
      writer.color('black')
      writer.write("Black wins.", align='center', font=("Arial", 80, "bold"))
    else:
      writer.color('red')
      writer.write("Red wins!", align='center', font=("Arial", 80, "bold"))
    wn.tracer(True)
    wn.update()

def select_route(x,y):
  """
  Determine which rout was clicked and proceed with the move.
  """
  global selected_checker, route_list, tile_side_len

  for route in route_list:
    change_tile_color(route, reset_tile=True)
    if abs(x-route.xcor()) < half_tile_side_len:
      if abs(y-route.ycor()) < half_tile_side_len:
        single_jump(selected_checker, route)
        move_selected_checker(selected_checker)

def single_jump(selected_checker, to_tile):
  """
  Execute a single jump.
  """
  global turn_is_red, black_checkers, red_checkers, window_side, spacing

  half_new_x_pos = selected_checker.xcor() + (to_tile.xcor() - selected_checker.xcor())/2
  half_new_y_pos = selected_checker.ycor() + (to_tile.ycor() - selected_checker.ycor())/2

  selected_checker.goto(to_tile.position())

  # remove checker that got jumped
  checker_list = black_checkers if turn_is_red else red_checkers
  for checker in checker_list:
    if checker.position() == (half_new_x_pos,half_new_y_pos):
      checker_list.remove(checker)
      xcor = window_side/2 - 80
      ycor = -window_side/2 + 140
      team_multiplier = 1 if turn_is_red else -1
      time.sleep(0.125)
      checker.goto(xcor*team_multiplier, ycor*team_multiplier + spacing*team_multiplier)
      spacing += 20
  
def change_tile_color(tile, reset_tile=False):
  """
  Determine the and set the correct color for the given tile.
  """
  global rows, possible_moves_list, tile_colors

  # find tile cordinates
  for row in rows:
    try:
      tile_index = row.index(tile)
      row_index = rows.index(row)
    except:
      None
  # determine color
  color = 3 if tile_index % 2 == row_index % 2 else 2
  # change color
  if not reset_tile:
    if tile not in possible_moves_list:
      color += 2
    tile.color(tile_colors[color])
    tile.showturtle()
  else: 
    tile.hideturtle()

def end_selection(x,y):
  """
  Determine whether the user clicked a valid move. If so, begin executino of the move.
  """
  global possible_moves_list, tile_side_len, selecting, selected_checker, global_to_tile

  if selecting:
    for move in possible_moves_list:
      if abs(x-move.xcor()) < half_tile_side_len:
        if abs(y-move.ycor()) < half_tile_side_len:
          wn.onclick(None)
          selecting = False
          change_tile_color(move, reset_tile=True)
          global_to_tile = move
          move_selected_checker(selected_checker)
          break

def on_tile(x,y):
  """
  Return the tile closest to the input window cordinates
  """
  global rows, last_two_tiles

  x -= wn.window_width() - 75
  y += wn.window_height()/2 + 51
  tile_apothem = half_tile_side_len
  if abs(x) > 250 or abs(y) > 250:  # if the mouse goes outside of the board
    last_two_tiles = []
  for row in rows:  # find tile
    for tile in row:
      if abs(tile.xcor() - x) < tile_apothem:
        if abs(tile.ycor() - y) < tile_apothem:
          return tile

def selection_loop():
  """
  Run during the 'selection phase' when the user has already dicided what checker to move.
  This function highishts the board tile the right color.
  """
  global last_two_tiles, selecting, selected_checker, rows
  x,y = wn.getcanvas().winfo_pointerxy()  # get mouse position
  tile = on_tile(x,-y)  # get the tile the mouse is on
  if tile != None:
    if len(last_two_tiles) == 0:
      last_two_tiles.append(tile)
      if not is_ocupied(tile):
        if tile.position() != selected_checker.position():
          change_tile_color(tile)
    else:
      if not tile == last_two_tiles[len(last_two_tiles)-1]:
        if len(last_two_tiles) == 2:
          last_two_tiles.pop(0)
          last_two_tiles.append(tile)
          change_tile_color(last_two_tiles[0], reset_tile=True)
        else:
          last_two_tiles.append(tile)
          change_tile_color(last_two_tiles[0], reset_tile=True)
        if not is_ocupied(tile):
          if tile.position() != selected_checker.position():
            change_tile_color(tile)
  else:
    if last_two_tiles == []:  # the mouse is not on the board
      # clear all highlights
      for row in rows:
        for tile in row:
          tile.ht()
  if selecting:
    wn.ontimer(selection_loop, 10) # loop untile a move is selected
    # this loop terminates with the end_selection function.

def find_checker_clicked(x,y):
  """
  This functino is called when the user clickes on a checker to move.
  The function determines which checker was clicked and then enter the
  'selection phase' where the user selects a move.
  """
  global rows, black_checkers, red_checkers, turn_is_red, possible_moves_list, selecting, selected_checker

  checkers = red_checkers if turn_is_red else black_checkers
  checker_radius = 30

  for checker in checkers:
    dist_from_center = math.sqrt(abs(checker.xcor()-x)**2 + abs(checker.ycor()-y)**2)
    if dist_from_center < checker_radius:
      if checker != selected_checker:
        selected_checker = checker # global
        possible_moves_list = possible_moves(checker).copy()  # global
        if not selecting:
          wn.onclick(end_selection, add=True) # start 'selection phase'
          selecting = True
          selection_loop()
        break

def move_to_start(xdummy=None,ydummy=None):
  """
  This functio is in reaction to the start button event.
  It moves all the checkers to their starting positions
  and starts a red turn.
  """
  global rows, black_checkers, red_checkers

  start_btn.hideturtle()
  start_btn.onclick(None) # clear start button event
  # move all the checkers
  b_index, r_index, tile_num = 0,0,0
  for row in rows:
    for tile in row:
      if tile.ycor() > 70 and (tile_num % 2) == 1:
        black_checkers[b_index].goto(tile.position())
        b_index += 1
      if tile.ycor() < -70 and (tile_num % 2) == 1:
        red_checkers[r_index].goto(tile.position())
        r_index += 1
      if b_index > len(black_checkers) - 1:
        break
      tile_num += 1
    tile_num += 1
  # start red turn
  wn.onclick(find_checker_clicked)

start_btn.onclick(move_to_start)

wn.mainloop()