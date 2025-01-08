import sys
import math
from typing import *
import tkinter
from tkinter import filedialog
from PIL import Image
import pygame
from pygame.locals import *
pygame.init()

from ColorPallette256 import colors
points = []
chroma_sliders = [0, 100, None]
lightness_sliders = [0, 100, None]
selected_color = None
clicked_color = 0
dragged_index = 0
drag_mode_delay = 0
hilighted_colors = []
pallette_colors = [None for _ in range(140)]
shifted_pallette_colors = [None for _ in range(140)]

MainClock = pygame.time.Clock()
font = pygame.font.SysFont("bahnschrift", 20)
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
pygame.display.set_caption('Pixel Editor v1')
#icon = pygame.image.load(r"icon.png").convert_alpha()
#pygame.display.set_icon(icon)
origin = (screen.get_width() // 2, screen.get_height() // 2)
camera_angles = [0, 0]
current_input = []
initial_mouse_position = (0, 0)
initial_mouse_position2 = (0, 0)
buttons = [False, False, False, False, False]
state = ""

image = None
canvases = []
canvas_index = -1
background_color = (255, 255, 255)
pixel_size = 20
position = [0, 0]
canvas_position = None
canvas_history = []
canvas_history_index = []
canvas_save_location = []
canvas_selection = []
canvas_selection_toggle = False
selection_canvas = []
selection_canvas_position = [0, 0]
selection_canvas_offset = [0, 0]

def update():
    global initial_mouse_position
    global dragged_index, shifted_pallette_colors, drag_mode_delay
    global canvas_position, selection_canvas_position, selection_canvas_offset
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        if all(e > 0 and e < 550 for e in pygame.mouse.get_pos()) and\
           all(e > 0 and e < 550 for e in initial_mouse_position) and\
           (lightness_sliders[2] == None and chroma_sliders[2] == None) and state == "color picker":
            camera_angles[0] += (pygame.mouse.get_pos()[0] - initial_mouse_position[0]) / 3
            camera_angles[0] %= 360
            camera_angles[1] += (pygame.mouse.get_pos()[1] - initial_mouse_position[1]) / 3
            if camera_angles[1] > 90:
                camera_angles[1] = 90
            if camera_angles[1] < -90:
                camera_angles[1] = -90
            initial_mouse_position = pygame.mouse.get_pos()
        
        if mouse_x > 550 and mouse_x < 600 and mouse_y > 0 and mouse_y < 600 and\
           initial_mouse_position[0] > 550 and initial_mouse_position[0] < 600 and\
           initial_mouse_position[1] > 0 and initial_mouse_position[1] < 600 and state == "color picker":
            if abs(mouse_y - ((lightness_sliders[0] / 100) * 515) - 30) < 10:
                lightness_sliders[2] = 0
            if abs(mouse_y - ((lightness_sliders[1] / 100) * 515) - 30) < 10:
                lightness_sliders[2] = 1
        if lightness_sliders[2] == 0:
            lightness_sliders[0] = max(0, min(lightness_sliders[1] - 2, ((mouse_y - 30) / 515) * 100))
        if lightness_sliders[2] == 1:
            lightness_sliders[1] = max(lightness_sliders[0] + 2, min(100, ((mouse_y - 30) / 515) * 100))
        if mouse_x > 0 and mouse_x < 600 and mouse_y > 550 and mouse_y < 600 and\
           initial_mouse_position[0] > 0 and initial_mouse_position[0] < 600 and\
           initial_mouse_position[1] > 550 and initial_mouse_position[1] < 600 and state == "color picker":
            if abs(mouse_x - ((chroma_sliders[0] / 100) * 515) - 30) < 10:
                chroma_sliders[2] = 0
            if abs(mouse_x - ((chroma_sliders[1] / 100) * 515) - 30) < 10:
                chroma_sliders[2] = 1
        if chroma_sliders[2] == 0:
            chroma_sliders[0] = max(0, min(chroma_sliders[1] - 2, ((mouse_x - 30) / 515) * 100))
        if chroma_sliders[2] == 1:
            chroma_sliders[1] = max(chroma_sliders[0] + 2, min(100, ((mouse_x - 30) / 515) * 100))
        
        if mouse_x > 0 and mouse_x < 600 and mouse_y > 600 and mouse_y < screen.get_height() and\
           state == "color pallette":
            if pallette_colors[clicked_color]:
                dragged_index = max(0, min(19, (pygame.mouse.get_pos()[0] - 21) // 27)) + \
                                (max(0, min(6, (pygame.mouse.get_pos()[1] - 598) // 27)) * 20)
                if K_LSHIFT in current_input:
                    shifted_pallette_colors = [color for color in pallette_colors]
                    shifted_pallette_colors.pop(clicked_color)
                    shifted_pallette_colors.insert(dragged_index, selected_color)
                    pygame.draw.rect(screen, (42, 45, 51), [0, 600, 600, screen.get_height()])
                    for i, color in enumerate(shifted_pallette_colors):
                        if color:
                            if color in hilighted_colors:
                                pygame.draw.rect(screen, (255, 255, 0), 
                                                 [(27 * (i % 20)) + 19, (27 * (i // 20)) + 600, 24, 24], 0, 5)
                            if color == selected_color:
                                pygame.draw.rect(screen, (255, 255, 255), 
                                                 [(27 * (i % 20)) + 19, (27 * (i // 20)) + 600, 24, 24], 0, 5)
                            pygame.draw.rect(screen, colors[color], 
                                             [(27 * (i % 20)) + 21, (27 * (i // 20)) + 602, 20, 20], 0, 4)
                        else:
                            pygame.draw.rect(screen, (89, 95, 106), 
                                             [(27 * (i % 20)) + 21, (27 * (i // 20)) + 602, 20, 20], 0, 4)
                else:
                    render_color_pallette(False)
                    pygame.draw.rect(screen, (42, 45, 51), 
                                     [(27 * (clicked_color % 20)) + 19, 
                                     (27 * (clicked_color // 20)) + 600, 24, 24], 0, 5)
                    pygame.draw.rect(screen, (89, 95, 106), 
                                     [(27 * (clicked_color % 20)) + 21, 
                                     (27 * (clicked_color // 20)) + 602, 20, 20], 0, 4)
                    pygame.draw.rect(screen, (255, 255, 255), 
                                     [(27 * (dragged_index % 20)) + 19, 
                                     (27 * (dragged_index // 20)) + 600, 24, 24], 0, 5)
                    pygame.draw.rect(screen, colors[selected_color], 
                                     [(27 * (dragged_index % 20)) + 21, 
                                     (27 * (dragged_index // 20)) + 602, 20, 20], 0, 4)
                    pygame.display.update()
    else:
        chroma_sliders[2] = None
        lightness_sliders[2] = None
    if state == "color picker" or state == "color pallette":
        render_color_points()
    elif mouse_x > 600 and mouse_x < 1400 and mouse_y > 0 and mouse_y < screen.get_height() and canvases:
        canvas_position = [((mouse_x - position[0]) - 600) // pixel_size, (mouse_y - position[1]) // pixel_size]
        if canvas_position[0] < 0 or canvas_position[0] >= len(canvases[canvas_index]) or\
           canvas_position[1] < 0 or canvas_position[1] >= len(canvases[canvas_index][0]):
            canvas_position = None
        if canvas_position and pygame.mouse.get_pressed()[0]:
            if canvas_selection_toggle:
                if K_LSHIFT in current_input:
                    selection_canvas_position = \
                        [((mouse_x - initial_mouse_position2[0]) + selection_canvas_offset[0]) // pixel_size, 
                         ((mouse_y - initial_mouse_position2[1]) + selection_canvas_offset[1]) // pixel_size]
                else:
                    if (canvas_position not in canvas_selection) and (K_LALT not in current_input):
                        canvas_selection.append(canvas_position)
                    elif (canvas_position in canvas_selection) and (K_LALT in current_input):
                        canvas_selection.remove(canvas_position)
            else:
                if selected_color and K_LALT not in current_input:
                    canvases[canvas_index][int(canvas_position[0])][int(canvas_position[1])] = colors[selected_color]
                else:
                    canvases[canvas_index][int(canvas_position[0])][int(canvas_position[1])] = None
        render_canvas()
    if drag_mode_delay and K_LSHIFT not in current_input:
        drag_mode_delay -= 1
        
def calcuate_color_point(point):
    rotated_point = [100 * ((point[0] / 100) ** 0.8333), point[1], point[2] + camera_angles[0]]
    rotated_point = [2.5 * rotated_point[1] * math.cos(math.radians(rotated_point[2])), 
                     5 * (50 - rotated_point[0]), 
                     2.5 * rotated_point[1] * math.sin(math.radians(rotated_point[2])),]
    θ = math.radians(camera_angles[1])
    rotated_point = [rotated_point[0],
                     (rotated_point[1] * math.cos(θ)) - (rotated_point[2] * math.sin(θ)), 
                     (rotated_point[1] * math.sin(θ)) + (rotated_point[2] * math.cos(θ))]
    return (rotated_point[0] + 275, rotated_point[1] + 275, rotated_point[2])
    
def render_color_points(update=True):
    global points
    pygame.draw.rect(screen, (42, 45, 51), [0, 0, 600, 600])

    pygame.draw.line(screen, (89, 95, 106), (575, 30), (575, 545), 1)
    for slider in lightness_sliders[:2]:
        pygame.draw.circle(screen, (89, 95, 106), (575, round((slider / 100) * 515) + 30), 5)
    pygame.draw.line(screen, (89, 95, 106), (30, 575), (545, 575), 1)
    for slider in chroma_sliders[:2]:
        pygame.draw.circle(screen, (89, 95, 106), (round((slider / 100) * 515) + 30, 575), 5)

    points = []
    for color in colors:
        if (100 * (((100 - color[0]) / 100) ** 0.8333)) > lightness_sliders[0] and\
           (100 * (((100 -  color[0]) / 100) ** 0.8333)) < lightness_sliders[1] and\
           color[1] >= chroma_sliders[0] and color[1] <= chroma_sliders[1]:
            points.append((color, calcuate_color_point(color)))
    points.sort(key=lambda x: x[1][2], reverse=True)
    for point in points:
        if point[0] in hilighted_colors:
            pygame.draw.circle(screen, (255, 255, 0), [point[1][0], point[1][1]], 10)
        if point[0] == selected_color:
            pygame.draw.circle(screen, (255, 255, 255), [point[1][0], point[1][1]], 10)
        pygame.draw.circle(screen, colors[point[0]], [point[1][0], point[1][1]], 8)
    if update:
        pygame.display.update()

def render_color_pallette(update=True):
    pygame.draw.rect(screen, (42, 45, 51), [0, 600, 600, screen.get_height()])
    for i, color in enumerate(pallette_colors):
        if color:
            if color in hilighted_colors:
                pygame.draw.rect(screen, (255, 255, 0), 
                                 [(27 * (i % 20)) + 19, (27 * (i // 20)) + 600, 24, 24], 0, 5)
            if color == selected_color:
                pygame.draw.rect(screen, (255, 255, 255), 
                                 [(27 * (i % 20)) + 19, (27 * (i // 20)) + 600, 24, 24], 0, 5)
            pygame.draw.rect(screen, colors[color], 
                             [(27 * (i % 20)) + 21, (27 * (i // 20)) + 602, 20, 20], 0, 4)
        else:
            pygame.draw.rect(screen, (89, 95, 106), 
                             [(27 * (i % 20)) + 21, (27 * (i // 20)) + 602, 20, 20], 0, 4)
    if update:
        pygame.display.update()
    
def render_canvas(update=True):
    global canvas_position, selection_canvas_position
    pygame.draw.rect(screen, (89, 95, 106), [600, 0, 800, screen.get_height()])
    if canvases:
        for x in range(len(canvases[canvas_index])):
            for y in range(len(canvases[canvas_index][x])):
                if ((x + 1) * pixel_size) + position[0] > 0 and (x * pixel_size) + position[0] < 800 and\
                   ((y + 1) * pixel_size) + position[1] > 0 and (y * pixel_size) + position[1] < 800:
                    if canvases[canvas_index][x][y]:
                        pygame.draw.rect(screen, canvases[canvas_index][x][y], 
                                        [600 + max(0, (x * pixel_size) + position[0]), 
                                         max(0, (y * pixel_size) + position[1]), 
                                         min(800, ((x + 1) * pixel_size) + position[0]) -\
                                         max(0, (x * pixel_size) + position[0]), 
                                         min(800, ((y + 1) * pixel_size) + position[1]) -\
                                         max(0, (y * pixel_size) + position[1])])
                    else:
                        pygame.draw.rect(screen, background_color, 
                                        [600 + max(0, (x * pixel_size) + position[0]), 
                                         max(0, (y * pixel_size) + position[1]), 
                                         min(800, ((x + 1) * pixel_size) + position[0]) -\
                                         max(0, (x * pixel_size) + position[0]), 
                                         min(800, ((y + 1) * pixel_size) + position[1]) -\
                                         max(0, (y * pixel_size) + position[1])])
    
    if K_LSHIFT not in current_input:
        if canvas_position and not (canvas_selection_toggle and (K_LALT in current_input)):
            if ((canvas_position[0] + 1) * pixel_size) + position[0] > 0 and\
            (canvas_position[0] * pixel_size) + position[0] < 800 and\
            ((canvas_position[1] + 1) * pixel_size) + position[1] > 0 and\
            (canvas_position[1] * pixel_size) + position[1] < 800:
                pygame.draw.rect(screen, (0, 0, 0), 
                                [600 + max(0, (canvas_position[0] * pixel_size) + position[0]), 
                                max(0, (canvas_position[1] * pixel_size) + position[1]), 
                                min(800, ((canvas_position[0] + 1) * pixel_size) + position[0]) -\
                                max(0, (canvas_position[0] * pixel_size) + position[0]), 
                                min(800, ((canvas_position[1] + 1) * pixel_size) + position[1]) -\
                                max(0, (canvas_position[1] * pixel_size) + position[1])], 1, round(pixel_size / 10))
        for selection in canvas_selection:
            if ((selection[0] + 1) * pixel_size) + position[0] > 0 and\
            (selection[0] * pixel_size) + position[0] < 800 and\
            ((selection[1] + 1) * pixel_size) + position[1] > 0 and\
            (selection[1] * pixel_size) + position[1] < 800:
                pygame.draw.rect(screen, (0, 0, 0), 
                                [600 + max(0, (selection[0] * pixel_size) + position[0]), 
                                max(0, (selection[1] * pixel_size) + position[1]), 
                                min(800, ((selection[0] + 1) * pixel_size) + position[0]) -\
                                max(0, (selection[0] * pixel_size) + position[0]), 
                                min(800, ((selection[1] + 1) * pixel_size) + position[1]) -\
                                max(0, (selection[1] * pixel_size) + position[1])], 1, round(pixel_size / 10))
    else:
        for selection in selection_canvas:
            if ((selection[0][0] + selection_canvas_position[0] + 1) * pixel_size) + position[0] > 0 and\
            ((selection[0][0] + selection_canvas_position[0]) * pixel_size) + position[0] < 800 and\
            ((selection[0][1] + selection_canvas_position[1] + 1) * pixel_size) + position[1] > 0 and\
            ((selection[0][1] + selection_canvas_position[1]) * pixel_size) + position[1] < 800:
                if selection[1]:
                    pygame.draw.rect(screen, selection[1], 
                                    [600 + max(0, ((selection[0][0] + selection_canvas_position[0]) * pixel_size) + position[0]), 
                                    max(0, ((selection[0][1] + selection_canvas_position[1]) * pixel_size) + position[1]), 
                                    min(800, ((selection[0][0] + selection_canvas_position[0] + 1) * pixel_size) + position[0]) -\
                                    max(0, ((selection[0][0] + selection_canvas_position[0]) * pixel_size) + position[0]), 
                                    min(800, ((selection[0][1] + selection_canvas_position[1] + 1) * pixel_size) + position[1]) -\
                                    max(0, ((selection[0][1] + selection_canvas_position[1]) * pixel_size) + position[1])])
                pygame.draw.rect(screen, (0, 0, 0), 
                                [600 + max(0, ((selection[0][0] + selection_canvas_position[0]) * pixel_size) + position[0]), 
                                max(0, ((selection[0][1] + selection_canvas_position[1]) * pixel_size) + position[1]), 
                                min(800, ((selection[0][0] + selection_canvas_position[0] + 1) * pixel_size) + position[0]) -\
                                max(0, ((selection[0][0] + selection_canvas_position[0]) * pixel_size) + position[0]), 
                                min(800, ((selection[0][1] + selection_canvas_position[1] + 1) * pixel_size) + position[1]) -\
                                max(0, ((selection[0][1] + selection_canvas_position[1]) * pixel_size) + position[1])], 1, 
                                round(pixel_size / 10))
    if update:
        pygame.display.update()

def render_buttons(update=True):
    pygame.draw.rect(screen, (42, 45, 51), [1400, 0, screen.get_width() - 1400, screen.get_height()])
    pygame.draw.rect(screen, (89, 95, 106), [1410, 10, 120, 30], 0, 5)
    screen.blit(font.render("Create File", True, (42, 45, 51)), (1419, 16))
    pygame.draw.rect(screen, (89, 95, 106), [1410, 50, 120, 30], 0, 5)
    screen.blit(font.render("Load File", True, (42, 45, 51)), (1428, 56))
    pygame.draw.rect(screen, (89, 95, 106), [1410, 90, 120, 30], 0, 5)
    screen.blit(font.render("Save As", True, (42, 45, 51)), (1434, 96))
    pygame.draw.rect(screen, (89, 95, 106), [1410, 130, 120, 30], 0, 5)
    screen.blit(font.render("Close File", True, (42, 45, 51)), (1426, 136))
    pygame.draw.rect(screen, (89, 95, 106), [1410, 170, 120, 30], 0, 5)
    screen.blit(font.render("Copy File", True, (42, 45, 51)), (1429, 176))
    screen.blit(font.render("Canvas", True, (89, 95, 106)), (1413, 740))
    screen.blit(font.render("Number", True, (89, 95, 106)), (1410, 760))
    screen.blit(font.render(str(canvas_index + 1), True, (89, 95, 106)), (1498, 753))
    if update:
        pygame.display.update()

def render():
    render_color_points(False)
    render_color_pallette(False)
    render_canvas(False)
    render_buttons(False)
    pygame.display.update()
render()


running  = True
while running:
    update()
    # handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == WINDOWRESIZED:
            render()
        
        if event.type == MOUSEBUTTONDOWN:
            initial_mouse_position = pygame.mouse.get_pos()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and\
               mouse_x > 0 and mouse_x < 600 and mouse_y > 0 and mouse_y < 600:
                state = "color picker"
                for point in reversed(points):
                    distance = (((point[1][0] - pygame.mouse.get_pos()[0]) ** 2) + \
                                ((point[1][1] - pygame.mouse.get_pos()[1]) ** 2)) ** 0.5
                    if distance < 8:
                        selected_color = point[0]
                        render_color_points(False)
                        render_color_pallette()
                        break
            if mouse_x > 0 and mouse_x < 600 and mouse_y > 600 and mouse_y < screen.get_height():
                state = "color pallette"
                initial_mouse_position = pygame.mouse.get_pos()
                clicked_color = max(0, min(19, (pygame.mouse.get_pos()[0] - 21) // 27)) + \
                                (max(0, min(6, (pygame.mouse.get_pos()[1] - 598) // 27)) * 20)
                if pygame.mouse.get_pressed()[0]:
                    selected_color = pallette_colors[clicked_color]
                if pygame.mouse.get_pressed()[2]:
                    if pallette_colors[clicked_color] in hilighted_colors:
                        hilighted_colors.remove(pallette_colors[clicked_color])
                    else:
                        hilighted_colors.append(pallette_colors[clicked_color])
                render_color_points(False)
                render_color_pallette()
            if mouse_x > 600 and mouse_x < 1400 and\
               mouse_y > 0 and mouse_y < screen.get_height():
                state = "drawing"
                initial_mouse_position2 = pygame.mouse.get_pos()
            if mouse_x > 1410 and mouse_x < 1530 and mouse_y > 10 and mouse_y < 40:
                state = "buttons"
                buttons[0] = True
                pygame.draw.rect(screen, (42, 45, 51), [1410, 10, 120, 30], 0, 5)
                pygame.draw.rect(screen, (89, 95, 106), [1411, 11, 118, 28], 0, 5)
                screen.blit(font.render("Create File", True, (42, 45, 51)), (1419, 16))
                pygame.display.update()
            if mouse_x > 1410 and mouse_x < 1530 and mouse_y > 50 and mouse_y < 80:
                state = "buttons"
                buttons[1] = True
                pygame.draw.rect(screen, (42, 45, 51), [1410, 50, 120, 30], 0, 5)
                pygame.draw.rect(screen, (89, 95, 106), [1411, 51, 118, 28], 0, 5)
                screen.blit(font.render("Load File", True, (42, 45, 51)), (1428, 56))
                pygame.display.update()
            if mouse_x > 1410 and mouse_x < 1530 and mouse_y > 90 and mouse_y < 120:
                state = "buttons"
                buttons[2] = True
                pygame.draw.rect(screen, (42, 45, 51), [1410, 90, 120, 30], 0, 5)
                pygame.draw.rect(screen, (89, 95, 106), [1411, 91, 118, 28], 0, 5)
                screen.blit(font.render("Save As", True, (42, 45, 51)), (1434, 96))
                pygame.display.update()
            if mouse_x > 1410 and mouse_x < 1530 and mouse_y > 130 and mouse_y < 160:
                state = "buttons"
                buttons[3] = True
                pygame.draw.rect(screen, (42, 45, 51), [1410, 130, 120, 30], 0, 5)
                pygame.draw.rect(screen, (89, 95, 106), [1411, 131, 118, 28], 0, 5)
                screen.blit(font.render("Close File", True, (42, 45, 51)), (1426, 136))
                pygame.display.update()
            if mouse_x > 1410 and mouse_x < 1530 and mouse_y > 170 and mouse_y < 200:
                state = "buttons"
                buttons[4] = True
                pygame.draw.rect(screen, (42, 45, 51), [1410, 170, 120, 30], 0, 5)
                pygame.draw.rect(screen, (89, 95, 106), [1411, 171, 118, 28], 0, 5)
                screen.blit(font.render("Copy File", True, (42, 45, 51)), (1429, 176))
                pygame.display.update()
        
        if event.type == MOUSEBUTTONUP:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if state == "color pallette":
                if dragged_index != None and\
                   selected_color and pallette_colors[clicked_color] == selected_color and\
                   mouse_x > 0 and mouse_x < 600 and mouse_y > 600 and mouse_y < screen.get_height():
                    if drag_mode_delay:
                        pallette_colors = [color for color in shifted_pallette_colors]
                    else:
                        if pallette_colors[dragged_index] in hilighted_colors and \
                        pallette_colors.count(pallette_colors[dragged_index]) == 1:
                            hilighted_colors.remove(pallette_colors[dragged_index])
                            render_color_points(False)
                        pallette_colors[clicked_color] = None
                        pallette_colors[dragged_index] = selected_color
                    clicked_color = int(dragged_index)
                    dragged_index = None
                render_color_pallette()
            if state == "buttons":
                canvas_selection_toggle = False
                canvas_selection = []
                selection_canvas_offset = [0, 0]
                render_buttons()
                if buttons[0] and\
                   mouse_x > 1410 and mouse_x < 1530 and mouse_y > 10 and mouse_y < 40:
                    root = tkinter.Tk()
                    root.title("Input Width and Height")
                    root.geometry("200x200")
                    tkinter.Label(root, text="Width:").pack(pady=5)
                    width = tkinter.Entry(root)
                    width.pack(pady=5)
                    tkinter.Label(root, text="Height:").pack(pady=5)
                    height = tkinter.Entry(root)
                    height.pack(pady=5)
                    def submit():
                        global canvases, canvas_index, width, height, canvas_history, canvas_history_index
                        try:
                            w = int(width.get())
                            h = int(height.get())
                        except:
                            return
                        if w > 0 and w < 2000 and h > 0 and h < 2000:
                            canvas_index = len(canvases)
                            canvases.append([[None for _ in range(h)] for _ in range(w)])
                            render_canvas(False)
                            canvas_history.append([[[None for _ in range(h)] for _ in range(w)]])
                            canvas_history_index.append(0)
                            canvas_save_location.append(None)
                            root.destroy()
                    create_button = tkinter.Button(root, text="Create", command=submit).pack(pady=20)
                    root.mainloop()
                if buttons[1] and\
                   mouse_x > 1410 and mouse_x < 1530 and mouse_y > 50 and mouse_y < 80:
                    root = tkinter.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                    root.destroy()
                    if file_path:
                        image = pygame.image.load(file_path)
                        if image.get_width() < 2000 and image.get_height() < 2000:
                            canvas_index += 1
                            canvases.append([[image.get_at((x, y)) 
                                            for y in range(image.get_height())] 
                                            for x in range(image.get_width())])
                            canvas_history.append([[[image.get_at((x, y)) 
                                                  for y in range(image.get_height())] 
                                                  for x in range(image.get_width())]])
                            canvas_history_index.append(0)
                            canvas_save_location.append(None)
                            render_canvas(False)
                if buttons[2] and\
                   mouse_x > 1410 and mouse_x < 1530 and mouse_y > 90 and mouse_y < 120:
                    root = tkinter.Tk()
                    root.withdraw()
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.png"), ("All files", "*.*")],
                        title="Save As"
                    )
                    root.destroy()
                    canvas_save_location[canvas_index] = file_path
                    flat_data = [(canvases[canvas_index][row][col][0], canvases[canvas_index][row][col][1], canvases[canvas_index][row][col][2], 255) 
                                 if canvases[canvas_index][row][col] is not None else (0, 0, 0, 0) 
                                 for col in range(len(canvases[canvas_index]))
                                 for row in range(len(canvases[canvas_index][col]))]
                    img = Image.new('RGBA', (len(canvases[canvas_index][0]), 
                                             len(canvases[canvas_index])))
                    img.putdata(flat_data)
                    img.save(canvas_save_location[canvas_index])
                if buttons[3] and\
                   mouse_x > 1410 and mouse_x < 1530 and mouse_y > 130 and mouse_y < 160:
                    if canvases:
                        canvases.pop(canvas_index)
                        canvas_history.pop(canvas_index)
                        canvas_history_index.pop(canvas_index)
                        canvas_save_location.pop(canvas_index)
                        canvas_index -= 1
                    render_canvas(False)
                if buttons[4] and\
                   mouse_x > 1410 and mouse_x < 1530 and mouse_y > 170 and mouse_y < 200:
                    if canvases:
                        canvases.append([[canvases[canvas_index][x][y]\
                                          for y in range(len(canvases[canvas_index][0]))]\
                                          for x in range(len(canvases[canvas_index]))])
                        canvas_index = len(canvases) - 1
                    render_canvas(False)
                render_buttons()
                buttons = [False, False, False, False, False]
            if state == "drawing" and canvas_index != 0: 
                if not canvas_selection_toggle:
                    if not all([canvases[canvas_index][i][j] == canvas_history[canvas_index][0][i][j] \
                                for i in range(len(canvases[canvas_index])) \
                                for j in range(len(canvases[canvas_index][0]))]):
                        canvas_history[canvas_index] = canvas_history[canvas_index][canvas_history_index[canvas_index]:]
                        canvas_history_index[canvas_index] = 0
                        canvas_history[canvas_index].insert(0, [[canvases[canvas_index][j][i] 
                                                                for i in range(len(canvases[canvas_index][0]))]
                                                                for j in range(len(canvases[canvas_index]))])
                        if len(canvas_history[canvas_index]) > 50:
                            canvas_history[canvas_index].pop()
            if K_LSHIFT in current_input and canvas_selection_toggle:
                selection_canvas_offset[0] += pygame.mouse.get_pos()[0] - initial_mouse_position2[0]
                selection_canvas_offset[1] += pygame.mouse.get_pos()[1] - initial_mouse_position2[1]
                print(selection_canvas_offset)
            state = ""
                
        if event.type == KEYDOWN:
            current_input.append(event.key)
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_a:
                pallette_colors.insert(0, selected_color)
                pallette_colors.pop()
                render_color_pallette()
            if event.key == K_q:
                if canvas_position:
                    if canvases[canvas_index][int(canvas_position[0])][int(canvas_position[1])]:
                        value = canvases[canvas_index][int(canvas_position[0])][int(canvas_position[1])]
                        pallette_colors.insert(0, list(colors.keys())[list(colors.values()).index(value)])
                        pallette_colors.pop()
                        selected_color = pallette_colors[0]
                        render_color_pallette()
            if event.key == K_x:
                hilighted_colors = []
                render_color_points(False)
                render_color_pallette()
            if event.key == K_DELETE:
                if pallette_colors[clicked_color] == selected_color:
                    if pallette_colors[clicked_color] in hilighted_colors and \
                       pallette_colors.count(pallette_colors[clicked_color]) == 1:
                        hilighted_colors.remove(pallette_colors[clicked_color])
                    pallette_colors.pop(clicked_color)
                    pallette_colors.append(None)
                    if clicked_color != 0:
                        clicked_color -= 1
                    while clicked_color != 0 and pallette_colors[clicked_color] == None:
                        clicked_color -= 1
                    selected_color = pallette_colors[clicked_color]
                    render_color_points(False)
                    render_color_pallette()
            if event.key == K_LSHIFT:
                if canvas_selection_toggle:
                    selection_canvas = [[selection, 
                                         canvases[canvas_index][int(selection[0])][int(selection[1])]] 
                                         for selection in canvas_selection]
                    for selection in canvas_selection:
                        canvases[canvas_index][int(selection[0])][int(selection[1])] = None
                else:
                    drag_mode_delay = 10
            if event.key == K_RIGHT:
                if K_RSHIFT in current_input and canvas_index != len(canvases) - 1:
                    canvases[canvas_index], canvases[canvas_index + 1] =\
                    canvases[canvas_index + 1], canvases[canvas_index]
                canvas_index += 1
                canvas_index %= len(canvases)
                canvas_selection_toggle = False
                canvas_selection = []
                selection_canvas_offset = [0, 0]
                render_canvas(False)
                render_buttons()
            if event.key == K_LEFT:
                if K_RSHIFT in current_input and canvas_index != 0:
                    canvases[canvas_index], canvases[canvas_index - 1] =\
                    canvases[canvas_index - 1], canvases[canvas_index]
                canvas_index -= 1
                canvas_index %= len(canvases)
                canvas_selection_toggle = False
                canvas_selection = []
                selection_canvas_offset = [0, 0]
                render_canvas(False)
                render_buttons()
            if event.key == K_b:
                if selected_color:
                    background_color = colors[selected_color]
                else:
                    background_color = (89, 95, 106)
                render_canvas()
            if event.key == K_s:
                if K_LCTRL in current_input:
                    if canvas_save_location[canvas_index]:
                        flat_data = [(canvases[canvas_index][row][col][0], canvases[canvas_index][row][col][1], canvases[canvas_index][row][col][2], 255) 
                                     if canvases[canvas_index][row][col] is not None else (0, 0, 0, 0) 
                                     for col in range(len(canvases[canvas_index]))
                                     for row in range(len(canvases[canvas_index][col]))]
                        img = Image.new('RGBA', (len(canvases[canvas_index][0]), 
                                                 len(canvases[canvas_index])))
                        img.putdata(flat_data)
                        img.save(canvas_save_location[canvas_index])
                else:
                    if canvas_position:
                        if canvas_selection_toggle:
                            canvas_selection = []
                            canvas_selection_toggle = False
                            selection_canvas_offset = [0, 0]
                        else:
                            canvas_selection_toggle = True
            if event.key == K_z and K_LCTRL in current_input:
                if K_LSHIFT in current_input:
                    if canvas_history_index[canvas_index] != 0:
                        canvas_history_index[canvas_index] -= 1
                else:
                    if canvas_history_index[canvas_index] != len(canvas_history[canvas_index]) - 1:
                        canvas_history_index[canvas_index] += 1
                canvases[canvas_index] = \
                [[canvas_history[canvas_index][canvas_history_index[canvas_index]][j][i] 
                for i in range(len(canvas_history[canvas_index][canvas_history_index[canvas_index]][0]))]
                for j in range(len(canvas_history[canvas_index][canvas_history_index[canvas_index]]))]
                render_canvas()
        if event.type == KEYUP:
            current_input.remove(event.key)
            if event.key == K_LSHIFT and state != "color pallette":
                for selection in selection_canvas:
                    if selection[0][0] + selection_canvas_position[0] > 0 and \
                       selection[0][0] + selection_canvas_position[0] < len(canvases[canvas_index]) and \
                       selection[0][1] + selection_canvas_position[1] > 0 and \
                       selection[0][1] + selection_canvas_position[1] < len(canvases[canvas_index][0]):
                        canvases[canvas_index] \
                                [int(selection[0][0] + selection_canvas_position[0])] \
                                [int(selection[0][1] + selection_canvas_position[1])] = selection[1]
                selection_canvas = []
                canvas_selection = []
                canvas_selection_toggle = False
                selection_canvas_offset = [0, 0]
                if not all([canvases[canvas_index][i][j] == canvas_history[canvas_index][0][i][j] \
                            for i in range(len(canvases[canvas_index])) \
                            for j in range(len(canvases[canvas_index][0]))]):
                    canvas_history[canvas_index] = canvas_history[canvas_index][canvas_history_index[canvas_index]:]
                    canvas_history_index[canvas_index] = 0
                    canvas_history[canvas_index].insert(0, [[canvases[canvas_index][j][i] 
                                                            for i in range(len(canvases[canvas_index][0]))]
                                                            for j in range(len(canvases[canvas_index]))])
                    if len(canvas_history[canvas_index]) > 50:
                        canvas_history[canvas_index].pop()
        
        if event.type == MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x > 600 and mouse_x < 1400 and\
               mouse_y > 0 and mouse_y < screen.get_height():
                if event.precise_y == 1 or event.precise_y == -1:
                    pixel_size += event.precise_y
                    pixel_size = max(4, min(100, pixel_size))
                else:
                    position[0] -= 4 * event.x
                    position[1] += 4 * event.y
                    position[0] = max(-700, min(700, position[0]))
                    position[1] = max(-700, min(700, position[1]))
                render_canvas()
        
    MainClock.tick(30)

pygame.quit()
sys.exit()