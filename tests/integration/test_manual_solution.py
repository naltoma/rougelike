#!/usr/bin/env python3

def solve():
    turn_left()
    for i in range(5): move()
    turn_left()
    for i in range(2): move()
    for i in range(2): attack()
    for i in range(5): move()
