from .constants import (
    FRONT, BACK, RIGHT, LEFT, UP, DOWN,
    BOTTOM_ROW, TOP_ROW,
    LEFT_COL, RIGHT_COL,
    WHITE, BLUE, RED, GREEN, ORANGE, YELLOW
)
import random
import re

class Cube:
    """A class representing a 3x3 Rubik's Cube using a vector representation."""

    """
    State representation:
    0-8: Up face
    9-17: Front face
    18-26: Left face
    27-35: Back face
    36-44: Right face
    45-53: Down face

    Each face is represented by 9 consecutive integers.
    Colors: 0=White, 1=Blue, 2=Red, 3=Green, 4=Orange, 5=Yellow
    """

    # Configurations for clockwise rotations
    # Each configuration specifies:
    # - face: the face that rotates
    # - adjacent_cycle: list of tuples (face, accessor, indices) that define the cycle of adjacent faces
    #   accessor can be 'row' or 'col'
    #   indices is the index of the row/column
    # - reverse: list of booleans indicating whether to reverse the order of values for each element of the cycle
    ROTATION_CONFIGS = {
        FRONT: {
            'face': FRONT,
            'adjacent_cycle': [
                (UP, 'row', BOTTOM_ROW),
                (RIGHT, 'col', LEFT_COL),
                (DOWN, 'row', TOP_ROW),
                (LEFT, 'col', RIGHT_COL),
            ],
            'reverse': [True, False, True, False],
        },
        BACK: {
            'face': BACK,
            'adjacent_cycle': [
                (UP, 'row', TOP_ROW),
                (LEFT, 'col', LEFT_COL),
                (DOWN, 'row', BOTTOM_ROW),
                (RIGHT, 'col', RIGHT_COL),
            ],
            'reverse': [False, True, False, True],
        },
        RIGHT: {
            'face': RIGHT,
            'adjacent_cycle': [
                (UP, 'col', RIGHT_COL),
                (BACK, 'col', LEFT_COL),
                (DOWN, 'col', RIGHT_COL),
                (FRONT, 'col', RIGHT_COL),
            ],
            'reverse': [False, True, True, False],
        },
        LEFT: {
            'face': LEFT,
            'adjacent_cycle': [
                (UP, 'col', LEFT_COL),
                (FRONT, 'col', LEFT_COL),
                (DOWN, 'col', LEFT_COL),
                (BACK, 'col', RIGHT_COL),
            ],
            'reverse': [True, False, False, True],
        },
        UP: {
            'face': UP,
            'adjacent_cycle': [
                (FRONT, 'row', TOP_ROW),
                (LEFT, 'row', TOP_ROW),
                (BACK, 'row', TOP_ROW),
                (RIGHT, 'row', TOP_ROW),
            ],
            'reverse': [False, False, False, False],
        },
        DOWN: {
            'face': DOWN,
            'adjacent_cycle': [
                (FRONT, 'row', BOTTOM_ROW),
                (RIGHT, 'row', BOTTOM_ROW),
                (BACK, 'row', BOTTOM_ROW),
                (LEFT, 'row', BOTTOM_ROW),
            ],
            'reverse': [False, False, False, False],
        },
    }

    def __init__(self):
        self.state = self._create_solved_state()

    def _create_solved_state(self):
        """Vector representation of a solved cube.
        First nine elements are the up face, next nine are the front face, and so on.
        Up face is 0, front face is 1, left face is 2, back face is 3, right face is 4, down face is 5.
        White is 0, blue is 1, red is 2, green is 3, orange is 4, yellow is 5."""
        return [WHITE]*9 + [BLUE]*9 + [RED]*9 + [GREEN]*9 + [ORANGE]*9 + [YELLOW]*9
    
    def _get_row_values(self, state, face, row):
        start = face * 9 + row * 3
        return state[start:start + 3]

    def _get_column_values(self, state, face, col):
        base = face * 9 + col
        return [state[base], state[base + 3], state[base + 6]]
    
    def _set_row_values(self, state, face, row, values):
        start = face * 9 + row * 3
        state[start:start + 3] = values

    def _set_column_values(self, state, face, col, values):
        base = face * 9 + col
        state[base] = values[0]
        state[base + 3] = values[1]
        state[base + 6] = values[2]

    def _get_values(self, state, face, accessor, index):
        if accessor == 'row':
            return self._get_row_values(state, face, index)
        else:
            return self._get_column_values(state, face, index)
    
    def _set_values(self, state, face, accessor, index, values):
        if accessor == 'row':
            self._set_row_values(state, face, index, values)
        else:
            self._set_column_values(state, face, index, values)

    def rotate(self, face, clockwise=True):
        """
        Rotate a specific face of the cube.
        
        Args:
            face: the face to rotate (UP, FRONT, LEFT, BACK, RIGHT, DOWN)
            clockwise: True for clockwise rotation, False for counterclockwise
        """
        
        config = self.ROTATION_CONFIGS[face]
        
        adjacent_values = []
        for face_idx, accessor, index in config['adjacent_cycle']:
            values = self._get_values(self.state, face_idx, accessor, index)
            adjacent_values.append(values)
        
        if clockwise:
            for i, (face_idx, accessor, index) in enumerate(config['adjacent_cycle']):
                prev_idx = (i - 1) % len(adjacent_values)
                values = adjacent_values[prev_idx]
                if config['reverse'][i]:
                    values = values[::-1]
                self._set_values(self.state, face_idx, accessor, index, values)
        else:
            for i, (face_idx, accessor, index) in enumerate(config['adjacent_cycle']):
                next_idx = (i + 1) % len(adjacent_values)
                values = adjacent_values[next_idx]
                if config['reverse'][next_idx]:
                    values = values[::-1]
                self._set_values(self.state, face_idx, accessor, index, values)
    
        self._rotate_face_internal(config['face'], clockwise)

    def _rotate_face_internal(self, face, clockwise=True):
        """
        Rotate the internal structure of a face.
        
        Args:
            face: face to rotate
            clockwise: rotation direction
        """
        left_col = self._get_column_values(self.state, face, LEFT_COL)
        top_row = self._get_row_values(self.state, face, TOP_ROW)
        right_col = self._get_column_values(self.state, face, RIGHT_COL)
        bottom_row = self._get_row_values(self.state, face, BOTTOM_ROW)
        
        if clockwise:
            self._set_row_values(self.state, face, TOP_ROW, left_col[::-1])
            self._set_column_values(self.state, face, RIGHT_COL, top_row)
            self._set_row_values(self.state, face, BOTTOM_ROW, right_col[::-1])
            self._set_column_values(self.state, face, LEFT_COL, bottom_row)
        else:
            self._set_row_values(self.state, face, TOP_ROW, right_col)
            self._set_column_values(self.state, face, RIGHT_COL, bottom_row[::-1])
            self._set_row_values(self.state, face, BOTTOM_ROW, left_col)
            self._set_column_values(self.state, face, LEFT_COL, top_row[::-1])

    def is_solved(self):
        return self.state == self._create_solved_state()
    
    def execute_algorithm(self, algorithm):
        """
        Execute an algorithm of moves on the cube.
        
        Args:
            algorithm: string containing the moves (e.g.: "R U R' U'", "f'ru'b2d'r", "F R U L")
        """
        if not algorithm:
            return
        
        face_map = {
            'F': FRONT, 'B': BACK, 'R': RIGHT,
            'L': LEFT, 'U': UP, 'D': DOWN
        }
        
        moves = self._parse_moves(algorithm.strip().upper())
        
        for move in moves:
            self._execute_single_move(move, face_map)

    def _parse_moves(self, algorithm):
        """
        Parse algorithm string into individual moves.
        
        Args:
            algorithm: sanitized algorithm string
            
        Returns:
            list: list of move strings
        """
        pattern = r"[FBLRUD](?:'?2?|2'?)"
        return re.findall(pattern, algorithm)

    def _execute_single_move(self, move, face_map):
        """
        Execute a single move on the cube.
        
        Args:
            move: single move string (e.g., "R", "U'", "F2", "L2'")
            face_map: dictionary mapping face letters to face constants
        """
        if not move or move[0] not in face_map:
            return
        
        face = face_map[move[0]]
        modifier = move[1:] if len(move) > 1 else ""
        
        clockwise, repetitions = self._parse_move_modifier(modifier)
        
        for _ in range(repetitions):
            self.rotate(face, clockwise=clockwise)

    def _parse_move_modifier(self, modifier):
        """
        Parse move modifier to determine rotation direction and repetitions.
        
        Args:
            modifier: modifier part of the move (e.g., "", "'", "2", "2'")
            
        Returns:
            tuple: (clockwise: bool, repetitions: int)
        """
        if not modifier:
            return True, 1  # Standard clockwise rotation
        elif modifier == "'":
            return False, 1  # Counterclockwise rotation
        elif modifier == "2":
            return True, 2  # Double clockwise rotation
        elif modifier in ["2'", "'2"]:
            return False, 2  # Double counterclockwise rotation
        else:
            return True, 1  # Default fallback

    def scramble(self, moves=20):
        faces = ['F', 'B', 'R', 'L', 'U', 'D']
        
        modifiers = ['', "'", '2']
        
        scramble_moves = []
        last_face = None
        
        for _ in range(moves):
            available_faces = [face for face in faces if face != last_face]

            face = random.choice(available_faces)
            modifier = random.choice(modifiers)

            move = face + modifier
            scramble_moves.append(move)
            
            last_face = face
        
        algorithm = ' '.join(scramble_moves)
        self.execute_algorithm(algorithm)
        
        return algorithm
