import pygame, sys, random

screen_w, screen_l = 1000, 700
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_l))
clock = pygame.time.Clock()


# класс корабля
class Space_ship(pygame.sprite.Sprite):
    def __init__(self, ind, pos_x, pos_y):
        super().__init__()
        self.ships_angles = ["player.png", "playerRight.png", "playerLeft.png", "playerDamaged.png"]
        self.image = pygame.image.load(self.ships_angles[ind]).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.mask = pygame.mask.from_surface(self.image)
        self.bullets_paths = ["laserGreen.png", "laserRed.png"]
        self.laser = pygame.mixer.Sound("laserfire01.ogg")

    def update(self, pos_x, pos_y, ind):
        self.image = pygame.image.load(self.ships_angles[ind])
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.mask = pygame.mask.from_surface(self.image)

    def shoot(self):
        self.laser.play()

    def create_bullet(self, ind, velocity_y, velocity_x):
        return Bullet(self.rect.x + 49, self.rect.y, self.bullets_paths[ind], velocity_y, velocity_x)

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y


# класс лазерного выстрела
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path, velocity_y, velocity_x=0):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.vel_x, self.vel_y = velocity_x, velocity_y
        self.mask = pygame.mask.from_surface(self.image)
        self.sounds = [
            pygame.mixer.Sound("retro_explosion_01.ogg"),
            pygame.mixer.Sound("retro_explosion_02.ogg"),
            pygame.mixer.Sound("retro_explosion_03.ogg"),
            pygame.mixer.Sound("retro_explosion_04.ogg"),
            pygame.mixer.Sound("retro_explosion_05.ogg")]

    def hit_sound(self):
        self.sounds[random.randrange(0, 5)].play()

    def update(self):
        self.rect.y -= self.vel_y
        self.rect.x += self.vel_x

        # проверяем на выход за границы экрана
        if self.rect.y < -10:
            self.kill()

        if self.rect.x >= 1030:
            self.kill()

        if self.rect.x <= -30:
            self.kill()

        for sprite_m in meteors:
            if pygame.sprite.collide_mask(self, sprite_m):
                bullets_flashes.add(Muzzle_flash(self.rect.y, self.rect.x))
                sprite_m.kill()
                self.kill()
                self.hit_sound()
                print('bullet hit')


# класс метеорита
class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type_of_meteor, velocity_y, velocity_x):
        super().__init__()
        self.type = type_of_meteor
        self.meteors_types = ["meteorBig.png", "meteorSmall.png", "enemyShip.png", "enemyUFO.png"]
        self.image = pygame.image.load(self.meteors_types[type_of_meteor]).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.mask = pygame.mask.from_surface(self.image)
        self.num = 0
        self.vel_x = velocity_x
        self.vel_y = velocity_y
        self.shield_gain = pygame.mixer.Sound("key2 pickup.ogg")
        self.enemy_bullet_sound = [pygame.mixer.Sound("synth_laser_01.ogg"),
                                   pygame.mixer.Sound("synth_laser_02.ogg"),
                                   pygame.mixer.Sound("synth_laser_03.ogg"),
                                   pygame.mixer.Sound("synth_laser_04.ogg"),
                                   pygame.mixer.Sound("synth_laser_05.ogg"),
                                   pygame.mixer.Sound("synth_laser_06.ogg"),
                                   pygame.mixer.Sound("synth_laser_07.ogg"),
                                   pygame.mixer.Sound("synth_laser_08.ogg")]

    def update(self):
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x

        self.num += 1
        # проверяем на воход за границы и удаляем
        if self.rect.y >= screen_l + 10:
            self.kill()

        if self.rect.x <= -30:
            self.kill()

        if self.rect.x >= 1030:
            self.kill()

        if self.type == 2 and self.num % 90 == 0:
            enemy_bullets.add(self.create_bullet())
            self.enemy_bullet_sound[random.randrange(8)].play()

        # убираем метеориты котрые пересекаются
        if pygame.sprite.spritecollide(self, meteors, False):
            pass

        # проверяем на столкновение с игроком
        if pygame.sprite.collide_mask(self, space_ship):
            if self.type == 3:
                for i in shield:
                    i.kill()
                shield.add(Shield_for_player(space_ship.get_x(), space_ship.get_y()))
                self.shield_gain.play()
            print('collision with meteor')

    # функция стрельбы
    def create_bullet(self):
        return Enemy_bullet(self.rect.x + 49, self.rect.y + 5, "laserRed.png", -7)


class Enemy_bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path, velocity):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y + 5]
        self.velocity = velocity
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y -= self.velocity

        # проверяем на выход за границы экрана
        if self.rect.y < -10:
            self.kill()

        if pygame.sprite.collide_mask(self, space_ship):
            self.kill()
            print('player hit')


