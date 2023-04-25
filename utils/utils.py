from PIL import Image, ImageDraw, ImageFont
import db.db
import random
import numpy as np


###############################################################################
PLACE = (0.3, 0.7)  # (x, y) of (1, 1)


def put_text(file_name):
    global TEXT_SIZE
    img = Image.open(file_name)
    graphics = ImageDraw.Draw(img)
    my_font = ImageFont.truetype(db.db.font, db.db.fontsize)
    size = np.array(img).shape
    point = (int(size[1] * PLACE[0]), int(size[0] * PLACE[1]))
    graphics.text(
        point,
        db.db.phrases[random.randint(0, len(db.db.phrases) - 1)],
        font=my_font,
        fill=(255, 255, 255),
    )
    img.save(file_name + ".png")
