import pygame
import sys

def pause_game(screen):
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    paused_text = font.render("Game Paused", True, (255, 255, 255))
    paused_rect = paused_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(paused_text, paused_rect)

    resume_text = font.render("Resume", True, (255, 255, 255))
    resume_rect = resume_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(resume_text, resume_rect)

    quit_text = font.render("Quit", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(quit_text, quit_rect)

    pygame.display.update()

    # Chờ người chơi nhấn chuột vào resume hoặc quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if resume_rect.collidepoint(mouse_pos):
                    return "resume"
                elif quit_rect.collidepoint(mouse_pos):
                    return "quit"
