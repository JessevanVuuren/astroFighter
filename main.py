# https://www.youtube.com/watch?v=L3ktUWfAMPg&ab_channel=TechWithTim
from colour import Color

import asyncio
import random
import pygame
import math
import time


def random_color(startC, endC, amount):
    index = random.randint(0, amount - 1)
    range = list(Color(startC).range_to(Color(endC), amount))
    return range[index].get_hex_l()

def gradient_color(startC, endC, amount):
    range = list(Color(startC).range_to(Color(endC), amount))
    return [color.get_hex_l() for color in range]


class Entity:
    def __init__(self, x, y, width, height) -> None:
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        
    def setPOS(self,x,y):
        self.x = x
        self.y = y

class MainScreen:
    def __init__(self, width, height, title) -> None:
        self.width = width
        self.height = height
        self.title = title

        self.screen = pygame.display.set_mode((width, height))

    def img_scaler(self, img, factor):
        size = round(img.get_width() * factor), round(img.get_height()* factor)
        return pygame.transform.scale(img, size)
    

    def wrap_around(self, objects):
        for object in objects:
            if (object.x > self.width):
                object.moveTO(-object.width, object.y)
            if (object.y > self.height):
                object.moveTO(object.x, -object.height)
            if (object.x < -object.width - 10):
                object.moveTO(self.width, object.y)
            if (object.y < -object.height - 10):
                object.moveTO(object.x, self.height)
        


class Particle():
    def __init__(self, x, y, size, ttl) -> None:
        self.timer = pygame.time.get_ticks()
        self.pos = pygame.Vector2(x, y)

        self.x = x
        self.y = y
        
        self.is_active = True
        self.seconds = 0
        self.size = size
        self.ttl = ttl

    def place(self):
        if (self.is_active and self.color):
            pygame.draw.circle(main.screen, self.color, self.pos, self.size)

        self.update()

    def update(self):
        seconds = (pygame.time.get_ticks() - self.timer) / 1000
        if (seconds > self.ttl):
            self.is_active = False


class ParticleSmoke(Particle):
    def __init__(self, rocked, x_off, y_off, size, ttl, color_range, width) -> None:
        super().__init__(0, 0, size, ttl)
        self.color = color_range[0]
        self.color_range = color_range
        self.gradient_count = 0
        new_off = random.randint(0, width) - width //2

        x, y = rocked.rot_form_origin(x_off, y_off + new_off)
        self.pos.y = y
        self.pos.x = x

    def draw(self):
        if (self.gradient_count < len(self.color_range) - 1):
            self.gradient_count += 1
            self.color = self.color_range[self.gradient_count]
        super().place()



class ParticleExhaust(Particle):
    def __init__(self, rocked, x_off, y_off, size, ttl, color_range, force, arc) -> None:
        super().__init__(0, 0, size, ttl)
        self.color = color_range[random.randint(0, len(color_range) - 1)]
        self.cone = random.randrange(0, arc) - arc//2
        self.rocked = rocked
        self.force = force
        self.moving = 0

        self.x_off = x_off
        self.y_off = y_off

    def draw(self):
        rotation = math.radians(self.rocked.angle + self.cone)
        x, y = self.rocked.rot_form_origin(self.x_off, self.y_off)

        self.moving += self.force

        self.pos.y = y - self.moving * math.sin(rotation)
        self.pos.x = x - self.moving * math.cos(rotation)

        super().place()



class ParticleSystem:
    def __init__(self) -> None:
        self.particles = []

    def add_particle(self, particle):
        self.particles.append(particle)

    def update(self):
        for particle in self.particles:
            if (particle.is_active):
                particle.draw()
            else:
                self.particles.remove(particle)



