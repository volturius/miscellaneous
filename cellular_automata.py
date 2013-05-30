#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import time
import os
from random import randint

debug = 0
interval =  0
generations = 109999
columns, rows = os.popen('stty size', 'r').read().split()
xdimension = int(rows)/2
ydimension = int(columns)
min_neighbors_to_live = 2
max_neighbors_to_live = 3

ALIVE = '•'
DEAD  = ' '

if debug:
    xdimension -= 5
    ydimension -= 5
    DEAD  = '·'

ca = list(range(xdimension))
for x in range(xdimension):
    ca[x] = list(range(ydimension))
    for y in range(ydimension):
        ca[x][y] = DEAD

# slider from the top left
ca[1][2] = ALIVE
ca[2][3] = ALIVE
ca[3][1] = ALIVE
ca[3][2] = ALIVE
ca[3][3] = ALIVE

# slider from top right
ca[xdimension-12][2] = ALIVE
ca[xdimension-12][3] = ALIVE
ca[xdimension-12][4] = ALIVE
ca[xdimension-11][4] = ALIVE
ca[xdimension-10][3] = ALIVE

def print_playfield(matrix):
    if (debug > 0):
        for x in range(xdimension):
            if x == 0:
                print "    ",
            print "%s" % x,
        print

    for row in range(ydimension):
        for col in range(xdimension):
            if debug > 0:
                if col == 0:
                    print "%-4s %s" % (str(row), matrix[col][row]),
                else:
                    print "%s" % matrix[col][row],
            else:
                print "%s" % matrix[col][row],

        print
    print

def generate(matrix):

    nextgen = copy.deepcopy(matrix)
    living = 0

    for col in range(len(matrix)):
        for row in range(len(matrix[col])):
            next_status = death_panel(matrix, col, row)
            if next_status == ALIVE:
                living += 1
            nextgen[col][row] = next_status

    if living == 0:
        fill_random(nextgen)

    return nextgen

def death_panel(matrix, x, y):
    neighbor_count = 0
    prognosis = DEAD

    if debug > 2: print "DEBUG: checking %s,%s -> %s" % (x, y, matrix[x][y])

    for col in [x-1, x, x+1]:
        for row in [y-1, y, y+1]:

            if debug > 3: print "DEBUG: scanning cell %s,%s" % (col, row)

            if col == x and row == y:
                if debug > 3: print "DEBUG: Skipping myself"
                continue

            if row < 0 or row > ydimension - 1:
                if debug > 3: print "DEBUG: SKIP invalid row"
                continue

            if col < 0 or col > xdimension - 1:
                if debug > 3: print "DEBUG: SKIP invalid column"
                continue

            if matrix[col][row] == ALIVE:
                if debug > 3: print "DEBUG: neighbor is alive"
                neighbor_count += 1

    if matrix[x][y] == ALIVE:
        if neighbor_count >= min_neighbors_to_live and neighbor_count <= max_neighbors_to_live:
            prognosis = ALIVE
    else:
        if neighbor_count == max_neighbors_to_live:
            prognosis = ALIVE
       
    if debug > 1:
        if matrix[x][y] != prognosis:
            print "CHANGE: %s,%s -- neighbors:%s  %s -> %s" % (x, y, neighbor_count, matrix[x][y], prognosis)

    return prognosis

def fill_random(matrix):
    
    for col in range(len(matrix)):
        for row in range(len(matrix[col])):
            matrix[col][row] = ALIVE if randint(0,1) else DEAD
    return matrix

gen=0
while (gen < generations):

#    os.system('clear')
    print("\033[0;0H")

    print_playfield(ca)
    ca = generate(ca)

    time.sleep(interval)
    gen += 1
