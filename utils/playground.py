import sys
import os

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    from environment import Cube
    from environment.constants import UP, FRONT, LEFT, BACK, RIGHT, DOWN
    from utils.cube_visualizer import visualize_cube_3d
else:
    from ..environment import Cube
    from ..environment.constants import UP, FRONT, LEFT, BACK, RIGHT, DOWN
    from .cube_visualizer import visualize_cube_3d

def main():
    """Create a cube and visualize it with the 3D visualizer."""
    
    print("=== Rubik's Cube 3D Playground ===")
    print("Creating a solved cube...")
    
    cube = Cube()
    visualize_cube_3d(cube)
    cube.rotate(FRONT, True)
    visualize_cube_3d(cube)
    cube.rotate(RIGHT, True)
    visualize_cube_3d(cube)
    cube.rotate(BACK, True)
    visualize_cube_3d(cube)
    cube.rotate(LEFT, True)
    visualize_cube_3d(cube)
    cube.rotate(UP, True)
    visualize_cube_3d(cube)
    cube.rotate(DOWN, True)
    visualize_cube_3d(cube)

    print("Visualization ended.")

if __name__ == "__main__":
    main()