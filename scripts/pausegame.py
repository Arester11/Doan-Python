import pygame
import sys

def pause_game(screen):


    resume = (255, 255, 255)
    return_to_menu = (255, 255, 255)
    # Chờ người chơi nhấn chuột vào resume hoặc quit
    while True:
        
        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        paused_text = font.render("Game Paused", True, (255, 255, 255))
        paused_rect = paused_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
        screen.blit(paused_text, paused_rect)

        resume_text = font.render("Resume", True, resume)
        resume_rect = resume_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(resume_text, resume_rect)

        quit_text = font.render("Return To Main Menu", True, return_to_menu)
        quit_rect = quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(quit_text, quit_rect)
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
                
            if resume_rect.collidepoint(mouse_pos):
                
                resume = (150, 150, 150)
                
                if pygame.mouse.get_pressed()[0]:
                    return "resume"
            else:
                resume = (255, 255, 255)     
            
            if quit_rect.collidepoint(mouse_pos):
                
                return_to_menu = (150, 150, 150)
                
                if pygame.mouse.get_pressed()[0]:
                    return "quit"
            else:
                return_to_menu = (255, 255, 255)
        pygame.display.update()
