from OpenGL.GL import *
from OpenGL.GLUT import *

from scene import Scene
from config import *

def main(wsize, wposition):
    def refresh2d(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, width, height, 0, 0.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()

    def draw():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        refresh2d(*wsize)

        # draw the scene
        scene.draw()

        glutSwapBuffers()
    
    scene = Scene()

    glutInit()
    glutInitDisplayMode(GLUT_RGBA, GLUT_DEPTH)
    glutInitWindowSize(*wsize)
    glutInitWindowPosition(*wposition)
    window = glutCreateWindow("Day - Night Transition")
    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glutMainLoop()

if __name__ == "__main__":
    main(wsize, wposition)