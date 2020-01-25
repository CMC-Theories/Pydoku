"""
Chase Craig
Sudoku Solver

The idea of this project is to explore performing backtracking and graphics using python. Along with understanding how to implement history
"""
import copy
import math
import pygame
import queue
pygame.init() # Init immediately
pygame.font.init()

# Variables - Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
ERR_C = (255,0,0)
ERR_TEMP_C = (200,150,100)
SELECTED_C = (0,50,240)
TESTING_C = (100,150,100)

# Variables - Board
SIZE_CELL = 30
SIZE_BOARD = 5
LINE_WIDTH = 1
MAJOR_WIDTH = 3



class Board:
	def __init__(self, size = 3):
		self.n = size*size
		self.sqrtn = size
		self.board = [[0 for i in range(self.n)] for j in range(self.n)]
		self.history = {0: copy.deepcopy(self.board)}
		self.cur_step = 0
	def transpose(self):
		data = copy.deepcopy(self.board)
		for i in range(self.n):
			for j in range(self.n):
				self.board[i][j] = data[j][i]
		self.history[self.cur_step] = copy.deepcopy(self.board)
	def set(self, i,j, v):
		# Increase step, set the value, save the new state, check the board, return status + step
		self.cur_step = self.cur_step + 1
		previous = self.board[i][j]
		self.board[i][j] = v
		success = self.check_state()
		if not success:
			# Delete our entry.
			# It will highlight the previously conflicting numbers.
			self.board[i][j] = previous
			self.cur_step = self.cur_step - 1
			return (self.cur_step, False)

		self.history[self.cur_step] = copy.deepcopy(self.board)
		# If we had re-wound the board and made a change without jumping back, then we delete all future progress.
		if self.cur_step + 1 in self.history:
			ii = self.cur_step + 1
			while ii in self.history:
				self.history.pop(ii, None)
				ii = ii + 1
		return (self.cur_step, success)
	def rewind(self, step=-5):
		# Technically, this can be used to fast forward as well...
		if step == -5:
			step = self.cur_step - 1
		if step < 0 or step > max(list(self.history.keys())):
			return False
		self.cur_step = step
		self.board = copy.deepcopy(self.history[self.cur_step])
		return True
	def fetchState(self, step):
		# Fetch a state in the history of this board, return blank if invalid input (NAN, <0, >curSteps)
		if step not in self.history:
			return self.history[0]
		return copy.deepcopy(self.history[self.cur_step])
	def reset_checking(self):
		for i in range(self.n):
			for j in range(self.n):
				if self.board[i][j] > 200:
					self.board[i][j] = self.board[i][j] - 200
				elif self.board[i][j] < -200:
					self.board[i][j] = self.board[i][j] + 200
	def set_error_state(self, i, j):
		if self.board[i][j] < 200 and self.board[i][j] > -200 and self.board[i][j] != 0:
			self.board[i][j] = self.board[i][j] + (-200 if self.board[i][j] < 0 else 200)
	def check_success(self):
		for i in range(self.n):
			for j in range(self.n):
				if not (self.board[i][j] > -200 and self.board[i][j] < 200 and self.board[i][j] != 0):
					return False
		return True
	def check_state(self):
		# Reset past error markers.
		self.reset_checking()
		# Check the board, starting at i and j (early return on bad boards, so speed up by passing spot in question)
		#
		# __Line checks__
		for k in range(self.n):
			horiz = {}
			vert = {}
			for l in range(self.n):
				if abs(self.board[k][l]) in vert:
					# Mark the values before you go
					self.set_error_state(k, vert[abs(self.board[k][l])])
					self.set_error_state(k,l)
					return False
				if abs(self.board[l][k]) in horiz:
					self.set_error_state(horiz[abs(self.board[l][k])], k)
					self.set_error_state(l,k)
					return False
				# We ignore 0's
				if self.board[k][l] != 0:
					vert[abs(self.board[k][l])] = l
				if self.board[l][k] != 0:
					horiz[abs(self.board[l][k])] = l
		
		# __Cell checks__
		for ix in range(self.sqrtn):
			for iy in range(self.sqrtn):
				cellID = {}
				for k in range(self.sqrtn):
					for l in range(self.sqrtn):
						if abs(self.board[self.sqrtn * ix + k][self.sqrtn * iy + l]) in cellID:
							x,y = cellID[abs(self.board[self.sqrtn * ix + k][self.sqrtn * iy + l])]
							self.set_error_state(self.sqrtn * ix + k, self.sqrtn * iy + l)
							self.set_error_state(x,y)
							return False
						if (self.board[self.sqrtn * ix + k][self.sqrtn * iy + l]) != 0:
							cellID[abs(self.board[self.sqrtn * ix + k][self.sqrtn * iy + l])] = (self.sqrtn * ix + k,self.sqrtn * iy + l)
						
		return True


