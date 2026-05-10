# Imports
from pygame import *
import math
import sys

try:
    music_state = sys.argv[1]
    music_volume = int(sys.argv[2]) * 0.01
    sfx_volume = int(sys.argv[3]) * 0.01
except (IndexError, ValueError):
    music_state = "On"
    music_volume = 0.5
    sfx_volume = 0.5


init()
mixer.init()

#Variables
W, H = 640, 480
FPS = 60
ORANGE = (245, 108, 66)

#Classes
class Unit:
    def __init__(self, x, y, damage, cooldown, unit_range):
        self.x = x
        self.y = y
        self.damage = damage
        self.cooldown = cooldown
        self.range = unit_range

        #sounds
        self.shoot_sound = mixer.Sound("sounds/dragon-studio-clean-minimal-pop-467466.wav")
        self.shoot_sound.set_volume(sfx_volume)

        #images
        self.unit_img = transform.scale(image.load("images/unit_images/unit.png"), (64, 64))
        self.rotated_image = self.unit_img.copy()
        self.rect = self.unit_img.get_rect(center=(x, y))

        self.angle = 0

        self.timer = 0
        self.targeted_enemy = None
        self.line_timer = 0
        self.is_placed = False

        self.rect.center = (self.x, self.y)

    def rotate(self, enemies):
        target = None
        min_distance = 999999

        for enemy in enemies:
            distance = math.hypot(enemy.rect.centerx - self.rect.centerx,
                                  enemy.rect.centery - self.rect.centery)
            if distance < min_distance:
                min_distance = distance
                target = enemy

        if target:
            distance_x = target.rect.centerx - self.rect.centerx
            distance_y = target.rect.centery - self.rect.centery

            rads = math.atan2(-distance_y, distance_x)
            self.angle = math.degrees(rads) - 90

            old_center = self.rect.center

            self.rotated_image = transform.rotate(self.unit_img, self.angle)
            self.rect = self.rotated_image.get_rect(center=old_center)

    def shoot(self, enemies):
        if not self.is_placed:
            return

        if self.timer > 0:
            self.timer -=1

        if self.line_timer > 0:
            self.line_timer -= 1


        if self.timer == 0:
            for enemy in enemies:
                distance = ((self.x - enemy.x)**2 + (self.y - enemy.y)**2)**0.5

                if distance <= self.range:
                    enemy.health -= self.damage
                    self.shoot_sound.play()
                    self.timer = self.cooldown
                    self.line_timer = 5
                    self.targeted_enemy = (enemy.x, enemy.y)
                    self.targeted_enemy = enemy
                    break
                else:
                    self.targeted_enemy = None

    def draw(self, window):
        #draw.rect(window, (0, 255, 0), self.rect)
        window.blit(self.rotated_image, self.rect)
        draw.circle(window, (255, 255, 255), self.rect.center, self.range, 1)

        if self.line_timer > 0 and self.targeted_enemy is not None:
            draw.line(window, (50, 94, 168), self.rect.center, self.targeted_enemy.rect.center, 3)




class Enemy:
    def __init__(self, speed, health):
        self.speed = speed
        self.health = health

        self.reached_base = False

        #animation
        image_size = (64, 64)

        self.down_images = [
            transform.scale(image.load("images/enemy_images/alien_FL.png"), image_size),
            transform.scale(image.load("images/enemy_images/alien_FR.png"), image_size)
        ]

        self.left_images = [
            transform.scale(image.load("images/enemy_images/alien_LL.png"), image_size),
            transform.scale(image.load("images/enemy_images/alien_LR.png"), image_size)
        ]

        self.timer = 0
        self.animation_speed = 0.1
        self.direction = "down"

        self.waypoints = [
            (560, -20),
            (560, 130),
            (120, 130),
            (120, 390),
            (490, 390),
            (490, 500),
        ]

        self.targeted_waypoint = 0
        self.x, self.y = self.waypoints[0]

        self.rect = Rect(self.x, self.y, image_size[0], image_size[1])

    def move(self):
        if self.targeted_waypoint < len(self.waypoints):
            waypoint_x, waypoint_y = self.waypoints[self.targeted_waypoint]

            if self.x < waypoint_x:
                self.x += self.speed
                self.direction = "right"

            elif self.x > waypoint_x:
                self.x -= self.speed
                self.direction = "left"

            elif self.y < waypoint_y:
                self.y += self.speed
                self.direction = "down"


            self.rect.center = (self.x, self.y)

            if abs(self.x - waypoint_x) < self.speed and abs(self.y - waypoint_y) < self.speed:
                self.x = waypoint_x
                self.y = waypoint_y
                self.targeted_waypoint += 1

        else:
            self.reached_base = True


    def draw(self, window):
        #draw.rect(window, (0, 0, 255), self.rect)

        self.timer+= 0.1

        image_index = int(self.timer) % 2
        img = self.down_images[image_index]

        if self.direction == "down":
            img = self.down_images[image_index]

        if self.direction == "left":
            img = self.left_images[image_index]

        if self.direction == "right":
            img = self.left_images[image_index]
            img = transform.flip(img, True, False)

        window.blit(img, self.rect)




