#!/usr/bin/env python3.8

import pygame
import numpy as np
import time as t
import sys as s

#second implementation of Conway's game of life, with random inital seed and toroidal borders

#colors:
col_to_die = (255,140,117)
col_alive = (252, 84, 119)
col_background = (10,10,40) #Blackblue
col_grid = (30,30,60) #grey ish
col_born = (252, 182, 254)#alive!


def main(width,height,cellsize):
    #print("\nType 'r' for a random seed, 's' for a 'Gosper-Glider' generator, or 'p' for a pantamino pattern,  and press enter.")
    #path = input("\nr/s/p: ")
    #if path == 'r' or path == 's' or path =='p':
    pygame.init() #initialize pygame
    surface = pygame.display.set_mode((width*cellsize,height*cellsize)) #set dimensions of board and cellsize -  WIDTH X HEIGHT    ~ special display surface
    pygame.display.set_caption("Game Of Life")
    cells = init(width,height) #passes width and height to init game
    while True:
        for event in pygame.event.get(): #event loop: script will quit if user exits window
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        surface.fill(col_grid) #fills surface with color
        cells = update(surface,cells,cellsize,width,height) #updates grid config
        pygame.display.update() #updates display from new .draw in update function
    else:
        exit()

def init(width,height):
    cells = np.zeros((width,height))
    #if path == 's':
        #pattern = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
                            #[1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],          #Gosper glider gun pattern
                            #[1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                            #[0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]);
        #pos = (3,3)
        #cells[pos[0]:pos[0]+pattern.shape[0],\
              #pos[1]:pos[1]+pattern.shape[1]] = pattern #magic
        #return cells
    #elif path == 'p':
        #pattern = np.array([[0, 1, 1], [1, 1, 0], [0, 1, 0]]); #R-pentamino
        #pos = (52,45)
        #cells[pos[0]:pos[0]+pattern.shape[0],\
                     #pos[1]:pos[1]+pattern.shape[1]] = pattern #magic
        #return cells
    #elif path == 'r':
    cells = np.asarray(np.random.randint(0,2,(width,height))) #initialize random seed
    return cells

def update(surface,cells,cellsize,width,height):

    next_ = np.zeros((cells.shape[0],cells.shape[1])) #initialie matrix of 0 - only live cells will be added
    for r, c in np.ndindex(cells.shape): #iterates through all cells in cells matrix
        update = False
        nearby_alive = alive_neighbors(cells,r,c,width,height) #get number of alive neighbors for each cell
        if (cells[r, c] == 1) and (nearby_alive < 2 or nearby_alive >3): #if cell alive, and nearby is less than 2 or more than 3 - die
            col = col_alive
        elif (cells[r, c] == 1) and (2 <= nearby_alive <= 3):  #if cell alive, an nearby is less or equal 3, OR cell dead and nearby alive equal 3 - birth
            next_[r, c] = 1
            col = col_alive
        elif (cells[r, c] == 0) and (nearby_alive == 3):  #cell is born
            next_[r,c] = 2 #born cells will be grn
        elif (cells[r, c] == 2) and (nearby_alive < 2) or (nearby_alive > 3): #die
            col = col_alive
        elif (cells[r, c] == 2) and (2 <= nearby_alive or nearby_alive <= 3):  #if cell alive, an nearby is less or equal 3, OR cell dead and nearby alive equal 3 - birth
            next_[r, c] = 1
            col = col_born #grn
        col = col if cells[r, c] == 1 or cells[r, c] == 2 else col_background #dead cells are background color
        pygame.draw.rect(surface, col, (r*cellsize, c*cellsize, \
                                        cellsize-.9, cellsize-.9)) #draw new cell

        #pygame.draw.circle(surface, col, [r*cellsize,c*cellsize], 3.5)
    #t.sleep(.2)
    return next_

def alive_neighbors(cells,r,c,width,height):
    leftcoord = (r-1) % width       #WIDTH IS WRAPPING - toroidal boundary conditions, meaning that the square grid wraps around so that its shape is a torus
    rightcoord = (r+1) % width      #e.g. : if on edge, width = 100, r = 99,  rightcoord = (r+1) % width  rightcoord then equals 0, or start   eg...    (1%10)=1
    abovecoord = (c-1) % height
    belowcoord = (c+1) % height
    #CHECK NEIGHBOR STATS
    neighbors = 0 #counter for live neighbors
    if cells[leftcoord][abovecoord] == 1 or cells[leftcoord][abovecoord] == 2:           #X#
        neighbors+=1#leftabove                                                            #C#
    if cells[r][abovecoord] == 1 or cells[r][abovecoord] == 2:                             #Y#
        neighbors+=1#above
    if cells[rightcoord][abovecoord] == 1 or cells[rightcoord][abovecoord] == 2:
        neighbors+=1#aboveright
    if cells[leftcoord][c] == 1 or cells[leftcoord][c] == 2:
        neighbors+=1#left
    if cells[rightcoord][c] == 1 or cells[rightcoord][c] == 2:
        neighbors+=1#right
    if cells[leftcoord][belowcoord] == 1 or cells[leftcoord][belowcoord] == 2:
        neighbors+=1#belowleft
    if cells[r][belowcoord] == 1 or cells[r][belowcoord] == 2:
        neighbors+=1#middleblow
    if cells[rightcoord][belowcoord] == 1 or cells[rightcoord][belowcoord] == 2:
        neighbors+=1#belowright

    return neighbors

#main(115,75,9)
main(200,130,5)

#only update changing cells using dirty rect animation https://www.pygame.org/docs/tut/newbieguide.html
#brief pause to view seed
