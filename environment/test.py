import sys
import os

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    from environment.cube import Cube
    from environment.constants import FRONT, BACK, RIGHT, LEFT, UP, DOWN
else:
    from .cube import Cube
    from .constants import FRONT, BACK, RIGHT, LEFT, UP, DOWN

def test_rotate(move_name, move_constant, clockwise, expected_changes):
    """Test a single rotation move on the cube."""
    cube = Cube()
    cube.state = list(range(54))
    
    direction = "clockwise" if clockwise else "counter-clockwise"
    print(f"\n=== Testing {move_name} {direction} ===")
    print("Initial state:", cube.state[:9], "...") 
    
    cube.rotate(move_constant, clockwise)
    print("After rotation:", cube.state[:9], "...")

    for position, expected_value in expected_changes.items():
        actual_value = cube.state[position]
        assert actual_value == expected_value, \
            f"Position {position}: expected {expected_value}, got {actual_value}"

    unchanged_positions = [i for i in range(54) if i not in expected_changes]
    for i in unchanged_positions:
        assert cube.state[i] == i, \
            f"Position {i} should be unchanged: expected {i}, got {cube.state[i]}"
    
    print(f"✓ {move_name} {direction} test passed!")

def run_all_tests():
    """Run all rotation tests systematically."""
    test_cases = [
        ("FRONT", FRONT, True, EXPECTED_CHANGES_FRONT_CW),
        ("FRONT", FRONT, False, EXPECTED_CHANGES_FRONT_CCW),
        ("RIGHT", RIGHT, True, EXPECTED_CHANGES_RIGHT_CW),
        ("RIGHT", RIGHT, False, EXPECTED_CHANGES_RIGHT_CCW),
        ("LEFT", LEFT, True, EXPECTED_CHANGES_LEFT_CW),
        ("LEFT", LEFT, False, EXPECTED_CHANGES_LEFT_CCW),
        ("BACK", BACK, True, EXPECTED_CHANGES_BACK_CW),
        ("BACK", BACK, False, EXPECTED_CHANGES_BACK_CCW),
        ("UP", UP, True, EXPECTED_CHANGES_UP_CW),
        ("UP", UP, False, EXPECTED_CHANGES_UP_CCW),
        ("DOWN", DOWN, True, EXPECTED_CHANGES_DOWN_CW),
        ("DOWN", DOWN, False, EXPECTED_CHANGES_DOWN_CCW),
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for move_name, move_constant, clockwise, expected_changes in test_cases:
        try:
            test_rotate(move_name, move_constant, clockwise, expected_changes)
            passed_tests += 1
        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"Unexpected error in {move_name} test: {e}")
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed_tests}/{total_tests}")
    if passed_tests == total_tests:
        print("All tests passed!")
    else:
        print(f"   {total_tests - passed_tests} tests failed")

# SOURCE OF TRUTH: Expected changes for each rotation
# These dictionaries define the authoritative behavior for cube rotations
EXPECTED_CHANGES_FRONT_CW = {
    6: 26, 7: 23, 8: 20,
    36: 6, 39: 7, 42: 8,
    47: 36, 46: 39, 45: 42,
    26: 47, 23: 46, 20: 45,
    9: 15, 10: 12, 11: 9,
    12: 16, 14: 10, 15: 17,
    16: 14, 17: 11
}

EXPECTED_CHANGES_FRONT_CCW = {
    6: 36, 7: 39, 8: 42,
    36: 47, 39: 46, 42: 45,
    45: 20, 46: 23, 47: 26,
    20: 8, 23: 7, 26: 6,
    9: 11, 10: 14, 11: 17,
    12: 10, 14: 16,
    15: 9, 16: 12, 17: 15
}

EXPECTED_CHANGES_RIGHT_CW = {
    2: 11, 5: 14, 8: 17,
    11: 47, 14: 50, 17: 53,
    27: 8, 30: 5, 33: 2,
    47: 33, 50: 30, 53: 27,
    36: 42, 37: 39, 38: 36,
    39: 43, 41: 37,
    42: 44, 43: 41, 44: 38
}

EXPECTED_CHANGES_RIGHT_CCW = {
    2: 33, 5: 30, 8: 27,
    11: 2, 14: 5, 17: 8,
    27: 53, 30: 50, 33: 47,
    47: 11, 50: 14, 53: 17,
    36: 38, 37: 41, 38: 44,
    39: 37, 41: 43,
    42: 36, 43: 39, 44: 42
}

EXPECTED_CHANGES_LEFT_CW = {
    0: 35, 3: 32, 6: 29,
    9: 0, 12: 3, 15: 6,
    29: 51, 32: 48, 35: 45,
    45: 9, 48: 12, 51: 15,
    18: 24, 19: 21, 20: 18,
    21: 25, 23: 19,
    24: 26, 25: 23, 26: 20
}

EXPECTED_CHANGES_LEFT_CCW = {
    0: 9, 3: 12, 6: 15,
    9: 45, 12: 48, 15: 51,
    29: 6, 32: 3, 35: 0,
    45: 35, 48: 32, 51: 29,
    18: 20, 19: 23, 20: 26,
    21: 19, 23: 25,
    24: 18, 25: 21, 26: 24
}

EXPECTED_CHANGES_BACK_CW = {
    0: 38, 1: 41, 2: 44,
    18: 2, 21: 1, 24: 0,
    38: 53, 41: 52, 44: 51,
    51: 18, 52: 21, 53: 24,
    27: 33, 28: 30, 29: 27,
    30: 34, 32: 28,
    33: 35, 34: 32, 35: 29
}

EXPECTED_CHANGES_BACK_CCW = {
    0: 24, 1: 21, 2: 18,
    18: 51, 21: 52, 24: 53,
    38: 0, 41: 1, 44: 2,
    51: 44, 52: 41, 53: 38,
    27: 29, 28: 32, 29: 35,
    30: 28, 32: 34,
    33: 27, 34: 30, 35: 33
}

EXPECTED_CHANGES_UP_CW = {
    9: 36, 10: 37, 11: 38,
    18: 9, 19: 10, 20: 11,
    27: 18, 28: 19, 29: 20,
    36: 27, 37: 28, 38: 29,
    0: 6, 1: 3, 2: 0,
    3: 7, 5: 1,
    6: 8, 7: 5, 8: 2
}

EXPECTED_CHANGES_UP_CCW = {
    9: 18, 10: 19, 11: 20,
    18: 27, 19: 28, 20: 29,
    27: 36, 28: 37, 29: 38,
    36: 9, 37: 10, 38: 11,
    0: 2, 1: 5, 2: 8,
    3: 1, 5: 7,
    6: 0, 7: 3, 8: 6
}

EXPECTED_CHANGES_DOWN_CW = {
    15: 24, 16: 25, 17: 26,
    24: 33, 25: 34, 26: 35,
    33: 42, 34: 43, 35: 44,
    42: 15, 43: 16, 44: 17,
    45: 51, 46: 48, 47: 45,
    48: 52, 50: 46,
    51: 53, 52: 50, 53: 47
}

EXPECTED_CHANGES_DOWN_CCW = {
    15: 42, 16: 43, 17: 44,
    24: 15, 25: 16, 26: 17,
    33: 24, 34: 25, 35: 26,
    42: 33, 43: 34, 44: 35,
    45: 47, 46: 50, 47: 53,
    48: 46, 50: 52,
    51: 45, 52: 48, 53: 51
}

def main():
    """Main function for running tests."""
    run_all_tests()

if __name__ == "__main__":
    main()