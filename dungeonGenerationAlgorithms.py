'''
=============================
Dungeon Generation Algorithms
=============================

This is an implimentation of some of the dungeon generating
algorithms that are often brought up when talking about roguelikes.

Most of these algorithms have been copied from online sources.
I've included those sources where aplicable.

A lot of my implimentations of these algorithms are overly complicated
(especially in how the different algorithm classes interact with
the rest of the module). The main reason for this is that I wanted 
each of the algorithm classes to be easily portable into other
projects. My success in that reguard is up for debate.
'''

import tcod
import random
from math import sqrt
from collections import OrderedDict

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60
TEXTBOX_HEIGHT = 10

MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT - TEXTBOX_HEIGHT

USE_PREFABS = False

# ==== Display Class ====

class UserInterface:
	def __init__(self):
		tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
		tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike Dungeon Comparison', False) #TODO: Change Game Name
		self.con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		self.textBox = tcod.console_new(SCREEN_WIDTH,TEXTBOX_HEIGHT)
		self.helpText = OrderedDict([
		("1","Tunneling Algorithm"),
		("2","BSP Tree Algorithm"),
		("3","Random Walk Algorithm"),
		("4","Cellular Automata"),
		("5","Room Addition"),
		("6","City Buildings"),
		("7","Maze with Rooms"),
		("8","Messy BSP Tree"),
		("9"," "),
		("0","Change Color Scheme"),
		("Space","Remake Dungeon")
		])

		self._colorScheme = 0
		self.setColorScheme(self._colorScheme)

		global keyboard

		keyboard = tcod.Key()

		self.map = Map()
		self.map.generateLevel(MAP_WIDTH,MAP_HEIGHT)

	def mainLoop(self):

		while not tcod.console_is_window_closed():
			global keyboard

			#Input
			keyboard = tcod.console_check_for_keypress()
			exit = self.handleInput(keyboard)
			if (exit): break

			#Render
			self.renderAll()

			tcod.console_flush()

	def handleInput(self,keyboard):
		if (keyboard.vk	== tcod.KEY_ESCAPE): 
			return True #Exit Program	

		if (keyboard.vk == tcod.KEY_SPACE):
			# Generate a level based on the last generator used
			self.map.level = self.map._previousGenerator.generateLevel(MAP_WIDTH,MAP_HEIGHT)

		if (keyboard.vk == tcod.KEY_0):
			# cycle through color schemes
			self._colorScheme = (self._colorScheme+1) % len(ColorScheme._scheme)
			self.setColorScheme(self._colorScheme)

		if (keyboard.vk == tcod.KEY_1):
			# generate map with tunneling algorithm
			self.map.useTunnelingAlgorithm()

		if (keyboard.vk == tcod.KEY_2):
			# generate map with bsp tree
			self.map.useBSPTree()

		if (keyboard.vk == tcod.KEY_3):
			# generate map with drunkard's walk algorithm
			self.map.useDrunkardsWalk()

		if (keyboard.vk == tcod.KEY_4):
			# generate map with cellular automata
			self.map.useCellularAutomata()

		if (keyboard.vk == tcod.KEY_5):
			# generate map with room adition
			self.map.useRoomAddition()

		if (keyboard.vk == tcod.KEY_6):
			# generate map with cellular automata
			self.map.useCityWalls()

		if (keyboard.vk == tcod.KEY_7):
			# generate map with maze with rooms algorithm
			self.map.useMazeWithRooms()

		if (keyboard.vk == tcod.KEY_8):
			# generate map with messy bsp tree
			self.map.useMessyBSPTree()

	def renderAll(self):
		# ==== Render Level ====
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				if self.map.level[x][y] == 1:
					tcod.console_put_char_ex(self.con, x, y, '#', self.color_light_wall_fore, self.color_light_wall_back)
				else:
					tcod.console_put_char_ex(self.con, x, y, '.', self.color_light_ground_fore, self.color_light_ground_back)
	
		#TODO: Print Instructions to Screen
		self.renderTextBox()
		# ==== Blit Console to Screen ====
		tcod.console_blit(self.con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

	def renderTextBox(self):
		tcod.console_set_default_background(self.textBox, tcod.black)
		tcod.console_set_default_foreground(self.textBox, tcod.white)
		tcod.console_clear(self.textBox)

		keys = self.helpText.keys()
		x = 2
		y = 1
		for key in keys:

			tcod.console_print_ex(self.textBox,x,y,tcod.BKGND_NONE, tcod.LEFT,
				key + ") " + self.helpText[key])
			

			if 0 < (y + 2) < TEXTBOX_HEIGHT-1:
				y += 2
			else:
				x += 26
				y = 1

		tcod.console_blit(self.textBox,0,0,SCREEN_WIDTH,TEXTBOX_HEIGHT,0,0,SCREEN_HEIGHT - TEXTBOX_HEIGHT)

	def setColorScheme(self, colorScheme):
		self.color_light_wall_fore = ColorScheme._scheme[colorScheme][0]
		self.color_light_wall_back = ColorScheme._scheme[colorScheme][1]
		self.color_light_ground_fore = ColorScheme._scheme[colorScheme][2]
		self.color_light_ground_back = ColorScheme._scheme[colorScheme][3]

class ColorScheme():
	_scheme = []

	#DEFAULT
	BLUE = [
	tcod.Color(100, 100, 100),	# color_light_wall_fore
	tcod.Color(50, 50, 150),	# color_light_wall_back
	tcod.gray, 				# color_light_ground_fore
	tcod.Color(10, 10, 10) 	# color_light_ground_back
	]
	_scheme.append(BLUE)

	MAUVE = [
	tcod.Color(50, 50, 50),	# color_light_wall_fore
	tcod.Color(204, 153, 255),	# color_light_wall_back
	tcod.gray, 				# color_light_ground_fore
	tcod.Color(10, 10, 10) 	# color_light_ground_back
	]
	_scheme.append(MAUVE)

	GRAYSCALE = [
	tcod.black, 				# color_light_wall_fore
	tcod.gray,			# color_light_wall_back
	tcod.white, 				# color_light_ground_fore
	tcod.black 				# color_light_ground_back
	]
	_scheme.append(GRAYSCALE)

	TEXTONLY = [
	tcod.white, 				# color_light_wall_fore
	tcod.black,			# color_light_wall_back
	tcod.white, 				# color_light_ground_fore
	tcod.black 				# color_light_ground_back
	]
	_scheme.append(TEXTONLY)

# ==== Map Class ====

class Map:
	def __init__(self):
		self.level = []
		'''
		level values of 1 are walls
		level values of 0 are floors
		'''
		self._previousGenerator = self
		self.tunnelingAlgorithm = TunnelingAlgorithm()
		self.bspTree = BSPTree()
		self.drunkardsWalk = DrunkardsWalk()
		self.cellularAutomata = CellularAutomata()
		self.roomAddition = RoomAddition()
		self.mazeWithRooms = MazeWithRooms()

		self.cityWalls = CityWalls()

		self.messyBSPTree = MessyBSPTree()

	def generateLevel(self, MAP_WIDTH, MAP_HEIGHT):
		# Creates an empty 2D array or clears existing array
		self.level = [[0
			for y in range(MAP_HEIGHT)]
				for x in range(MAP_WIDTH)]

		return self.level

		print("Flag: map.generateLevel()")

	def useTunnelingAlgorithm(self):
		self.level = self.tunnelingAlgorithm.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.tunnelingAlgorithm

	def useBSPTree(self):
		self.level = self.bspTree.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.bspTree

	def useDrunkardsWalk(self):
		self.level = self.drunkardsWalk.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.drunkardsWalk

	def useCellularAutomata(self):
		self.level = self.cellularAutomata.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.cellularAutomata

	def useRoomAddition(self):
		self.level = self.roomAddition.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.roomAddition

	def useCityWalls(self):
		self.level = self.cityWalls.generateLevel(MAP_WIDTH, MAP_HEIGHT)
		self._previousGenerator = self.cityWalls

	def useMazeWithRooms(self):
		self.level = self.mazeWithRooms.generateLevel(MAP_WIDTH,MAP_HEIGHT)
		self._previousGenerator = self.mazeWithRooms

	def useMessyBSPTree(self):
		self.level = self.messyBSPTree.generateLevel(MAP_WIDTH,MAP_HEIGHT)
		self._previousGenerator = self.messyBSPTree

# ==== Tunneling Algorithm ====
class TunnelingAlgorithm:
	'''
	This version of the tunneling algorithm is essentially
	identical to the tunneling algorithm in the Complete Roguelike
	Tutorial using Python, which can be found at
	http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_1
	
	Requires random.randint() and the Rect class defined below.
	'''
	def __init__(self):
		self.level = []
		self.ROOM_MAX_SIZE = 15
		self.ROOM_MIN_SIZE = 6
		self.MAX_ROOMS = 30
		# TODO: raise an error if any necessary classes are missing

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		rooms = []
		num_rooms = 0

		for r in range(self.MAX_ROOMS):
			# random width and height
			w = random.randint(self.ROOM_MIN_SIZE,self.ROOM_MAX_SIZE)
			h = random.randint(self.ROOM_MIN_SIZE,self.ROOM_MAX_SIZE)
			# random position within map boundries
			x = random.randint(0, MAP_WIDTH - w -1)
			y = random.randint(0, MAP_HEIGHT - h -1)

			new_room = Rect(x, y, w, h)
			# check for overlap with previous rooms
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break

			if not failed:
				self.createRoom(new_room)
				(new_x, new_y) = new_room.center()

				if num_rooms != 0:
					# all rooms after the first one
					# connect to the previous room

					#center coordinates of the previous room
					(prev_x, prev_y) = rooms[num_rooms-1].center()

					# 50% chance that a tunnel will start horizontally
					if random.randint(0,1) == 1:
						self.createHorTunnel(prev_x, new_x, prev_y)
						self.createVirTunnel(prev_y, new_y, new_x)

					else: # else it starts virtically
						self.createVirTunnel(prev_y, new_y, prev_x)
						self.createHorTunnel(prev_x, new_x, new_y)

				# append the new room to the list
				rooms.append(new_room)
				num_rooms += 1



		return self.level

	def createRoom(self, room):
		# set all tiles within a rectangle to 0
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1+1, room.y2):
				self.level[x][y] = 0

	def createHorTunnel(self, x1, x2, y):
		for x in range(min(x1,x2),max(x1,x2)+1):
			self.level[x][y] = 0

	def createVirTunnel(self, y1, y2, x):
		for y in range(min(y1,y2),max(y1,y2)+1):
			self.level[x][y] = 0

