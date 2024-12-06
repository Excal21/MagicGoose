import pygame
import sys
import random

#Játékos textúrája: https://axolotl-jim.itch.io/wizard-goose-sp
#Szellemek textúrája: https://ossiron.itch.io/pixel-ghost

# Színek
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Ablak méretei
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Játékos osztály
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)  # A játékos egy négyzet
        self.image = pygame.image.load("player.png")  # Játékos textúra betöltése
        self.image = pygame.transform.scale(self.image, (90, 90))  # Méretezés
        self.speed = 5
        self.lives = 10
        self.is_alive = True

    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)  # Játékos textúrájának megjelenítése

    def take_damage(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.is_alive = False

# Lövedék osztály
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 14, 14)  # A lövedék egy 10x10-es négyzet
        self.color = (193, 236, 255)  # Világoskék szín (light blue)
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed  # Felfelé mozog

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, 7)  # Kerek lövedék (5 pixel átmérő)

# Ellenfél osztály
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)  # Az ellenfél egy téglalap
        self.image = pygame.image.load("pixelghost.png")  # Textúra betöltése
        self.image = pygame.transform.scale(self.image, (40, 40))  # Méretezés

    def update(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += 1
        elif self.rect.x > player.rect.x:
            self.rect.x -= 1
        if self.rect.y < player.rect.y:
            self.rect.y += 1
        elif self.rect.y > player.rect.y:
            self.rect.y -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)  # A textúra megjelenítése

# Fő játék osztály
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Lövöldözős Játék")
        self.clock = pygame.time.Clock()
        self.running = True

        self.reset_game()

    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT // 2)
        self.bullets = []
        self.enemies = []
        self.spawn_timer = 0
        self.score = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.is_alive:  # Lövés
                    bullet = Bullet(self.player.rect.centerx - 5, self.player.rect.top)
                    self.bullets.append(bullet)
                if event.key == pygame.K_r and not self.player.is_alive:  # Újraindítás
                    self.reset_game()

    def spawn_enemy(self):
        x = random.choice([0, SCREEN_WIDTH])  # Balról vagy jobbról érkezik
        y = random.randint(0, SCREEN_HEIGHT)
        enemy = Enemy(x, y)
        self.enemies.append(enemy)

    def update(self):
        if not self.player.is_alive:
            return  # Ha a játékos halott, a játék nem frissül tovább

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # Lövedékek frissítése
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:  # Ha a lövedék elhagyja a képernyőt
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

        # Ellenfelek frissítése
        for enemy in self.enemies[:]:
            enemy.update(self.player)

            # Ütközés ellenőrzése a játékossal
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage()  # Sebzés
                if enemy in self.enemies:
                    self.enemies.remove(enemy)  # Ellenfél eltűnik

        # Lövedékek és ellenségek ütközésének ellenőrzése
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10

        # Ellenfelek megjelenítése időzítő alapján
        self.spawn_timer += 1
        if self.spawn_timer >= 60:  # 1 másodpercenként
            self.spawn_enemy()
            self.spawn_timer = 0

    def draw(self):
        self.screen.fill(BLACK)

        if self.player.is_alive:
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            # Életek kijelzése
            lives_text = pygame.font.SysFont(None, 36).render(f"Lives: {self.player.lives}", True, GREEN)
            self.screen.blit(lives_text, (10, 10))

            # Pontszám kijelzése
            score_text = pygame.font.SysFont(None, 36).render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 50))
        else:
            # Játék vége képernyő
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

            restart_text = pygame.font.SysFont(None, 36).render("Press 'R' to Restart", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

# Játék indítása
if __name__ == "__main__":
    game = Game()
    try:
        game.run()
    except SystemExit:
        game.quit()
