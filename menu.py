import pygame
from scripts.button import Button

def game_menu(self):
        main_menu = True
        
        #khai bao nut
        resume_img = pygame.image.load('data/images/button/button_resume.png').convert_alpha()
        quit_img = pygame.image.load('data/images/button/button_quit.png').convert_alpha()
        resume_button = Button(320, 100, resume_img, 0.5)
        quit_button = Button(320, 200, quit_img, 0.5)
        while main_menu:
            
            #ve nut
            if resume_button.draw(self.screen) == True:
                pause_menu = True
                game_paused = False
                
                resume_button_pause = Button(320, 100, resume_img, 0.5)
                quit_button_pause = Button(320, 200, quit_img, 0.5)
                
                
                
            if quit_button.draw(self.screen) == True:
                main_menu = False
            
            pygame.display.update()