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
else:
    try:
        from ..environment.constants import WHITE, BLUE, RED, GREEN, ORANGE, YELLOW, UP, FRONT, LEFT, BACK, RIGHT, DOWN
    except ImportError:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        from environment.constants import WHITE, BLUE, RED, GREEN, ORANGE, YELLOW, UP, FRONT, LEFT, BACK, RIGHT, DOWN

class Cube3DVisualizer:
    
    def __init__(self):
        self.rotation_x = 20
        self.rotation_y = -30
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.zoom = -8.0
        
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

def visualize_cube_3d(cube):
    """Utility function to visualize a cube."""
    visualizer = Cube3DVisualizer()
    visualizer.run_visualization(cube)