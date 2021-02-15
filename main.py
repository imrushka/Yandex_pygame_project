import random
import sqlite3
import sys
from datetime import date

import pygame

# инициализация базовых вещей
screen_w, screen_l = 1000, 700
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_l))
clock = pygame.time.Clock()


# класс корабля
class Space_ship(pygame.sprite.Sprite):
    def __init__(self, ind, pos_x, pos_y):
        super().__init__()
        # массив картинок для анимации
        self.ships_angles = ["player.png", "playerRight.png", "playerLeft.png"]
        # грузим картинки
        self.image = pygame.image.load(self.ships_angles[ind]).convert_alpha()
        # распологаем картинку
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        # снимаем маску для проверки столкновений
        self.mask = pygame.mask.from_surface(self.image)
        # массив картинок для разных пуль
        self.bullets_paths = ["laserGreen.png", "laserRed.png"]
        # массив разных звуков стрельбы
        self.laser = pygame.mixer.Sound("laserfire01.ogg")
        # звук для стрельбы при путой обойме(нет пуль)
        self.beep_sound = [pygame.mixer.Sound("synth_beep_01.ogg"), pygame.mixer.Sound("synth_beep_02.ogg")]

    # логика и движение
    def update(self, pos_x, pos_y, ind):
        self.image = pygame.image.load(self.ships_angles[ind])
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.mask = pygame.mask.from_surface(self.image)

    # звук стрельбы
    def shoot(self):
        self.laser.play()

    # звук для пустого магазина
    def beep(self):
        self.beep_sound[random.randrange(len(self.beep_sound))].play()

    # создаем пулю
    def create_bullet(self, ind, velocity_y, velocity_x):
        return Bullet(self.rect.centerx, self.rect.y, self.bullets_paths[ind], velocity_y, velocity_x)

    # для получения координат
    def get_x(self):
        return self.rect.centerx

    def get_y(self):
        return self.rect.centery


# класс лазерного выстрела
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path, velocity_y, velocity_x=0):
        super().__init__()
        # грузим и рапологаем картинку
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.vel_x, self.vel_y = velocity_x, velocity_y
        self.mask = pygame.mask.from_surface(self.image)
        # для разных звуков
        self.sounds = [
            pygame.mixer.Sound("retro_explosion_01.ogg"),
            pygame.mixer.Sound("retro_explosion_02.ogg"),
            pygame.mixer.Sound("retro_explosion_03.ogg"),
            pygame.mixer.Sound("retro_explosion_04.ogg"),
            pygame.mixer.Sound("retro_explosion_05.ogg")]

    # воспроизводим звук
    def hit_sound(self):
        self.sounds[random.randrange(len(self.sounds))].play()

    # логика и движение
    def update(self):
        self.rect.y -= self.vel_y
        self.rect.x += self.vel_x

        # проверяем на выход за границы экрана
        # самоуничтожение если вышли за грани
        if self.rect.y < -10:
            self.kill()

        if self.rect.x >= 1030:
            self.kill()

        if self.rect.x <= -30:
            self.kill()
        # проверка на столкновение
        # описывем логику столкновений
        # рассомтрим все метеориты
        for sprite_m in meteors:
            # проверим по маске
            if pygame.sprite.collide_mask(self, sprite_m):
                # взрывы и вспышки при столкновеии
                bullets_flashes.add(Muzzle_flash(self.rect.y, self.rect.x))
                shield_explosions.add(sprite_m.collided_with_shield())
                # уничтожение спрайтов
                sprite_m.kill()
                stats.targets_destroyed += 1
                self.kill()
                # звуки при столкновении
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

    # логика и движение
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
            self.enemy_bullet_sound[random.randrange(len(self.enemy_bullet_sound))].play()

        # убираем метеориты котрые пересекаются
        if pygame.sprite.spritecollide(self, meteors, False):
            pass

        # проверяем на столкновение с игроком
        if pygame.sprite.collide_mask(self, space_ship):
            if self.type == 3:
                self.kill()
                stats.overall_shields += 1
                shield.add(Shield_for_player(space_ship.get_x(), space_ship.get_y()))
                self.shield_gain.play()
            else:
                global MENU, Reason
                pygame.mixer.Sound("retro_die_01.ogg").play()
                Reason = "colision with meteor"
                restart()


    # функция стрельбы
    def create_bullet(self):
        return Enemy_bullet(self.rect.x + 49, self.rect.y + 5, "laserRed.png", -7)

    # функция для взрыва обьекта после столкновения с щитом
    def collided_with_shield(self):
        return Shield_explosion(self.rect.centerx, self.rect.centery, self.image.get_size())

    # узнаем тарелка ли это или нет
    def get_type(self):
        if self.type == 3:
            return "bonus"


