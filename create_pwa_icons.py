from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

ICONS_DIR = Path(r"c:\Users\Junior do Titico\Desktop\TJPE-2026\icons")
ICONS_DIR.mkdir(exist_ok=True)

def draw_justice_balance(draw, center_x, center_y, scale, color_primary, color_gold):
    """
    Desenha uma balança da justiça e elementos heráldicos institucionais
    """
    # Haste central
    stem_w = max(2, int(6 * scale))
    stem_h = int(70 * scale)
    draw.rectangle([center_x - stem_w//2, center_y - stem_h//2, center_x + stem_w//2, center_y + stem_h//2 + int(10*scale)], fill=color_gold)

    # Base da haste
    base_w = int(50 * scale)
    base_h = int(8 * scale)
    draw.rounded_rectangle([center_x - base_w//2, center_y + stem_h//2 + int(6*scale), center_x + base_w//2, center_y + stem_h//2 + int(6*scale) + base_h], radius=int(3*scale), fill=color_gold)

    # Travessão horizontal superior (braço da balança)
    beam_w = int(100 * scale)
    beam_h = int(5 * scale)
    beam_y = center_y - stem_h//2 + int(10*scale)
    draw.rounded_rectangle([center_x - beam_w//2, beam_y, center_x + beam_w//2, beam_y + beam_h], radius=int(2*scale), fill=color_gold)

    # Ponto focal central (cúpula/esfera)
    c_rad = int(7 * scale)
    draw.ellipse([center_x - c_rad, beam_y - c_rad + beam_h//2, center_x + c_rad, beam_y + c_rad + beam_h//2], fill=color_gold)

    # Pratos da balança (Esquerdo e Direito)
    pan_w = int(36 * scale)
    pan_h = int(12 * scale)
    string_len = int(32 * scale)

    for side in [-1, 1]:
        px = center_x + side * (beam_w // 2 - int(6*scale))
        py = beam_y + string_len
        
        # Cordas do prato
        draw.line([px, beam_y + beam_h, px - pan_w//3, py], fill=color_gold, width=max(1, int(2*scale)))
        draw.line([px, beam_y + beam_h, px + pan_w//3, py], fill=color_gold, width=max(1, int(2*scale)))
        
        # Prato (semicírculo / arco)
        draw.chord([px - pan_w//2, py - pan_h//2, px + pan_w//2, py + pan_h//2], start=0, end=180, fill=color_gold)

def create_pwa_icon(size, is_maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    navy_dark = (15, 33, 55, 255)       # #0F2137
    navy_light = (30, 58, 138, 255)     # #1E3A8A
    gold = (212, 160, 23, 255)          # #D4A017
    gold_light = (250, 204, 21, 255)    # #FACC15
    white = (255, 255, 255, 255)

    # Fundo com cantos arredondados ou quadrado completo se maskable
    corner_radius = int(size * 0.22) if not is_maskable else 0
    
    # Preenchimento com gradiente vertical simulado
    for y in range(size):
        interp = y / float(size)
        r = int(navy_dark[0] * (1 - interp) + navy_light[0] * interp)
        g = int(navy_dark[1] * (1 - interp) + navy_light[1] * interp)
        b = int(navy_dark[2] * (1 - interp) + navy_light[2] * interp)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Borda dourada institucional elegante
    border_w = max(2, int(size * 0.025))
    draw.rectangle([border_w//2, border_w//2, size - border_w//2, size - border_w//2], outline=gold, width=border_w)

    # Escala para maskable (safe area é o centro 80%)
    scale_factor = (size / 200.0) * (0.75 if is_maskable else 0.9)
    center_x = size // 2
    center_y = int(size * 0.44)

    # Desenhar Balança da Justiça
    draw_justice_balance(draw, center_x, center_y, scale_factor, navy_dark, gold_light)

    # Desenhar Monograma / Texto "TJPE 2026"
    text_y = int(size * 0.74)
    # Tenta carregar fonte do sistema ou desenha texto proporcional
    try:
        font_size_main = int(size * 0.13)
        font_size_sub = int(size * 0.07)
        font_main = ImageFont.truetype("arialbd.ttf", font_size_main)
        font_sub = ImageFont.truetype("arial.ttf", font_size_sub)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # "TJPE"
    bbox1 = draw.textbbox((0, 0), "TJPE", font=font_main)
    w1 = bbox1[2] - bbox1[0]
    draw.text((center_x - w1 // 2, text_y), "TJPE", fill=white, font=font_main)

    # "2026"
    bbox2 = draw.textbbox((0, 0), "2026", font=font_sub)
    w2 = bbox2[2] - bbox2[0]
    draw.text((center_x - w2 // 2, text_y + int(size * 0.13)), "2026", fill=gold_light, font=font_sub)

    return img

def main():
    sizes = [192, 512]
    for sz in sizes:
        # Standard icon
        icon = create_pwa_icon(sz, is_maskable=False)
        out_path = ICONS_DIR / f"icon-{sz}.png"
        icon.save(out_path, "PNG")
        print(f"Salvo: {out_path}")

        # Maskable icon (Android adaptive)
        maskable = create_pwa_icon(sz, is_maskable=True)
        out_mask = ICONS_DIR / f"icon-maskable-{sz}.png"
        maskable.save(out_mask, "PNG")
        print(f"Salvo: {out_mask}")

    # Favicon 32x32 e 64x64
    fav = create_pwa_icon(64, is_maskable=False)
    fav.save(ICONS_DIR / "favicon.png", "PNG")
    fav.resize((32, 32)).save(ICONS_DIR / "favicon-32.png", "PNG")
    print("Favicons criados com sucesso!")

if __name__ == "__main__":
    main()
