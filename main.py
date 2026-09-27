import pygame
import random
import sys
import math

# Pygame Başlatma
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
except Exception:
    pass

# Ekran Ayarları
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w if info.current_w > 0 else 800
SCREEN_HEIGHT = info.current_h if info.current_h > 0 else 450
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SL'NİN GEOMETRY DASHI")

# Oyunun Dahili Çözünürlüğü
GAME_WIDTH = 480
GAME_HEIGHT = 270
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

# Renk Tanımlamaları
FLOOR_COLOR = (30, 35, 50)
LINE_COLOR = (0, 230, 200)
OBSTACLE_COLOR = (30, 30, 35)
OBSTACLE_BORDER = (70, 70, 75)
TEXT_COLOR = (255, 255, 255)
NEW_RECORD_COLOR = (50, 255, 120)
BUTTON_BG = (40, 50, 80)
BUTTON_BORDER = (0, 230, 200)
ORB_COLOR = (255, 220, 0)

# Dil Sözlüğü (TR / EN)
LANGUAGES = {
    "TR": {
        "welcome": "Oyuna Hoşgeldin!",
        "title": "SL'NİN GEOMETRY DASHI",
        "subtitle": "(coded by gemini)",
        "play": "Oyna!",
        "exit": "Oyundan Çık",
        "settings": "Ayarlar",
        "select_diff": "ZORLUK SEÇ",
        "easy": "Kolay Mod!",
        "hard": "Zor Mod!",
        "lang_btn": "Dil / Language: TR",
        "skins_btn": "Görünümler",
        "credits_btn": "Yapımcılar",
        "back": "Geri",
        "score": "Skor",
        "high_score": "Rekor",
        "game_over": "Öldün! Yeniden başlamak için ekrana tıkla",
        "paused": "OYUN DURDURULDU",
        "resume": "Devam Et",
        "quit": "Oyunu Kapat"
    },
    "EN": {
        "welcome": "Welcome to the Game!",
        "title": "SL'S GEOMETRY DASH",
        "subtitle": "(coded by gemini)",
        "play": "Play!",
        "exit": "Exit Game",
        "settings": "Settings",
        "select_diff": "SELECT DIFFICULTY",
        "easy": "Easy Mode!",
        "hard": "Hard Mode!",
        "lang_btn": "Language / Dil: EN",
        "skins_btn": "Skins",
        "credits_btn": "Credits",
        "back": "Back",
        "score": "Score",
        "high_score": "High Score",
        "game_over": "You Died! Tap screen to restart",
        "paused": "GAME PAUSED",
        "resume": "Resume",
        "quit": "Quit Game"
    }
}
current_lang = "TR"

# Skin Listesi
SKINS = [
    {"name": "Sarı Küp", "color": (255, 200, 0), "border": (255, 255, 255)},
    {"name": "Neon Yeşil", "color": (50, 255, 100), "border": (0, 150, 50)},
    {"name": "Alev Kırmızı", "color": (255, 50, 50), "border": (255, 200, 0)},
    {"name": "Buz Mavi", "color": (0, 200, 255), "border": (255, 255, 255)}
]
selected_skin_index = 0

# Oyun Sabitleri
GRAVITY = 1.1
JUMP_STRENGTH = -14
ORB_JUMP_STRENGTH = -16.5
FLOOR_Y = GAME_HEIGHT - 60
game_speed = 6

# Saat ve Fontlar
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16, bold=True)
small_font = pygame.font.SysFont("Arial", 10, bold=True)
menu_font = pygame.font.SysFont("Arial", 13, bold=True)
title_font = pygame.font.SysFont("Arial", 18, bold=True)