# ==== BSP Tree ====
class BSPTree:
	def __init__(self):
		self.level = []
		self.room = None
		self.MAX_LEAF_SIZE = 24
		self.ROOM_MAX_SIZE = 15
		self.ROOM_MIN_SIZE = 6

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._leafs = []

		rootLeaf = Leaf(0,0,mapWidth,mapHeight)
		self._leafs.append(rootLeaf)

		splitSuccessfully = True
		# loop through all leaves until they can no longer split successfully
		while (splitSuccessfully):
			splitSuccessfully = False
			for l in self._leafs:
				if (l.child_1 == None) and (l.child_2 == None):
					if ((l.width > self.MAX_LEAF_SIZE) or 
					(l.height > self.MAX_LEAF_SIZE) or
					(random.random() > 0.8)):
						if (l.splitLeaf()): #try to split the leaf
							self._leafs.append(l.child_1)
							self._leafs.append(l.child_2)
							splitSuccessfully = True

		rootLeaf.createRooms(self)

		return self.level

	def createRoom(self, room):
		# set all tiles within a rectangle to 0
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1+1, room.y2):
				self.level[x][y] = 0

	def createHall(self, room1, room2):
		# connect two rooms by hallways
		x1, y1 = room1.center()
		x2, y2 = room2.center()
		# 50% chance that a tunnel will start horizontally
		if random.randint(0,1) == 1:
			self.createHorTunnel(x1, x2, y1)
			self.createVirTunnel(y1, y2, x2)

		else: # else it starts virtically
			self.createVirTunnel(y1, y2, x1)
			self.createHorTunnel(x1, x2, y2)

	def createHorTunnel(self, x1, x2, y):
		for x in range(min(x1,x2),max(x1,x2)+1):
			self.level[x][y] = 0

	def createVirTunnel(self, y1, y2, x):
		for y in range(min(y1,y2),max(y1,y2)+1):
			self.level[x][y] = 0

# ==== Drunkards Walk ====
class DrunkardsWalk:
	def __init__(self):
		self.level = []
		self._percentGoal = .4
		self.walkIterations = 25000 # cut off in case _percentGoal in never reached
		self.weightedTowardCenter = 0.15
		self.weightedTowardPreviousDirection = 0.7

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.walkIterations = max(self.walkIterations, (mapWidth*mapHeight*10))
		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._filled = 0
		self._previousDirection = None

		self.drunkardX = random.randint(2,mapWidth-2)
		self.drunkardY = random.randint(2,mapHeight-2)
		self.filledGoal = mapWidth*mapHeight*self._percentGoal

		for i in range(self.walkIterations):
			self.walk(mapWidth, mapHeight)
			if (self._filled >= self.filledGoal):
				break

		return self.level

	def walk(self,mapWidth, mapHeight):
		# ==== Choose Direction ====
		north = 1.0
		south = 1.0
		east = 1.0
		west = 1.0

		# weight the random walk against edges
		if self.drunkardX < mapWidth*0.25: # drunkard is at far left side of map
			east += self.weightedTowardCenter
		elif self.drunkardX > mapWidth*0.75: # drunkard is at far right side of map
			west += self.weightedTowardCenter
		if self.drunkardY < mapHeight*0.25: # drunkard is at the top of the map
			south += self.weightedTowardCenter
		elif self.drunkardY > mapHeight*0.75: # drunkard is at the bottom of the map
			north += self.weightedTowardCenter

		# weight the random walk in favor of the previous direction
		if self._previousDirection == "north":
			north += self.weightedTowardPreviousDirection
		if self._previousDirection == "south":
			south += self.weightedTowardPreviousDirection
		if self._previousDirection == "east":
			east += self.weightedTowardPreviousDirection
		if self._previousDirection == "west":
			west += self.weightedTowardPreviousDirection
		
		# normalize probabilities so they form a range from 0 to 1
		total = north+south+east+west

		north /= total
		south /= total
		east /= total
		west /= total

		# choose the direction
		choice = random.random()
		if 0 <= choice < north:
			dx = 0
			dy = -1
			direction = "north"
		elif north <= choice < (north+south):
			dx = 0
			dy = 1
			direction = "south"
		elif (north+south) <= choice < (north+south+east):
			dx = 1
			dy = 0
			direction = "east"
		else:
			dx = -1
			dy = 0
			direction = "west"

		# ==== Walk ====
		# check colision at edges TODO: change so it stops one tile from edge
		if (0 < self.drunkardX+dx < mapWidth-1) and (0 < self.drunkardY+dy < mapHeight-1):
			self.drunkardX += dx
			self.drunkardY += dy
			if self.level[self.drunkardX][self.drunkardY] == 1:
				self.level[self.drunkardX][self.drunkardY] = 0
				self._filled += 1
			self._previousDirection = direction