class Muzzle_flash(pygame.sprite.Sprite):
    def __init__(self, pos_y, pos_x):
        super().__init__()
        self.image = pygame.image.load("laserGreenShot.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.num = 0

    def update(self):
        self.num += 1
        if self.num == 10:
            self.kill()


class Shield_for_player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.image.load("shield.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.collided = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.col_sound = pygame.mixer.Sound("clink1.wav")

    # доюавить музыку при столконовении
    def collision_sound(self):
        self.col_sound.play()

    # защищаем корабль
    def update(self, pos_x, pos_y):
        self.rect.center = (pos_x, pos_y)

        if pygame.sprite.spritecollide(self, meteors, True):
            self.collided += 1
            self.collision_sound()
            print("collision with shield")

        if pygame.sprite.spritecollide(self, enemy_bullets, True):
            self.collided += 1
            self.collision_sound()
            print('collision with shield')

        if self.collided >= 5:
            self.kill()


# будем держать корабль в поле зрения
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


# загружаем фон космоса
background_surface = pygame.image.load("background_space.jpg")
background_surface = pygame.transform.scale(background_surface, (1000, 700))

# группа для корабля
space_ship = Space_ship(0, 500, 600)
space_ship_group = pygame.sprite.Group()
space_ship_group.add(space_ship)

# группа для лазерных пуль
bullets = pygame.sprite.Group()

enemy_bullets = pygame.sprite.Group()

bullets_flashes = pygame.sprite.Group()

shield = pygame.sprite.Group()
# группа для метеоров
meteors = pygame.sprite.Group()

SAPWNMETEOR = pygame.USEREVENT
pygame.time.set_timer(SAPWNMETEOR, 1200)

# прячем мышь
pygame.mouse.set_visible(False)

# переменные для позиции кораблика
cur_pos_x = 500
cur_pos_y = 600

# переменные для движения
up = False
down = False
right = False
left = False

ship_velocity = 2

game_difficulty = 0

cur_angle = 0

do_pause = False
while True:
    # print(game_difficulty)
    # отлавливаем события

    for event in pygame.event.get():

        # если выходим из игры
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # описываем движение
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d and not do_pause:
                right = True
                cur_angle = 1

            if event.key == pygame.K_LEFT or event.key == pygame.K_a and not do_pause:
                left = True
                cur_angle = 2

            if event.key == pygame.K_DOWN or event.key == pygame.K_s and not do_pause:
                down = True

            if event.key == pygame.K_UP or event.key == pygame.K_w and not do_pause:
                up = True

            if event.key == pygame.K_ESCAPE:
                if do_pause:
                    do_pause = False
                else:
                    do_pause = True


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d and not do_pause:
                right = False
                cur_angle = 0

            if event.key == pygame.K_LEFT or event.key == pygame.K_a and not do_pause:
                left = False
                cur_angle = 0

            if event.key == pygame.K_DOWN or event.key == pygame.K_s and not do_pause:
                down = False

            if event.key == pygame.K_UP or event.key == pygame.K_w and not do_pause:
                up = False



        # описываем стрельбу
        if event.type == pygame.MOUSEBUTTONDOWN and not do_pause:
            space_ship.shoot()
            bullets.add(space_ship.create_bullet(0, 5, 0))

            #bullets.add(space_ship.create_bullet(0, 6, 0))
            #bullets.add(space_ship.create_bullet(0, 5, 1))
            #bullets.add(space_ship.create_bullet(0, 5, -1))


        # генерим метеориты
        if event.type == SAPWNMETEOR and not do_pause:

            game_difficulty += 1
            for met in range(random.randrange(6)):
                meteors.add(Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1),
                                   random.randrange(0, 2), random.randrange(3, 6), 0))

            if game_difficulty % 3 == 0:
                meteors.add(
                    Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1), 3,
                           random.randrange(3, 6), 0))
            if game_difficulty % 2 == 0:
                meteors.add(
                    Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1), 2,
                           random.randrange(3, 6), 0))


    # двигаем корабль
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

    # ставим фон космоса
    screen.blit(background_surface, (0, 0))

    space_ship_group.draw(screen)
    shield.draw(screen)
    bullets.draw(screen)
    enemy_bullets.draw(screen)
    meteors.draw(screen)
    bullets_flashes.draw(screen)


    if not do_pause:
        space_ship_group.update(cur_pos_x, cur_pos_y, cur_angle)
        shield.update(cur_pos_x, cur_pos_y)
        enemy_bullets.update()
        bullets.update()
        meteors.update()
        bullets_flashes.update()

    pygame.display.flip()
    clock.tick(120)
