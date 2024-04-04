import pygame
import gameplay

from scripts.button import Button

resume_img = pygame.image.load('images/button/button_resume.png').convert_alpha()
quit_img = pygame.image.load('images/button/button_quit.png').convert_alpha()
resume_button = Button(320, 100, resume_img)
quit_button = Button(320, 200, quit_img)
clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode((1280, 720))
    
run_menu = True
    
while run_menu:
             
    pygame.display.update()
    clock.tick(30)