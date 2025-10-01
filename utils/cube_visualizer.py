import sys
import os

os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import math
from pygame.locals import *

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print(f"OpenGL import error: {e}")
    print("Install with: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    from environment.constants import WHITE, BLUE, RED, GREEN, ORANGE, YELLOW, UP, FRONT, LEFT, BACK, RIGHT, DOWN
    from .move_parser import parse_moves_to_tuples
else:
    try:
        from ..environment.constants import WHITE, BLUE, RED, GREEN, ORANGE, YELLOW, UP, FRONT, LEFT, BACK, RIGHT, DOWN
        from .move_parser import parse_moves_to_tuples
    except ImportError:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        from environment.constants import WHITE, BLUE, RED, GREEN, ORANGE, YELLOW, UP, FRONT, LEFT, BACK, RIGHT, DOWN
        from utils.move_parser import parse_moves_to_tuples

class Cube3DVisualizer:
    
    def __init__(self):
        self.rotation_x = 20
        self.rotation_y = -30
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.zoom = -8.0
        
        self.animation_speed = 2.5 
        self.animation_duration = 90 
        
        self.colors = {
            WHITE: (1.0, 1.0, 1.0),
            BLUE: (0.0, 0.0, 1.0), 
            RED: (1.0, 0.0, 0.0),
            GREEN: (0.0, 0.8, 0.0),
            ORANGE: (1.0, 0.5, 0.0),
            YELLOW: (1.0, 1.0, 0.0)
        }

    def _setup_perspective(self, width, height):
        """Setup manual perspective without gluPerspective."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        fov = 45.0
        aspect = width / height
        near = 0.1
        far = 50.0
        
        fH = math.tan(fov * math.pi / 360.0) * near
        fW = fH * aspect
        
        glFrustum(-fW, fW, -fH, fH, near, far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def init_display(self, width=1000, height=800):
        """Initialize OpenGL display with error handling."""
        try:
            pygame.display.init()
            
            display = (width, height)
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
            pygame.display.set_caption("Rubik's Cube 3D")
            
            self._setup_perspective(display[0], display[1])
            glViewport(0, 0, display[0], display[1])
            glTranslatef(0.0, 0.0, self.zoom)
            
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
            glFrontFace(GL_CCW)
            
            glClearColor(0.1, 0.1, 0.1, 1.0)
            glDisable(GL_LIGHTING)
            
            return True
        except Exception as e:
            print(f"Display init error: {e}")
            return False

    def render_cube(self, cube_state):
        """Render the cube."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        self._draw_rubiks_cube(cube_state)
        
        glPopMatrix()
        pygame.display.flip()

    def _draw_rubiks_cube(self, cube_state):
        """Draw a 3x3x3 Rubik's cube with proper 3D structure."""
        cube_size = 0.97
        
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pos_x = (x - 1) * cube_size
                    pos_y = (y - 1) * cube_size  
                    pos_z = (z - 1) * cube_size
                    
                    glPushMatrix()
                    glTranslatef(pos_x, pos_y, pos_z)
                    self._draw_small_cube(x, y, z, cube_state)
                    glPopMatrix()

    def _draw_small_cube(self, x, y, z, cube_state):
        """Draw a single small cube with colored faces based on cube state."""
        size = 0.95
        
        faces_to_draw = []
        
        if x == 0:  # Left face visible
            color_idx = cube_state[LEFT * 9 + (2-y) * 3 + z]
            faces_to_draw.append(('left', self.colors[color_idx]))
        if x == 2:  # Right face visible
            color_idx = cube_state[RIGHT * 9 + (2-y) * 3 + (2-z)]
            faces_to_draw.append(('right', self.colors[color_idx]))
        if y == 0:  # Bottom face visible
            color_idx = cube_state[DOWN * 9 + (2-z) * 3 + x]
            faces_to_draw.append(('bottom', self.colors[color_idx]))
        if y == 2:  # Top face visible
            color_idx = cube_state[UP * 9 + z * 3 + x]
            faces_to_draw.append(('top', self.colors[color_idx]))
        if z == 0:  # Back face visible
            color_idx = cube_state[BACK * 9 + (2-y) * 3 + (2-x)]
            faces_to_draw.append(('back', self.colors[color_idx]))
        if z == 2:  # Front face visible
            color_idx = cube_state[FRONT * 9 + (2-y) * 3 + x]
            faces_to_draw.append(('front', self.colors[color_idx]))
        
        # Draw the visible faces
        for face_name, color in faces_to_draw:
            glColor3f(*color)
            self._draw_cube_face(face_name, size)
            
        # Draw edges in black
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2)
        self._draw_cube_edges(size)

    def _draw_cube_face(self, face_name, size):
        """Draw a single face of a cube."""
        s = size / 2
        
        glBegin(GL_QUADS)
        
        if face_name == 'front':
            glVertex3f(-s, -s, s)
            glVertex3f(s, -s, s)
            glVertex3f(s, s, s)
            glVertex3f(-s, s, s)
        elif face_name == 'back':
            glVertex3f(s, -s, -s)
            glVertex3f(-s, -s, -s)
            glVertex3f(-s, s, -s)
            glVertex3f(s, s, -s)
        elif face_name == 'left':
            glVertex3f(-s, -s, -s)
            glVertex3f(-s, -s, s)
            glVertex3f(-s, s, s)
            glVertex3f(-s, s, -s)
        elif face_name == 'right':
            glVertex3f(s, -s, s)
            glVertex3f(s, -s, -s)
            glVertex3f(s, s, -s)
            glVertex3f(s, s, s)
        elif face_name == 'top':
            glVertex3f(-s, s, s)
            glVertex3f(s, s, s)
            glVertex3f(s, s, -s)
            glVertex3f(-s, s, -s)
        elif face_name == 'bottom':
            glVertex3f(-s, -s, -s)
            glVertex3f(s, -s, -s)
            glVertex3f(s, -s, s)
            glVertex3f(-s, -s, s)
            
        glEnd()

    def _draw_cube_edges(self, size):
        """Draw the edges of a cube."""
        s = size / 2
        
        glBegin(GL_LINES)
        # Front face
        glVertex3f(-s, -s, s); glVertex3f(s, -s, s)
        glVertex3f(s, -s, s); glVertex3f(s, s, s)
        glVertex3f(s, s, s); glVertex3f(-s, s, s)
        glVertex3f(-s, s, s); glVertex3f(-s, -s, s)
        
        # Back face
        glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, s, -s); glVertex3f(-s, s, -s)
        glVertex3f(-s, s, -s); glVertex3f(-s, -s, -s)
        
        # Connecting edges
        glVertex3f(-s, -s, s); glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, s); glVertex3f(s, -s, -s)
        glVertex3f(s, s, s); glVertex3f(s, s, -s)
        glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        glEnd()

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_dragging = True
                    self.last_mouse_pos = event.pos
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
            elif event.type == MOUSEMOTION:
                if self.mouse_dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.rotation_y += dx * 0.5
                    self.rotation_x += dy * 0.5
                    self.last_mouse_pos = event.pos
            elif event.type == KEYDOWN and event.key == K_r:
                self.rotation_x = 20
                self.rotation_y = -30
        return True

    def run_visualization(self, cube):
        """Run the main visualization loop."""
        if not self.init_display():
            print("Failed to initialize display")
            return
            
        clock = pygame.time.Clock()
        running = True
        
        print("Visualizer started. ESC to exit, R to reset view, drag to rotate.")
        
        try:
            while running:
                running = self.handle_events()
                self.render_cube(cube.state)
                clock.tick(144)
        except Exception as e:
            print(f"Visualization error: {e}")
        finally:
            pygame.quit()

    def _is_cube_in_rotating_face(self, x, y, z, face):
        """
        Check if a cube at position (x,y,z) is part of the rotating face.
        
        Args:
            x, y, z: cube position (0-2 range)
            face: rotating face
            
        Returns:
            bool: True if cube is part of the rotating face
        """
        if face == UP and y == 2:
            return True
        elif face == DOWN and y == 0:
            return True
        elif face == FRONT and z == 2:
            return True
        elif face == BACK and z == 0:
            return True
        elif face == RIGHT and x == 2:
            return True
        elif face == LEFT and x == 0:
            return True
        return False

    def set_animation_speed(self, speed):
        """
        Set the animation speed.
        
        Args:
            speed: degrees per frame (lower = slower)
                   Typical values: 0.5 (very slow), 1.5 (slow), 3.0 (normal), 6.0 (fast)
        """
        self.animation_speed = max(0.1, speed)  # Minimum speed to avoid infinite loops

    def _move_to_string(self, face, clockwise):
        """
        Convert face and clockwise to move string for display.
        
        Args:
            face: face constant
            clockwise: rotation direction
            
        Returns:
            str: move string (e.g., "R", "U'", etc.)
        """
        face_map = {
            FRONT: 'F', BACK: 'B', RIGHT: 'R',
            LEFT: 'L', UP: 'U', DOWN: 'D'
        }
        
        move = face_map.get(face, '?')
        if not clockwise:
            move += "'"
            
        return move

    def execute_animated_algorithm(self, cube, algorithm):
        """
        Execute an algorithm with animated rotations.
        
        Args:
            cube: Cube object to apply rotations to
            algorithm: string containing the moves (e.g.: "R U R' U'")
            
        Returns:
            bool: True if all animations completed successfully, False if interrupted
        """
        moves = parse_moves_to_tuples(algorithm.upper())
        
        for i, (face, clockwise) in enumerate(moves):
            print(f"Executing move {i+1}/{len(moves)}: {self._move_to_string(face, clockwise)}")
            
            if not self._animate_rotation(cube, face, clockwise):
                return False  # Animation was interrupted
                
        return True

    def _animate_rotation(self, cube, face, clockwise):
        """
        Animate a single rotation.
        
        Args:
            cube: Cube object to rotate
            face: face to rotate
            clockwise: rotation direction
            
        Returns:
            bool: True if animation completed successfully, False if interrupted
        """
        initial_state = cube.state.copy()
        
        # Apply the rotation to get the final state
        cube.rotate(face, clockwise)
        final_state = cube.state.copy()
        
        # Reset to initial state for animation
        cube.state = initial_state
        
        total_angle = 90.0
        if not clockwise:
            total_angle = -90.0
            
        current_angle = 0.0
        frames = int(abs(total_angle) / self.animation_speed)
        
        clock = pygame.time.Clock()
        
        for frame in range(frames + 1):
            if not self.handle_events():
                return False  # Animation was interrupted
                
            t = frame / frames if frames > 0 else 1.0
            current_angle = total_angle * t
            
            self._render_animated_cube(cube.state, face, current_angle)
            
            clock.tick(60)
        
        cube.state = final_state
        
        self.render_cube(cube.state)
        pygame.time.wait(200)
        
        return True

    def _render_animated_cube(self, cube_state, rotating_face, angle):
        """
        Render the cube with animated rotation for a specific face.
        
        Args:
            cube_state: current cube state
            rotating_face: face being rotated
            angle: current rotation angle
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        self._draw_animated_rubiks_cube(cube_state, rotating_face, angle)
        
        glPopMatrix()
        pygame.display.flip()

    def _draw_animated_rubiks_cube(self, cube_state, rotating_face, angle):
        """
        Draw the Rubik's cube with animation applied to the rotating face.
        
        Args:
            cube_state: current cube state
            rotating_face: face being rotated
            angle: current rotation angle
        """
        cube_size = 0.97
        
        # Separate cubes into rotating and non-rotating
        rotating_cubes = []
        static_cubes = []
        
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pos_x = (x - 1) * cube_size
                    pos_y = (y - 1) * cube_size  
                    pos_z = (z - 1) * cube_size
                    
                    cube_info = (x, y, z, pos_x, pos_y, pos_z)
                    
                    if self._is_cube_in_rotating_face(x, y, z, rotating_face):
                        rotating_cubes.append(cube_info)
                    else:
                        static_cubes.append(cube_info)
        
        # Draw static cubes
        for x, y, z, pos_x, pos_y, pos_z in static_cubes:
            glPushMatrix()
            glTranslatef(pos_x, pos_y, pos_z)
            self._draw_small_cube(x, y, z, cube_state)
            glPopMatrix()
        
        # Draw rotating cubes with corrected rotation direction
        for x, y, z, pos_x, pos_y, pos_z in rotating_cubes:
            glPushMatrix()
            
            # Apply rotation around the axis through cube center
            # Invert angles to match logical rotation
            if rotating_face == UP or rotating_face == DOWN:
                # Rotate around Y axis
                glRotatef(-angle if rotating_face == UP else angle, 0, 1, 0)
            elif rotating_face == FRONT or rotating_face == BACK:
                # Rotate around Z axis
                glRotatef(-angle if rotating_face == FRONT else angle, 0, 0, 1)
            elif rotating_face == RIGHT or rotating_face == LEFT:
                # Rotate around X axis
                glRotatef(-angle if rotating_face == RIGHT else angle, 1, 0, 0)
            
            glTranslatef(pos_x, pos_y, pos_z)
            self._draw_small_cube(x, y, z, cube_state)
            glPopMatrix()

    def _get_face_center_offset(self, face):
        """
        Get the offset to the center of rotation for a face.
        
        Args:
            face: face constant
            
        Returns:
            tuple: (x, y, z) offset to face center
        """
        if face == UP:
            return (0, 0.97, 0)  # Center of top face
        elif face == DOWN:
            return (0, -0.97, 0)  # Center of bottom face
        elif face == FRONT:
            return (0, 0, 0.97)  # Center of front face
        elif face == BACK:
            return (0, 0, -0.97)  # Center of back face
        elif face == RIGHT:
            return (0.97, 0, 0)  # Center of right face
        elif face == LEFT:
            return (-0.97, 0, 0)  # Center of left face
        return (0, 0, 0)

    def _apply_face_rotation(self, face, angle):
        """
        Apply rotation transformation for the given face around the cube's center.
        
        Args:
            face: face being rotated
            angle: rotation angle in degrees
        """
        # Move to cube center, rotate, then move back
        glTranslatef(0, 0, 0) # Cube centered at origin
        
        if face == UP:
            glRotatef(angle, 0, 1, 0)
        elif face == DOWN:
            glRotatef(-angle, 0, 1, 0)
        elif face == FRONT:
            glRotatef(angle, 0, 0, 1)
        elif face == BACK:
            glRotatef(-angle, 0, 0, 1)
        elif face == RIGHT:
            glRotatef(angle, 1, 0, 0)
        elif face == LEFT:
            glRotatef(-angle, 1, 0, 0)

    def _apply_face_rotation_around_center(self, face, angle):
        """
        Apply rotation around the face center for more natural animation.
        
        Args:
            face: face being rotated
            angle: rotation angle in degrees
        """
        offset_x, offset_y, offset_z = self._get_face_center_offset(face)
        
        glTranslatef(offset_x, offset_y, offset_z)
        
        # Apply rotation
        if face == UP:
            glRotatef(angle, 0, 1, 0)
        elif face == DOWN:
            glRotatef(-angle, 0, 1, 0)
        elif face == FRONT:
            glRotatef(angle, 0, 0, 1)
        elif face == BACK:
            glRotatef(-angle, 0, 0, 1)
        elif face == RIGHT:
            glRotatef(angle, 1, 0, 0)
        elif face == LEFT:
            glRotatef(-angle, 1, 0, 0)
        
        glTranslatef(-offset_x, -offset_y, -offset_z)

    def run_animated_visualization(self, cube, algorithm):
        """
        Run the visualization with an animated algorithm execution.
        
        Args:
            cube: Cube object to visualize
            algorithm: string containing the moves to animate
        """
        if not self.init_display():
            print("Failed to initialize display")
            return
            
        print("Animated visualization started. ESC to exit, R to reset view, drag to rotate.")
        print(f"Executing algorithm: {algorithm}")
        
        # Show initial state for a moment
        self.render_cube(cube.state)
        pygame.time.wait(1000)
        
        try:
            success = self.execute_animated_algorithm(cube, algorithm)
            
            if success:
                print("Algorithm execution completed!")
            else:
                print("Animation was interrupted.")
                
            print("Final state displayed. ESC to exit, R to reset view, drag to rotate.")
            clock = pygame.time.Clock()
            running = True
            while running:
                running = self.handle_events()
                self.render_cube(cube.state)
                clock.tick(60)
                
        except Exception as e:
            print(f"Animation error: {e}")
        finally:
            pygame.quit()

def visualize_cube_3d(cube):
    """Utility function to visualize a cube."""
    visualizer = Cube3DVisualizer()
    visualizer.run_visualization(cube)

def visualize_algorithm_3d(cube, algorithm):
    """Utility function to visualize an algorithm execution."""
    visualizer = Cube3DVisualizer()
    visualizer.run_animated_visualization(cube, algorithm)