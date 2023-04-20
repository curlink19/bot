from PIL import Image, ImageDraw, ImageFont
import db.db
import random
import numpy as np


###############################################################################
TEXT_SIZE = 40


def put_text(file_name):
    global TEXT_SIZE
    img = Image.open(file_name)
    graphics = ImageDraw.Draw(img)
    my_font = ImageFont.truetype(db.db.font, TEXT_SIZE)
    size = np.array(img).shape
    graphics.text(
        ((size[0] * 2) // 3 - TEXT_SIZE, size[1] // 4),
        db.db.phrases[random.randint(0, len(db.db.phrases) - 1)],
        font=my_font,
        fill=(255, 0, 0),
        align="center",
    )
    img.save(file_name + ".png")
