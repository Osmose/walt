#!/usr/bin/env python
"""
Convert a series of images to a CSS animation.

Usage: walt FILENAMES... [options]

Options:
  -h --help               Show this screen.
  --version               Show version.
  --out-image <filename>  Filename for composite image. [default: walt.png]
  --trim                  Trim the edges of the images.
  --trim-color <color>    Color to trim with.
"""
from docopt import docopt
from PIL import Image, ImageChops


__version__ = '0.1'


def find_trimmed_bbox(image, background_color=None):
    """
    Find the bounding box of non-background regions in the image. If no
    background color is given, the color at the top left corner is
    considered the background color.
    """
    background_color = background_color or image.getpixel((0, 0))
    background = Image.new(image.mode, image.size, background_color)
    diff = ImageChops.difference(image, background)
    return diff.getbbox()


def main():
    args = docopt(__doc__, version=__version__)

    # Open each image in the sequence.
    images = []
    for filename in args['FILENAMES']:
        images.append(Image.open(filename))

    # If requested, trim excess background space from each frame.
    if args['--trim']:
        # Find the bounding box for each image.
        bboxes = []
        for image in images:
            bboxes.append(find_trimmed_bbox(image, args['--trim-color']))

        # Find the maximum bounding box that contains all the bounding
        # boxes in the sequence.
        lefts, tops, rights, bottoms = zip(*bboxes)
        left = min(lefts)
        top = min(tops)
        right = max(rights)
        bottom = max(bottoms)
        width = right - left
        height = bottom - top
        bbox = (left, top, right, bottom)

        # Crop each image.
        cropped_images = []
        for image in images:
            cropped_images.append(image.crop(bbox))
        images = cropped_images
    else:
        width, height = images[0].size

    # Generate a composite image of each image in the sequence.
    final_image = Image.new('RGBA', (width * len(images), height))
    for k, image in enumerate(images):
        final_image.paste(image, (width * k, 0), image)
    final_image.save(args['--out-image'])


if __name__ == 'main':
    main()
