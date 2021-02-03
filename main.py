import pygame, sys, random

screen_w, screen_l = 1000, 700
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_l))
clock = pygame.time.Clock()

#класс корабля
class Space_ship(pygame.sprite.Sprite):
    def __init__(self, path, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.bullets_paths = ["laserGreen.png", "laserRed.png"]
        self.laser = pygame.mixer.Sound("laserfire01.ogg")

    def update(self, pos_x, pos_y):
        self.rect.center = (pos_x, pos_y)

    def shoot(self):
        self.laser.play()

    def create_bullet(self, ind, velocity):
        return Bullet(self.rect.x + 49, self.rect.y, self.bullets_paths[ind], velocity)


#класс лазерного выстрела
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path, velocity):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.velocity = velocity

    def update(self):
        self.rect.y -= self.velocity

        #проверяем на выход за границы экрана
        if self.rect.y < -10:
            self.kill()

#класс метеорита
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

def keep_in_frame(type, num):
    if type == 1:
        if num >= 1000:
            num = 1000
        if num <= 0:
            num = 0
    else:
        if num >= 700:
            num = 700
        if num <= 0:
            num = 0
    return num

#загружаем фон космоса
background_surface = pygame.image.load("background_space.jpg")
background_surface = pygame.transform.scale(background_surface, (1000, 700))

#группа для корабля
space_ship = Space_ship("player.png", 500, 600)
space_ship_group = pygame.sprite.Group()
space_ship_group.add(space_ship)

#группа для лазерных пуль
bullets = pygame.sprite.Group()

#группа для метеоров
meteors = pygame.sprite.Group()
SAPWNMETEOR = pygame.USEREVENT
pygame.time.set_timer(SAPWNMETEOR, 1200)

#прячем мышь
pygame.mouse.set_visible(False)

#переменные для позиции кораблика
cur_pos_x = 500
cur_pos_y = 600

#переменные для движения
up = False
down = False
right = False
left = False

ship_velocity = 5
while True:
    #отлавливаем события
    for event in pygame.event.get():

        #если выходим из игры
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        #описываем движение
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right = True

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left = True

            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                down = True

            if event.key == pygame.K_UP or event.key == pygame.K_w:
                up = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right = False

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left = False

            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                down = False

            if event.key == pygame.K_UP or event.key == pygame.K_w:
                up = False

        #описываем стрельбу
        if event.type == pygame.MOUSEBUTTONDOWN:
            space_ship.shoot()
            bullets.add(space_ship.create_bullet(random.randrange(0, 2, 1), 5))
        if event.type == SAPWNMETEOR:
            meteors.add(Meteor(random.randrange(30, screen_w - 30), -10))

    #двигаем корабль
    if up:
        cur_pos_y -= ship_velocity
        cur_pos_y = keep_in_frame(2, cur_pos_y)
    if down:
        cur_pos_y += ship_velocity
        cur_pos_y = keep_in_frame(2, cur_pos_y)
    if right:
        cur_pos_x += ship_velocity
        cur_pos_x = keep_in_frame(1, cur_pos_x)
    if left:
        cur_pos_x -= ship_velocity
        cur_pos_x = keep_in_frame(1, cur_pos_x)

    #ставим фон космоса
    screen.blit(background_surface, (0, 0))

    space_ship_group.draw(screen)
    space_ship_group.update(cur_pos_x, cur_pos_y)

    bullets.draw(screen)
    bullets.update()

    meteors.update()
    meteors.draw(screen)

    pygame.display.flip()
    clock.tick(120)
