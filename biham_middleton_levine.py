#!/usr/bin/env python3.8

import pygame
import numpy as np
import matplotlib.pyplot as plt
import time
import math
import powerlaw 


#imnplementation of Biham_Middleton_Levine cellular automota

#blue cells move down
#red cells move right
#blue cell yields to red

#colors:
col_grid = (255, 255, 204) #lightblue
empty = (255, 255, 204) #fug
red_cell = (241,0,0)
blue_cell = (20,0,218)




def main(width,height,cellsize,density):
    counter = 0
    pygame.init() #initialize pygame
    surface = pygame.display.set_mode((width*cellsize,height*cellsize)) #set dimensions of board and cellsize -  WIDTH X HEIGHT
    cells,density_report = init(width,height,density) #passes width and height to init game
    pygame.display.set_caption(f"Density: {round(density_report,2)} %")
    
    #main program loop
    global ratio_red_jammed,ratio_blue_jammed,ratio_all_jammed,delta_jammed

    ratio_red_jammed = [0]
    ratio_blue_jammed = [0]
    ratio_all_jammed = [0]
    delta_jammed =[]
    

    while True:
        for event in pygame.event.get(): #event loop: script will quit if user exits window
            
            if event.type == pygame.QUIT:
                pygame.quit()
    
                
                plt.figure(figsize=(12,7))
                # An "interface" to matplotlib.axes.Axes.hist() method
                n, bins, patches = plt.hist(x=ratio_all_jammed[1:], bins='auto', color='red',
                                            alpha=0.8, rwidth=0.85)
                
                #plot avalanches histrogram - i.e. the delta jammed 
                plt.xlabel('Ratio Jammed')
                plt.ylabel('Frequency')
                plt.title('Ratio of jammed Cells in any given Epoch')
               

                #plot avalanches - i.e. the delta jammed 
                plt.figure(figsize=(12,7))
                plt.scatter((np.arange(0,len(delta_jammed[5:]),1)),sorted(delta_jammed[5:],reverse=True),c='red',s=3)
                plt.title("Change in number of cells jammed from one Epoch to the next")
                plt.ylabel("Delta Ratio Jammed")
                plt.setp(plt.gcf().get_axes(), xticks=[])
                #test for linearity
                # plt.yscale('log')
                # plt.xscale('log')

                #plt ratios of jammed traffic
                plt.figure(figsize=(12,7))
                plt.plot(np.arange(0,len(ratio_red_jammed[5:]),1),ratio_red_jammed[5:],c='r',linewidth=1.3)
                plt.plot(np.arange(0,len(ratio_blue_jammed[5:]),1),ratio_blue_jammed[5:],c='b',linewidth=1.3)
                plt.plot(np.arange(0,len(ratio_all_jammed[5:]),1),ratio_all_jammed[5:],c='g',linewidth=1.3)
                plt.xlabel("Epoch")
                plt.ylabel("Jammed/Flowing") 
                plt.title(f"Ratio of Jammed Cells to Flowing Cells --- Density: {density} % ")
    
                plt.show()
                return

        surface.fill(col_grid) #fills surface with color
        cells = update(surface,cells,cellsize,width,height,counter) #updates grid config
        counter += 1 #red then blue then red...
        if counter == 2:
            counter = 0
        pygame.display.update() #updates display from new .draw in update function



def init(width,height,density):

    #generate an array with desired density 
    leftover = 1 - density
    n = width * height
    cells = np.random.choice([1,2,0],n,p=[density/2,density/2,leftover])
    cells = cells.reshape(width,height)
    
    density_report = np.count_nonzero(cells)/(width*height)*100
    print(f"\nThe density of the board init is: {density_report}  %")
    return cells, density_report



def update(surface,cells,cellsize,width,height,counter):
    next_ = np.zeros((cells.shape[0],cells.shape[1])) #initialie matrix of 0 - only live cells will be added
    
    red_jammed = 0
    blue_jammed = 0
    
    for r, c in np.ndindex(cells.shape): #iterates through all cells in cells matrix
        
        rightcoord = (r+1) % width                      #width and height wrap toroidally
        belowcoord = (c+1) % height

        if counter == 0:
            if cells[r,c] == 0:
                col = (255, 255, 204)
            
            elif cells[r,c] == 1: #red cell
                if cells[rightcoord,c] == 0:
                    next_[rightcoord,c] = 1
                    col = red_cell                     #red turn
                else:
                    next_[r,c] = cells[r,c]
                    red_jammed +=1
                    col = red_cell
            
            elif cells[r,c]==2: #blue
                next_[r,c] = cells[r,c]
                col = blue_cell

                
            else:
                col = (255, 255, 204) #missing anything?
            pygame.draw.rect(surface, col, (r*cellsize, c*cellsize, \
                                            cellsize-.05, cellsize-.05)) #draw new cell
        
        elif counter == 1:
            if cells[r,c] == 0:
                col = (255, 255, 204)
            elif cells[r,c] == 2 : #blue cell
                if cells[r,belowcoord] == 0:
                    next_[r,belowcoord] = 2
                    col = blue_cell                    #blue turn
                else:
                    next_[r,c] = cells[r,c]
                    col = blue_cell
                    blue_jammed +=1
            
            elif cells[r,c] == 1 : #red
                next_[r,c] = cells[r,c]
                col = red_cell
                
            else:
                col = (0) #missing anything?
            pygame.draw.rect(surface, col, (r*cellsize, c*cellsize, \
                                             cellsize-.05, cellsize-.05)) #draw new cell
    
    #red
    if counter  == 0:
        ratio_red_jammed.append(red_jammed / np.count_nonzero(cells))
        ratio_blue_jammed.append(ratio_blue_jammed[-1])
        #all
        ratio_all_jammed.append((red_jammed / np.count_nonzero(cells))+ratio_blue_jammed[-1])

    #blue
    if counter == 1:
        ratio_blue_jammed.append(blue_jammed / np.count_nonzero(cells))
        ratio_red_jammed.append(ratio_red_jammed[-1])
        #all
        ratio_all_jammed.append((blue_jammed / np.count_nonzero(cells))+ratio_red_jammed[-1])
    
    delta_jammed.append(abs(ratio_all_jammed[-1]-ratio_all_jammed[-2]))
    return next_


main(width = 181,
     height = 181,
     cellsize = 4,
     density = .50)


#181 x 181 .385
#density 38 61x61 -- disordered intermediate