# ==== Cellular Automata ====
class CellularAutomata:
	'''
	Rather than implement a traditional cellular automata, I 
	decided to try my hand at a method discribed by "Evil
	Scientist" Andy Stobirski that I recently learned about
	on the Grid Sage Games blog.
	'''
	def __init__(self):
		self.level = []

		self.iterations = 30000
		self.neighbors = 4 # number of neighboring walls for this cell to become a wall
		self.wallProbability = 0.50 # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

		self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
		self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

		self.smoothEdges = True
		self.smoothing =  1

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.caves = []

		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self.randomFillMap(mapWidth,mapHeight)
		
		self.createCaves(mapWidth,mapHeight)

		self.getCaves(mapWidth,mapHeight)

		self.connectCaves(mapWidth,mapHeight)

		self.cleanUpMap(mapWidth,mapHeight)
		return self.level

	def randomFillMap(self,mapWidth,mapHeight):
		for y in range (1,mapHeight-1):
			for x in range (1,mapWidth-1):
				#print("(",x,y,") = ",self.level[x][y])
				if random.random() >= self.wallProbability:
					self.level[x][y] = 0

	def createCaves(self,mapWidth,mapHeight):
		# ==== Create distinct caves ====
		for i in range (0,self.iterations):
			# Pick a random point with a buffer around the edges of the map
			tileX = random.randint(1,mapWidth-2) #(2,mapWidth-3)
			tileY = random.randint(1,mapHeight-2) #(2,mapHeight-3)

			# if the cell's neighboring walls > self.neighbors, set it to 1
			if self.getAdjacentWalls(tileX,tileY) > self.neighbors:
				self.level[tileX][tileY] = 1
			# or set it to 0
			elif self.getAdjacentWalls(tileX,tileY) < self.neighbors:
				self.level[tileX][tileY] = 0

		# ==== Clean Up Map ====
		self.cleanUpMap(mapWidth,mapHeight)

	def cleanUpMap(self,mapWidth,mapHeight):
		if (self.smoothEdges):
			for i in range (0,5):
				# Look at each cell individually and check for smoothness
				for x in range(1,mapWidth-1):
					for y in range (1,mapHeight-1):
						if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
							self.level[x][y] = 0

	def createTunnel(self,point1,point2,currentCave,mapWidth,mapHeight):
		# run a heavily weighted random Walk 
		# from point1 to point1
		drunkardX = point2[0]
		drunkardY = point2[1]
		while (drunkardX,drunkardY) not in currentCave:
			# ==== Choose Direction ====
			north = 1.0
			south = 1.0
			east = 1.0
			west = 1.0

			weight = 1

			# weight the random walk against edges
			if drunkardX < point1[0]: # drunkard is left of point1
				east += weight
			elif drunkardX > point1[0]: # drunkard is right of point1
				west += weight
			if drunkardY < point1[1]: # drunkard is above point1
				south += weight
			elif drunkardY > point1[1]: # drunkard is below point1
				north += weight

			# normalize probabilities so they form a range from 0 to 1
			total = north+south+east+west
			north /= total
			south /= total
			east /= total
			west /= total

			# choose the direction
			choice = random.random()
			if 0 <= choice < north:
				dx = 0
				dy = -1
			elif north <= choice < (north+south):
				dx = 0
				dy = 1
			elif (north+south) <= choice < (north+south+east):
				dx = 1
				dy = 0
			else:
				dx = -1
				dy = 0

			# ==== Walk ====
			# check colision at edges
			if (0 < drunkardX+dx < mapWidth-1) and (0 < drunkardY+dy < mapHeight-1):
				drunkardX += dx
				drunkardY += dy
				if self.level[drunkardX][drunkardY] == 1:
					self.level[drunkardX][drunkardY] = 0

	def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
		wallCounter = 0
		#print("(",x,",",y,") = ",self.level[x][y])
		if (self.level[x][y-1] == 1): # Check north
			wallCounter += 1
		if (self.level[x][y+1] == 1): # Check south
			wallCounter += 1
		if (self.level[x-1][y] == 1): # Check west
			wallCounter += 1
		if (self.level[x+1][y] == 1): # Check east
			wallCounter += 1

		return wallCounter

	def getAdjacentWalls(self, tileX, tileY): # finds the walls in 8 directions
		pass
		wallCounter = 0
		for x in range (tileX-1, tileX+2):
			for y in range (tileY-1, tileY+2):
				if (self.level[x][y] == 1):
					if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
						wallCounter += 1
		return wallCounter

	def getCaves(self, mapWidth, mapHeight):
		# locate all the caves within self.level and stor them in self.caves
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 0:
					self.floodFill(x,y)

		for set in self.caves:
			for tile in set:
				self.level[tile[0]][tile[1]] = 0

		# check for 2 that weren't changed.
		'''
		The following bit of code doesn't do anything. I 
		put this in to help find mistakes in an earlier 
		version of the algorithm. Still, I don't really 
		want to remove it.
		'''
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 2:
					print("(",x,",",y,")")

	def floodFill(self,x,y):
		'''
		flood fill the separate regions of the level, discard
		the regions that are smaller than a minimum size, and 
		create a reference for the rest.
		'''
		cave = set()
		tile = (x,y)
		toBeFilled = set([tile])
		while toBeFilled:
			tile = toBeFilled.pop()
			
			if tile not in cave:
				cave.add(tile)
				
				self.level[tile[0]][tile[1]] = 1
				
				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)
				
				for direction in [north,south,east,west]:
	
					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in cave:
							toBeFilled.add(direction)

		if len(cave) >= self.ROOM_MIN_SIZE:
			self.caves.append(cave)

	def connectCaves(self, mapWidth, mapHeight):
		# Find the closest cave to the current cave
		for currentCave in self.caves:
			for point1 in currentCave: break # get an element from cave1
			point2 = None
			distance = 0
			for nextCave in self.caves:
				if nextCave != currentCave and not self.checkConnectivity(currentCave,nextCave):
					# choose a random point from nextCave
					for nextPoint in nextCave: break # get an element from cave1
					# compare distance of point1 to old and new point2
					newDistance = self.distanceFormula(point1,nextPoint)
					if (newDistance < distance) or distance == 0:
						point2 = nextPoint
						distance = newDistance

			if point2: # if all tunnels are connected, point2 == None
				self.createTunnel(point1,point2,currentCave,mapWidth,mapHeight)

	def distanceFormula(self,point1,point2):
		d = sqrt( (point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)
		return d

	def checkConnectivity(self,cave1,cave2):
		# floods cave1, then checks a point in cave2 for the flood

		connectedRegion = set()
		for start in cave1: break # get an element from cave1
		
		toBeFilled = set([start])
		while toBeFilled:
			tile = toBeFilled.pop()

			if tile not in connectedRegion:
				connectedRegion.add(tile)

				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)

				for direction in [north,south,east,west]:
	
					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in connectedRegion:
							toBeFilled.add(direction)

		for end in cave2: break # get an element from cave2

		if end in connectedRegion: return True

		else: return False