size = tuple(SIZE_CELL * SIZE_BOARD*SIZE_BOARD + LINE_WIDTH * (SIZE_BOARD * SIZE_BOARD - 1) for i in range(2))
screen = pygame.display.set_mode(size)
pygame.display.set_caption(str(SIZE_BOARD) + "x" + str(SIZE_BOARD)+" Sudoku")
pygame.display.set_icon(pygame.image.load('icon.png'))
running = True
clock = pygame.time.Clock() # Really shouldn't need this, but to prevent going faster than 30 fps
bb = Board(size=SIZE_BOARD)
TEXTS = [i for i in "0123456789ABCDEFGHIJKLMNOP"]
TEXTS = TEXTS[:SIZE_BOARD*SIZE_BOARD + 1]
font = pygame.font.SysFont('arial', 20)
font_bold = pygame.font.SysFont('arialblack', 20)
texts_rects = [font.render(i, True, BLACK) for i in TEXTS]
temp_texts_rects = [font.render(i, True, TESTING_C) for i in TEXTS]
temp_err_texts_rects = [font_bold.render(i, True, ERR_TEMP_C) for i in TEXTS]
err_texts_rects = [font_bold.render(i, True, ERR_C) for i in TEXTS]
texts_sizes = [i.get_rect() for i in texts_rects]
texts_sizes_bold = [i.get_rect() for i in err_texts_rects]



if SIZE_BOARD == 2:
	pass
elif SIZE_BOARD == 3:
	bb.board = [
	[0,0,0,0,7,1,0,6,4],
	[0,0,0,0,0,0,2,0,7],
	[8,2,0,0,6,0,0,0,0],
	[3,0,0,0,4,2,9,8,1],
	[0,0,0,3,0,5,0,0,0],
	[2,1,6,7,9,0,0,0,3],
	[0,0,0,0,5,0,0,2,8],
	[1,0,3,0,0,0,0,0,0],
	[9,5,0,1,8,0,0,0,0]
	]
elif SIZE_BOARD == 4:
	pass
