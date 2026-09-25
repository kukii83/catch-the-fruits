import pygame
import random
import sys
import os

# ------------------ SETUP DASAR ------------------
pygame.init()
pygame.mixer.init()

FOLDER_ASSET = os.path.join(os.path.dirname(__file__), "assets")
LEBAR, TINGGI = 800, 500
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Catch the Fruits!")
icon = pygame.image.load(os.path.join(FOLDER_ASSET, "icon.png"))
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
FPS = 60

# Warna
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (200, 30, 30)
BIRU = (30, 100, 220)
HIJAU = (30, 180, 90)
KUNING = (230, 200, 30)
UNGU = (150, 60, 200)
ABU = (90, 90, 90)

font = pygame.font.Font("PixelifySans-VariableFont_wght.ttf", 26)
font_kecil = pygame.font.Font("PixelifySans-VariableFont_wght.ttf", 18)
font_besar = pygame.font.Font("PixelifySans-VariableFont_wght.ttf", 48)


# ------------------ KERANJANG (PLAYER) ------------------
keranjang_lebar_dasar = 100
keranjang_tinggi = 20
keranjang_x = LEBAR // 2 - keranjang_lebar_dasar // 2
keranjang_y = TINGGI - 40
keranjang_kecepatan_dasar = 8

# Dash skill
DASH_KECEPATAN = 20      
DASH_DURASI = 200 
DASH_COOLDOWN = 10000

dash_aktif_sampai = 0
dash_bisa_dipakai_lagi = 0 
dash_arah = 0 
# ------------------ OBJEK JATUH ------------------
objek_lebar = 30
objek_tinggi = 30
objek_kecepatan_dasar = 4
daftar_objek = []  # list of dict: {"rect": Rect, "jenis": "normal"/"powerup", "powerup_id": key atau None}

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1000)

PELUANG_POWERUP = 0.20  # 20%

# ------------------ FRUITS ------------------
FRUITS = {

    "apple":  {"gambar": None, "file": "apple.png",  "skor": 1},
    "orange": {"gambar": None, "file": "orange.png", "skor": 1},
    "lemon":  {"gambar": None, "file": "lemon.png",  "skor": 1},
    "coconut": {"gambar": None, "file": "coconut.png", "skor": 2},
    "melon": {"gambar": None, "file": "melon.png", "skor": 2},
    "banana": {"gambar": None, "file": "banana.png", "skor": 2},
    "peach": {"gambar": None, "file": "peach.png", "skor": 3},
    "grapes": {"gambar": None, "file": "grapes.png", "skor": 3},
    "watermelon": {"gambar": None, "file": "watermelon.png", "skor": 3},

}

# ------------------ DEFINISI POWER-UP ------------------
POWERUPS = {
    "Swiftness":       {"file": "swiftness.png","durasi": 6, "kategori": "good"},
    "Upsize":        {"file": "upsize.png","durasi": 6, "kategori": "good"},
    "extraLife":     {"file": "lifeup.png","durasi": None, "kategori": "good"},
    "Double Points":       {"file": "2xpoints.png","durasi": 6, "kategori": "good"},
    "Magnet":         {"file": "magnet.png","durasi": 5, "kategori": "good"},
    "Time Slow":      {"file": "timeslow.png","durasi": 5, "kategori": "good"},

    "Slowness":     {"file": "slowness.png","durasi": 5, "kategori": "bad"},
    "Blindness":          {"file": "blindness.png","durasi": 5, "kategori": "bad"},
    "Inverted":         {"file": "inverted.png", "durasi": 6, "kategori": "bad"},
}

# effect_end menyimpan waktu (dalam ms, dari pygame.time.get_ticks()) kapan efek berakhir.
# Kalau key tidak ada di dict ini, berarti efek itu sedang tidak aktif.
effect_end = {}

def efek_aktif(nama):
    return nama in effect_end and pygame.time.get_ticks() < effect_end[nama]

