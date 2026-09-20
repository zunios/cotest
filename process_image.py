from PIL import Image, ImageFilter

pi = 3.141592653589793
e  = 2.718281828459045

def process_image(data):
    # Open and resize
    img = Image.open(data).convert("RGBA")
    x, y, wx, wy = 6, 5, 12, 13
    target_w, target_h = 512 - x - wx, 512 - y - wy
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    alpha = img.split()[-1]
    alpha = alpha.point(lambda a: max(0, 4*a - 765))
    # img.putalpha(alpha); return img
    # Place on white canvas
    canvas = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    canvas.paste(img, (x, y), alpha)
    sharpened = canvas.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=0))

    # Build alpha mask on full canvas
    luma = Image.new("L", (512, 512), 0)
    luma.paste(alpha, (x, y))


    r = 5 # size
    # Gaussian stroke
    k = .4
    b1 = 8 # ~89% spread
    b2 = 0
    expanded = (
        luma.point(lambda p: 255*min(max(128 + 5 * (p - 128), 0), 1)) # sharpen original edges
            .filter(ImageFilter.GaussianBlur(k*r))
            .point(lambda p: 255*min(max((p - b2) / (b1 - b2), 0), 1)) # convert blur to stroke
            .convert("L")
    )

    # square-max stroke
    # expanded = luma.filter(ImageFilter.MaxFilter(r*2+1))

    sharpened.putalpha(expanded)


    # Shadow
    r = 4 # size
    dx = -4 # -4.3 ≈ -5 * cos(30deg)
    dy = 3 # 2.5 = 5 * sin(30deg)
    pad = 2*r
    shadow_padded = Image.new("L", (512+2*pad, 512+2*pad), 0)
    shadow_padded.paste(alpha, (x+pad, y+pad))
    shadow_padded = shadow_padded.filter(ImageFilter.GaussianBlur(r))

    shadow_luma = Image.new("L", (512, 512), 0)
    shadow_luma.paste(shadow_padded, (-pad + dx, -pad + dy))

    shadow = Image.new("L", (512, 512), 0)
    shadow.putalpha(shadow_luma.point(lambda a: int(a * 0.25))) # 25% opacity

    # final compositing
    return Image.alpha_composite(shadow.convert("RGBA"), sharpened)
