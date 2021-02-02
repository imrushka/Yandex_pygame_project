import pygame, sys

screen_w, screen_l = 1000, 700
pygame.init()
screen = pygame.display.set_mode((screen_w, screen_l))
clock = pygame.time.Clock()

background_suraface = pygame.image.load("background_space.jpg")
background_suraface = pygame.transform.scale(background_suraface, (1000, 700))

while True:
    #отлавливаем события
    for event in pygame.event.get():
        #если выходим
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(background_suraface, (0, 0))

    pygame.display.update()
    clock.tick(120)
