# Import Library
import pygame
import random
import math

# Inisialisasi Pygame
pygame.mixer.init()

# Memberikan suara setiap kali bola bertabrakan dengan paddle / player
paddle_collision_left_sound = pygame.mixer.Sound("assets/sounds/paddle_collision_left.ogg")
paddle_collision_right_sound = pygame.mixer.Sound("assets/sounds/paddle_collision_right.ogg")
pygame.init()

# Mengatur komponen pada game
WIDTH, HEIGHT = 800, 500
BALL_RADIUS = 15
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 90
FPS = 60
COLOR = (0, 0, 0)

## Mengatur game pada class PongGame
class PongGame:
    def __init__(self):
        # Inisialisasi game state-nya
        self.width = WIDTH
        self.height = HEIGHT
        self.ball = {'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': 7, 'speed_y': 7}
        self.left_paddle = {'x': 10, 'y': HEIGHT // 2 - PADDLE_HEIGHT // 2, 'speed': 2, 'score': 0}
        self.right_paddle = {'x': WIDTH - 20 - PADDLE_WIDTH, 'y': HEIGHT // 2 - PADDLE_HEIGHT // 2, 'speed': 10, 'score': 0}
        self.middle_line = {'x': WIDTH // 2, 'height': HEIGHT, 'width': 2}
        self.winner = None
        self.winner_time = None

    def move_ball(self):
        # Menggerakkan bola dan meng-handle collision pada bola
        self.ball['x'] += self.ball['speed_x']
        self.ball['y'] += self.ball['speed_y']

        # Bola bertabrakkan dengan paddle kiri maka bola akan memantul
        if self.ball['x'] <= self.left_paddle['x'] + PADDLE_WIDTH and \
                self.left_paddle['y'] <= self.ball['y'] <= self.left_paddle['y'] + PADDLE_HEIGHT:
            self.ball['speed_x'] = abs(self.ball['speed_x'])
            self.ball['speed_y'] = random.uniform(-7, 7)  # Mengatur arah pantulan yang bermacam-macam berdasarkan sumbu y
            paddle_collision_left_sound.play()  # Mengeluarkan suara jika bertabrakkan dengan paddle kiri

        # Bola bertabrakkan dengan paddle kanan maka bola akan memantul
        if self.ball['x'] >= self.right_paddle['x'] - BALL_RADIUS and \
                self.right_paddle['y'] <= self.ball['y'] <= self.right_paddle['y'] + PADDLE_HEIGHT:
            self.ball['speed_x'] = -abs(self.ball['speed_x'])
            self.ball['speed_y'] = random.uniform(-7, 7)  # Mengatur arah pantulan yang bermacam-macam berdasarkan sumbu y
            paddle_collision_right_sound.play()  # Mengeluarkan suara jika bertabrakkan dengan paddle kanan

        # Bola memantul jika bertabrakkan dengan sisi atas/bawah dari window (layar)
        if self.ball['y'] <= 0 or self.ball['y'] >= HEIGHT:
            self.ball['speed_y'] = -self.ball['speed_y']

        ## Jika bola bertabrakkan pada sisi ujung kiri/kanan dari layar, maka game akan direset
        # bola bertabrakkan dengan sisi ujung kiri
        if self.ball['x'] <= 0:
            self.right_paddle['score'] += 1
            self.check_winner()
            self.reset_ball_to_right()
        # bola bertabrakkan dengan sisi ujung kanan
        elif self.ball['x'] >= WIDTH:
            self.left_paddle['score'] += 1
            self.check_winner()
            self.reset_ball_to_left()

    def reset_ball_to_left(self):
        # mereset posisi bola dan kecepatannya ke arah paddle kiri setelah paddle kanan mendapat 1 skor
        self.ball['x'] = WIDTH // 2
        self.ball['y'] = HEIGHT // 2
        self.ball['speed_x'] = -7
        self.ball['speed_y'] = -7

    def reset_ball_to_right(self):
        # mereset posisi bola dan kecepatannya ke arah paddle kanan setelah paddle kiri mendapat 1 skor
        self.ball['x'] = WIDTH // 2
        self.ball['y'] = HEIGHT // 2
        self.ball['speed_x'] = 7
        self.ball['speed_y'] = 7

    def move_paddle(self, paddle, direction):
        # Menggerakkan paddle ke atas dan ke bawah berdasarkan arah yang ditentukan
        if direction == 'up' and paddle['y'] > 0:
            paddle['y'] -= paddle['speed']
        elif direction == 'down' and paddle['y'] < HEIGHT - PADDLE_HEIGHT:
            paddle['y'] += paddle['speed']

    def update(self, left_action, right_action):
        # Memperbarui status permainan setelah salah satu player mendapat skor
        if self.winner is None:
            self.move_paddle(self.left_paddle, left_action)
            self.move_paddle(self.right_paddle, right_action)
            self.move_ball()

    def check_winner(self):
        # Mengecek pemenang ketika salah satu paddle / player mencapai target (5 poin) maka player tersebut jadi pemenang
        if self.left_paddle['score'] == 5:
            self.winner = 'First Player'
            self.winner_time = pygame.time.get_ticks()
            pygame.mixer.Sound("assets/sounds/winner_sound.ogg").play() # Suara ketika output pemenang dikeluarkan
        elif self.right_paddle['score'] == 5:
            self.winner = 'Second Player'
            self.winner_time = pygame.time.get_ticks()
            pygame.mixer.Sound("assets/sounds/winner_sound.ogg").play() # Suara ketika output pemenang dikeluarkan

## Genetic Algorithm
class GeneticAlgorithm:
    def __init__(self, population_size):
        # Menginisialisasi komponen pada GA untuk mengontrol permainan AI
        self.population_size = population_size
        self.population = [{'left_gene': random.uniform(-1, 1), 'right_gene': random.uniform(-1, 1)} for _ in range(population_size)]
        self.current_agent = 0

    def get_next_agent(self):
        # Berfungsi untuk mengembalikan nilai agen dari populasi secara bergantian
        agent = self.population[self.current_agent]
        self.current_agent = (self.current_agent + 1) % self.population_size
        return agent

def sigmoid(x):
    # Fungsi aktivasi yang dipakai dalam GA untuk menghasilkan nilai antara 0 dan 1
    return 1 / (1 + math.exp(-x))

# Update Pong game
def update(pong_game, left_gene, right_gene):
    # Memperbarui posisi paddle kiri berdasarkan kontrol AI dengan GA
    if pong_game.left_paddle['y'] + PADDLE_HEIGHT / 2 < pong_game.ball['y']:
        left_action = 'down'
    else:
        left_action = 'up'

    # Memperbarui posisi paddle kanan berdasarkan kontrol AI dengan GA
    if pong_game.right_paddle['y'] + PADDLE_HEIGHT / 2 < pong_game.ball['y']:
        right_action = 'down'
    else:
        right_action = 'up'

    ## komen salah satu bagian ini jika ingin mengontrol paddle secara manual baik kiri/kanan
    pong_game.move_paddle(pong_game.left_paddle, left_action)
    pong_game.move_paddle(pong_game.right_paddle, right_action)

    pong_game.move_ball() # untuk menggerakkan bola


## Main function
def main():
    ## Mengatur inisialisasi permainan (pygame, window, font, gambar, loop, dll)

    # Mengatur window / screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Game")
    font = pygame.font.SysFont("comicsans", 36) # Mengatur gaya font & size-nya

    clock = pygame.time.Clock() # Mengatur kecepatan permainan berdasarkan FPS
    pong_game = PongGame() # Memanggil class PongGame

    genetic_algorithm = GeneticAlgorithm(population_size=10) # Mengatur populasi pada GA

    # asset gambar untuk paddle kiri
    left_paddle_image = pygame.image.load("assets/images/left_paddle.png")
    left_paddle_image = pygame.transform.scale(left_paddle_image, (PADDLE_WIDTH, PADDLE_HEIGHT))

    # asset gambar untuk paddle kanan
    right_paddle_image = pygame.image.load("assets/images/right_paddle.png")
    right_paddle_image = pygame.transform.scale(right_paddle_image, (PADDLE_WIDTH, PADDLE_HEIGHT))

    # asset gambar untuk bola
    ball_image = pygame.image.load("assets/images/ball.png")
    ball_image = pygame.transform.scale(ball_image, (BALL_RADIUS * 2, BALL_RADIUS * 2))

    # asset gambar untuk backgorund
    table_image = pygame.image.load("assets/images/table.png")
    table_image = pygame.transform.scale(table_image, (WIDTH, HEIGHT))

    # desain garis tengah
    middle_line_image = pygame.Surface((pong_game.middle_line['width'], pong_game.middle_line['height']))
    middle_line_image.fill(COLOR)

    # Suara ketika pemenang sudah di outputkan
    winner_sound = pygame.mixer.Sound("assets/sounds/winner_sound.ogg")
    running = True

    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Mendapatkan nilai gen (aksi) dari GA untuk mengontrol AI
        current_agent = genetic_algorithm.get_next_agent()
        left_gene = current_agent['left_gene']
        current_agent = genetic_algorithm.get_next_agent()
        right_gene = current_agent['right_gene']

        # Memperbarui posisi paddle dan bola berdasarkan kontrol AI atau user
        update(pong_game, left_gene, right_gene)

        # Mendapatkan input keyboard untuk menggerakkan paddle kanan
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            pong_game.move_paddle(pong_game.right_paddle, 'up')
        elif keys[pygame.K_DOWN]:
            pong_game.move_paddle(pong_game.right_paddle, 'down')

        # Mendapatkan input keyboard untuk menggerakkan paddle kiri
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            pong_game.move_paddle(pong_game.left_paddle, 'up')
        elif keys[pygame.K_s]:
            pong_game.move_paddle(pong_game.left_paddle, 'down')

        # Menampilkan background, kedua paddle, dan bola di screen
        screen.blit(table_image, (0, 0))
        screen.blit(left_paddle_image, (pong_game.left_paddle['x'], pong_game.left_paddle['y']))
        screen.blit(right_paddle_image, (pong_game.right_paddle['x'], pong_game.right_paddle['y']))
        screen.blit(ball_image, (pong_game.ball['x'] - BALL_RADIUS, pong_game.ball['y'] - BALL_RADIUS))

        # Menampilkan desain garis tengah
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, COLOR, (pong_game.middle_line['x'], y, pong_game.middle_line['width'], 10))

        # Menampilkan skor player kiri & kanan pada layar
        left_score_text = font.render(f"{pong_game.left_paddle['score']}", True, COLOR)
        right_score_text = font.render(f"{pong_game.right_paddle['score']}", True, COLOR)
        screen.blit(left_score_text, (200, 20)) # posisi skor player kiri
        screen.blit(right_score_text, (WIDTH - 200, 20)) # posisi skor player kanan

        # Menampilkan teks output bagi player pemenang (player tersebut telah mencapai 5 skor)
        if pong_game.winner:
            winner_text = font.render(f"{pong_game.winner} Win, Game End", True, COLOR)
            screen.blit(winner_text, (WIDTH // 2 - 250, HEIGHT // 2))

            # Game berhenti (game over) setelah output pemenang dikeluarkan selama 3 detik
            if pygame.time.get_ticks() - pong_game.winner_time > 3000:
                running = False

        pygame.display.flip()

        # Mengatur kecepatan permainan sesuai dengan FPS
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
