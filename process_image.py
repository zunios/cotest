from PIL import Image, ImageFilter, ImageChops

def process_image(data):
    img = Image.open(data).convert("RGBA")
    target_w, target_h = 256, 256
    img.thumbnail((target_w, target_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    x, y = 128, 128
    canvas.paste(img, (x, y), img)

    alpha_canvas = Image.new("L", (512, 512), 0)
    alpha_canvas.paste(img.split()[-1], (x, y))

    expanded = alpha_canvas.filter(ImageFilter.GaussianBlur(6))
    stroke_band = ImageChops.subtract(expanded, alpha_canvas)
    stroke_layer = Image.new("RGBA", (512, 512), (255, 0, 0, 255))
    stroke_layer.putalpha(stroke_band)

    shadow_alpha = stroke_band.filter(ImageFilter.GaussianBlur(10))
    shadow_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 150))
    shadow_layer.putalpha(shadow_alpha)

    composed = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    composed.paste(shadow_layer, (x+5, y+5), shadow_layer)
    composed = Image.alpha_composite(composed, stroke_layer)
    composed = Image.alpha_composite(composed, canvas)

    return composed