class Game:
    def __init__(self):
        self.window = display.set_mode((W, H))
        display.set_caption("Mars Defense")
        self.bg_path = image.load("images/background_images/path_updated.png")
        self.bg_path = transform.scale(self.bg_path, (W, H))

        self.clock = time.Clock()
        self.game = True

        #fonts
        font.init()
        self.orbitron_font = font.SysFont("Orbitron", 40, "bold")

        self.enemies = []
        self.units = []
        self.placing_unit = None
        self.can_place = False
        self.gold = 30
        self.base_health = 3

        #sounds and music
        self.win_sound = mixer.Sound("sounds/Win sound.wav")
        self.lose_sound = mixer.Sound("sounds/losetrumpet.wav")

        if music_state == "On":
            mixer.music.load("music/JRPG_Theme_Loop_Ready_KLICKAUD.mp3")
            mixer.music.play(-1)
            mixer.music.set_volume(music_volume)

        #wave variables
        self.wave = 1
        self.enemies_to_spawn = 2
        self.enemies_spawned = 0
        self.enemy_speed = 2
        self.enemy_health = 100
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.is_break = True
        self.break_duration = 300
        self.break_timer = self.break_duration


        self.path_rects = [
            Rect(530, 0, 55, 145),
            Rect(135, 112, 410, 30),
            Rect(90, 110, 55, 300),
            Rect(115, 370, 400, 40),
            Rect(460, 380, 55, 100),
        ]

        #temp
        self.waypoints = [
            (560, -20),
            (560, 130),
            (120, 130),
            (120, 390),
            (490, 390),
            (490, 500),
        ]

    def game_loop(self):
        while self.game:
            for e in event.get():
                if e.type == QUIT:
                    self.game = False

                if e.type == KEYDOWN:
                    if e.key == K_1:
                        self.placing_unit = Unit(0, 0, 30, 60, 100)

                if e.type == MOUSEBUTTONDOWN:
                   if e.button == 1 and self.placing_unit is not None and self.gold >= 15 and self.can_place:
                        self.placing_unit.is_placed = True
                        self.gold -= 15

                        self.units.append(self.placing_unit)
                        self.placing_unit = None

            #Creating waves
            if self.is_break:
                self.break_timer -= 1
                if self.break_timer <= 0:
                    self.is_break = False
                    self.enemies_spawned = 0
            else:
                if self.enemies_spawned < self.enemies_to_spawn:
                    self.spawn_timer += 1
                    if self.spawn_timer >= self.spawn_delay:
                        new_enemy = Enemy(self.enemy_speed, self.enemy_health)
                        self.enemies.append(new_enemy)
                        self.enemies_spawned += 1
                        self.spawn_timer = 0

                if self.enemies_spawned >= self.enemies_to_spawn and len(self.enemies) == 0:
                    self.is_break = True
                    self.break_timer = self.break_duration

                    self.wave += 1
                    self.enemies_to_spawn += 2
                    self.enemy_speed += 0.2
                    self.enemy_health += 15

                if self.wave == 5:
                    self.spawn_delay = 45
                if self.wave == 8:
                    self.spawn_delay = 30
                if self.wave == 10:
                    self.spawn_delay = 23


            for enemy in self.enemies[:]:
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.gold += 5

            gold_text = self.orbitron_font.render(f"Gold: {self.gold}", True, (232, 229, 21))
            base_health_text = self.orbitron_font.render(f"Base health: {self.base_health}", True, (255, 0, 0))
            wave_text = self.orbitron_font.render(f"Wave: {self.wave}/10", True, (255, 255, 255))

            self.window.blit(self.bg_path, (0, 0))

            self.window.blit(gold_text, (10, 10))
            self.window.blit(base_health_text, (10, 40))
            self.window.blit(wave_text, (W // 2, 10))

            #debugging
            #for path_rect in self.path_rects:
                #draw.rect(self.window, (0, 255, 0), path_rect, 2)

            #if len(self.waypoints) > 1:
                #draw.lines(self.window, (255, 0, 0), False, self.waypoints, 5)

            if self.placing_unit is not None:
                mouse_pos = mouse.get_pos()
                self.placing_unit.rect.center = mouse_pos
                self.placing_unit.x = mouse_pos[0]
                self.placing_unit.y = mouse_pos[1]

                self.can_place = True
                if self.placing_unit.rect.collidelist(self.path_rects) != -1:
                    self.can_place = False

                if self.placing_unit.rect.collidelist([unit.rect for unit in self.units]) != -1:
                    self.can_place = False
            else:
                self.can_place = False

            for enemy in self.enemies[:]:
                enemy.move()
                enemy.draw(self.window)
                if enemy.reached_base:
                    self.base_health -= 1
                    enemy.reached_base = False
                    self.enemies.remove(enemy)

            for unit in self.units:
                unit.shoot(self.enemies)
                unit.rotate(self.enemies)
                unit.draw(self.window)

            if self.placing_unit is not None:
                self.placing_unit.draw(self.window)

            #win or lose conditions
            if self.base_health <= 0:
                mixer.music.stop()
                self.lose_sound.play()
                time.delay(3000)
                self.game = False

            if self.wave > 10:
                mixer.music.stop()
                self.win_sound.play()
                time.delay(3000)
                self.game = False

            self.clock.tick(FPS)
            display.update()

if __name__ == "__main__":
    app = Game()
    app.game_loop()