# Bip Ses Üreticisi
def generate_beep_sound(frequency=880, duration=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    max_amp = 3000
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = int(max_amp * math.sin(2.0 * math.pi * frequency * t))
        buf.extend(val.to_bytes(2, byteorder='little', signed=True))
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None

beep_sound = generate_beep_sound(frequency=880, duration=0.1)

class Player:
    def __init__(self):
        self.size = 35
        self.x = 70
        self.y = FLOOR_Y - self.size
        self.vel_y = 0
        self.is_jumping = False
        self.rotation = 0
        self.on_ground = True

    def jump(self):
        if self.on_ground or not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True
            self.on_ground = False

    def orb_jump(self):
        self.vel_y = ORB_JUMP_STRENGTH
        self.is_jumping = True
        self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y >= FLOOR_Y - self.size:
            self.y = FLOOR_Y - self.size
            self.vel_y = 0
            self.is_jumping = False
            self.on_ground = True
            self.rotation = (self.rotation // 90) * 90

        if self.is_jumping:
            self.rotation -= 8

    def draw(self, surface):
        skin = SKINS[selected_skin_index]
        player_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        player_surface.fill(skin["color"])
        pygame.draw.rect(player_surface, skin["border"], player_surface.get_rect(), 3)
        
        rotated_surface = pygame.transform.rotate(player_surface, self.rotation)
        new_rect = rotated_surface.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        surface.blit(rotated_surface, new_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)


class SpikeGroup:
    def __init__(self, x, count=1):
        self.width = 35
        self.height = 35
        self.x = x
        self.y = FLOOR_Y
        self.count = count

    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        for i in range(self.count):
            sx = self.x + i * self.width
            point1 = (sx, self.y)
            point2 = (sx + self.width // 2, self.y - self.height)
            point3 = (sx + self.width, self.y)
            
            pygame.draw.polygon(surface, OBSTACLE_COLOR, [point1, point2, point3])
            pygame.draw.polygon(surface, OBSTACLE_BORDER, [point1, point2, point3], 2)

    def get_rect(self):
        total_width = self.width * self.count
        return pygame.Rect(self.x + 8, self.y - self.height + 8, total_width - 16, self.height - 8)


class Block:
    def __init__(self, x, y=FLOOR_Y - 35, count=1):
        self.x = x
        self.y = y
        self.size = 35
        self.count = count

    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        for i in range(self.count):
            bx = self.x + i * self.size
            b_rect = pygame.Rect(bx, self.y, self.size, self.size)
            pygame.draw.rect(surface, (10, 15, 45), b_rect)
            pygame.draw.rect(surface, (120, 200, 255), b_rect, 3)
            inner_rect = b_rect.inflate(-8, -8)
            pygame.draw.rect(surface, (30, 60, 120), inner_rect, 1)

    def get_rects(self):
        return [pygame.Rect(self.x + i * self.size, self.y, self.size, self.size) for i in range(self.count)]


class JumpOrb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.pulse = 0

    def update(self, speed):
        self.x -= speed
        self.pulse += 0.15

    def draw(self, surface):
        pulse_r = self.radius + int(math.sin(self.pulse) * 3)
        pygame.draw.circle(surface, ORB_COLOR, (int(self.x), int(self.y)), pulse_r, 2)
        pygame.draw.circle(surface, (255, 255, 200), (int(self.x), int(self.y)), self.radius - 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 4)

    def get_trigger_rect(self):
        return pygame.Rect(self.x - self.radius - 12, self.y - self.radius - 12, (self.radius + 12) * 2, (self.radius + 12) * 2)


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)
        self.size = random.randint(3, 6)
        skin = SKINS[selected_skin_index]
        self.color = random.choice([skin["color"], (255, 100, 0), (255, 255, 255)])
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 10
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        if self.alpha > 0:
            p_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            p_surface.fill((*self.color, self.alpha))
            surface.blit(p_surface, (self.x, self.y))


def draw_button(surface, rect, text):
    pygame.draw.rect(surface, BUTTON_BG, rect, border_radius=8)
    pygame.draw.rect(surface, BUTTON_BORDER, rect, 2, border_radius=8)
    lbl = menu_font.render(text, True, TEXT_COLOR)
    lbl_rect = lbl.get_rect(center=rect.center)
    surface.blit(lbl, lbl_rect)


def reset_game():
    player = Player()
    obstacles = [SpikeGroup(GAME_WIDTH + 100, count=1)]
    blocks = []
    orbs = []
    score = 0
    particles = []
    return player, obstacles, blocks, orbs, score, particles


def handle_jump_action(player, orbs):
    p_rect = player.get_rect()
    orb_triggered = False
    
    for orb in orbs:
        if p_rect.colliderect(orb.get_trigger_rect()):
            player.orb_jump()
            orb_triggered = True
            break
            
    if not orb_triggered:
        player.jump()


def main():
    global selected_skin_index, current_lang, game_speed
    
    player, obstacles, blocks, orbs, score, particles = reset_game()
    spawn_timer = 0
    game_over = False
    is_paused = False
    
    # Durumlar: 'WELCOME', 'MAIN_MENU', 'DIFF_MENU', 'SETTINGS_MENU', 'SKIN_MENU', 'CREDITS_MENU', 'PLAYING'
    game_state = 'WELCOME'
    welcome_timer = 0
    
    # Arka Plan Otomatik Oynatıcı
    bg_player = Player()
    bg_obstacles = []
    bg_orbs = []
    bg_blocks = []
    bg_spawn_timer = 0
    
    bg_timer = 0
    high_score = 0
    new_record_achieved = False
    last_beep_milestone = 0

    # Ana Menü Butonları (Soldan Sağa 3'lü)
    btn_w, btn_h = 130, 38
    btn_y = 175
    exit_btn_rect    = pygame.Rect(25, btn_y, btn_w, btn_h)
    play_btn_rect    = pygame.Rect(175, btn_y, btn_w, btn_h)
    settings_btn_rect= pygame.Rect(325, btn_y, btn_w, btn_h)

    # Zorluk Menüsü
    diff_easy_rect = pygame.Rect(160, 100, 160, 36)
    diff_hard_rect = pygame.Rect(160, 150, 160, 36)
    diff_back_rect = pygame.Rect(190, 215, 100, 30)

    # Ayarlar Menüsü
    set_lang_rect    = pygame.Rect(150, 80, 180, 34)
    set_skins_rect   = pygame.Rect(150, 125, 180, 34)
    set_credits_rect = pygame.Rect(150, 170, 180, 34)
    set_back_rect    = pygame.Rect(190, 220, 100, 30)

    # Duraklatma Butonları
    pause_btn_rect  = pygame.Rect(GAME_WIDTH - 40, 10, 30, 30)
    resume_btn_rect = pygame.Rect((GAME_WIDTH - 160)//2, 70, 160, 35)
    skin_btn_rect   = pygame.Rect((GAME_WIDTH - 160)//2, 115, 160, 35)
    quit_btn_rect   = pygame.Rect((GAME_WIDTH - 160)//2, 160, 160, 35)

    while True:
        clock.tick(60)
        bg_timer += 0.03
        L = LANGUAGES[current_lang]

        click_pos = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                click_pos = (int(mx * (GAME_WIDTH / SCREEN_WIDTH)), int(my * (GAME_HEIGHT / SCREEN_HEIGHT)))

            if event.type == pygame.FINGERDOWN:
                click_pos = (int(event.x * GAME_WIDTH), int(event.y * GAME_HEIGHT))

            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_state == 'PLAYING' and not is_paused:
                    if game_over:
                        player, obstacles, blocks, orbs, score, particles = reset_game()
                        game_over = False
                        new_record_achieved = False
                        last_beep_milestone = 0
                    else:
                        handle_jump_action(player, orbs)

        # --- MENÜ ARKAPLAN OTOMATİK OYNATIŞI ---
        if game_state != 'PLAYING':
            bg_player.update()
            bg_spawn_timer += 1
            if bg_spawn_timer > 80:
                bg_obstacles.append(SpikeGroup(GAME_WIDTH + 20, count=random.choice([1, 2])))
                bg_spawn_timer = 0

            for obs in list(bg_obstacles):
                obs.update(5)
                if obs.x < -100: bg_obstacles.remove(obs)
                # Otonom Zıplama Mantığı
                if 0 < obs.x - bg_player.x < 70 and bg_player.on_ground:
                    bg_player.jump()

        # --- WELCOME INTRO EKRANI ---
        if game_state == 'WELCOME':
            welcome_timer += 1
            if welcome_timer > 90 or click_pos: # ~1.5 Saniye Sonra Geçer
                game_state = 'MAIN_MENU'

        # --- DOKUNMA / TIKLAMA KONTROLLERİ ---
        if click_pos:
            cx, cy = click_pos

            if game_state == 'MAIN_MENU':
                if exit_btn_rect.collidepoint(cx, cy):
                    pygame.quit()
                    sys.exit()
                elif play_btn_rect.collidepoint(cx, cy):
                    game_state = 'DIFF_MENU'
                elif settings_btn_rect.collidepoint(cx, cy):
                    game_state = 'SETTINGS_MENU'

            elif game_state == 'DIFF_MENU':
                if diff_easy_rect.collidepoint(cx, cy):
                    game_speed = 6
                    player, obstacles, blocks, orbs, score, particles = reset_game()
                    game_over = False
                    game_state = 'PLAYING'
                elif diff_hard_rect.collidepoint(cx, cy):
                    game_speed = 8.2  # Daha hızlı oyun
                    player, obstacles, blocks, orbs, score, particles = reset_game()
                    game_over = False
                    game_state = 'PLAYING'
                elif diff_back_rect.collidepoint(cx, cy):
                    game_state = 'MAIN_MENU'

            elif game_state == 'SETTINGS_MENU':
                if set_lang_rect.collidepoint(cx, cy):
                    current_lang = "EN" if current_lang == "TR" else "TR"
                elif set_skins_rect.collidepoint(cx, cy):
                    game_state = 'SKIN_MENU'
                elif set_credits_rect.collidepoint(cx, cy):
                    game_state = 'CREDITS_MENU'
                elif set_back_rect.collidepoint(cx, cy):
                    game_state = 'MAIN_MENU'

            elif game_state == 'SKIN_MENU':
                for i in range(len(SKINS)):
                    s_rect = pygame.Rect((GAME_WIDTH - 200)//2, 50 + i * 40, 200, 32)
                    if s_rect.collidepoint(cx, cy):
                        selected_skin_index = i
                back_rect = pygame.Rect((GAME_WIDTH - 100)//2, 225, 100, 30)
                if back_rect.collidepoint(cx, cy):
                    game_state = 'SETTINGS_MENU' if not is_paused else 'PLAYING'

            elif game_state == 'CREDITS_MENU':
                c_back = pygame.Rect((GAME_WIDTH - 100)//2, 230, 100, 30)
                if c_back.collidepoint(cx, cy):
                    game_state = 'SETTINGS_MENU'

            elif game_state == 'PLAYING':
                if is_paused:
                    if resume_btn_rect.collidepoint(cx, cy):
                        is_paused = False
                    elif skin_btn_rect.collidepoint(cx, cy):
                        game_state = 'SKIN_MENU'
                    elif quit_btn_rect.collidepoint(cx, cy):
                        game_state = 'MAIN_MENU'
                        is_paused = False
                else:
                    if pause_btn_rect.collidepoint(cx, cy) and not game_over:
                        is_paused = True
                    else:
                        if game_over:
                            player, obstacles, blocks, orbs, score, particles = reset_game()
                            game_over = False
                            new_record_achieved = False
                            last_beep_milestone = 0
                        else:
                            handle_jump_action(player, orbs)

        # --- OYUN İÇİ MANTIĞI ---
        if game_state == 'PLAYING' and not game_over and not is_paused:
            player.update()
            score += 1
            current_points = score // 10

            if current_points > 0 and current_points % 100 == 0 and current_points != last_beep_milestone:
                if beep_sound: beep_sound.play()
                last_beep_milestone = current_points

            if current_points > high_score:
                if high_score > 0: new_record_achieved = True
                high_score = current_points

            spawn_timer += 1
            max_spawn = 50 if game_speed > 7 else 65
            if spawn_timer > random.randint(max_spawn, max_spawn + 35):
                rand_val = random.random()
                start_x = GAME_WIDTH + 20

                if rand_val < 0.3:
                    orbs.append(JumpOrb(start_x, FLOOR_Y - 65))
                    obstacles.append(SpikeGroup(start_x + 35, count=4))
                elif rand_val < 0.6:
                    b_count = random.choice([1, 2])
                    blocks.append(Block(start_x, count=b_count))
                    if random.random() < 0.5:
                        obstacles.append(SpikeGroup(start_x + b_count * 35, count=1))
                else:
                    c = random.choice([1, 2, 3])
                    obstacles.append(SpikeGroup(start_x, count=c))

                spawn_timer = 0

            for obstacle in list(obstacles):
                obstacle.update(game_speed)
                if obstacle.x < -200: obstacles.remove(obstacle)
                if player.get_rect().colliderect(obstacle.get_rect()): game_over = True

            for block_obj in list(blocks):
                block_obj.update(game_speed)
                if block_obj.x < -200: blocks.remove(block_obj)

                for b_rect in block_obj.get_rects():
                    if player.get_rect().colliderect(b_rect):
                        if player.vel_y >= 0 and player.get_rect().bottom - player.vel_y <= b_rect.top + 10:
                            player.y = b_rect.top - player.size
                            player.vel_y = 0
                            player.is_jumping = False
                            player.on_ground = True
                            player.rotation = (player.rotation // 90) * 90
                        else:
                            game_over = True

            if game_over:
                px = player.x + player.size // 2
                py = player.y + player.size // 2
                particles = [Particle(px, py) for _ in range(25)]

            for orb in list(orbs):
                orb.update(game_speed)
                if orb.x < -50: orbs.remove(orb)

        if game_state == 'PLAYING' and not is_paused:
            for p in list(particles):
                p.update()
                if p.alpha <= 0: particles.remove(p)

        # --- ÇİZİM AŞAMASI ---
        blue_val = int(180 + math.sin(bg_timer) * 40)
        green_val = int(120 + math.cos(bg_timer * 0.7) * 30)
        game_surface.fill((20, green_val, blue_val))

        # Zemin
        pygame.draw.rect(game_surface, FLOOR_COLOR, (0, FLOOR_Y, GAME_WIDTH, GAME_HEIGHT - FLOOR_Y))
        pygame.draw.line(game_surface, LINE_COLOR, (0, FLOOR_Y), (GAME_WIDTH, FLOOR_Y), 2)

        # MENÜ VEYA INTRO ARKAPLAN ÇİZİMİ
        if game_state != 'PLAYING':
            bg_player.draw(game_surface)
            for obs in bg_obstacles: obs.draw(game_surface)
            dim_overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            dim_overlay.fill((0, 0, 0, 130))
            game_surface.blit(dim_overlay, (0, 0))

        # INTRO EKRANI
        if game_state == 'WELCOME':
            w_lbl = title_font.render(L["welcome"], True, TEXT_COLOR)
            game_surface.blit(w_lbl, w_lbl.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2)))

        # ANA MENÜ (Baldi's Basics Tarzı)
        elif game_state == 'MAIN_MENU':
            t1 = title_font.render(L["title"], True, NEW_RECORD_COLOR)
            t2 = small_font.render(L["subtitle"], True, TEXT_COLOR)
            game_surface.blit(t1, t1.get_rect(center=(GAME_WIDTH//2, 45)))
            game_surface.blit(t2, t2.get_rect(center=(GAME_WIDTH//2, 68)))

            draw_button(game_surface, exit_btn_rect, L["exit"])
            draw_button(game_surface, play_btn_rect, L["play"])
            draw_button(game_surface, settings_btn_rect, L["settings"])

        # ZORLUK SEÇİM MENÜSÜ
        elif game_state == 'DIFF_MENU':
            d_lbl = title_font.render(L["select_diff"], True, TEXT_COLOR)
            game_surface.blit(d_lbl, d_lbl.get_rect(center=(GAME_WIDTH//2, 50)))
            
            draw_button(game_surface, diff_easy_rect, L["easy"])
            draw_button(game_surface, diff_hard_rect, L["hard"])
            draw_button(game_surface, diff_back_rect, L["back"])

        # AYARLAR MENÜSÜ
        elif game_state == 'SETTINGS_MENU':
            s_lbl = title_font.render(L["settings"], True, TEXT_COLOR)
            game_surface.blit(s_lbl, s_lbl.get_rect(center=(GAME_WIDTH//2, 35)))

            draw_button(game_surface, set_lang_rect, L["lang_btn"])
            draw_button(game_surface, set_skins_rect, L["skins_btn"])
            draw_button(game_surface, set_credits_rect, L["credits_btn"])
            draw_button(game_surface, set_back_rect, L["back"])

        # YAPIMCILAR (CREDITS) MENÜSÜ
        elif game_state == 'CREDITS_MENU':
            credits_text = [
                "Kodları yazan: Gemini",
                "Promtları yazan: SL_865",
                "Textureler: Gemini",
                "Fikir: SL_865",
                "Yapılma sebebi: Bende bilmiyom",
                "Neyse daha fazla bakma git oyuna gir btw",
                "Ve bence güzel oldu BURAYA BAKMA OYUNA GİR"
            ]
            for i, line in enumerate(credits_text):
                col = NEW_RECORD_COLOR if i == 6 else TEXT_COLOR
                f_size = small_font if i >= 4 else menu_font
                c_lbl = f_size.render(line, True, col)
                game_surface.blit(c_lbl, c_lbl.get_rect(center=(GAME_WIDTH//2, 25 + i * 26)))

            c_back = pygame.Rect((GAME_WIDTH - 100)//2, 230, 100, 30)
            draw_button(game_surface, c_back, L["back"])

        # GÖRÜNÜMLER MENÜSÜ
        elif game_state == 'SKIN_MENU':
            s_title = font.render(L["skins_btn"], True, TEXT_COLOR)
            game_surface.blit(s_title, s_title.get_rect(center=(GAME_WIDTH // 2, 25)))

            for i, skin in enumerate(SKINS):
                s_rect = pygame.Rect((GAME_WIDTH - 200)//2, 55 + i * 40, 200, 32)
                is_selected = (i == selected_skin_index)
                bg_col = (60, 80, 130) if is_selected else BUTTON_BG
                border_col = NEW_RECORD_COLOR if is_selected else BUTTON_BORDER
                
                pygame.draw.rect(game_surface, bg_col, s_rect, border_radius=6)
                pygame.draw.rect(game_surface, border_col, s_rect, 2, border_radius=6)
                
                preview_rect = pygame.Rect(s_rect.x + 10, s_rect.y + 6, 20, 20)
                pygame.draw.rect(game_surface, skin["color"], preview_rect)
                pygame.draw.rect(game_surface, skin["border"], preview_rect, 2)
                
                txt = menu_font.render(skin["name"], True, TEXT_COLOR)
                game_surface.blit(txt, (s_rect.x + 40, s_rect.y + 6))

            back_rect = pygame.Rect((GAME_WIDTH - 100)//2, 225, 100, 30)
            draw_button(game_surface, back_rect, L["back"])

        # OYUN EKRANI (PLAYING)
        elif game_state == 'PLAYING':
            for orb in orbs: orb.draw(game_surface)
            for block_obj in blocks: block_obj.draw(game_surface)
            if not game_over: player.draw(game_surface)
            for obstacle in obstacles: obstacle.draw(game_surface)
            for p in particles: p.draw(game_surface)

            curr_score_val = score // 10
            score_text = font.render(f"{L['score']}: {curr_score_val}", True, TEXT_COLOR)
            high_score_text = font.render(f"{L['high_score']}: {high_score}", True, TEXT_COLOR)
            game_surface.blit(score_text, (15, 10))
            game_surface.blit(high_score_text, (15, 30))

            if new_record_achieved:
                rec_text = small_font.render("YENİ REKOR!", True, NEW_RECORD_COLOR)
                game_surface.blit(rec_text, (15, 52))

            if not game_over and not is_paused:
                pygame.draw.rect(game_surface, BUTTON_BG, pause_btn_rect, border_radius=6)
                pygame.draw.rect(game_surface, BUTTON_BORDER, pause_btn_rect, 2, border_radius=6)
                pause_lbl = font.render("||", True, TEXT_COLOR)
                p_rect = pause_lbl.get_rect(center=pause_btn_rect.center)
                game_surface.blit(pause_lbl, p_rect)

            if game_over and not is_paused:
                over_text = font.render(L["game_over"], True, (255, 255, 255))
                text_rect = over_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
                game_surface.blit(over_text, text_rect)

            if is_paused:
                overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                game_surface.blit(overlay, (0, 0))

                p_title = font.render(L["paused"], True, TEXT_COLOR)
                game_surface.blit(p_title, p_title.get_rect(center=(GAME_WIDTH // 2, 35)))

                draw_button(game_surface, resume_btn_rect, L["resume"])
                draw_button(game_surface, skin_btn_rect, L["skins_btn"])
                draw_button(game_surface, quit_btn_rect, L["quit"])

        # Ekrana Ölçeklendirip Yansıtma
        scaled_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main()
