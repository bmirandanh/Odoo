from PIL import Image, ImageDraw, ImageFont
import math
import textwrap

imagew = 1280
imageh = 740

imagearea = imagew * imageh
text = "Lorem ipsum sdfsdfs sdfsdf sdf sdf sdf sdf sdfsdfsdfsd sdfsdfsdfsd sdfsdfsdfsdfdf"
textlen = len(text)

chararea = imagearea // textlen
charsqrt = int(math.sqrt(chararea))
linelen = int(imagew / (charsqrt * 0.45))

lines = textwrap.wrap(text, width = linelen)
font = ImageFont.truetype('TT Ricks Trial Variable.ttf', int(charsqrt * 0.85) )

image = Image.new('RGB', (imagew, imageh), color=(255, 255, 255))
draw = ImageDraw.Draw(image)

print(imagearea)
print(textlen)
print(chararea)
print(charsqrt)

x = 50
y = 50

for line in lines:
    print(line)
    draw.text((x, y), line, font=font, fill=(0, 0, 0))
    y += charsqrt

image.save('output.png')
