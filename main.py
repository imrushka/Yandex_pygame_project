import pygame, sys, random

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
        self.laser = pygame.mixer.Sound("laserfire01.ogg")

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def shoot(self):
        self.laser.play()

    def create_bullet(self):
        return Bullet(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load("laserGreen.png")
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

    def update(self):
        self.rect.y -= 5

        #проверяем на выход за границы экрана
        if self.rect.y < -10:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load("meteorBig.png")
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]

    def update(self):
        self.rect.y += 2

        #проверяем на воход за границы и удаляем
        if self.rect.y >= screen_l + 10:
            self.kill()





#загружаем фон космоса
background_surface = pygame.image.load("background_space.jpg")
background_surface = pygame.transform.scale(background_surface, (1000, 700))

space_ship = Space_ship("player.png", 500, 600)
space_ship_group = pygame.sprite.Group()
space_ship_group.add(space_ship)

bullets = pygame.sprite.Group()

meteors = pygame.sprite.Group()
SAPWNMETEOR = pygame.USEREVENT
pygame.time.set_timer(SAPWNMETEOR, 1200)

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            space_ship.shoot()
            bullets.add(space_ship.create_bullet())
        if event.type == SAPWNMETEOR:
            meteors.add(Meteor(random.randrange(30, screen_w - 30), -10))

    #ставим фон космоса
    screen.blit(background_surface, (0, 0))

    space_ship_group.draw(screen)

    bullets.draw(screen)
    bullets.update()

    meteors.draw(screen)
    meteors.update()

    pygame.display.flip()
    clock.tick(120)