def aktifkan_efek(nama, durasi_detik):
    """Set/reset timer efek. Jika efek sudah aktif, durasinya diperpanjang (bukan ditumpuk)."""
    effect_end[nama] = pygame.time.get_ticks() + durasi_detik * 1000

def buat_objek_baru():
    x = random.randint(0, LEBAR - objek_lebar)
    y = -objek_tinggi
    rect = pygame.Rect(x, y, objek_lebar, objek_tinggi)

    if random.random() < PELUANG_POWERUP:
        powerup_id = random.choice(list(POWERUPS.keys()))
        return {"rect": rect, "jenis": "powerup", "powerup_id": powerup_id}
    else:
        buah_id = random.choice(list(FRUITS.keys()))
        return {"rect": rect, "jenis": "normal", "buah_id": buah_id}

    # ================== LOAD SEMUA ASSET ==================
FOLDER_ASSET = os.path.join(os.path.dirname(__file__), "assets")

pygame.mixer.music.load(os.path.join(FOLDER_ASSET, "audio", "bgm.mp3"))
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)


sfx_ambil_buah = pygame.mixer.Sound(os.path.join(FOLDER_ASSET, "audio", "fruit_collect.mp3"))
sfx_powerup_good = pygame.mixer.Sound(os.path.join(FOLDER_ASSET, "audio", "powerup_good.mp3"))
sfx_powerup_bad = pygame.mixer.Sound(os.path.join(FOLDER_ASSET, "audio", "powerup_bad.mp3"))
sfx_game_over = pygame.mixer.Sound(os.path.join(FOLDER_ASSET, "audio", "gameover.mp3"))
sfx_buah_jatuh = pygame.mixer.Sound(os.path.join(FOLDER_ASSET, "audio", "miss.mp3"))

sfx_buah_jatuh.set_volume(0.5)
sfx_ambil_buah.set_volume(0.5)
sfx_powerup_good.set_volume(0.6)
sfx_powerup_bad.set_volume(0.6)
sfx_game_over.set_volume(0.6)

def load_gambar(*path_parts, ukuran=None):
    """Helper untuk load + scale gambar sekali panggil, biar tidak menulis ulang kode yang sama."""
    path_lengkap = os.path.join(FOLDER_ASSET, *path_parts)
    img = pygame.image.load(path_lengkap).convert_alpha()
    if ukuran:
        img = pygame.transform.scale(img, ukuran)
    return img

# --- Keranjang ---
KERANJANG_VISUAL_LEBAR = 100
KERANJANG_VISUAL_TINGGI = 70

gambar_keranjang = load_gambar("basket.png", ukuran=(KERANJANG_VISUAL_LEBAR, KERANJANG_VISUAL_TINGGI))

# --- Background ---
gambar_background = load_gambar("bg.png", ukuran=(LEBAR, TINGGI))

# --- Buah ---
for key, data in FRUITS.items():
    data["gambar"] = load_gambar("fruits", data["file"], ukuran=(objek_lebar, objek_tinggi))

# --- Power-up ---
for key, data in POWERUPS.items():
    data["gambar"] = load_gambar("powerups", data["file"], ukuran=(objek_lebar, objek_tinggi))

# ========================================================

# ------------------ VARIABEL GAME ------------------
skor = 0
nyawa = 3
game_over = False
pesan_popup = ""       # pesan singkat saat mengambil power-up, misal "Speed Up!"
pesan_popup_waktu = 0   # kapan pesan ini harus hilang (ms)

def gambar_teks(teks, font_obj, warna, x, y):
    permukaan = font_obj.render(teks, True, warna)
    layar.blit(permukaan, (x, y))


def tampilkan_pesan(teks):
    global pesan_popup, pesan_popup_waktu
    pesan_popup = teks
    pesan_popup_waktu = pygame.time.get_ticks() + 1500  # tampil 1.5 detik