# ==== Room Addition ====
class RoomAddition:
	'''
	What I'm calling the Room Addition algorithm is an attempt to 
	recreate the dungeon generation algorithm used in Brogue, as
	discussed at https://www.rockpapershotgun.com/2015/07/28/how-do-roguelikes-generate-levels/
	I don't think Brian Walker has ever given a name to his
	dungeon generation algorithm, so I've taken to calling it the 
	Room Addition Algorithm, after the way in which it builds the 
	dungeon by adding rooms one at a time to the existing dungeon.
	This isn't a perfect recreation of Brian Walker's algorithm,
	but I think it's good enough to demonstrait the concept.
	'''
	def __init__(self):
		self.level = []

		self.ROOM_MAX_SIZE = 18 # max height and width for cellular automata rooms
		self.ROOM_MIN_SIZE = 16 # min size in number of floor tiles, not height and width
		self.MAX_NUM_ROOMS = 30

		self.SQUARE_ROOM_MAX_SIZE = 12
		self.SQUARE_ROOM_MIN_SIZE = 6

		self.CROSS_ROOM_MAX_SIZE = 12
		self.CROSS_ROOM_MIN_SIZE = 6

		self.cavernChance = 0.40 # probability that the first room will be a cavern
		self.CAVERN_MAX_SIZE = 35 # max height an width

		self.wallProbability = 0.45
		self.neighbors = 4

		self.squareRoomChance = 0.2
		self.crossRoomChance = 0.15

		self.buildRoomAttempts = 500
		self.placeRoomAttempts = 20
		self.maxTunnelLength = 12

		self.includeShortcuts = True
		self.shortcutAttempts = 500
		self.shortcutLength = 5
		self.minPathfindingDistance = 50

	def generateLevel(self,mapWidth,mapHeight):
		self.rooms = []

		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		# generate the first room
		room = self.generateRoom()
		roomWidth,roomHeight = self.getRoomDimensions(room)
		roomX = (mapWidth/2 - roomWidth/2)-1
		roomY = (mapHeight/2 - roomHeight/2)-1
		self.addRoom(roomX,roomY,room)
		
		# generate other rooms
		for i in range(self.buildRoomAttempts):
			room = self.generateRoom()
			# try to position the room, get roomX and roomY
			roomX,roomY,wallTile,direction, tunnelLength = self.placeRoom(room,mapWidth,mapHeight)
			if roomX and roomY:
				self.addRoom(roomX,roomY,room)
				self.addTunnel(wallTile,direction,tunnelLength)
				if len(self.rooms) >= self.MAX_NUM_ROOMS:
					break

		if self.includeShortcuts == True:
			self.addShortcuts(mapWidth,mapHeight)

		return self.level

	def generateRoom(self):
		# select a room type to generate
		# generate and return that room
		if self.rooms:
			#There is at least one room already
			choice = random.random()

			if choice <self.squareRoomChance:
				room = self.generateRoomSquare()
			elif self.squareRoomChance <= choice < (self.squareRoomChance+self.crossRoomChance):
				room = self.generateRoomCross() 
			else:
				room = self.generateRoomCellularAutomata()

		else: #it's the first room
			choice = random.random()
			if choice < self.cavernChance:
				room = self.generateRoomCavern()
			else:
				room = self.generateRoomSquare()

		return room

	def generateRoomCross(self):
		roomHorWidth = int((random.randint(self.CROSS_ROOM_MIN_SIZE+2,self.CROSS_ROOM_MAX_SIZE))/2*2)

		roomVirHeight = int((random.randint(self.CROSS_ROOM_MIN_SIZE+2,self.CROSS_ROOM_MAX_SIZE))/2*2)

		roomHorHeight = int((random.randint(self.CROSS_ROOM_MIN_SIZE,roomVirHeight-2))/2*2)

		roomVirWidth = int((random.randint(self.CROSS_ROOM_MIN_SIZE,roomHorWidth-2))/2*2)

		room = [[1
			for y in range(roomVirHeight)]
				for x in range(roomHorWidth)]

		# Fill in horizontal space
		virOffset = int(roomVirHeight/2 - roomHorHeight/2)
		for y in range(virOffset,roomHorHeight+virOffset):
			for x in range(0,roomHorWidth):
				room[x][y] = 0

		# Fill in virtical space
		horOffset = int(roomHorWidth/2 - roomVirWidth/2)
		for y in range(0,roomVirHeight):
			for x in range(horOffset,roomVirWidth+horOffset):
				room[x][y] = 0

		return room

	def generateRoomSquare(self):
		roomWidth = random.randint(self.SQUARE_ROOM_MIN_SIZE,self.SQUARE_ROOM_MAX_SIZE)
		roomHeight = random.randint(max(int(roomWidth*0.5),self.SQUARE_ROOM_MIN_SIZE),min(int(roomWidth*1.5),self.SQUARE_ROOM_MAX_SIZE))
		
		room = [[1
			for y in range(roomHeight)]
				for x in range(roomWidth)]

		room = [[0
			for y in range(1,roomHeight-1)]
				for x in range(1,roomWidth-1)]

		return room

	def generateRoomCellularAutomata(self):
		while True:
			# if a room is too small, generate another
			room = [[1
				for y in range(self.ROOM_MAX_SIZE)]
					for x in range(self.ROOM_MAX_SIZE)]

			# random fill map
			for y in range (2,self.ROOM_MAX_SIZE-2):
				for x in range (2,self.ROOM_MAX_SIZE-2):
					if random.random() >= self.wallProbability:
						room[x][y] = 0

			# create distinctive regions
			for i in range(4):
				for y in range (1,self.ROOM_MAX_SIZE-1):
					for x in range (1,self.ROOM_MAX_SIZE-1):

						# if the cell's neighboring walls > self.neighbors, set it to 1
						if self.getAdjacentWalls(x,y,room) > self.neighbors:
							room[x][y] = 1
						# otherwise, set it to 0
						elif self.getAdjacentWalls(x,y,room) < self.neighbors:
							room[x][y] = 0

			# floodfill to remove small caverns
			room = self.floodFill(room)

			# start over if the room is completely filled in
			roomWidth,roomHeight = self.getRoomDimensions(room)
			for x in range (roomWidth):
				for y in range (roomHeight):
					if room[x][y] == 0:
						return room

	def generateRoomCavern(self):
		while True:
			# if a room is too small, generate another
			room = [[1
				for y in range(self.CAVERN_MAX_SIZE)]
					for x in range(self.CAVERN_MAX_SIZE)]

			# random fill map
			for y in range (2,self.CAVERN_MAX_SIZE-2):
				for x in range (2,self.CAVERN_MAX_SIZE-2):
					if random.random() >= self.wallProbability:
						room[x][y] = 0

			# create distinctive regions
			for i in range(4):
				for y in range (1,self.CAVERN_MAX_SIZE-1):
					for x in range (1,self.CAVERN_MAX_SIZE-1):

						# if the cell's neighboring walls > self.neighbors, set it to 1
						if self.getAdjacentWalls(x,y,room) > self.neighbors:
							room[x][y] = 1
						# otherwise, set it to 0
						elif self.getAdjacentWalls(x,y,room) < self.neighbors:
							room[x][y] = 0

			# floodfill to remove small caverns
			room = self.floodFill(room)

			# start over if the room is completely filled in
			roomWidth,roomHeight = self.getRoomDimensions(room)
			for x in range (roomWidth):
				for y in range (roomHeight):
					if room[x][y] == 0:
						return room

	def floodFill(self,room):
		'''
		Find the largest region. Fill in all other regions.
		'''
		roomWidth,roomHeight = self.getRoomDimensions(room)
		largestRegion = set()

		for x in range (roomWidth):
			for y in range (roomHeight):
				if room[x][y] == 0:
					newRegion = set()
					tile = (x,y)
					toBeFilled = set([tile])
					while toBeFilled:
						tile = toBeFilled.pop()

						if tile not in newRegion:
							newRegion.add(tile)

							room[tile[0]][tile[1]] = 1

							# check adjacent cells
							x = tile[0]
							y = tile[1]
							north = (x,y-1)
							south = (x,y+1)
							east = (x+1,y)
							west = (x-1,y)

							for direction in [north,south,east,west]:

								if room[direction[0]][direction[1]] == 0:
									if direction not in toBeFilled and direction not in newRegion:
										toBeFilled.add(direction)

					if len(newRegion) >= self.ROOM_MIN_SIZE:
						if len(newRegion) > len(largestRegion):
							largestRegion.clear()
							largestRegion.update(newRegion)
		
		for tile in largestRegion:
			room[tile[0]][tile[1]] = 0

		return room

	def placeRoom(self,room, mapWidth, mapHeight): #(self,room,direction,)
		roomX = None
		roomY = None

		roomWidth, roomHeight = self.getRoomDimensions(room)

		# try n times to find a wall that lets you build room in that direction
		for i in range(self.placeRoomAttempts):
			# try to place the room against the tile, else connected by a tunnel of length i

			wallTile = None
			direction = self.getDirection()
			while not wallTile:
				'''
				randomly select tiles until you find
				a wall that has another wall in the
				chosen direction and has a floor in the 
				opposite direction.
				'''
				#direction == tuple(dx,dy)
				tileX = random.randint(1,mapWidth-2)
				tileY = random.randint(1,mapHeight-2)
				if ((self.level[tileX][tileY] == 1) and
					(self.level[tileX+direction[0]][tileY+direction[1]] == 1) and
					(self.level[tileX-direction[0]][tileY-direction[1]] == 0)):
					wallTile = (tileX,tileY)

			#spawn the room touching wallTile
			startRoomX = None
			startRoomY = None
			'''
			TODO: replace this with a method that returns a 
			random floor tile instead of the top left floor tile
			'''
			while not startRoomX and not startRoomY:
				x = random.randint(0,roomWidth-1)
				y =  random.randint(0,roomHeight-1)
				if room[x][y] == 0:
					startRoomX = wallTile[0] - x
					startRoomY = wallTile[1] - y

			#then slide it until it doesn't touch anything
			for tunnelLength in range(self.maxTunnelLength):
				possibleRoomX = startRoomX + direction[0]*tunnelLength
				possibleRoomY = startRoomY + direction[1]*tunnelLength

				enoughRoom = self.getOverlap(room,possibleRoomX,possibleRoomY,mapWidth,mapHeight)

				if enoughRoom:
					roomX = possibleRoomX 
					roomY = possibleRoomY 

					# build connecting tunnel
					#Attempt 1
					'''
					for i in range(tunnelLength+1):
						x = wallTile[0] + direction[0]*i
						y = wallTile[1] + direction[1]*i
						self.level[x][y] = 0
					'''
					# moved tunnel code into self.generateLevel()

					return roomX,roomY, wallTile, direction, tunnelLength

		return None, None, None, None, None

	def addRoom(self,roomX,roomY,room):
		roomWidth,roomHeight = self.getRoomDimensions(room)
		for x in range (roomWidth):
			for y in range (roomHeight):
				if room[x][y] == 0:
					self.level[int(roomX+x)][int(roomY+y)] = 0

		self.rooms.append(room)

	def addTunnel(self,wallTile,direction,tunnelLength):
		# carve a tunnel from a point in the room back to 
		# the wall tile that was used in its original placement
		
		startX = wallTile[0] + direction[0]*tunnelLength
		startY = wallTile[1] + direction[1]*tunnelLength
		#self.level[startX][startY] = 1
		
		for i in range(self.maxTunnelLength):
			x = startX - direction[0]*i
			y = startY - direction[1]*i
			self.level[x][y] = 0
			# If you want doors, this is where the code should go
			if ((x+direction[0]) == wallTile[0] and 
				(y+direction[1]) == wallTile[1]):
				break
		
	def getRoomDimensions(self,room):
		if room:
			roomWidth = len(room)
			roomHeight = len(room[0])
			return roomWidth, roomHeight
		else:
			roomWidth = 0
			roomHeight = 0
			return roomWidth, roomHeight

	def getAdjacentWalls(self, tileX, tileY, room): # finds the walls in 8 directions
		wallCounter = 0
		for x in range (tileX-1, tileX+2):
			for y in range (tileY-1, tileY+2):
				if (room[x][y] == 1):
					if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
						wallCounter += 1
		return wallCounter

	def getDirection(self):
		# direction = (dx,dy)
		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		direction = random.choice([north,south,east,west])
		return direction

	def getOverlap(self,room,roomX,roomY,mapWidth,mapHeight):
		'''
		for each 0 in room, check the cooresponding tile in
		self.level and the eight tiles around it. Though slow,
		that should insure that there is a wall between each of
		the rooms created in this way.
		<> check for overlap with self.level
		<> check for out of bounds
		'''
		roomWidth, roomHeight = self.getRoomDimensions(room)
		for x in range(roomWidth):
			for y in range(roomHeight):
				if room[x][y] == 0:
					# Check to see if the room is out of bounds
					if ((1 <= (x+roomX) < mapWidth-1) and
						(1 <= (y+roomY) < mapHeight-1)):
						#Check for overlap with a one tile buffer
						if self.level[x+roomX-1][y+roomY-1] == 0: # top left
							return False
						if self.level[x+roomX][y+roomY-1] == 0: # top center
							return False
						if self.level[x+roomX+1][y+roomY-1] == 0: # top right
							return False

						if self.level[x+roomX-1][y+roomY] == 0: # left
							return False
						if self.level[x+roomX][y+roomY] == 0: # center
							return False
						if self.level[x+roomX+1][y+roomY] == 0: # right
							return False																				
		
						if self.level[x+roomX-1][y+roomY+1] == 0: # bottom left
							return False
						if self.level[x+roomX][y+roomY+1] == 0: # bottom center
							return False
						if self.level[x+roomX+1][y+roomY+1] == 0: # bottom right
							return False							

					else: #room is out of bounds
						return False
		return True

	def addShortcuts(self,mapWidth,mapHeight):
		'''
		I use libtcodpy's built in pathfinding here, since I'm
		already using libtcodpy for the iu. At the moment, 
		the way I find the distance between
		two points to see if I should put a shortcut there
		is horrible, and its easily the slowest part of this
		algorithm. If I think of a better way to do this in
		the future, I'll implement it.
		'''
		
		
		#initialize the libtcodpy map
		libtcodMap = tcod.map_new(mapWidth,mapHeight)
		self.recomputePathMap(mapWidth,mapHeight,libtcodMap)

		for i in range(self.shortcutAttempts):
			# check i times for places where shortcuts can be made
			while True:
				#Pick a random floor tile
				floorX = random.randint(self.shortcutLength+1,(mapWidth-self.shortcutLength-1))
				floorY = random.randint(self.shortcutLength+1,(mapHeight-self.shortcutLength-1))
				if self.level[floorX][floorY] == 0: 
					if (self.level[floorX-1][floorY] == 1 or
						self.level[floorX+1][floorY] == 1 or
						self.level[floorX][floorY-1] == 1 or
						self.level[floorX][floorY+1] == 1):
						break

			# look around the tile for other floor tiles
			for x in range(-1,2):
				for y in range(-1,2):
					if x != 0 or y != 0: # Exclude the center tile
						newX = floorX + (x*self.shortcutLength)
						newY = floorY + (y*self.shortcutLength)
						if self.level[newX][newY] == 0:
						# run pathfinding algorithm between the two points
							#back to the libtcodpy nonesense
							pathMap = tcod.path_new_using_map(libtcodMap)
							tcod.path_compute(pathMap,floorX,floorY,newX,newY)
							distance = tcod.path_size(pathMap)

							if distance > self.minPathfindingDistance:
								# make shortcut
								self.carveShortcut(floorX,floorY,newX,newY)
								self.recomputePathMap(mapWidth,mapHeight,libtcodMap)


		# destroy the path object
		tcod.path_delete(pathMap)

	def recomputePathMap(self,mapWidth,mapHeight,libtcodMap):
		for x in range(mapWidth):
			for y in range(mapHeight):
				if self.level[x][y] == 1:
					tcod.map_set_properties(libtcodMap,x,y,False,False)
				else:
					tcod.map_set_properties(libtcodMap,x,y,True,True)

	def carveShortcut(self,x1,y1,x2,y2):
		if x1-x2 == 0:
			# Carve virtical tunnel
			for y in range(min(y1,y2),max(y1,y2)+1):
				self.level[x1][y] = 0

		elif y1-y2 == 0:
			# Carve Horizontal tunnel
			for x in range(min(x1,x2),max(x1,x2)+1):
				self.level[x][y1] = 0

		elif (y1-y2)/(x1-x2) == 1:
			# Carve NW to SE Tunnel
			x = min(x1,x2)
			y = min(y1,y2)
			while x != max(x1,x2):
				x+=1
				self.level[x][y] = 0
				y+=1
				self.level[x][y] = 0

		elif (y1-y2)/(x1-x2) == -1:
			# Carve NE to SW Tunnel
			x = min(x1,x2)
			y = max(y1,y2)
			while x != max(x1,x2):
				x += 1
				self.level[x][y] = 0
				y -= 1
				self.level[x][y] = 0

	def checkRoomExists(self,room):
		roomWidth, roomHeight = self.getRoomDimensions(room)
		for x in range(roomWidth):
			for y in range(roomHeight):
				if room[x][y] == 0:
					return True
		return False

