from PIL import Image, ImageFilter, ImageChops

pi = 3.141592653589793
e  = 2.718281828459045

def process_image(data):
    # Open and resize
    img = Image.open(data).convert("RGBA")
    target_w, target_h = 512 - 6 - 12, 512 - 5 - 13
    img.thumbnail((target_w, target_h), Image.LANCZOS)

    # Place on white canvas
    canvas = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    x, y = 6, 5
    canvas.paste(img, (x, y), img)

    # Build alpha mask on full canvas
    alpha_canvas = Image.new("L", (512, 512), 0)
    alpha_canvas.paste(img.split()[-1], (x, y))

    r = 5 # size
    # Gaussian stroke
    k = .4
    b1 = 8 # 89% spread
    b2 = 0
    expanded = (
        alpha_canvas
            .point(lambda p: 255*min(max(128 + 5 * (p - 128), 0), 1)) # sharpen original edges
            .filter(ImageFilter.GaussianBlur(k*r))
            .point(lambda p: 255*min(max((p - b2) / (b1 - b2), 0), 1)) # convert blur to stroke
            .convert("L")
    )

    # square-max stroke
    # expanded = alpha_canvas.filter(ImageFilter.MaxFilter(r*2+1))

    sharpened = canvas.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=0))
    sharpened.putalpha(expanded)
    # expanded.paste(img, (x,y), img)

    # Shadow
    r = 10 # size
    dx = 3 # 2.5 = 5 * cos(120deg)
    dy = 4 # 4.3 = 5 * sin(120deg)
    pad = 0#2*r
    shadow = Image.new("L", (512+2*pad, 512+2*pad), 0)
    shadow.putalpha(expanded)
    shadow = ImageChops.offset(shadow, pad+dx, pad+dy).filter(ImageFilter.GaussianBlur(r))

    # # Shadow: from stroke band, blurred, with offset
    # shadow_alpha = stroke_band.filter(ImageFilter.GaussianBlur(10))
    # shadow_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 150))
    # shadow_layer.putalpha(shadow_alpha)

    # # Compose in correct order: shadow → stroke → image
    # composed = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    # composed.paste(shadow_layer, (x+5, y+5), shadow_layer)  # offset shadow
    # composed = Image.alpha_composite(composed, stroke_layer)
    # composed = Image.alpha_composite(composed, canvas)

    return shadow