elif SIZE_BOARD == 5:
	bb.board = 	[[0, 0, 12, 6, 0, 0, 7, 0, 18, 0, 5, 24, 0, 10, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0], [2, 0, 19, 0, 13, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 22, 0, 0, 0, 0, 3, 0, 2, 0, 0, 14, 12, 0, 16, 8, 25, 0, 0], [0, 16, 0, 0, 0, 2, 23, 0, 0, 13, 12, 22, 0, 0, 0, 21, 15, 19, 3, 0, 0, 0, 0, 14, 0], [23, 0, 24, 0, 0, 0, 0, 0, 25, 8, 4, 0, 16, 19, 21, 0, 0, 7, 0, 0, 0, 3, 12, 0, 9], [0, 4, 0, 2, 0, 0, 0, 0, 0, 0, 0, 10, 0, 24, 12, 17, 16, 0, 0, 0, 5, 0, 0, 0, 0], [0, 0, 9, 0, 0, 6, 25, 0, 0, 0, 8, 0, 5, 3, 0, 0, 0, 0, 0, 0, 20, 0, 0, 18, 19], [15, 0, 10, 11, 0, 0, 0, 18, 12, 19, 0, 0, 0, 0, 0, 0, 0, 23, 0, 0, 7, 0, 0, 4, 0], [0, 0, 0, 0, 0, 0, 0, 14, 0, 22, 0, 0, 18, 16, 20, 0, 6, 11, 13, 0, 0, 0, 0, 0, 0], [0, 22, 0, 25, 0, 0, 1, 17, 5, 4, 7, 0, 0, 14, 0, 8, 3, 21, 0, 0, 11, 0, 0, 0, 6], [0, 20, 13, 15, 0, 0, 0, 0, 0, 0, 9, 0, 0, 2, 0, 25, 0, 1, 8, 0, 0, 5, 0, 21, 0], [0, 1, 0, 0, 0, 0, 16, 10, 0, 7, 0, 0, 4, 20, 0, 0, 9, 0, 0, 14, 0, 24, 0, 17, 0], [25, 2, 5, 0, 0, 0, 0, 0, 13, 0, 0, 0, 0, 0, 22, 0, 0, 0, 0, 0, 19, 1, 8, 0, 0], [0, 0, 7, 21, 0, 0, 12, 0, 2, 17, 0, 0, 0, 18, 6, 16, 0, 0, 15, 0, 0, 13, 0, 10, 0], [8, 10, 18, 12, 16, 9, 0, 0, 0, 5, 0, 0, 0, 0, 19, 0, 0, 17, 0, 21, 0, 15, 0, 0, 22], [0, 8, 0, 0, 15, 0, 3, 0, 6, 0, 21, 0, 0, 7, 0, 18, 14, 5, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 19, 0, 1, 0, 16, 11, 0, 0, 0, 10, 22, 25, 15, 0, 0, 0, 0, 0, 0, 21, 0, 0], [0, 3, 1, 0, 21, 0, 0, 4, 0, 0, 0, 0, 2, 0, 13, 0, 24, 25, 0, 0, 14, 0, 0, 6, 0], [0, 0, 0, 0, 0, 0, 0, 15, 0, 12, 14, 0, 6, 17, 24, 0, 0, 0, 0, 0, 0, 0, 13, 0, 0], [0, 5, 23, 16, 4, 0, 13, 24, 7, 2, 0, 9, 0, 0, 15, 3, 0, 22, 0, 0, 0, 0, 0, 0, 8], [0, 0, 25, 20, 2, 0, 19, 0, 0, 0, 0, 1, 0, 0, 0, 0, 21, 3, 0, 0, 12, 0, 0, 0, 0], [16, 12, 0, 5, 0, 11, 21, 0, 23, 0, 0, 15, 0, 0, 0, 0, 19, 9, 0, 0, 0, 0, 0, 25, 10], [0, 0, 0, 0, 9, 20, 22, 7, 4, 0, 3, 0, 14, 25, 18, 0, 11, 0, 0, 0, 0, 0, 1, 0, 15], [24, 0, 6, 0, 22, 8, 0, 25, 14, 0, 10, 11, 0, 9, 0, 20, 1, 16, 0, 7, 0, 23, 0, 0, 13], [14, 13, 21, 1, 0, 0, 5, 0, 0, 0, 6, 0, 22, 0, 23, 10, 0, 0, 0, 2, 0, 0, 18, 7, 11]]
bb.transpose()


index_selected = -1

"""

"""
bb.check_state()

timeout = -1

winner = False
delta = 0


is_running_auto = False
stack_frame = queue.LifoQueue()

