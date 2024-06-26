import pygame
import sys
import random
import math 
import os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.pausegame import pause_game

class Game:
    def __init__(self, WINDOW_SIZE):
        pygame.init()

        pygame.display.set_caption('Platformer game')
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        self.display = pygame.Surface((WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2))
        self.WINDOW_SIZE = WINDOW_SIZE

        self.clock = pygame.time.Clock()

        self.movement = [False,False]

        self.assets = {
            'decor':load_images('tiles/decor'),
            'grass':load_images('tiles/grass'),
            'large_decor':load_images('tiles/large_decor'),
            'stone':load_images('tiles/stone'),
            'player':load_image('entities/player.png'),
            'background':load_image('background.png'),
            'clouds':load_images('clouds'),
            'enemy/idle':Animation(load_images('entities/enemy/idle'),img_dur=6),
            'enemy/run':Animation(load_images('entities/enemy/run'),img_dur=4),
            'player/idle':Animation(load_images('entities/player/idle'),img_dur=6),
            'player/run':Animation(load_images('entities/player/run'),img_dur=4),
            'player/jump':Animation(load_images('entities/player/jump')),
            'player/slide':Animation(load_images('entities/player/slide')),
            'player/wall_slide':Animation(load_images('entities/player/wall_slide')),
            'particle/leaf':Animation(load_images('particles/leaf'),img_dur=20,loop=False),
            'particle/particle':Animation(load_images('particles/particle'),img_dur=6,loop=False),
            'gun':load_image('gun.png'),
            'projectile':load_image('projectile.png'),
        }

        self.clouds = Clouds(self.assets['clouds'],count = 16)

        self.player=Player(self,(50,50),(8,15))

        self.tilemap = Tilemap(self,tile_size=16)

        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0
    
    def load_level(self,map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1)]):
            if spawner['variant']== 0:
                self.player.pos=spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self,spawner['pos'],(8,15)))

        self.projectiles = []
        self.particles=[]
        self.sparks = []

        self.scroll = [0,0]
        self.dead = 0
        self.transition = -30

    def run(self):
        paused = False
        run = True
        
        while run:
            self.display.fill((0,0,0,0))
            self.display_2.blit(pygame.transform.scale(self.assets['background'], self.WINDOW_SIZE),(0,0))

            self.screenshake = max(0,self.screenshake - 1)

            if len(self.enemies):
                self.transition+=1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    if self.level == 3:
                        a = endgame(self.screen, self.WINDOW_SIZE)
                        if a == "menu":
                            run = False
                        if a == "retry":
                            self.level = -1
                    else:
                        self.load_level(self.level)
            if self.transition<0:
                self.transition+=1

            if self.dead:
                self.dead+=1
                if self.dead>=10:
                    self.transition = min(30,self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

            self.scroll[0]+=(self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])/30
            self.scroll[1]+=(self.player.rect().centery - self.display.get_height()/2 - self.scroll[1])/30
            render_scroll= (int(self.scroll[0]),int(self.scroll[1]))

            for rect in self.leaf_spawners:
                if random.random()*49999 <rect.width *rect.height:
                    pos= (rect.x + random.random()*rect.width,rect.y +random.random()*rect.height)
                    self.particles.append(Particle(self,'leaf',pos,velocity=[-0.1,0.3],frame = random.randint(0,20)))

            self.clouds.update()
            self.clouds.render(self.display_2,offset=render_scroll)

            self.tilemap.render(self.display,offset=render_scroll)

            for  enemy in  self.enemies.copy():
                kill = enemy.update(self.tilemap,(0,0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            for projectile in self.projectiles.copy():
                projectile[0][0]+=projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width()/2 - render_scroll[0],projectile[0][1] - img.get_height()/2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 +(math.pi if projectile[1]>0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing)<50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.screenshake = max(16,self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi *2
                            speed = random.random()*5
                            self.sparks.append(Spark(self.player.rect().center,angle,2 + random.random()))
                            self.particles.append(Particle(self,'particle',self.player.rect().center,velocity=[math.cos(angle+angle+math.pi)*speed*0.5,math.sin(angle + math.pi)*speed*0.5],frame=random.randint(0,7)))

            if not self.dead:
                self.player.update(self.tilemap,(self.movement[1]-self.movement[0],0))
                self.player.render(self.display,offset=render_scroll)

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display,offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,180),unsetcolor=(0,0,0,0))
            for offset in [(-1,0),(1,0),(0,-1),(0,1)]:
                self.display_2.blit(display_sillhouette,offset)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display,offset=render_scroll)
                if particle.type =='leaf':
                    particle.pos[0]+= math.sin(particle.animation.frame * 0.035)*0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type ==pygame.KEYDOWN:
                    if event.key==pygame.K_a:
                        self.movement[0] = True
                    if event.key==pygame.K_d:
                        self.movement[1]=True
                    if event.key==pygame.K_SPACE:
                        self.player.jump()
                    if event.key==pygame.K_LSHIFT:
                        self.player.dash()
                if event.type ==pygame.KEYUP:
                    if event.key==pygame.K_a:
                        self.movement[0] = False
                    if event.key==pygame.K_d:
                        self.movement[1]=False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused 
                        if paused:
                            result = pause_game(self.screen)
                            if result == "quit":
                                run = False
                            elif result == "resume":
                                paused = False     
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf,(255,255,255),(self.display.get_width()//2,self.display.get_height()//2),(30-abs(self.transition))*15)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf,(0,0))

            self.display_2.blit(self.display,(0,0))
            
            screenskake_offset = (random.random()*self.screenshake - self.screenshake / 2,random.random()*self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2,self.screen.get_size()),(screenskake_offset))
            pygame.display.update()
            self.clock.tick(60)

