"""
RL-Rubik-Cube: Reinforcement Learning for Rubik's Cube solving.

This project implements a reinforcement learning approach to solve the Rubik's Cube.
It includes:
- Environment: Cube representation and operations
- Utils: Visualization and utilities
- Agent: RL agents (to be implemented)  
- Training: Training algorithms (to be implemented)
"""

from .environment import Cube
from .environment.constants import *

__all__ = [
    # Colors
    'WHITE', 'BLUE', 'RED', 'GREEN', 'ORANGE', 'YELLOW',
    # Faces 
    'UP', 'FRONT', 'LEFT', 'BACK', 'RIGHT', 'DOWN',
    # Rows and columns
    'TOP_ROW', 'MIDDLE_ROW', 'BOTTOM_ROW',
    'LEFT_COL', 'CENTER_COL', 'RIGHT_COL',
    # Classes
    'Cube'
]