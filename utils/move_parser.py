import re
from environment.constants import FRONT, BACK, LEFT, RIGHT, UP, DOWN

def parse_moves_to_tuples(move_sequence):
    """
    Parse algorithm string into individual moves and return as tuples.

    Args:
        move_sequence: string containing move sequence to parse

    Returns:
        list: list of tuples (face, clockwise) for each individual move
    """
    pattern = r"[FBLRUD](?:'?2?|2'?)"
    moves = re.findall(pattern, move_sequence.strip().upper())
    
    face_map = {
        'F': FRONT, 'B': BACK, 'R': RIGHT,
        'L': LEFT, 'U': UP, 'D': DOWN
    }
    
    result = []
    
    for move in moves:
        if not move or move[0] not in face_map:
            continue
        
        face = face_map[move[0]]
        modifier = move[1:] if len(move) > 1 else ""
        
        if not modifier:
            clockwise, repetitions = True, 1
        elif modifier == "'":
            clockwise, repetitions = False, 1
        elif modifier == "2":
            clockwise, repetitions = True, 2
        elif modifier in ["2'", "'2"]:
            clockwise, repetitions = False, 2
        else:
            clockwise, repetitions = True, 1
        
        for _ in range(repetitions):
            result.append((face, clockwise))
    
    return result
