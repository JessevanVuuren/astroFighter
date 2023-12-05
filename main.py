# https://www.youtube.com/watch?v=L3ktUWfAMPg&ab_channel=TechWithTim
from threading import Thread
from colour import Color

import random
import pygame
import math
import time

WIDTH = 1280
HEIGHT = 720

FPS = 60

def img_scaler(img, factor):
    size = round(img.get_width() * factor), round(img.get_height()* factor)
    return pygame.transform.scale(img, size)

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

running = True
delta_time = 0

ROCKED_IMG = img_scaler(pygame.image.load("./spaceship.png"), .2)


def random_color(startC, endC, amount):
    index = random.randint(0, amount - 1)
    range = list(Color(startC).range_to(Color(endC), amount))
    return range[index].get_hex_l()



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

        self.color = Color("#000000")

    def place(self):
        if (self.is_active and self.color):
            pygame.draw.circle(SCREEN, self.color.get_hex_l(), self.pos, self.size)

        self.update()

    def update(self):
        seconds = (pygame.time.get_ticks() - self.timer) / 1000
        if (seconds > self.ttl):
            self.is_active = False
        

class ParticleGradient(Particle):
    def __init__(self, x, y, size, ttl, cStart, cEnd) -> None:
        super().__init__(x, y, size, ttl)
        self.startColor = Color(cStart)
        self.endColor = Color(cEnd)
        self.range = self.startColor.range_to(self.endColor, ttl * 60)
        

    def draw(self):
        self.color = next(self.range, False)
        super().place()


class ParticleForce(Particle):
    def __init__(self, rocked, x, y, size, ttl, color, force, arc) -> None:
        super().__init__(x, y, size, ttl)
        self.cone = random.randrange(0, arc) - arc//2
        self.color = Color(color)
        self.rocked = rocked
        self.force = force
        self.moving = 0

    def draw(self):
        rotation = math.radians(self.rocked.angle + self.cone)

        self.moving += self.force
        x, y = self.rocked.rot_form_origin(-25,0)

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



class Rocked:
    def __init__(self, x, y, image, size, acceleration, rotation_velocity, max_velocity, brake_force) -> None:
        self.rotation_velocity = rotation_velocity;
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.brake_force = brake_force

        self.velocity = 0
        self.angle = -90

        self.pos = pygame.Vector2(x, y)
        self.image = image
        self.size = size

        self.rect = None


    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.thrust_effect("middle", smoke=True)
            self.velocity = min(self.velocity + self.acceleration, self.max_velocity)
        elif (self.velocity > 0):
            self.velocity = self.velocity * math.pow((1 - self.brake_force), delta_time) 
        else:
            self.velocity = 0

        if keys[pygame.K_a]:
            self.smoke_effect("right")
            self.angle -= self.rotation_velocity
        if keys[pygame.K_d]:
            self.smoke_effect("left")
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

    def thrust_effect(self, direction, smoke=False):
        smoke = self.rot_form_origin(-25, 0)
        color = random_color("red", "yellow", 10)
        ps.add_particle(ParticleForce(self, smoke[0], smoke[1], 4, .2, color, 4, 30))
        
        if (smoke):
            self.smoke_effect(direction)

    def smoke_effect(self, direction):
        if (direction == "left"):
            smoke = self.rot_form_origin(-25, -31.4)
        elif(direction == "right"):
            smoke = self.rot_form_origin(-25, 31.4)
        elif(direction == "middle"):
            smoke = self.rot_form_origin(-25, 0)
        
        ps.add_particle(ParticleGradient(smoke[0], smoke[1], 4, 1, "white", "black"))


    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.velocity
        horizontal = math.sin(radians) * self.velocity

        self.pos.x += vertical
        self.pos.y += horizontal

    def draw_rocked(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle - 90)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.pos.x, self.pos.y)).center)
        SCREEN.blit(rotated_image, new_rect.topleft)


player = Rocked(WIDTH//2, HEIGHT//2, ROCKED_IMG, 40, .4, 4, 10, .9)
ps = ParticleSystem()


while running:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False

    SCREEN.fill("black")

    ps.update()
    player.update(delta_time)

    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000

pygame.quit()