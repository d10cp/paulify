# -*- coding: utf-8 -*-
import traceback
import sys
import os
import json
import math
import operator
import re
import time
from unidecode import unidecode
from PIL import Image, ImageDraw

PY2 = sys.version_info.major == 2
characters = 'abcdefghijklmnopqrstuvwxyz0123456789äöüß!"%&/()=?+\'#-.:,;<>'


def remove_emoji(data):
    if not data:
        return data
    if not isinstance(data, basestring):
        return data

    try:
        # Wide UCS-4 build
        emoji_pattern = re.compile(u'['
                                   u'\U0001F300-\U0001F64F'
                                   u'\U0001F680-\U0001F6FF'
                                   u'\u2600-\u26FF\u2700-\u27BF]+',
                                   flags=re.UNICODE)
    except re.error:
        # Narrow UCS-2 build
        emoji_pattern = re.compile(u'('
                                   u'\ud83c[\udf00-\udfff]|'
                                   u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                                   u'[\u2600-\u26FF\u2700-\u27BF])+',
                                   flags=re.UNICODE)

    return emoji_pattern.sub('', data)


def process_text(message):
    processed_text = unicode('')
    # text = message.decode('utf-8')
    text = message
    # remove emojis
    text = remove_emoji(text)
    # set text to lower case
    text = text.lower()
    # remove accents
    for letter in text:
        if letter in u'äöüß':
            pass
        else:
            letter = unicode(unidecode(letter))
        processed_text += letter
    # replace unknown characters with whitespace
    processed_text = ''.join([letter if letter in characters.decode(
        'utf-8') else u' ' for letter in processed_text])

    return unicode(processed_text)


def text_to_image(outfile, text, imagewidth=600, offset=3, footer=60):
    # set text lowercase and remove/replace unknown characters and emojis
    # text = process_text(text)

    with open('colors.json', 'r') as col_file:
        colscheme = json.loads(col_file.read())

    hw_ratio = 3.0 / 4.0  # height / width
    x = int(math.ceil(math.sqrt(len(text) / hw_ratio)))
    y = int(math.ceil(len(text) / float(x)))
    swatchsize = int(imagewidth / x)

    if len(text) < x * y:
        diff = int(x * y - len(text))
        text += diff * ' '

    img = Image.new('RGB', (swatchsize * x, swatchsize * y + offset + footer))
    draw = ImageDraw.Draw(img)

    # draw.line([0, 0, swatchsize-1, 0], fill=(180,180,180), width=offset-2)
    # draw.line([swatchsize, 0, imagewidth-1, 0], fill=(255,255,255), width=offset-2)
    draw.rectangle([0, 0, img.size[0], offset], fill=(255, 255, 255))
    draw.line([0, 0, swatchsize - 1, 0], fill=(180, 180, 180), width=1)
    posx = 0
    posy = offset

    col = 0
    row = 0
    while row < y:
        while col < x:
            letter = text[(row) * x + col]
            color = tuple(colscheme[letter])
            draw.rectangle([posx, posy, posx + swatchsize,
                            posy + swatchsize], fill=color)
            posx = posx + swatchsize
            col += 1
        posx = 0
        posy += swatchsize
        col = 0
        row += 1

    footer_y = img.size[1] - offset - footer
    draw.rectangle([0, footer_y, img.size[0], img.size[1]],
                   fill=(255, 255, 255))
    del draw

    img_footer = Image.open('footer.png')
    footer_x = img.size[0] - img_footer.size[0]
    img.paste(img_footer, (footer_x, footer_y))

    img.convert('P', palette=Image.ADAPTIVE)
    img.save(outfile, 'PNG')


def main():
    try:
        # Check for text message
        # assert isinstance(sys.argv[1], unicode if PY2 else str)
        message = sys.argv[1]
        print type(message)

        # set message lowercase and remove/replace unknown characters and
        # emojis
        message = process_text(message)
        # check for message length (140 char limit)
        message_length = len(message)
        print '>>> ' + message

        if message_length == 0:
            print 'Sorry, I don\'t understand emojis and stickers :-( Please use plain text for your message.\nLet\'s try again! :-)'
        elif message_length > 140:
            print 'Sorry, your message had ' + str(message_length) + ' characters and was too long. Please send me a shorter message (up to 140 characters).'
        else:
            generated_image = 'paul-image.png'
            text_to_image(generated_image, message)

    except Exception as e:
        print traceback.format_exc()  # something went wrong


if __name__ == '__main__':
    main()