class Enemy_bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, path, velocity):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y + 10]
        self.velocity = velocity
        self.mask = pygame.mask.from_surface(self.image)

    # логика и движение
    def update(self):
        self.rect.y -= self.velocity

        # проверяем на выход за границы экрана
        if self.rect.y < -10:
            self.kill()
        # проверим на столкновение
        if pygame.sprite.collide_mask(self, space_ship):
            self.kill()
            restart()
            global MENU, Reason
            pygame.mixer.Sound("retro_die_02.ogg").play()
            Reason = "player hit"

    # будем добавлять вспышки
    def add_flash(self):
        return Enemy_muzzle_flash(self.rect.centerx, self.rect.centery)


# для вспышки при столкновении с нашей пулей
class Muzzle_flash(pygame.sprite.Sprite):
    def __init__(self, pos_y, pos_x):
        super().__init__()
        self.image = pygame.image.load("laserGreenShot.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.num = 0

    # логика и движение
    def update(self):
        self.num += 1
        if self.num == 10:
            self.kill()


# для вспышки при столкновении с вражетской пулей
class Enemy_muzzle_flash(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load("laserRedShot.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos_x, pos_y
        self.num = 0

    # логика и движениеsa
    def update(self):
        self.num += 1
        if self.num == 10:
            self.kill()


# для щита
class Shield_for_player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.image.load("spr_shield.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (151, 118))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos_x, pos_y
        # будем вести щет столкновений с щитом
        self.collided = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.col_sound = [pygame.mixer.Sound("clink1.wav"), pygame.mixer.Sound("retro_misc_01.ogg"),
                          pygame.mixer.Sound("retro_misc_02.ogg"), pygame.mixer.Sound("retro_misc_03.ogg")]

    # доюавить музыку при столконовении
    def collision_sound(self):
        self.col_sound[random.randrange(len(self.col_sound))].play()

    # защищаем корабль
    # логика и движение
    def update(self, pos_x, pos_y):
        self.rect.centerx, self.rect.centery = pos_x, pos_y
        for meteor_m in pygame.sprite.spritecollide(self, meteors, False, pygame.sprite.collide_mask):
            if meteor_m.get_type() != "bonus":
                self.collided += 1
                stats.targets_destroyed += 1
                self.collision_sound()
                shield_explosions.add(meteor_m.collided_with_shield())
                meteor_m.kill()
                print("collision with shield")

        for bullet in pygame.sprite.spritecollide(self, enemy_bullets, False, pygame.sprite.collide_mask):
            self.collision_sound()
            enemy_flashes.add(bullet.add_flash())
            bullet.kill()
            print('collision with shield')
            self.collided += 1

        if self.collided >= 3:
            self.kill()


# анимация взрыва
class Shield_explosion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, scale):
        super().__init__()
        self.animation = ["bubble_explo2.png",
                          "bubble_explo3.png", "bubble_explo4.png",
                          "bubble_explo5.png", "bubble_explo6.png",
                          "bubble_explo7.png", "bubble_explo8.png",
                          "bubble_explo9.png", "bubble_explo10.png"]
        self.image = pygame.image.load("bubble_explo1.png").convert_alpha()
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos_x, pos_y
        self.pos_x, self.pos_y = pos_x, pos_y
        self.num = 0
        self.scale = scale

    # логика и движение
    def update(self):
        self.image = pygame.image.load(self.animation[int(self.num)]).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.pos_x, self.pos_y
        self.num += 0.15
        if int(self.num) == 8:
            self.kill()


class Statistics:
    def __init__(self, targets_destroyed, overall_time, overall_shields, date_time, bullet_count, tri_bullet_count):
        self.targets_destroyed = targets_destroyed
        self.overall_time = overall_time
        self.overall_shields = overall_shields
        self.date_time = date_time
        self.bullet_count = bullet_count
        self.tri_bullet_count = tri_bullet_count

    def reset(self):
        self.targets_destroyed = 0
        self.overall_time = 0
        self.overall_shields = 0
        self.date_time = 0
        self.bullet_count = 0
        self.tri_bullet_count = 0

    def get_stats(self):
        return f'targets_destroyed {self.targets_destroyed} overall_time {self.overall_time} ' \
               f'overall_shields {self.overall_shields} date_time {self.date_time} bullet_count {self.bullet_count}' \
               f' tri_bullet_count {self.tri_bullet_count}'

    def get__stats(self):
        return self.targets_destroyed, self.overall_time, self.overall_shields, self.date_time, self.bullet_count, self.tri_bullet_count


# будем держать корабль в поле зрения при его перемещении
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


# отрисовка меню
def drawmenu():
    backgraund_image = pygame.transform.scale(pygame.image.load("menu.jpg").convert(), (screen_w, screen_l))
    screen.blit(backgraund_image, (0, 0))
    arrow_image = pygame.transform.scale(pygame.image.load("arrow1.png").convert_alpha(), (100, 50))
    if state == 0:
        screen.blit(arrow_image, (300, 250))
    if state == 1:
        screen.blit(arrow_image, (300, 400))
    if state == 2:
        screen.blit(arrow_image, (300, 550))

    screen.blit(pygame.font.Font(None, 150).render("SPACE MISSION", 1, (200, 100, 50)), (130, 100))
    screen.blit(pygame.font.Font(None, 150).render("Play", 2, (255, 255, 255)), (400, 250))
    screen.blit(pygame.font.Font(None, 150).render("Result", 2, (255, 255, 255)), (400, 400))
    screen.blit(pygame.font.Font(None, 150).render("Exit", 2, (255, 255, 255)), (400, 550))


# экран вывода 5 лучших результатов
def drawscores():
    backgraund_image = pygame.transform.scale(pygame.image.load("background_space.jpg").convert(), (screen_w, screen_l))
    screen.blit(backgraund_image, (0, 0))

    screen.blit(pygame.font.Font(None, 100).render("Results", 2, (255, 255, 255)), (280, 20))
    screen.blit(pygame.font.Font(None, 50).render("date", 2, (255, 255, 255)), (200, 100))
    screen.blit(pygame.font.Font(None, 50).render("score", 2, (255, 255, 255)), (460, 100))
    screen.blit(pygame.font.Font(None, 50).render("shields", 2, (255, 255, 255)), (620, 100))
    screen.blit(pygame.font.Font(None, 50).render("bullets", 2, (255, 255, 255)), (800, 100))
    results = new_result()
    for i in range(0, min(5, len(results))):
        player_score = f'{i + 1}.{results[i][0]}   {results[i][1]}      {results[i][2]}      {results[i][3]}'
        screen.blit(pygame.font.Font(None, 100).render(player_score, 2, (255, 255, 255)), (50, 150 + i * 100))


# перезапуск игры когда игрок проигрывает
def restart():
    score_writer(f"{date.today().day}/{date.today().month}/{date.today().year}", stats.get__stats()[0],
                 stats.get__stats()[2], stats.get__stats()[-1] + stats.get__stats()[-2])
    stats.reset()
    global MENU, meteors, space_ship, space_ship_group, bullets, enemy_bullets, bullets_flashes, shield, shield_explosions, enemy_flashes, cur_pos_x, cur_pos_y, up, down, left, ship_velocity, right, leftship_velocity, game_difficulty, cur_angle
    MENU = 3
    meteors = pygame.sprite.Group()
    space_ship = Space_ship(0, 500, 600)
    space_ship_group = pygame.sprite.Group()
    space_ship_group.add(space_ship)
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    bullets_flashes = pygame.sprite.Group()
    shield = pygame.sprite.Group()
    shield_explosions = pygame.sprite.Group()
    enemy_flashes = pygame.sprite.Group()
    cur_pos_x = 500
    cur_pos_y = 600
    up = False
    down = False
    right = False
    left = False
    ship_velocity = 2
    game_difficulty = 0
    cur_angle = 0


def drawgameover():
    # abackgraund_image = pygame.transform.scale(pygame.image.load("background_space.jpg").convert(), (screen_w, screen_l))
    # screen.blit(backgraund_image, (0, 0))

    screen.blit(pygame.font.Font(None, 190).render("Game over", 1, (255, 0, 0)), (160, 100))
    global Reason
    screen.blit(pygame.font.Font(None, 100).render(Reason, 1, (255, 0, 0)), (180, 250))
    screen.blit(pygame.font.Font(None, 50).render("press enter to return to menu", 1, (255, 255, 255)), (250, 400))


def score_writer(x, y, z, c):
    a = sqlite3.connect("data.db")
    b = a.cursor()
    b.execute(f"INSERT INTO result(data,score,shield_score,bullets_score) VALUES(?,?,?,?)", (x, y, z, c))
    a.commit()
    a.close()


def new_result():
    a = sqlite3.connect("data.db")
    b = a.cursor()
    c = b.execute("SELECT * FROM result").fetchall()
    return sorted(c, reverse=True, key=lambda x: x[1])


# загружаем фон космоса
background_surface = pygame.image.load("background_space.jpg")
background_surface = pygame.transform.scale(background_surface, (1000, 700))

# группа для корабля
space_ship = Space_ship(0, 500, 600)
space_ship_group = pygame.sprite.Group()
space_ship_group.add(space_ship)

# группа для всего
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bullets_flashes = pygame.sprite.Group()
shield = pygame.sprite.Group()
shield_explosions = pygame.sprite.Group()
enemy_flashes = pygame.sprite.Group()
# группа для метеоров
meteors = pygame.sprite.Group()
# генерим меторы с периодичностью
SAPWNMETEOR = pygame.USEREVENT
pygame.time.set_timer(SAPWNMETEOR, 300)
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
# пауза
do_pause = False
# открыто меню либо игра
MENU = 1
# причина проигрыша
Reason = ""
# для перемещения стрелки
state = 0
# текущее количесво пуль в обойме
bullet_bar = 3
# максимальное количество пуль в обойме
max_bullet_bar = 3
# количество тройных супер пуль
triple_bullet_bar = 4
level_num = 0
game_spped = 100
# будем вести счет для текущей игры
stats = Statistics(0, 0, 0, 0, 0, 0)
shield_health = 0
pygame.mixer.Sound("Tony-igy-astronomia_Kamola.net.mp3").play()
while True:
    if not pygame.mixer.get_busy():
        pygame.mixer.Sound("Tony-igy-astronomia_Kamola.net.mp3").play()

    if MENU == 1:
        for event in pygame.event.get():

            # если выходим из игры
            if event.type == pygame.QUIT:
                print(stats.get_stats())
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    state = (state - 1 + 3) % 3
                if event.key == pygame.K_DOWN:
                    state = (state + 1) % 3
                if event.key == pygame.K_RETURN:
                    if state == 0:
                        pygame.mixer.Sound("synth_misc_04.ogg").play()
                        MENU = 0
                    if state == 1:
                        pygame.mixer.Sound("synth_misc_03.ogg").play()
                        MENU = 2
                    if state == 2:
                        pygame.mixer.Sound("synth_misc_04.ogg").play()
                        pygame.quit()
                        sys.exit()
        drawmenu()

    if MENU == 0:
        for event in pygame.event.get():

            # если выходим из игры
            if event.type == pygame.QUIT:
                print(stats.get_stats())
                pygame.quit()
                sys.exit()

            # описываем движение
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not do_pause:
                    right = True
                    cur_angle = 1
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not do_pause:
                    left = True
                    cur_angle = 2
                if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not do_pause:
                    down = True
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and not do_pause:
                    up = True
                if event.key == pygame.K_ESCAPE:
                    if do_pause:
                        do_pause = False
                    else:
                        pygame.mixer.Sound("synth_misc_01.ogg").play()
                        do_pause = True

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not do_pause:
                    right = False
                    cur_angle = 0
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not do_pause:
                    left = False
                    cur_angle = 0
                if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not do_pause:
                    down = False
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and not do_pause:
                    up = False

            # описываем стрельбу
            if event.type == pygame.MOUSEBUTTONDOWN and not do_pause:
                if event.button == 1:
                    if bullet_bar > 0:
                        stats.bullet_count += 1
                        space_ship.shoot()
                        bullets.add(space_ship.create_bullet(0, 5, 0))
                        bullet_bar -= 1
                    else:
                        space_ship.beep()

                elif event.button == 3:
                    if triple_bullet_bar >= 4:
                        triple_bullet_bar -= 4
                        space_ship.shoot()
                        stats.bullet_count += 3
                        bullets.add(space_ship.create_bullet(0, 6, 0))
                        bullets.add(space_ship.create_bullet(0, 5, 1))
                        bullets.add(space_ship.create_bullet(0, 5, -1))
                    else:
                        space_ship.beep()

            # генерим метеориты
            if event.type == SAPWNMETEOR:
                stats.overall_time += 0.3
                if not do_pause:
                    bullet_bar += 1
                    triple_bullet_bar += 1
                    if triple_bullet_bar >= 4:
                        triple_bullet_bar = 4
                    if bullet_bar >= max_bullet_bar:
                        bullet_bar = max_bullet_bar
                    game_difficulty += 1
                    for met in range(random.randrange(2)):
                        meteors.add(Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1),
                                           random.randrange(0, 2), random.randrange(3, 6), 0))
                    if game_difficulty % 12 == 0:
                        meteors.add(
                            Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1), 3,
                                   random.randrange(3, 6), 0))

                    if game_difficulty % 6 == 0:
                        meteors.add(
                            Meteor(random.randrange(30, screen_w - 30), -1 * random.randrange(20, 500, 1), 2,
                                   random.randrange(3, 6), 0))

                        meteors.add(
                            Meteor(cur_pos_x + 45, -1 * random.randrange(20, 500, 1), 2,
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

        # отрисовка
        c = stats.get__stats()

        screen.blit(background_surface, (0, 0))
        shield.draw(screen)
        bullets.draw(screen)
        space_ship_group.draw(screen)
        enemy_bullets.draw(screen)
        meteors.draw(screen)
        bullets_flashes.draw(screen)
        shield_explosions.draw(screen)
        enemy_flashes.draw(screen)
        screen.blit(pygame.font.Font(None, 50).render(str(c[0]), 2, (200, 100, 50)), (0, 0))

        # обновление
        if not do_pause:
            space_ship_group.update(cur_pos_x, cur_pos_y, cur_angle)
            shield.update(cur_pos_x, cur_pos_y)
            enemy_flashes.update()
            enemy_bullets.update()
            bullets.update()
            meteors.update()
            bullets_flashes.update()
            shield_explosions.update()
        else:
            screen.blit(pygame.font.Font(None, 150).render("Pause", 2, (255, 0, 0)), (350, 250))
            screen.blit(pygame.font.Font(None, 40).render(f"current score: {stats.targets_destroyed}", 2, (255, 0, 0)), (350, 500))
            screen.blit(pygame.font.Font(None, 40).render(f"current bullets fired: {stats.bullet_count}", 2, (255, 0, 0)),
                        (350, 550))



    if MENU == 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(stats.get_stats())
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    MENU = 1
        drawscores()

    if MENU == 3:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(stats.get_stats())
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    MENU = 1
        drawgameover()

    pygame.display.flip()
    clock.tick(120)
