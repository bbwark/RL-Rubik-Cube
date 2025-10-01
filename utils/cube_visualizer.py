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


class RenderConfig:
    def __init__(self):
        self.cube_size = 0.97
        self.small_cube_size = 0.95
        self.line_width = 2
        self.edge_color = (0.0, 0.0, 0.0)
        self.background_color = (0.1, 0.1, 0.1, 1.0)
        self.colors = {
            WHITE: (1.0, 1.0, 1.0),
            BLUE: (0.0, 0.0, 1.0), 
            RED: (1.0, 0.0, 0.0),
            GREEN: (0.0, 0.8, 0.0),
            ORANGE: (1.0, 0.5, 0.0),
            YELLOW: (1.0, 1.0, 0.0)
        }


class ViewState:
    def __init__(self):
        self.rotation_x = 20
        self.rotation_y = -30
        self.zoom = -8.0
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
    
    def reset_rotation(self):
        self.rotation_x = 20
        self.rotation_y = -30


class AnimationConfig:
    def __init__(self):
        self.speed = 2.5
        self.duration = 90
        self.fps = 60
        self.pause_between_moves = 200
    
    def set_speed(self, speed):
        self.speed = max(0.1, speed)


class OpenGLSetup:
    @staticmethod
    def setup_perspective(width, height):
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

    @staticmethod
    def initialize_display(width=1000, height=800, zoom=-8.0):
        try:
            pygame.display.init()
            
            display = (width, height)
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
            pygame.display.set_caption("Rubik's Cube 3D")
            
            OpenGLSetup.setup_perspective(display[0], display[1])
            glViewport(0, 0, display[0], display[1])
            glTranslatef(0.0, 0.0, zoom)
            
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