def reset_game():
    global keranjang_x, daftar_objek, skor, nyawa, game_over, effect_end
    global dash_aktif_sampai, dash_bisa_dipakai_lagi, dash_arah
    keranjang_x = LEBAR // 2 - keranjang_lebar_dasar // 2
    daftar_objek = []
    skor = 0
    nyawa = 3
    game_over = False
    effect_end = {}
    dash_aktif_sampai = 0
    dash_bisa_dipakai_lagi = 0
    dash_arah = 0
    pygame.mixer.music.play(-1)

def terapkan_efek_powerup(powerup_id):
    """Dipanggil sekali saat power-up berhasil ditangkap."""
    global nyawa, skor
    info = POWERUPS[powerup_id]

    if info["kategori"] == "good":
        sfx_powerup_good.play()
    else:
        sfx_powerup_bad.play() 

    if powerup_id == "extraLife":
        nyawa += 1
        tampilkan_pesan("+1 Life!")
    else:
        aktifkan_efek(powerup_id, info["durasi"])
        label = {
            "Swiftness": "Speed Up!",
            "Upsize": "Size Up!",
            "Double Points": "Score x2!",
            "Magnet": "Magnet Active!",
            "Time Slow": "Time Slow...",
            "Slowness": "Speed Down...",
            "Blindness": "Blindness...!",
            "Inverted": "Inverted Controls...",
        }[powerup_id]
        tampilkan_pesan(label)


