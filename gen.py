# Get xRooms, yRooms and Room size
# Pick random room as spawn point
# Connect to unconnected neighbour
# Make that cell the current room
# Rinse. Repeat for all neighbours
# Within each room randomise interior.
# add staircases and corrdors to connect between cells

import random
import itertools
import sys


class Room(object):
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.isConnected = False
        self.connectedRooms = []
        self.interior = None

    def connect(self, next):
        self.connectedRooms.append(next)
        next.connectedRooms.append(self)
        self.isConnected = True
        next.isConnected = True

    def str(self):
        return "ID : "+str(self.id)+" X : "+str(self.x)+" Y : "+str(self.y)



def AStar(start, goal):
    def heuristic(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def reconstructPath(n):
        if n == start:
            return [n]
        return reconstructPath(cameFrom[n]) + [n]

    def neighbors(n):
        x, y = n
        return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

    closed = set()
    open = set()
    open.add(start)
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, goal)}

    while open:
        current = None
        for i in open:
            if current is None or fScore[i] < fScore[current]:
                current = i

        if current == goal:
            return reconstructPath(goal)

        open.remove(current)
        closed.add(current)

        for neighbor in neighbors(current):
            if neighbor in closed:
                continue
            g = gScore[current] + 1

            if neighbor not in open or g < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = g
                fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open:
                    open.add(neighbor)
    return ()


def genesis(sizeX, sizeY, roomSize):
    rooms = {}
    for x in range(sizeX):
        for y in range(sizeX):
            room = Room(x , y, len(rooms))
            rooms[(x,y)] = room

    currentRoom = firstRoom = lastRoom = random.choice(list(rooms.values()))
    currentRoom.isConnected = True

    # print(currentRoom.str())

    def getAllNeighbours(room):
        for x, y in ((-1,0),(0,-1),(1,0),(0,1)):
            try:
                yield(rooms[(room.x + x, room.y + y)])
            except:
                continue

    while True:
        unconnected = list(filter(lambda x: not x.isConnected, getAllNeighbours(currentRoom)))
        # unconnected = [x for x in getAllNeighbours(currentRoom) if not x.isConnected]
        if not unconnected:
            break

        neighbor = random.choice(unconnected)
        currentRoom.connect(neighbor)
        currentRoom = lastRoom = neighbor

    while list(filter(lambda x: not x.isConnected, rooms.values())):
        candidates = []
        for room in list(filter(lambda x: x.isConnected, rooms.values())):
            neighbors = list(filter(lambda x: not x.isConnected, getAllNeighbours(room)))
            if not neighbors:
                continue
            candidates.append((room, neighbors))
        room, neighbors = random.choice(candidates)
        room.connect(random.choice(neighbors))

    extraConnections = random.randint(int((sizeX + sizeY) / 4), int((sizeX + sizeY) / 1.2))
    maxRetries = 10
    while extraConnections > 0 and maxRetries > 0:
        room = random.choice(list(rooms.values()))
        neighbor = random.choice(list(getAllNeighbours(room)))
        if room in neighbor.connectedRooms:
            maxRetries -= 1
            continue
        room.connect(neighbor)
        extraConnections -= 1

    #  create a room of random shape
    roomInteriors = []
    for room in list(rooms.values()):
        width = random.randint(3, roomSize - 2)
        height = random.randint(3, roomSize - 2)
        x = (room.x * roomSize) + random.randint(1, roomSize - width - 1)
        y = (room.y * roomSize) + random.randint(1, roomSize - height - 1)
        floorTiles = []
        for i in range(width):
            for j in range(height):
                floorTiles.append((x + i, y + j))
        room.interior = floorTiles
        roomInteriors.append(floorTiles)

    connections = {}
    for c in list(rooms.values()):
        for other in c.connectedRooms:
            connections[tuple(sorted((c.id, other.id)))] = (c.interior, other.interior)
    for a, b in list(connections.values()):
        # 7a. Create a random corridor between the rooms in each cell.
        start = random.choice(a)
        end = random.choice(b)

        corridor = []
        for tile in AStar(start, end):
            if tile not in a and not tile in b:
                corridor.append(tile)
        roomInteriors.append(corridor)

    stairsUp = random.choice(firstRoom.interior)
    stairsDown = random.choice(lastRoom.interior)

    # create tiles
    tiles = {}
    tilesX = sizeX * roomSize
    tilesY = sizeY * roomSize
    for x in range(tilesX):
        for y in range(tilesY):
            tiles[(x, y)] = " "
    for xy in itertools.chain.from_iterable(roomInteriors):
        tiles[xy] = "."

    def getNeighborTiles(xy):
        tx, ty = xy
        for x, y in ((-1, -1), (0, -1), (1, -1),
                     (-1, 0), (1, 0),
                     (-1, 1), (0, 1), (1, 1)):
            try:
                yield tiles[(tx + x, ty + y)]
            except KeyError:
                continue

    for xy, tile in tiles.items():
        if not tile == "." and "." in getNeighborTiles(xy):
            tiles[xy] = "#"
    tiles[stairsUp] = "<"
    tiles[stairsDown] = ">"

    for y in range(tilesY):
        for x in range(tilesX):
            sys.stdout.write(tiles[(x, y)])
        sys.stdout.write("\n")

    return tiles





if len(sys.argv) != 4:
    print("Usage: python3 gen.py <number of rows> <number of columns> <size of each room>")
    print("Example: python3 gen.py 5 6 8")
else:
    genesis(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
