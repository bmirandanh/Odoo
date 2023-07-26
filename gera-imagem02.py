from PIL import Image, ImageDraw, ImageFont
import math
import textwrap


def imageGenerator(text,fontname,color,filename):
    imagew = int(1280 * 1.5)
    imageh = int(740 * 1.5)
    imagearea = imagew * imageh
    textlen = len(text)
    chararea = imagearea // textlen
    charsqrt = int(math.sqrt(chararea))
    linelen = int(imagew / (charsqrt * 0.45))
    lines = textwrap.wrap(text, width = linelen)
    font = ImageFont.truetype(fontname, int(charsqrt * 0.85) )
    container = Image.new('RGBA', (650, 260), color=(0, 0, 0, 0))
    image = Image.new('RGBA', (imagew, imageh), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    x = 0
    y = 0
    maxwidth = 0
    for line in lines:
        pixelsize = draw.textsize(line, font=font)
        if(pixelsize[0] > maxwidth):
            maxwidth = pixelsize[0]

    for line in lines:
        pixelsize = draw.textsize(line, font=font)
        tempx = (int(maxwidth/2)) - (int(pixelsize[0] / 2))
        draw.text((tempx, y), line, font=font, fill=color)
        y += pixelsize[1]
    image = image.crop((0, 0, maxwidth, y))
    image.thumbnail((650, 260), Image.ANTIALIAS)
    pastey = 260 - image.height
    container.paste(image, (0, pastey))
    container.save(filename)

imageGenerator("Olá Mundo","TT Ricks Trial Bold.ttf","#add8e6","nome_para_text.png")