#!/usr/bin/env python3
"""
Generate PWA icons for CV Optimizer Pro
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_icon(size, filename, maskable=False):
    """Create an icon with gradient and rocket symbol"""
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(size):
        # Gradient from blue to purple
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size) 
        b = int(234 + (162 - 234) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Add padding for maskable icons
    padding = int(size * 0.1) if maskable else 0
    icon_size = size - (padding * 2)
    
    # Draw rocket icon
    center_x = size // 2
    center_y = size // 2
    rocket_size = icon_size // 3
    
    # Rocket body (white)
    rocket_points = [
        (center_x, center_y - rocket_size),
        (center_x - rocket_size//3, center_y + rocket_size//3),
        (center_x + rocket_size//3, center_y + rocket_size//3)
    ]
    draw.polygon(rocket_points, fill=(255, 255, 255, 255))
    
    # Rocket flames (orange/red)
    flame_points = [
        (center_x - rocket_size//4, center_y + rocket_size//3),
        (center_x, center_y + rocket_size),
        (center_x + rocket_size//4, center_y + rocket_size//3)
    ]
    draw.polygon(flame_points, fill=(255, 107, 107, 255))
    
    # Save icon
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Create all required PWA icon sizes
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    # Regular icon
    create_gradient_icon(size, f'icon-{size}x{size}.png', maskable=False)
    
    # Maskable icon for larger sizes
    if size >= 192:
        create_gradient_icon(size, f'icon-{size}x{size}-maskable.png', maskable=True)

print("All PWA icons generated successfully!")