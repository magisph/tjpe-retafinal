from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

ICONS_DIR = Path(r"c:\Users\Junior do Titico\Desktop\TJPE-2026\icons")
ICONS_DIR.mkdir(exist_ok=True)

def draw_justice_balance(draw, center_x, center_y, scale, color_gold, color_gold_light):
    """
    Desenha uma balança minimalista, elegante e geométrica
    """
    # Haste central fina e esguia
    stem_w = max(2, int(3 * scale))
    stem_h = int(64 * scale)
    draw.rounded_rectangle([center_x - stem_w//2, center_y - stem_h//2, center_x + stem_w//2, center_y + stem_h//2 + int(6*scale)], radius=int(1.5*scale), fill=color_gold_light)

    # Cúpula / esfera superior
    top_rad = max(2, int(4.5 * scale))
    draw.ellipse([center_x - top_rad, center_y - stem_h//2 - top_rad, center_x + top_rad, center_y - stem_h//2 + top_rad], fill=color_gold_light)

    # Braço horizontal (travessão) minimalista
    beam_w = int(88 * scale)
    beam_h = max(2, int(3 * scale))
    beam_y = center_y - stem_h//2 + int(8 * scale)
    draw.rounded_rectangle([center_x - beam_w//2, beam_y, center_x + beam_w//2, beam_y + beam_h], radius=int(1.5*scale), fill=color_gold_light)

    # Pratos e cabos de suspensão
    pan_r = int(14 * scale)
    cord_len = int(24 * scale)
    cord_w = max(1, int(1.5 * scale))

    for side in [-1, 1]:
        px = center_x + side * (beam_w // 2 - int(4 * scale))
        py = beam_y + cord_len
        
        # Cabos em V invertido / linhas anguladas sutis
        draw.line([px, beam_y + beam_h, px - pan_r, py], fill=color_gold, width=cord_w)
        draw.line([px, beam_y + beam_h, px + pan_r, py], fill=color_gold, width=cord_w)
        
        # Prato em semicírculo estilizado
        draw.chord([px - pan_r, py - pan_r//2, px + pan_r, py + pan_r], start=0, end=180, fill=color_gold_light, outline=color_gold, width=cord_w)

    # Base sólida estilizada do tribunal
    base_w = int(42 * scale)
    base_h = max(2, int(3.5 * scale))
    base_y = center_y + stem_h//2 + int(6 * scale)
    draw.rounded_rectangle([center_x - base_w//2, base_y, center_x + base_w//2, base_y + base_h], radius=int(1.5*scale), fill=color_gold)

def create_pwa_icon(size, is_maskable=False, is_favicon=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    navy_deep = (11, 23, 43, 255)       # #0B172B
    navy_mid = (19, 36, 62, 255)        # #13243E
    gold = (212, 175, 55, 255)          # #D4AF37
    gold_light = (253, 230, 138, 255)   # #FDE68A
    white = (255, 255, 255, 255)

    # Gradiente vertical suave azul marinho nobre
    for y in range(size):
        interp = y / float(size)
        r = int(navy_deep[0] * (1 - interp) + navy_mid[0] * interp)
        g = int(navy_deep[1] * (1 - interp) + navy_mid[1] * interp)
        b = int(navy_deep[2] * (1 - interp) + navy_mid[2] * interp)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Borda dourada sutil com opacidade elegante apenas para ícones não-maskable
    if not is_maskable and not is_favicon:
        border_w = max(1, int(size * 0.015))
        draw.rectangle([border_w//2, border_w//2, size - border_w//2, size - border_w//2], outline=(212, 175, 55, 140), width=border_w)

    center_x = size // 2
    cy = size // 2

    if is_favicon:
        # Para favicons pequenos (64 e 32), balança geométrica nobre ampliada para máxima nitidez na aba
        scale_factor = (size / 200.0) * 1.35
        draw_justice_balance(draw, center_x, cy, scale_factor, gold, gold_light)
        return img

    # Escala calibrada para respeitar com folga a Safe Zone (W3C Maskable Icon Spec)
    # Permite cortes circulares agressivos no Android sem tocar em nenhum elemento
    scale_factor = (size / 200.0) * (0.72 if is_maskable else 0.78)

    stem_h = int(64 * scale_factor)
    top_rad = max(2, int(4.5 * scale_factor))
    base_h = max(2, int(3.5 * scale_factor))

    balance_top_rel = stem_h // 2 + top_rad
    balance_bottom_rel = stem_h // 2 + int(6 * scale_factor) + base_h
    balance_total_h = balance_top_rel + balance_bottom_rel

    try:
        font_size_main = int(size * (0.096 if is_maskable else 0.105))
        font_size_sub = int(size * (0.052 if is_maskable else 0.058))
        font_main = ImageFont.truetype("arialbd.ttf", font_size_main)
        font_sub = ImageFont.truetype("arial.ttf", font_size_sub)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # "TJPE" com tracking/kerning visual
    title_text = "T J P E"
    bbox1 = draw.textbbox((0, 0), title_text, font=font_main)
    h1 = bbox1[3] - bbox1[1]
    w1 = bbox1[2] - bbox1[0]

    # "2026"
    sub_text = "2 0 2 6"
    bbox2 = draw.textbbox((0, 0), sub_text, font=font_sub)
    h2 = bbox2[3] - bbox2[1]
    w2 = bbox2[2] - bbox2[0]

    gap_balance_text = int(size * 0.035)
    gap_sub = int(size * 0.015)

    total_content_h = balance_total_h + gap_balance_text + h1 + gap_sub + h2

    # Centralização precisa de todo o bloco no centro geométrico (cy) do ícone
    content_top_y = cy - total_content_h // 2
    center_y_balance = content_top_y + balance_top_rel

    # Desenhar Balança Minimalista
    draw_justice_balance(draw, center_x, center_y_balance, scale_factor, gold, gold_light)

    # Desenhar "TJPE"
    text_main_y = center_y_balance + balance_bottom_rel + gap_balance_text - bbox1[1]
    draw.text((center_x - w1 // 2, text_main_y), title_text, fill=white, font=font_main)

    # Desenhar "2026"
    text_sub_y = text_main_y + bbox1[3] + gap_sub - bbox2[1]
    draw.text((center_x - w2 // 2, text_sub_y), sub_text, fill=gold_light, font=font_sub)

    return img

def main():
    sizes = [192, 512]
    for sz in sizes:
        # Standard icon
        icon = create_pwa_icon(sz, is_maskable=False)
        out_path = ICONS_DIR / f"icon-{sz}.png"
        icon.save(out_path, "PNG")
        print(f"Salvo: {out_path}")

        # Maskable icon (Android adaptive splash screen)
        maskable = create_pwa_icon(sz, is_maskable=True)
        out_mask = ICONS_DIR / f"icon-maskable-{sz}.png"
        maskable.save(out_mask, "PNG")
        print(f"Salvo: {out_mask}")

    # Favicon 32x32 e 64x64 de alta nitidez
    fav = create_pwa_icon(64, is_maskable=False, is_favicon=True)
    fav.save(ICONS_DIR / "favicon.png", "PNG")
    fav.resize((32, 32), Image.Resampling.LANCZOS).save(ICONS_DIR / "favicon-32.png", "PNG")
    print("Favicons criados com sucesso!")

if __name__ == "__main__":
    main()
