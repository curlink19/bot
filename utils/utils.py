from PIL import Image, ImageDraw, ImageFont
import db.db
import random


###############################################################################


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)


def get_size(text_string, font):
    a, b = 0, 0
    for x in text_string.split("\n"):
        if len(x) == 0:
            continue
        cur = get_text_dimensions(x, font)
        b += cur[1] + 4
        a = max(a, cur[0])
    return a, b


def put_text(file_name, PLACE, auto):
    global TEXT_SIZE
    img = Image.open(file_name)
    graphics = ImageDraw.Draw(img)
    my_font = ImageFont.truetype(db.db.font, db.db.fontsize)
    size = img.size
    text = db.db.phrases[random.randint(0, len(db.db.phrases) - 1)]

    if auto:
        border = get_size(text, my_font)
        point = (
            int(size[0] - border[0]) // 2,
            int(size[1] * (1 - db.db.indent)) - border[1],
        )
    else:
        point = (int(size[0] * PLACE[0]), int(size[1] * PLACE[1]))

    graphics.text(
        point,
        text,
        font=my_font,
        fill=(255, 255, 255),
    )

    img.save(file_name + ".png")