def get_next_free_cell(selected_index):
	global bb
	for i in range(selected_index+1,bb.n*bb.n):
		if bb.board[i % bb.n][i // bb.n] == 0:
			return i
	return -1
def process_auto(selected_index):
	global bb, stack_frame
	#item = None # Pre-define the variable even when assigning it down both routes
	#if not stack_frame.empty():
		# Find first free spot!
	#	item = stack_frame.get()
	#	selected_index = get_next_free_cell(selected_index)
	#else:
	#	item = (-1,-1)
	#	selected_index = get_next_free_cell(-1)
	if stack_frame.empty():
		selected_index = get_next_free_cell(-1)
		item = 0
	else:
		items = stack_frame.get()
		item = items[0] # 
		time = items[1]
		selected_index = items[2] 
		if bb.cur_step > time:
			bb.rewind(time)
		# Cool.
	
	if item == bb.n:
		# Failed to assign this space, it must be a PRIOR value. 
		# Return without replacement.
		if stack_frame.empty():
			print("Unsolvable puzzle! Reverting...")
			bb.rewind(0)
		return selected_index

	new_time,success = bb.set(selected_index % bb.n, selected_index // bb.n, -(item+1))
	stack_frame.put([item+1, new_time, selected_index])
	if success:
		stack_frame.put([0, new_time, get_next_free_cell(selected_index)])
		return get_next_free_cell(selected_index)
	return selected_index

	# Idea:
	# For the selected space, try a value, and check it.
	# If it fails, push this spot on the stack with the value
	# If it succeeds, push this spot and value onto the stack
	# both return the selected index, if it succeeds then the value stayed
	# 
	
	

# __Main loop__
while running:
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			running = False
		elif e.type == pygame.MOUSEBUTTONDOWN:
			# Select this square, or unselect it if previously selected.
			pos = pygame.mouse.get_pos()
			x = pos[0] // (SIZE_CELL + LINE_WIDTH)
			y = pos[1] // (SIZE_CELL + LINE_WIDTH)
			if index_selected == y*SIZE_BOARD*SIZE_BOARD + x:
				index_selected = -1
			else:
				index_selected = y*SIZE_BOARD*SIZE_BOARD + x
		elif e.type == pygame.KEYDOWN:
			# On first type of the key....
			# GET ACTUAL KEY FROM KEY LIST!
			
			if index_selected != -1:
				key = pygame.key.name(e.key).upper()
				TX = index_selected % (SIZE_BOARD*SIZE_BOARD)
				TY = index_selected // (SIZE_BOARD*SIZE_BOARD)
				if key == "BACKSPACE":
					# Delete this space by simply setting it to zero...
					# You can not back space black tiles!!!
					if bb.board[TX][TY] < 0:
						bb.set(TX, TY, 0)
				elif key == "Z":
					# Undo key... Basically call the re-wind call.
					keys= pygame.key.get_mods()
					if keys & pygame.KMOD_LCTRL:
						bb.rewind()
				elif key == "Y":
					keys= pygame.key.get_mods()
					if keys & pygame.KMOD_LCTRL:
						bb.rewind(step = bb.cur_step + 1)
				elif key == "RIGHT":
					if index_selected < (SIZE_BOARD ** 4) - 1 and (index_selected + 1) % SIZE_BOARD**2 != 0: 
						index_selected= index_selected + 1
				elif key == "LEFT":
					if index_selected > 0  and (index_selected) % SIZE_BOARD**2 != 0:
						index_selected = index_selected - 1
				elif key == "UP":
					if index_selected >= SIZE_BOARD ** 2:
						index_selected = index_selected - SIZE_BOARD**2
				elif key == "DOWN":
					if index_selected < (SIZE_BOARD ** 4) - (SIZE_BOARD ** 2):
						index_selected = index_selected + SIZE_BOARD**2
				elif key == "S":
					# Auto solve it.
					if not is_running_auto:
						index_selected = 0
					is_running_auto = True
				elif key in TEXTS:
					# Actually try to put a number into the board (NOTE: REFRESH BOARD!)
					if bb.board[TX][TY] <= 0:
						res = bb.set(TX,TY,-TEXTS.index(key))
						if not res[1]:
							timeout = 20
						else:
							index_selected = get_next_free_cell(index_selected)
							winner = bb.check_success()
	
	if is_running_auto and not winner:
		if SIZE_BOARD > 3:
			for i in range(10**(SIZE_BOARD-2)):
				index_selected = process_auto(index_selected)
		winner = bb.check_success()

	timeout = timeout - 1
	if timeout == 0:
		bb.check_state()
	# __Board Logic__
	# __Board Rendering__
	if winner:
		special_color = (int(255 * (math.sin(delta*2*math.pi / 36.0)**2)), int(255 * (math.cos(delta*2*math.pi / 36.0)**2)), 255)
		print(special_color)
		screen.fill(special_color)
		delta = delta + 1
	else:
		screen.fill(WHITE)
	
	for i in range(SIZE_BOARD * SIZE_BOARD - 1):
		pygame.draw.line(screen, BLACK, [(SIZE_CELL*(i+1) + LINE_WIDTH*i),0], [(SIZE_CELL*(i+1) + LINE_WIDTH*i),size[1]], LINE_WIDTH if (i+1) % SIZE_BOARD != 0 else MAJOR_WIDTH)
		pygame.draw.line(screen, BLACK, [0,(SIZE_CELL*(i+1) + LINE_WIDTH*i)], [size[0],(SIZE_CELL*(i+1) + LINE_WIDTH*i)], LINE_WIDTH if (i+1) % SIZE_BOARD != 0 else MAJOR_WIDTH)
	for i in range(SIZE_BOARD * SIZE_BOARD):
		for j in range(SIZE_BOARD * SIZE_BOARD):
			if bb.board[i][j] > 0 and bb.board[i][j] < 200:
				screen.blit(texts_rects[bb.board[i][j]], (int((i+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes[bb.board[i][j]].width/2), int((j+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes[bb.board[i][j]].height/2 )))
			elif bb.board[i][j] > 0:
				screen.blit(err_texts_rects[bb.board[i][j] - 200], (int((i+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes_bold[bb.board[i][j]-200].width/2), int((j+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes_bold[bb.board[i][j]-200].height/2 )))
			elif bb.board[i][j] < 0 and bb.board[i][j] > -200:
				screen.blit(temp_texts_rects[-bb.board[i][j]], (int((i+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes[-bb.board[i][j]].width/2), int((j+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes[-bb.board[i][j]].height/2 )))
			elif bb.board[i][j] < 0:
				screen.blit(temp_err_texts_rects[-bb.board[i][j] - 200], (int((i+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes_bold[-bb.board[i][j] - 200].width/2), int((j+.5) * (SIZE_CELL + LINE_WIDTH) - texts_sizes_bold[-bb.board[i][j] - 200].height/2 )))
	if index_selected >= 0:
		TX = index_selected % (SIZE_BOARD*SIZE_BOARD)
		TY = index_selected // (SIZE_BOARD*SIZE_BOARD)
		pygame.draw.rect(screen, SELECTED_C, pygame.Rect(SIZE_CELL*(TX) + LINE_WIDTH*(TX-1), SIZE_CELL*(TY) + LINE_WIDTH*(TY-1), SIZE_CELL + LINE_WIDTH*2, SIZE_CELL + LINE_WIDTH*2), MAJOR_WIDTH)

	# __Flip pointer to the backbuffer
	pygame.display.flip()
	
	# __Limit speed of rendering by ensuring a minimum wait time
	if is_running_auto and SIZE_BOARD >= 4:
		# No tick restriction!
		pass
	elif is_running_auto and SIZE_BOARD == 3:
		clock.tick(60)
	else:
		clock.tick(30)

# Finished.
pygame.quit()
	


