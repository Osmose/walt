#!/usr/bin/env python
"""
Convert a series of images to a CSS animation. Outputs an image file
containing the frames of the animation and an HTML file with sample CSS
for embedding the animation on a page.

Usage: walt FILENAMES... [options]

Options:
  --help                  Show this screen.
  --version               Show version.
  --verbose               Output extra information during run.
  --out-image <filename>  Filename for composite image. [default: walt.png]
  --out-html <filename>   Filename for sample HTML. [default: walt.html]
  --trim                  Trim the edges of the images.
  --trim-color <color>    Color to trim with.
  --prefix <prefix>       Prefix to use for CSS classes in sample HTML. [default: walt]
  --duration <duration>   Duration of the animation. Defaults to a value
                          that ensures 24fps.
"""
import os.path

from docopt import docopt
from PIL import Image, ImageChops


__version__ = '0.1'


with open(os.path.join(os.path.dirname(__file__), 'sample_template.html')) as f:
        template = f.read()


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


def generate_html(filename, frame_width, frame_height, frame_count, image_filename, prefix,
                  duration=None):
    rendered_template = template.format(
        prefix=prefix,
        frame_width=frame_width,
        frame_height=frame_height,
        frame_count=frame_count,
        duration=duration or '{0:.2f}s'.format(float(frame_count) / 24.0),
        final_width=frame_width * frame_count,
    )

    with open(filename, 'w') as f:
        f.write(rendered_template)


def main():
    args = docopt(__doc__, version=__version__)

    # Utility function to output if verbose.
    def out(msg):
        if args['--verbose']:
            print msg

    # Open each image in the sequence.
    out('Loading images...')
    images = []
    for filename in args['FILENAMES']:
        images.append(Image.open(filename))

    # If requested, trim excess background space from each frame.
    if args['--trim']:
        out('Trimming edges...')

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

        out('Bounding Box: ' + unicode(bbox))
        out('Width: ' + unicode(width))
        out('Height: ' + unicode(height))

        # Crop each image.
        cropped_images = []
        for image in images:
            cropped_images.append(image.crop(bbox))
        images = cropped_images
    else:
        width, height = images[0].size

    # Generate a composite image of each image in the sequence.
    out('Generating composite image...')

    final_width = width * len(images)
    out('Composite width: ' + unicode(final_width))

    final_image = Image.new('RGBA', (final_width, height))
    for k, image in enumerate(images):
        final_image.paste(image, (width * k, 0), image)
    final_image.save(args['--out-image'])

    generate_html(
        filename=args['--out-html'],
        frame_width=width,
        frame_height=height,
        frame_count=len(images),
        image_filename=args['--out-image'],
        prefix=args['--prefix'],
        duration=args['--duration'],
    )

    out('Done!')


if __name__ == 'main':
    main()
