import pygame
import math
import time   # currently unused but safe to keep if adding timed expressions later


# color definitions used throughout BMO's face
BLACK = (0,0,0)
DARK_GREEN = (2, 48, 32)   # tongue shading color
GREEN = (127, 255, 212)    # background masking color


# draws BMO's eyes
# blink controls vertical squish amount (0=open, 1=closed)
# state controls whether eyes are open or sleeping arcs
# eye_offset allows idle look-left / look-right animation
def eyes(surface, blink, state, eye_offset):

    # get screen size so drawing scales automatically with resolution
    WIDTH, HEIGHT = surface.get_size()

    # screen center
    x = WIDTH//2
    y = HEIGHT//2

    # offsets for eye placement relative to center
    Xoffset = WIDTH * .25
    Yoffset = HEIGHT * 0.25

    # eye size scales with screen resolution
    eyeWidth = int(WIDTH * .0666666666)
    eyeHeight = int(HEIGHT * .1375)

    # calculate left/right eye positions
    leftx = x - Xoffset - (eyeWidth//2)
    rightx = x + Xoffset - (eyeWidth//2)

    # vertical eye position
    Eye_Y = y - (eyeHeight//2) - Yoffset

    # used when drawing sleeping eye arcs
    eye_angle = math.pi

    # arc thickness for sleeping eyes
    eye_arc_width = int(WIDTH * .0066666666)


    # BLINK SYSTEM
    # reduces visible eye height during blink animation

    bottom_of_eye = Eye_Y + eyeHeight

    blinkdirection = 1

    # shrink eye vertically based on blink value
    currentHeight = eyeHeight * (1 - blink) * blinkdirection

    # shift top edge downward as eye closes
    new_top = bottom_of_eye - currentHeight


    # SLEEP MODE EYES (curved arc shape)
    if state == "sleep":

        pygame.draw.arc(
            surface,
            BLACK,
            (leftx, Eye_Y, eyeWidth, eyeHeight),
            eye_angle,
            eye_angle * 2.0,
            eye_arc_width
        )

        pygame.draw.arc(
            surface,
            BLACK,
            (rightx, Eye_Y, eyeWidth, eyeHeight),
            eye_angle,
            eye_angle * 2.0,
            eye_arc_width
        )


    # NORMAL OPEN EYES (ellipses)
    else:

        pygame.draw.ellipse(
            surface,
            BLACK,
            (leftx + eye_offset, new_top, eyeWidth, currentHeight)
        )

        pygame.draw.ellipse(
            surface,
            BLACK,
            (rightx + eye_offset, new_top, eyeWidth, currentHeight)
        )



# draws BMO's mouth based on animation state
# breath_amount controls sleep breathing animation
def mouth_normal(surface, state, breath_amount):

    WIDTH, HEIGHT = surface.get_size()

    center_x = WIDTH // 2
    center_y = HEIGHT // 2


    # IDLE / HAPPY SMILE (default expression)
    if state in ("happy", "idle"):

        mouth_angle = math.pi

        # stroke thickness
        mouth_width = int(WIDTH * .0125)

        # mouth length
        mouth_length = int(WIDTH * .25)

        # arc height
        mouth_arc = int(WIDTH * .20)

        # left edge position
        leftx = center_x - mouth_length // 2


        # draw curved smile arc
        pygame.draw.arc(
            surface,
            BLACK,
            (leftx, center_y, mouth_length, mouth_arc),
            mouth_angle,
            mouth_angle * 2.0,
            mouth_width
        )


        # add rounded endpoints to arc
        arc_center_x = leftx + mouth_length // 2
        arc_center_y = center_y + mouth_arc // 2

        radius_x = mouth_length // 2
        radius_y = mouth_arc // 2


        left_x_arc = (
            arc_center_x +
            radius_x * math.cos(mouth_angle)
        ) + mouth_width // 2

        left_y_arc = arc_center_y + radius_y * math.sin(mouth_angle)


        right_x_arc = (
            arc_center_x +
            radius_x * math.cos(mouth_angle * 2)
        ) - mouth_width // 2

        right_y_arc = arc_center_y + radius_y * math.sin(mouth_angle * 2)


        pygame.draw.circle(
            surface,
            BLACK,
            (int(left_x_arc), int(left_y_arc)),
            mouth_width // 1.75
        )

        pygame.draw.circle(
            surface,
            BLACK,
            (int(right_x_arc), int(right_y_arc)),
            mouth_width // 1.75
        )



    # FULL OPEN TALKING MOUTH (largest speech frame)
    if state == "open":

        mouth_width = int(WIDTH * .125)
        mouth_width_half = mouth_width // 2

        leftx = center_x - mouth_width_half

        center_y = center_y + HEIGHT // 4 - mouth_width_half


        # main mouth shape (rectangle + rounded edges)
        pygame.draw.rect(surface, BLACK, (leftx, center_y, mouth_width, mouth_width))

        pygame.draw.circle(surface, BLACK,
                           (leftx, center_y + mouth_width_half),
                           mouth_width_half)

        pygame.draw.circle(surface, BLACK,
                           (leftx + mouth_width, center_y + mouth_width_half),
                           mouth_width_half)


        # tongue shape
        pygame.draw.ellipse(
            surface,
            DARK_GREEN,
            (leftx, center_y + mouth_width // 1.5,
             mouth_width, mouth_width // 3)
        )



    # SMALL OPEN TALKING MOUTH (short syllable frame)
    if state == "open_small":

        mouth_width = int(WIDTH * .125)
        mouth_width_half = mouth_width // 2

        leftx = center_x - mouth_width_half

        center_y = center_y + HEIGHT // 4 - mouth_width_half


        pygame.draw.circle(
            surface,
            BLACK,
            (leftx + mouth_width_half,
             center_y + mouth_width_half),
            mouth_width_half
        )



    # HALF-OPEN TALKING FRAME
    if state == "mouth_half":

        mouth_width = int(WIDTH * .125)
        mouth_width_half = mouth_width // 2

        leftx = center_x - mouth_width_half

        center_y = center_y + HEIGHT // 4 - mouth_width_half


        pygame.draw.circle(
            surface,
            BLACK,
            (leftx + mouth_width_half,
             center_y + mouth_width),
            mouth_width
        )


        # mask upper portion so only lower half visible
        pygame.draw.rect(
            surface,
            GREEN,
            (leftx - mouth_width_half,
             center_y + mouth_width,
             mouth_width * 2,
             mouth_width)
        )


        # tongue detail
        pygame.draw.ellipse(
            surface,
            DARK_GREEN,
            (leftx,
             center_y + mouth_width // 1.5,
             mouth_width,
             mouth_width // 3)
        )



    # SLEEP BREATHING MOUTH
    if state == "sleep":

        mouth_width = int(WIDTH * .125)
        mouth_width_half = mouth_width // 2

        leftx = center_x

        base_y = center_y + HEIGHT // 4


        base_radius = mouth_width_half


        # expand + shift mouth slightly for breathing effect
        radius = base_radius + breath_amount
        y_pos = base_y + breath_amount


        pygame.draw.circle(
            surface,
            BLACK,
            (leftx, int(y_pos)),
            int(radius)
        )



# master face drawing function called once per frame from main.py
def draw_face(surface, state, blink, eye_offset, breath_amount):

    # draw eyes first
    eyes(surface, blink, state, eye_offset)

    # draw mouth second
    mouth_normal(surface, state, breath_amount)
