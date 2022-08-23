from typing import Tuple
import pygame
import sys
import math
from python.config import (
    MAX_DEPTH, SCALE, SCREEN_WIDTH, SCREEN_HEIGHT, MAP, TILE_SIZE,
    HALF_FOV, CASTED_RAYS, STEP_ANGLE
)
from python.colors import (
    wall_color, background_color,
    BLACK, GREEN, BLUE, YELLOW,
    DARK_GRAY, CLEAR_GRAY
)


# Variables
player_x = SCREEN_HEIGHT / 2
player_y = SCREEN_HEIGHT / 2
player_angle = math.pi


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Raycasting')  # Name window

clock = pygame.time.Clock()


def matrix_rotation_2d(x: float, y: float, radians: float) -> Tuple[float, float]:

    """Function to take point x and y and rotate that vector
    a quantity of radians.

    Args:
        * x (float): vector's value in x axis.
        * y (float): vector's value in y axis.
        * radians (float): radians that vector will be rotated.

    Returns:
        * Tuple(float, float): returns coordinates x and y with vector
            rotated.
    """

    d = radians
    return (x * math.cos(d) - y * math.sin(d), x * math.sin(d) + y * math.cos(d))


def draw_map() -> None:

    """Function to draw map from MAP variable. This function
    takes a square matrix with ones and zeros as a grid, where
    ones are walls and zeros are empty spaces.
    """

    pygame.draw.rect(screen, BLACK, (0,0, SCREEN_HEIGHT, SCREEN_HEIGHT))

    for i, y in enumerate(MAP):
        for j, x in enumerate(y):
            pygame.draw.rect(
                screen,
                wall_color if x else background_color,
                (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1)
            )

    # draw player
    pygame.draw.circle(screen, GREEN, (player_x, player_y), 4)


# raycasting algorithm
def cast_rays() -> None:

    """Function to shot rays to cast the game's environment
    """

    start_angle = player_angle - HALF_FOV

    # caster rays
    for ray in range(CASTED_RAYS):

        for depth in range(MAX_DEPTH):

            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth
            # Calculate square map where ray is
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)

            # Verify if map's square is a wall
            if MAP[row][col]:
                pygame.draw.line(
                    screen, BLUE, (player_x, player_y), (target_x, target_y)
                )
                pygame.draw.rect(
                    screen, YELLOW,
                    (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1)
                )
                # Shading color
                color_depth = (depth / 50 + 0.001)
                color_aux = [
                        wall_color[0] / color_depth,
                        wall_color[1] / color_depth,
                        wall_color[2] / color_depth
                    ]

                for i, col in enumerate(color_aux):
                    if col > 255: color_aux[i] = wall_color[i]
                for i, col in enumerate(color_aux):
                    if col < 0: color_aux[i] = 0

                # fix fish eye effect
                depth *= math.cos(player_angle - start_angle)

                # Draw 3d wall rectangles
                wall_height = 21000 / (depth + 0.0001)
                pygame.draw.rect(
                    screen, color_aux, (SCREEN_HEIGHT + ray * SCALE,
                                        SCREEN_HEIGHT / 2 - wall_height / 2,
                                        SCALE, wall_height)
                )
                break

        start_angle += STEP_ANGLE


# Conect Xbox controller
joysticks = []
for i in range(0, pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
    joysticks[-1].init()
    print ("Detected joystick", joysticks[-1].get_name())

aux_angle = 0
pos_x_aux = 0
pos_y_aux = 0
control = [0, 0]
initial_angle =  math.pi - player_angle
tol = 0.15


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.JOYAXISMOTION:

            # Detect Joystick LS
            if event.axis == 0:
                # Avoid control's ultra-sensitivity in joystick LS in x axis
                control[0] = event.value if event.value <= -tol or event.value >= tol else 0
            if event.axis == 1:
                # Avoid control's ultra-sensitivity in joystick LS in y axis
                control[1] = event.value if event.value <= -tol or event.value >= tol else 0

            # Avoid control's ultra-sensitivity in joystick RS in x axis
            if event.axis == 2:
                aux_angle = event.value * 0.1 if event.value <= -tol or event.value >= tol else 0

        # if event.type == pygame.KEYDOWN

    player_angle += aux_angle
    initial_angle += aux_angle
    # Rotate control's vector to use in player's position
    pos_x_aux, pos_y_aux = matrix_rotation_2d(control[0], control[1], initial_angle)
    player_x += pos_x_aux
    player_y += pos_y_aux

    # update 3D map
    pygame.draw.rect(
            screen, CLEAR_GRAY, (SCREEN_HEIGHT, 0, SCREEN_HEIGHT, SCREEN_HEIGHT / 2)
        )
    pygame.draw.rect(
            screen, DARK_GRAY,
            (SCREEN_HEIGHT, SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT / 2)
        )

    draw_map()

    cast_rays()

    # update display
    pygame.display.flip()
    clock.tick(30)
