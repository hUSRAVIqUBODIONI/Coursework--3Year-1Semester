import pygame
import math
from OpenGL.GL import *
import numpy as np  # for easier matrix manipulations

def handle(last_pos,draw_rotating_enable,orbsmove):
    """
    Handles pygame events for camera move and zoom using arrow keys and mouse clicks
    """
    for event in pygame.event.get():
        # Exit cleanly if user quits window
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # Rotation with arrow keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                glRotatef(1, 0, 1, 0)  # Rotate left (around y-axis)
            if event.key == pygame.K_RIGHT:
                glRotatef(1, 0, -1, 0)  # Rotate right (around y-axis)
            if event.key == pygame.K_UP:
                glRotatef(1, -1, 0, 0)  # Rotate up (around x-axis)
            if event.key == pygame.K_DOWN:
                glRotatef(1, 1, 0, 0)  # Rotate down (around x-axis)

            # Move left when pressing 'A' key (camera-relative movement)
            if event.key == pygame.K_a:
                move_camera_left()
            # stop rotating all planets by pressing 'R'
            if event.key == pygame.K_r:
                orbsmove +=0.4
            if event.key == pygame.K_f:
                orbsmove -=0.4



            # Move right when pressing 'D' key (camera-relative movement)
            if event.key == pygame.K_d:
                move_camera_right()

            # Move forward when pressing 'W' key (camera-relative movement)
            if event.key == pygame.K_w:
                move_camera_forward()

            # Move backward when pressing 'S' key (camera-relative movement)
            if event.key == pygame.K_s:
                move_camera_backward()

        # Zoom in and out with mouse wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # wheel rolled up
                glScaled(1.05, 1.05, 1.05)
            if event.button == 5:  # wheel rolled down
                glScaled(0.95, 0.95, 0.95)

        # Rotate with mouse click and drag
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            dx = x - last_pos["x"]
            dy = y - last_pos["y"]
            mouseState = pygame.mouse.get_pressed()

            if mouseState[0]:  # If left mouse button is pressed
                modelView = (GLfloat * 16)()
                glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                # To combine x-axis and y-axis rotation
                temp = (GLfloat * 3)()
                temp[0] = modelView[0] * dy + modelView[1] * dx
                temp[1] = modelView[4] * dy + modelView[5] * dx
                temp[2] = modelView[8] * dy + modelView[9] * dx
                norm_xy = math.sqrt(temp[0] * temp[0] + temp[1] * temp[1] + temp[2] * temp[2])

                if norm_xy != 0:
                    glRotatef(math.sqrt(dx * dx + dy * dy), temp[0] / norm_xy, temp[1] / norm_xy, temp[2] / norm_xy)

            last_pos["x"] = x
            last_pos["y"] = y

    # Returns updated position
    return last_pos,draw_rotating_enable,orbsmove


def move_camera_left():
    """
    Moves the camera left relative to its current orientation (along the local right axis).
    """
    modelView = (GLfloat * 16)()
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

    # Right vector (camera's local x-axis) is modelView[0], modelView[4], modelView[8]
    right_vector = np.array([modelView[0], modelView[4], modelView[8]])

    # Translate camera along its local right direction
    glTranslatef(-0.5 * right_vector[0], -0.5 * right_vector[1], -0.5 * right_vector[2])


def move_camera_right():
    """
    Moves the camera right relative to its current orientation (along the local right axis).
    """
    modelView = (GLfloat * 16)()
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

    # Right vector (camera's local x-axis) is modelView[0], modelView[4], modelView[8]
    right_vector = np.array([modelView[0], modelView[4], modelView[8]])

    # Translate camera along its local right direction
    glTranslatef(0.5 * right_vector[0], 0.5 * right_vector[1], 0.5 * right_vector[2])


def move_camera_forward():
    """
    Moves the camera forward relative to its current orientation (along the local forward axis).
    """
    modelView = (GLfloat * 16)()
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

    # Forward vector (camera's local z-axis) is modelView[2], modelView[6], modelView[10]
    forward_vector = np.array([modelView[2], modelView[6], modelView[10]])

    # Translate camera along its local forward direction
    glTranslatef(-0.5 * forward_vector[0], -0.5 * forward_vector[1], -0.5 * forward_vector[2])


def move_camera_backward():
    """
    Moves the camera backward relative to its current orientation (along the local forward axis).
    """
    modelView = (GLfloat * 16)()
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

    # Forward vector (camera's local z-axis) is modelView[2], modelView[6], modelView[10]
    forward_vector = np.array([modelView[2], modelView[6], modelView[10]])

    # Translate camera along its local forward direction (opposite to moving forward)
    glTranslatef(0.5 * forward_vector[0], 0.5 * forward_vector[1], 0.5 * forward_vector[2])


