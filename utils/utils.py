from PIL import Image, ImageDraw, ImageFont


###############################################################################
def put_text(file_name):
    img = Image.open(file_name)
    graphics = ImageDraw.Draw(img)
    my_font = ImageFont.truetype("FreeMono.ttf", 65)
    graphics.text((10, 10), "Текст", font=my_font, fill=(255, 0, 0))
    img.save(file_name + ".png")
