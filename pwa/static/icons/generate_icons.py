#!/usr/bin/env python3
"""
Generuje ikony PWA w różnych rozmiarach
"""
from PIL import Image, ImageDraw
import os

def create_gradient_icon(size, filename, maskable=False):
    """Tworzy ikonę z gradientem i symbolem rakiety"""
    # Margin dla maskable icons (20% z każdej strony)
    margin = int(size * 0.2) if maskable else 0
    icon_size = size - (2 * margin)
    
    # Tworzymy obraz
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gradient tło
    for y in range(size):
        # Interpolacja kolorów gradientu
        ratio = y / size
        r = int(102 + (118 - 102) * ratio)  # 667eea -> 764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Zaokrąglone rogi
    corner_radius = size // 8
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], corner_radius, fill=255)
    
    # Aplikujemy maskę
    img.putalpha(mask)
    
    # Dodajemy ikonę rakiety w centrum
    center_x, center_y = size // 2, size // 2
    rocket_size = icon_size // 3
    
    # Rakieta (uproszczona wersja)
    rocket_points = [
        (center_x, center_y - rocket_size),  # góra
        (center_x - rocket_size//3, center_y + rocket_size//2),  # lewy bok
        (center_x, center_y + rocket_size//3),  # środek dół
        (center_x + rocket_size//3, center_y + rocket_size//2),  # prawy bok
    ]
    
    draw.polygon(rocket_points, fill=(255, 255, 255, 230))
    
    # Dodajemy okienko rakiety
    window_radius = rocket_size // 6
    draw.ellipse([
        center_x - window_radius, center_y - rocket_size//2 - window_radius,
        center_x + window_radius, center_y - rocket_size//2 + window_radius
    ], fill=(255, 255, 255, 255))
    
    img.save(filename)
    print(f"Utworzono: {filename}")

# Tworzymy folder jeśli nie istnieje
os.makedirs('.', exist_ok=True)

# Standardowe ikony
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    create_gradient_icon(size, f'icon-{size}x{size}.png')

# Maskable ikony
create_gradient_icon(192, 'maskable-icon-192x192.png', maskable=True)
create_gradient_icon(512, 'maskable-icon-512x512.png', maskable=True)

print("Wszystkie ikony zostały utworzone!")