class Rocked(Entity):
    def __init__(self, x, y, image, size, acceleration, rotation_velocity, max_velocity, brake_force) -> None:
        self.rotation_velocity = rotation_velocity;
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.brake_force = brake_force

        self.smokeRange = gradient_color("white", "#181818", 60)
        self.exhaustRange = gradient_color("red", "yellow", 60)

        self.velocity = 0
        self.angle = -90

        self.pos = pygame.Vector2(x, y)
        self.image = image
        self.size = size

        self.rect = None

        Entity.__init__(self, self.pos.x, self.pos.y, image.get_rect().w, image.get_rect().h)

    def moveTO(self,x,y):
        self.pos.x = x
        self.pos.y = y

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.thrust_effect("middle")
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        elif (self.velocity > 0):
            self.velocity = self.velocity * math.pow((1 - self.brake_force), delta_time) 
        else:
            self.velocity = 0

        if keys[pygame.K_a]:
            self.thrust_effect("right")
            self.angle -= self.rotation_velocity
        if keys[pygame.K_d]:
            self.thrust_effect("left")
            self.angle += self.rotation_velocity

        self.draw_rocked()
        self.move()

    def rot_form_origin(self, x_offset, y_offset):
        angle_radians = math.radians(self.angle)

        origin_x = self.pos.x + self.image.get_rect().w // 2
        origin_y = self.pos.y + self.image.get_rect().h // 2

        new_point_x = origin_x + x_offset
        new_point_y = origin_y + y_offset

        cos = math.cos(angle_radians)
        sin = math.sin(angle_radians)

        new_x1 = (new_point_x - origin_x) * cos - (new_point_y - origin_y) * sin + origin_x
        new_y1 = (new_point_x - origin_x) * sin + (new_point_y - origin_y) * cos + origin_y

        return (new_x1, new_y1)

    def thrust_effect(self, direction):
        if (direction == "left"):
            x, y, = -25, -31.4
        elif(direction == "right"):
            x, y = -25, 31.4
        elif(direction == "middle"):
            x, y = -25, 0

        ps.add_particle(ParticleExhaust(self, x, y, 3, .1, self.exhaustRange, 4, 30))
        ps.add_particle(ParticleSmoke(self, x - 20, y * 1.2, 4, 1, self.smokeRange, 15))


    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.velocity
        horizontal = math.sin(radians) * self.velocity

        self.pos.x += vertical
        self.pos.y += horizontal

        self.setPOS(self.pos.x, self.pos.y)

    def draw_rocked(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle - 90)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.pos.x, self.pos.y)).center)
        main.screen.blit(rotated_image, new_rect.topleft)


class Coin(Particle):
    def __init__(self, x, y) -> None:
    
        self.x = x
        self.y = y
        self.color = "#ffdd33"
        self.radius = 6

    def draw(self):
        pygame.draw.circle(main.screen, self.color, (self.x, self.y), self.radius)



class CoinSystem:
    def __init__(self) -> None:
        self.coins = []
        self.spawn_coin()

    def spawn_coin(self):
        randX = random.randint(10, WIDTH - 10)
        randY = random.randint(10, HEIGHT - 10)

        self.coins.append(Coin(randX, randY))

    def update(self, rocked):
        for coin in self.coins:
            if (math.sqrt(math.pow(rocked.x - coin.x, 2) + math.pow(rocked.y - coin.y, 2)) < coin.radius):
                print("Coinnned")

            coin.draw()



WIDTH = 1280
HEIGHT = 720
FPS = 60

pygame.init()

main = MainScreen(WIDTH, HEIGHT, "Astro")

clock = pygame.time.Clock()

running = True
delta_time = 0


rocked_image = main.img_scaler(pygame.image.load("./spaceship.png"), .2)
player = Rocked(WIDTH//2, HEIGHT//2, rocked_image, 40, .4, 4, 10, .9)


ps = ParticleSystem()
cs = CoinSystem()


while running:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False

    main.screen.fill("#181818")
    ps.update()

    player.update(delta_time)

    main.wrap_around([player])

    cs.update(player)

    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000
    # print(clock.get_fps())

pygame.quit()