class EventHandler:
    def __init__(self, view_state):
        self.view_state = view_state

    def handle_events(self):
        for event in pygame.event.get():
            if self._is_quit_event(event):
                return False
            self._handle_mouse_events(event)
            self._handle_keyboard_events(event)
        return True

    def _is_quit_event(self, event):
        return (event.type == pygame.QUIT or 
                (event.type == KEYDOWN and event.key == K_ESCAPE))

    def _handle_mouse_events(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.view_state.mouse_dragging = True
            self.view_state.last_mouse_pos = event.pos
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.view_state.mouse_dragging = False
        elif event.type == MOUSEMOTION and self.view_state.mouse_dragging:
            dx = event.pos[0] - self.view_state.last_mouse_pos[0]
            dy = event.pos[1] - self.view_state.last_mouse_pos[1]
            self.view_state.rotation_y += dx * 0.5
            self.view_state.rotation_x += dy * 0.5
            self.view_state.last_mouse_pos = event.pos

    def _handle_keyboard_events(self, event):
        if event.type == KEYDOWN and event.key == K_r:
            self.view_state.reset_rotation()


class CubeRenderer:
    def __init__(self, config):
        self.config = config

    def render_cube(self, cube_state):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._draw_rubiks_cube(cube_state)
        pygame.display.flip()

    def render_animated_cube(self, cube_state, rotating_face, angle):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._draw_animated_rubiks_cube(cube_state, rotating_face, angle)
        pygame.display.flip()

    def _draw_rubiks_cube(self, cube_state):
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pos_x = (x - 1) * self.config.cube_size
                    pos_y = (y - 1) * self.config.cube_size  
                    pos_z = (z - 1) * self.config.cube_size
                    
                    glPushMatrix()
                    glTranslatef(pos_x, pos_y, pos_z)
                    self._draw_small_cube(x, y, z, cube_state)
                    glPopMatrix()

    def _draw_small_cube(self, x, y, z, cube_state):
        faces_to_draw = self._get_visible_faces(x, y, z, cube_state)
        
        for face_name, color in faces_to_draw:
            glColor3f(*color)
            self._draw_cube_face(face_name, self.config.small_cube_size)
            
        glColor3f(*self.config.edge_color)
        glLineWidth(self.config.line_width)
        self._draw_cube_edges(self.config.small_cube_size)

    def _get_visible_faces(self, x, y, z, cube_state):
        faces_to_draw = []
        
        if x == 0:
            color_idx = cube_state[LEFT * 9 + (2-y) * 3 + z]
            faces_to_draw.append(('left', self.config.colors[color_idx]))
        if x == 2:
            color_idx = cube_state[RIGHT * 9 + (2-y) * 3 + (2-z)]
            faces_to_draw.append(('right', self.config.colors[color_idx]))
        if y == 0:
            color_idx = cube_state[DOWN * 9 + (2-z) * 3 + x]
            faces_to_draw.append(('bottom', self.config.colors[color_idx]))
        if y == 2:
            color_idx = cube_state[UP * 9 + z * 3 + x]
            faces_to_draw.append(('top', self.config.colors[color_idx]))
        if z == 0:
            color_idx = cube_state[BACK * 9 + (2-y) * 3 + (2-x)]
            faces_to_draw.append(('back', self.config.colors[color_idx]))
        if z == 2:
            color_idx = cube_state[FRONT * 9 + (2-y) * 3 + x]
            faces_to_draw.append(('front', self.config.colors[color_idx]))
            
        return faces_to_draw

    def _draw_cube_face(self, face_name, size):
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
        s = size / 2
        
        glBegin(GL_LINES)
        glVertex3f(-s, -s, s); glVertex3f(s, -s, s)
        glVertex3f(s, -s, s); glVertex3f(s, s, s)
        glVertex3f(s, s, s); glVertex3f(-s, s, s)
        glVertex3f(-s, s, s); glVertex3f(-s, -s, s)
        
        glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, s, -s); glVertex3f(-s, s, -s)
        glVertex3f(-s, s, -s); glVertex3f(-s, -s, -s)
        
        glVertex3f(-s, -s, s); glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, s); glVertex3f(s, -s, -s)
        glVertex3f(s, s, s); glVertex3f(s, s, -s)
        glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        glEnd()

    def _draw_animated_rubiks_cube(self, cube_state, rotating_face, angle):
        rotating_cubes, static_cubes = self._separate_cubes_by_rotation(rotating_face)
        
        for x, y, z, pos_x, pos_y, pos_z in static_cubes:
            glPushMatrix()
            glTranslatef(pos_x, pos_y, pos_z)
            self._draw_small_cube(x, y, z, cube_state)
            glPopMatrix()
        
        for x, y, z, pos_x, pos_y, pos_z in rotating_cubes:
            glPushMatrix()
            self._apply_rotation_for_face(rotating_face, angle)
            glTranslatef(pos_x, pos_y, pos_z)
            self._draw_small_cube(x, y, z, cube_state)
            glPopMatrix()

    def _separate_cubes_by_rotation(self, rotating_face):
        rotating_cubes = []
        static_cubes = []
        
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    pos_x = (x - 1) * self.config.cube_size
                    pos_y = (y - 1) * self.config.cube_size  
                    pos_z = (z - 1) * self.config.cube_size
                    
                    cube_info = (x, y, z, pos_x, pos_y, pos_z)
                    
                    if self._is_cube_in_rotating_face(x, y, z, rotating_face):
                        rotating_cubes.append(cube_info)
                    else:
                        static_cubes.append(cube_info)
        
        return rotating_cubes, static_cubes

    def _is_cube_in_rotating_face(self, x, y, z, face):
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

    def _apply_rotation_for_face(self, face, angle):
        if face == UP or face == DOWN:
            glRotatef(-angle if face == UP else angle, 0, 1, 0)
        elif face == FRONT or face == BACK:
            glRotatef(-angle if face == FRONT else angle, 0, 0, 1)
        elif face == RIGHT or face == LEFT:
            glRotatef(-angle if face == RIGHT else angle, 1, 0, 0)