# ==== City Walls ====
class CityWalls:
	'''
	The City Walls algorithm is very similar to the BSP Tree
	above. In fact their main difference is in how they generate
	rooms after the actual tree has been created. Instead of 
	starting with an array of solid walls and carving out
	rooms connected by tunnels, the City Walls generator
	starts with an array of floor tiles, then creates only the
	exterior of the rooms, then opens one wall for a door.
	'''
	def __init__(self):
		self.level = []
		self.room = None
		self.MAX_LEAF_SIZE = 30
		self.ROOM_MAX_SIZE = 16
		self.ROOM_MIN_SIZE = 8

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.level = [[0
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._leafs = []
		self.rooms = []

		rootLeaf = Leaf(0,0,mapWidth,mapHeight)
		self._leafs.append(rootLeaf)

		splitSuccessfully = True
		# loop through all leaves until they can no longer split successfully
		while (splitSuccessfully):
			splitSuccessfully = False
			for l in self._leafs:
				if (l.child_1 == None) and (l.child_2 == None):
					if ((l.width > self.MAX_LEAF_SIZE) or 
					(l.height > self.MAX_LEAF_SIZE) or
					(random.random() > 0.8)):
						if (l.splitLeaf()): #try to split the leaf
							self._leafs.append(l.child_1)
							self._leafs.append(l.child_2)
							splitSuccessfully = True

		rootLeaf.createRooms(self)
		self.createDoors()

		return self.level

	def createRoom(self, room):
		# Build Walls
		# set all tiles within a rectangle to 1
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1+1, room.y2):
				self.level[x][y] = 1
		# Build Interior
		for x in range(room.x1+2,room.x2-1):
			for y in range(room.y1+2,room.y2-1):
				self.level[x][y] = 0

	def createDoors(self):
		for room in self.rooms:
			(x,y) = room.center()

			wall = random.choice(["north","south","east","west"])
			if wall == "north":
				wallX = x
				wallY = room.y1 +1
			elif wall == "south":
				wallX = x
				wallY = room.y2 -1
			elif wall == "east":
				wallX = room.x2 -1
				wallY = y
			elif wall == "west":
				wallX = room.x1 +1
				wallY = y

			self.level[wallX][wallY] = 0

	def createHall(self, room1, room2):
		# This method actually creates a list of rooms,
		# but since it is called from an outside class that is also
		# used by other dungeon Generators, it was simpler to 
		# repurpose the createHall method that to alter the leaf class.
		for room in [room1, room2]:
			if room not in self.rooms:
				self.rooms.append(room)

# ==== Maze With Rooms ====
class MazeWithRooms:
	'''
	Python implimentation of the rooms and mazes algorithm found at
	http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/
	by Bob Nystrom
	'''
	def __init__(self):
		self.level = []

		self.ROOM_MAX_SIZE = 13
		self.ROOM_MIN_SIZE = 6


		self.buildRoomAttempts = 100
		self.connectionChance = 0.04
		self.windingPercent = 0.1
		self.allowDeadEnds = False

	def generateLevel(self,mapWidth,mapHeight):
		# The level dimensions must be odd
		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]
		if (mapWidth % 2 == 0): mapWidth -= 1
		if (mapHeight % 2 == 0): mapHeight -= 1

		self._regions = [[ None
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._currentRegion = -1 # the index of the current region in _regions

		self.addRooms(mapWidth,mapHeight)#?

		# Fill in the empty space around the rooms with mazes
		for y in range (1,mapHeight,2):
			for x in range(1,mapWidth,2):
				if self.level[x][y] != 1:
					continue
				start = (x,y)
				self.growMaze(start,mapWidth,mapHeight)

		self.connectRegions(mapWidth,mapHeight)

		if not self.allowDeadEnds: 
			self.removeDeadEnds(mapWidth,mapHeight)

		return self.level

	def growMaze(self,start,mapWidth,mapHeight):
		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		cells = []
		lastDirection = None

		self.startRegion()
		self.carve(start[0],start[1])

		cells.append(start)

		while cells:
			cell = cells[-1]

			# see if any adjacent cells are open
			unmadeCells = set()

			'''
			north = (0,-1)
			south = (0,1)
			east = (1,0)
			west = (-1,0)
			'''
			for direction in [north,south,east,west]:
				if self.canCarve(cell,direction,mapWidth,mapHeight):
					unmadeCells.add(direction)

			if (unmadeCells):
				'''
				Prefer to carve in the same direction, when
				it isn't necessary to do otherwise.
				'''
				if ((lastDirection in unmadeCells) and
					(random.random() > self.windingPercent)):
					direction = lastDirection
				else:
					direction = unmadeCells.pop()

				newCell = ((cell[0]+direction[0]),(cell[1]+direction[1]))
				self.carve(newCell[0],newCell[1])

				newCell = ((cell[0]+direction[0]*2),(cell[1]+direction[1]*2))
				self.carve(newCell[0],newCell[1])
				cells.append(newCell)

				lastDirection = direction

			else:
				# No adjacent uncarved cells
				cells.pop()
				lastDirection = None

	def addRooms(self,mapWidth,mapHeight):
		rooms = []
		for i in range(self.buildRoomAttempts):

			'''
			Pick a random room size and ensure that rooms have odd 
			dimensions and that rooms are not too narrow.
			'''
			roomWidth = random.randint(int(self.ROOM_MIN_SIZE/2),int(self.ROOM_MAX_SIZE/2))*2+1
			roomHeight = random.randint(int(self.ROOM_MIN_SIZE/2),int(self.ROOM_MAX_SIZE/2))*2+1
			x = int((random.randint(0,mapWidth-roomWidth-1)/2)*2+1)
			y = int((random.randint(0,mapHeight-roomHeight-1)/2)*2+1)

			room = Rect(x,y,roomWidth,roomHeight)
			# check for overlap with previous rooms
			failed = False
			for otherRoom in rooms:
				if room.intersect(otherRoom):
					failed = True
					break

			if not failed:
				rooms.append(room)

				self.startRegion()
				self.createRoom(room)

	def connectRegions(self,mapWidth,mapHeight):
		# Find all of the tiles that can connect two regions
		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		connectorRegions = [[ None
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		for x in range(1,mapWidth-1):
			for y in range(1,mapHeight-1):
				if self.level[x][y] != 1: continue

				# count the number of different regions the wall tile is touching
				regions = set()
				for direction in [north,south,east,west]:
					newX = x + direction[0]
					newY = y + direction[1]
					region = self._regions[newX][newY]
					if region != None: 
						regions.add(region)

				if (len(regions) < 2): continue

				# The wall tile touches at least two regions
				connectorRegions[x][y] = regions

		# make a list of all of the connectors
		connectors = set()
		for x in range(0,mapWidth):
			for y in range(0,mapHeight):
				if connectorRegions[x][y]:
					connectorPosition = (x,y)
					connectors.add(connectorPosition)

		# keep track of the regions that have been merged.
		merged = {}
		openRegions = set()
		for i in range(self._currentRegion+1):
			merged[i] = i
			openRegions.add(i)

		# connect the regions
		while len(openRegions) > 1:
			# get random connector
			#connector = connectors.pop()
			for connector in connectors: break

			# carve the connection
			self.addJunction(connector)

			# merge the connected regions
			x = connector[0]
			y = connector[1]
			
			# make a list of the regions at (x,y)
			regions = []
			for n in connectorRegions[x][y]:
				# get the regions in the form of merged[n]
				actualRegion = merged[n]
				regions.append(actualRegion)
				
			dest = regions[0]
			sources = regions[1:]

			'''
			Merge all of the effective regions. You must look
			at all of the regions, as some regions may have
			previously been merged with the ones we are
			connecting now.
			'''
			for i in range(self._currentRegion+1):
				if merged[i] in sources:
					merged[i] = dest

			# clear the sources, they are no longer needed
			for s in sources:
				openRegions.remove(s)

			# remove the unneeded connectors
			toBeRemoved = set()
			for pos in connectors:
				# remove connectors that are next to the current connector
				if self.distance(connector,pos) < 2:
					# remove it
					toBeRemoved.add(pos)
					continue

				regions = set()
				x = pos[0]
				y = pos[1]
				for n in connectorRegions[x][y]:
					actualRegion = merged[n]
					regions.add(actualRegion)
				if len(regions) > 1: 
					continue

				if random.random() < self.connectionChance:
					self.addJunction(pos)

				# remove it
				if len(regions) == 1:
					toBeRemoved.add(pos)

			connectors.difference_update(toBeRemoved)

	def createRoom(self, room):
		# set all tiles within a rectangle to 0
		for x in range(room.x1, room.x2):
			for y in range(room.y1, room.y2):
				self.carve(x,y)

	def addJunction(self,pos):
		self.level[pos[0]][pos[1]] = 0

	def removeDeadEnds(self,mapWidth,mapHeight):
		done = False

		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		while not done:
			done = True

			for y in range(1,mapHeight):
				for x in range(1,mapWidth):
					if self.level[x][y] == 0:
						
						exits = 0
						for direction in [north,south,east,west]:
							if self.level[x+direction[0]][y+direction[1]] == 0:
								exits += 1
						if exits > 1: continue

						done = False
						self.level[x][y] = 1

	def canCarve(self,pos,dir,mapWidth,mapHeight):
		'''
		gets whether an opening can be carved at the location
		adjacent to the cell at (pos) in the (dir) direction.
		returns False if the location is out of bounds or if the cell
		is already open.
		'''
		x = pos[0]+dir[0]*3
		y = pos[1]+dir[1]*3

		if not (0 < x < mapWidth) or not (0 < y < mapHeight):
			return False

		x = pos[0]+dir[0]*2
		y = pos[1]+dir[1]*2

		# return True if the cell is a wall (1)
		# false if the cell is a floor (0)
		return (self.level[x][y] == 1)

	def distance(self,point1,point2):
		d = sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
		return d

	def startRegion(self):
		self._currentRegion += 1

	def carve(self,x,y):
		self.level[x][y] = 0
		self._regions[x][y] = self._currentRegion

# ==== Maze ====

#==== Messy BSP Tree ====
class MessyBSPTree:
	'''
	A Binary Space Partition connected by a severely weighted
	drunkards walk algorithm.
	Requires Leaf and Rect classes.
	'''
	def __init__(self):
			self.level = []
			self.room = None
			self.MAX_LEAF_SIZE = 24
			self.ROOM_MAX_SIZE = 15
			self.ROOM_MIN_SIZE = 6
			self.smoothEdges = True
			self.smoothing = 1
			self.filling = 3

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.mapWidth = mapWidth
		self.mapHeight = mapHeight
		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._leafs = []

		rootLeaf = Leaf(0,0,mapWidth,mapHeight)
		self._leafs.append(rootLeaf)

		splitSuccessfully = True
		# loop through all leaves until they can no longer split successfully
		while (splitSuccessfully):
			splitSuccessfully = False
			for l in self._leafs:
				if (l.child_1 == None) and (l.child_2 == None):
					if ((l.width > self.MAX_LEAF_SIZE) or 
					(l.height > self.MAX_LEAF_SIZE) or
					(random.random() > 0.8)):
						if (l.splitLeaf()): #try to split the leaf
							self._leafs.append(l.child_1)
							self._leafs.append(l.child_2)
							splitSuccessfully = True

		rootLeaf.createRooms(self)
		self.cleanUpMap(mapWidth,mapHeight)

		return self.level

	def createRoom(self, room):
		# set all tiles within a rectangle to 0
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1+1, room.y2):
				self.level[x][y] = 0

	def createHall(self, room1, room2):
		# run a heavily weighted random Walk 
		# from point2 to point1
		drunkardX, drunkardY = room2.center()
		goalX,goalY = room1.center()
		while not (room1.x1 <= drunkardX <= room1.x2) or not (room1.y1 < drunkardY < room1.y2): #
			# ==== Choose Direction ====
			north = 1.0
			south = 1.0
			east = 1.0
			west = 1.0

			weight = 1

			# weight the random walk against edges
			if drunkardX < goalX: # drunkard is left of point1
				east += weight
			elif drunkardX > goalX: # drunkard is right of point1
				west += weight
			if drunkardY < goalY: # drunkard is above point1
				south += weight
			elif drunkardY > goalY: # drunkard is below point1
				north += weight

			# normalize probabilities so they form a range from 0 to 1
			total = north+south+east+west
			north /= total
			south /= total
			east /= total
			west /= total

			# choose the direction
			choice = random.random()
			if 0 <= choice < north:
				dx = 0
				dy = -1
			elif north <= choice < (north+south):
				dx = 0
				dy = 1
			elif (north+south) <= choice < (north+south+east):
				dx = 1
				dy = 0
			else:
				dx = -1
				dy = 0

			# ==== Walk ====
			# check colision at edges
			if (0 < drunkardX+dx < self.mapWidth-1) and (0 < drunkardY+dy < self.mapHeight-1):
				drunkardX += dx
				drunkardY += dy
				if self.level[drunkardX][drunkardY] == 1:
					self.level[drunkardX][drunkardY] = 0

	def cleanUpMap(self,mapWidth,mapHeight):
		if (self.smoothEdges):
			for i in range (3):
				# Look at each cell individually and check for smoothness
				for x in range(1,mapWidth-1):
					for y in range (1,mapHeight-1):
						if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
							self.level[x][y] = 0

						if (self.level[x][y] == 0) and (self.getAdjacentWallsSimple(x,y) >= self.filling):
							self.level[x][y] = 1

	def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
		wallCounter = 0
		#print("(",x,",",y,") = ",self.level[x][y])
		if (self.level[x][y-1] == 1): # Check north
			wallCounter += 1
		if (self.level[x][y+1] == 1): # Check south
			wallCounter += 1
		if (self.level[x-1][y] == 1): # Check west
			wallCounter += 1
		if (self.level[x+1][y] == 1): # Check east
			wallCounter += 1

		return wallCounter

# ==== TinyKeep ====
'''
https://www.reddit.com/r/gamedev/comments/1dlwc4/procedural_dungeon_generation_algorithm_explained/
and
http://www.gamasutra.com/blogs/AAdonaac/20150903/252889/Procedural_Dungeon_Generation_Algorithm.php
'''

# ==== Helper Classes ====
class Rect: # used for the tunneling algorithm
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x+w
		self.y2 = y+h

	def center(self):
		centerX = int((self.x1 + self.x2)/2)
		centerY = int((self.y1 + self.y2)/2)
		return (centerX, centerY)

	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
			self.y1 <= other.y2 and self.y2 >= other.y1)

class Leaf: # used for the BSP tree algorithm
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.MIN_LEAF_SIZE = 10
		self.child_1 = None
		self.child_2 = None
		self.room = None
		self.hall = None

	def splitLeaf(self):
		# begin splitting the leaf into two children
		if (self.child_1 != None) or (self.child_2 != None):
			return False # This leaf has already been split

		'''
		==== Determine the direction of the split ====
		If the width of the leaf is >25% larger than the height,
		split the leaf vertically.
		If the height of the leaf is >25 larger than the width,
		split the leaf horizontally.
		Otherwise, choose the direction at random.
		'''
		splitHorizontally = random.choice([True, False])
		if (self.width/self.height >= 1.25):
			splitHorizontally = False
		elif (self.height/self.width >= 1.25):
			splitHorizontally = True

		if (splitHorizontally):
			max = self.height - self.MIN_LEAF_SIZE
		else:
			max = self.width - self.MIN_LEAF_SIZE

		if (max <= self.MIN_LEAF_SIZE):
			return False # the leaf is too small to split further

		split = random.randint(self.MIN_LEAF_SIZE,max) #determine where to split the leaf

		if (splitHorizontally):
			self.child_1 = Leaf(self.x, self.y, self.width, split)
			self.child_2 = Leaf( self.x, self.y+split, self.width, self.height-split)
		else:
			self.child_1 = Leaf( self.x, self.y,split, self.height)
			self.child_2 = Leaf( self.x + split, self.y, self.width-split, self.height)

		return True

	def createRooms(self, bspTree):
		if (self.child_1) or (self.child_2):
			# recursively search for children until you hit the end of the branch
			if (self.child_1):
				self.child_1.createRooms(bspTree)
			if (self.child_2):
				self.child_2.createRooms(bspTree)

			if (self.child_1 and self.child_2):
				bspTree.createHall(self.child_1.getRoom(),
					self.child_2.getRoom())

		else:
		# Create rooms in the end branches of the bsp tree
			w = random.randint(bspTree.ROOM_MIN_SIZE, min(bspTree.ROOM_MAX_SIZE,self.width-1))
			h = random.randint(bspTree.ROOM_MIN_SIZE, min(bspTree.ROOM_MAX_SIZE,self.height-1))
			x = random.randint(self.x, self.x+(self.width-1)-w)
			y = random.randint(self.y, self.y+(self.height-1)-h)
			self.room = Rect(x,y,w,h)
			bspTree.createRoom(self.room)

	def getRoom(self):
		if (self.room): return self.room

		else:
			if (self.child_1):
				self.room_1 = self.child_1.getRoom()
			if (self.child_2):
				self.room_2 = self.child_2.getRoom()

			if (not self.child_1 and not self.child_2):
				# neither room_1 nor room_2
				return None

			elif (not self.room_2):
				# room_1 and !room_2
				return self.room_1

			elif (not self.room_1):
				# room_2 and !room_1
				return self.room_2

			# If both room_1 and room_2 exist, pick one
			elif (random.random() < 0.5):
				return self.room_1
			else:
				return self.room_2

class Prefab(Rect):
	pass

if __name__ == "__main__":
	ui = UserInterface()
	ui.mainLoop()