# ------------------ GAME LOOP ------------------
berjalan = True
while berjalan:
    clock.tick(FPS)
    sekarang = pygame.time.get_ticks()

    # ---------- 1. EVENT ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            berjalan = False

        if event.type == SPAWN_EVENT and not game_over:
            daftar_objek.append(buat_objek_baru())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

            if event.key == pygame.K_SPACE and not game_over:
                arah_saat_ini = 0
                tombol = pygame.key.get_pressed()
                if tombol[pygame.K_LEFT]:
                    arah_saat_ini = -1
                if tombol[pygame.K_RIGHT]:
                    arah_saat_ini = 1

                bisa_dash = sekarang >= dash_bisa_dipakai_lagi
                if bisa_dash and arah_saat_ini != 0:
                    dash_aktif_sampai = sekarang + DASH_DURASI
                    dash_bisa_dipakai_lagi = sekarang + DASH_COOLDOWN
                    dash_arah = arah_saat_ini

    if not game_over:
        # ---------- 2. HITUNG STATUS EFEK SAAT INI ----------
        keranjang_lebar = keranjang_lebar_dasar * (2 if efek_aktif("Upsize") else 1)

        kecepatan_gerak = keranjang_kecepatan_dasar
        if efek_aktif("Swiftness"):
            kecepatan_gerak *= 1.8
        if efek_aktif("Slowness"):
            kecepatan_gerak *= 0.5

        kecepatan_jatuh = objek_kecepatan_dasar
        if efek_aktif("Time Slow"):
            kecepatan_jatuh *= 0.5

        pengali_skor = 2 if efek_aktif("Double Points") else 1

        # ---------- 3. INPUT ----------
        tombol = pygame.key.get_pressed()
        arah = 0
        if tombol[pygame.K_LEFT]:
            arah = -1
        if tombol[pygame.K_RIGHT]:
            arah = 1

        if efek_aktif("Inverted"):
            arah = -arah

        # Dash movement
        sedang_dash = sekarang < dash_aktif_sampai

        if sedang_dash:
            keranjang_x += dash_arah * DASH_KECEPATAN
        else:
            keranjang_x += arah * kecepatan_gerak

        keranjang_x = max(0, min(LEBAR - keranjang_lebar, keranjang_x))

        keranjang_rect = pygame.Rect(keranjang_x, keranjang_y, keranjang_lebar, keranjang_tinggi)
        keranjang_tengah = keranjang_rect.center

        # ---------- 4. UPDATE OBJEK ----------
        for objek in daftar_objek[:]:
            rect = objek["rect"]
            rect.y += kecepatan_jatuh

            # Efek magnet: tarik objek "normal" (buah) mendekat ke arah x keranjang
            if efek_aktif("Magnet") and objek["jenis"] == "normal":
                if rect.centerx < keranjang_tengah[0]:
                    rect.x += min(4, keranjang_tengah[0] - rect.centerx)
                elif rect.centerx > keranjang_tengah[0]:
                    rect.x -= min(4, rect.centerx - keranjang_tengah[0])

            # Tabrakan dengan keranjang
            if keranjang_rect.colliderect(rect):
                daftar_objek.remove(objek)
                if objek["jenis"] == "normal":
                    skor += FRUITS[objek["buah_id"]]["skor"] * pengali_skor
                    sfx_ambil_buah.play()
                else:
                    terapkan_efek_powerup(objek["powerup_id"])
                continue

            # Lewat bawah layar
            if rect.y > TINGGI:
                daftar_objek.remove(objek)
                if objek["jenis"] == "normal":
                    nyawa -= 1
                    sfx_buah_jatuh.play()
                    if nyawa <= 0:
                        game_over = True
                        pygame.mixer.music.fadeout(1000)
                        sfx_game_over.play()

    # ---------- 5. GAMBAR ----------
    layar.blit(gambar_background, (0, 0))

    if not game_over:  
        keranjang_rect = pygame.Rect(keranjang_x, keranjang_y, keranjang_lebar, keranjang_tinggi)

        gambar_keranjang_scaled = pygame.transform.scale(
            gambar_keranjang, (int(keranjang_lebar), KERANJANG_VISUAL_TINGGI)
        )
        posisi_gambar_y = keranjang_rect.bottom - KERANJANG_VISUAL_TINGGI
        layar.blit(gambar_keranjang_scaled, (keranjang_rect.x, posisi_gambar_y))

        for objek in daftar_objek:
            rect = objek["rect"]
            if objek["jenis"] == "normal":
                layar.blit(FRUITS[objek["buah_id"]]["gambar"], rect)
            else:
                info = POWERUPS[objek["powerup_id"]]
                layar.blit(info["gambar"], rect)

        gambar_teks(f"Score: {skor}", font, PUTIH, 10, 10)
        gambar_teks(f"Lives: {nyawa}", font, PUTIH, LEBAR - 130, 10)

        # Tampilkan daftar efek aktif + sisa waktunya
        y_offset = 45
        for nama, akhir in effect_end.items():
            sisa = (akhir - sekarang) / 1000
            if sisa > 0:
                gambar_teks(f"{nama} ({sisa:.1f}s)", font_kecil, KUNING, 10, y_offset)
                y_offset += 20

        sisa_cooldown = max(0, (dash_bisa_dipakai_lagi - sekarang) / 1000)
        
        if sisa_cooldown > 0:
            gambar_teks(f"Dash: {sisa_cooldown:.1f}s", font_kecil, ABU, 10, y_offset)
        else:
            gambar_teks("Dash: READY", font_kecil, HIJAU, 10, y_offset)
            y_offset += 20
        
        # Pesan popup saat power-up diambil
        if sekarang < pesan_popup_waktu:
            gambar_teks(pesan_popup, font, HIJAU, LEBAR // 2 - 80, 60)

        # Efek visual "blind": tutupi bagian atas layar dengan kotak gelap semi transparan
        if efek_aktif("Blindness"):
            overlay = pygame.Surface((LEBAR, 250), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            layar.blit(overlay, (0, 0))
    else:
        overlay = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        layar.blit(overlay, (0, 0))
        gambar_teks("GAME OVER", font_besar, MERAH, LEBAR // 2 - 130, TINGGI // 2 - 60)
        gambar_teks(f"Final Score: {skor}", font, PUTIH, LEBAR // 2 - 80, TINGGI // 2)
        gambar_teks("Press R to play again", font, HIJAU, LEBAR // 2 - 140, TINGGI // 2 + 40)

    pygame.display.flip()

pygame.quit()
sys.exit()