def endgame(screen, WINDOW_SIZE):
    screen.fill((255, 255, 255))
    font = pygame.font.Font(pygame.font.get_default_font(), 50)
    background = load_image("background3.jpg")
    
    return_menu = retry = (255, 255, 255)
    
    run = True
    action = ""
    screen.blit(pygame.transform.scale(background, WINDOW_SIZE), (0, 0))
    
    while run:
        
        you_win_text = font.render("YOU WIN!!!", True, (255, 255, 0))
        retry_text = font.render("Retry", True, retry)
        return_text = font.render("Return To Main Menu", True, return_menu)
        
        you_win_rect = you_win_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50))
        retry_rect = retry_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))
        return_rect = return_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 150))
        
        
        screen.blit(you_win_text, you_win_rect)
        screen.blit(retry_text, retry_rect)
        screen.blit(return_text, return_rect)
        
        for event in pygame.event.get():
            
            mouse_pos = pygame.mouse.get_pos()
            
            if return_rect.collidepoint(mouse_pos):
                return_menu = (150, 150, 150)
                if pygame.mouse.get_pressed()[0]:
                    action = "menu"
                    run = False
            else:
                return_menu = (255, 255, 255)
                
            if retry_rect.collidepoint(mouse_pos):
                retry = (150, 150, 150)
                if pygame.mouse.get_pressed()[0]:
                    action = "retry"
                    run = False
            else:
                retry = (255, 255, 255)        
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            pygame.display.update()
    return action
    
#menu
def main_menu():
    
    WIDTH, HEIGHT = 640 ,480
    WINDOW_SIZE = (WIDTH, HEIGHT)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Ninja")

    start = (0, 0, 0)
    quit = (0, 0, 0)
    font = pygame.font.Font(pygame.font.get_default_font(), 50)
    background = load_image('background2.png')   
    
    running = True
    while running:
        start_text = font.render("Start", True, start)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        quit_text = font.render("Quit", True, quit)
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        screen.blit(pygame.transform.scale(background, WINDOW_SIZE),(0,0))
        screen.blit(start_text, start_rect)
        screen.blit(quit_text, quit_rect)
        pygame.display.update()

        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if start_rect.collidepoint(mouse_pos):
                
                start = (150, 150, 150)
                
                if pygame.mouse.get_pressed()[0]:
                    Game(WINDOW_SIZE).run()
            else:
                start = (37, 60, 100)        
            
            if quit_rect.collidepoint(mouse_pos):
                
                quit = (150, 150, 150)
                
                if pygame.mouse.get_pressed()[0]:
                    running = False
                    pygame.quit()
                    sys.exit()
            else:
                quit = (16,220,252)
                    

if __name__ == "__main__":
    pygame.init()
    # Mở menu chính
    main_menu()
