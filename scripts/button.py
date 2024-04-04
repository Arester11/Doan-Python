import pygame

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        
    def draw(self, screen):
        
        #lay vi tri chuot
        pos = pygame.mouse.get_pos()
        
        #ktra chuot va dieu kien click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                print("clicked")
                print(self.clicked)
                
        
        #ve nut len man hinh
        screen.blit(self.image, (self.rect.x, self.rect.y))