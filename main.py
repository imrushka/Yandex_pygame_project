import pygame, sys

screen_w, screen_l = 1000, 700
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_l))
clock = pygame.time.Clock()

class Space_ship(pygame.sprite.Sprite):
    def __init__(self, path, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

    def update(self):
        self.rect.center = pygame.mouse.get_pos()



#загружаем фон космоса
background_surface = pygame.image.load("background_space.jpg")
background_surface = pygame.transform.scale(background_surface, (1000, 700))

space_ship = Space_ship("player.png", 500, 600)
space_ship_group = pygame.sprite.Group()
space_ship_group.add(space_ship)

#прячем мышь
pygame.mouse.set_visible(False)


while True:
    #отлавливаем события
    for event in pygame.event.get():
        #если выходим из игры
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            space_ship_group.update()

    #ставим фон космоса
    screen.blit(background_surface, (0, 0))
    space_ship_group.draw(screen)

    pygame.display.flip()
    clock.tick(120)