class CubeAnimator:
    def __init__(self, renderer, animation_config, view_state):
        self.renderer = renderer
        self.config = animation_config
        self.view_state = view_state

    def execute_algorithm(self, cube, algorithm):
        moves = parse_moves_to_tuples(algorithm.upper())
        
        for i, (face, clockwise) in enumerate(moves):
            print(f"Executing move {i+1}/{len(moves)}: {self._move_to_string(face, clockwise)}")
            
            if not self._animate_single_move(cube, face, clockwise):
                return False
                
        return True

    def _animate_single_move(self, cube, face, clockwise):
        initial_state = cube.state.copy()
        
        cube.rotate(face, clockwise)
        final_state = cube.state.copy()
        
        cube.state = initial_state
        
        total_angle = 90.0 if clockwise else -90.0
        frames = int(abs(total_angle) / self.config.speed)
        
        clock = pygame.time.Clock()
        
        for frame in range(frames + 1):
            t = frame / frames if frames > 0 else 1.0
            current_angle = total_angle * t
            
            glPushMatrix()
            glRotatef(self.view_state.rotation_x, 1, 0, 0)
            glRotatef(self.view_state.rotation_y, 0, 1, 0)
            self.renderer.render_animated_cube(cube.state, face, current_angle)
            glPopMatrix()
            
            clock.tick(self.config.fps)
        
        cube.state = final_state
        
        glPushMatrix()
        glRotatef(self.view_state.rotation_x, 1, 0, 0)
        glRotatef(self.view_state.rotation_y, 0, 1, 0)
        self.renderer.render_cube(cube.state)
        glPopMatrix()
        
        pygame.time.wait(self.config.pause_between_moves)
        
        return True

    def _move_to_string(self, face, clockwise):
        face_map = {
            FRONT: 'F', BACK: 'B', RIGHT: 'R',
            LEFT: 'L', UP: 'U', DOWN: 'D'
        }
        
        move = face_map.get(face, '?')
        if not clockwise:
            move += "'"
            
        return move


class Cube3DVisualizer:
    def __init__(self):
        self.render_config = RenderConfig()
        self.view_state = ViewState()
        self.animation_config = AnimationConfig()
        
        self.renderer = CubeRenderer(self.render_config)
        self.event_handler = EventHandler(self.view_state)
        self.animator = CubeAnimator(self.renderer, self.animation_config, self.view_state)

    def set_animation_speed(self, speed):
        self.animation_config.set_speed(speed)

    def run_visualization(self, cube):
        if not OpenGLSetup.initialize_display(zoom=self.view_state.zoom):
            print("Failed to initialize display")
            return
            
        print("Visualizer started. ESC to exit, R to reset view, drag to rotate.")
        
        clock = pygame.time.Clock()
        running = True
        
        try:
            while running:
                running = self.event_handler.handle_events()
                self._render_with_view_transform(cube)
                clock.tick(144)
        except Exception as e:
            print(f"Visualization error: {e}")
        finally:
            pygame.quit()

    def run_animated_visualization(self, cube, algorithm):
        if not OpenGLSetup.initialize_display(zoom=self.view_state.zoom):
            print("Failed to initialize display")
            return
            
        print("Animated visualization started. ESC to exit, R to reset view, drag to rotate.")
        print(f"Executing algorithm: {algorithm}")
        
        self._show_initial_state(cube)
        
        try:
            success = self.animator.execute_algorithm(cube, algorithm)
            self._show_final_result(cube, success)
                
        except Exception as e:
            print(f"Animation error: {e}")
        finally:
            pygame.quit()

    def _render_with_view_transform(self, cube):
        glPushMatrix()
        glRotatef(self.view_state.rotation_x, 1, 0, 0)
        glRotatef(self.view_state.rotation_y, 0, 1, 0)
        self.renderer.render_cube(cube.state)
        glPopMatrix()

    def _show_initial_state(self, cube):
        glPushMatrix()
        glRotatef(self.view_state.rotation_x, 1, 0, 0)
        glRotatef(self.view_state.rotation_y, 0, 1, 0)
        self.renderer.render_cube(cube.state)
        glPopMatrix()
        pygame.time.wait(1000)

    def _show_final_result(self, cube, success):
        if success:
            print("Algorithm execution completed!")
        else:
            print("Animation was interrupted.")
            
        print("Final state displayed. ESC to exit, R to reset view, drag to rotate.")
        
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.event_handler.handle_events()
            self._render_with_view_transform(cube)
            clock.tick(60)


def visualize_cube_3d(cube):
    visualizer = Cube3DVisualizer()
    visualizer.run_visualization(cube)


def visualize_algorithm_3d(cube, algorithm):
    visualizer = Cube3DVisualizer()
    visualizer.run_animated_visualization(cube, algorithm)