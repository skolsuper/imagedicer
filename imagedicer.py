from PIL import Image
import os
import math
import argparse

# Set the root directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HTML_DIR = os.path.join(BASE_DIR, 'diced_images')


def dice(image_path, out_name, out_ext, outdir, slices):

    loaddir = outdir.split('/', 1)[1] # Path from html file to images
    
    img = Image.open(image_path) # Load image
    imageWidth, imageHeight = img.size # Get image dimensions

    hourglass = Image.open('hourglass-small.png')
    leftOffset = hourglass.size[0] / 2
    upOffset = hourglass.size[1] / 2

    placeholder_filename = 'placeholder.png'
    placeholder = Image.new('L', img.size, color=255)
    placeholder.paste(hourglass, (imageWidth/2 - leftOffset, imageHeight/2 - upOffset))
    placeholder_path = os.path.join(outdir, placeholder_filename)
    placeholder.save(placeholder_path)

    # Make sure the integer widths are bigger than the floats to avoid
    # making 1px wide slices at the edges 
    sliceWidth = int(math.ceil(float(imageWidth) / slices))
    sliceHeight = int(math.ceil(float(imageHeight) / slices))

    percent = 100.0 / slices
    
    html_file = open(os.path.join(HTML_DIR, out_name + '.html'), 'w+')
    html_file.write('''
        <style>
            #dicedimage {
                padding: 0; margin: 0; border-width: 0;
                height: 100%%; width: 100%%;
            }
            .dicedimage-row {
                width: %(imageWidth)spx; height: %(sliceHeight)spx;
                padding: 0; margin: 0; border-width: 0;
            }
            .dicedimage img {
                display: inline;
                padding: 0; margin: 0; border-width: 0;
            }
        </style>
        <div id="dicedimage">
        ''' % locals())

    left = 0 # Set the left-most edge
    upper = 0 # Set the top-most edge
    dice_paths = []
    while (upper < imageHeight):

        html_file.write('<div class="dicedimage-row"><!--\n')
        
        while (left < imageWidth):
            # If the bottom and right of the cropping box overruns the image.
            if (upper + sliceHeight > imageHeight and \
                left + sliceWidth > imageWidth):
                bbox = (left, upper, imageWidth, imageHeight)
            # If the right of the cropping box overruns the image
            elif (left + sliceWidth > imageWidth):
                bbox = (left, upper, imageWidth, upper + sliceHeight)
            # If the bottom of the cropping box overruns the image
            elif (upper + sliceHeight > imageHeight):
                bbox = (left, upper, left + sliceWidth, imageHeight)
            # If the entire cropping box is inside the image,
            # proceed normally.
            else:
                bbox = (left, upper, left + sliceWidth, upper + sliceHeight)
            working_slice = img.crop(bbox) # Crop image based on created bounds
            # Save your new cropped image.
            dice_name = '_'.join(['dice', str(upper), str(left)])
            dice_filename = dice_name + out_ext
            dice_path = os.path.join(outdir, dice_filename)
            working_slice.save(dice_path)
            dice_paths.append(dice_path)
            
            html_file.write(
                '''
                --><img class="dicedimage-piece"
                data-image-path="%(loaddir)s/%(dice_filename)s"
                data-top=%(upper)s
                data_left=%(left)s
                src="%(loaddir)s/%(placeholder_filename)s"><!--
                ''' % locals()
                )

            left += sliceWidth # Increment the horizontal position
        html_file.write('--></div>\n')
        upper += sliceHeight # Increment the vertical position
        left = 0
    html_file.write('</div>')
    html_file.write('''
        <script>
            var dicedimageDiv = document.getElementById('dicedimage');
            var pieces = document.getElementsByClassName('dicedimage-piece');
            var imageBox = dicedimageDiv.parentNode;

            imageBox.onscroll = function() {
                for (var i = 0; i < pieces.length; i++) {
                    if (pieces[i].hasAttribute('data-image-path') && isVisible(pieces[i])) {
                        pieces[i].src = pieces[i].getAttribute('data-image-path');
                        pieces[i].removeAttribute('data-image-path');
                    }
                }
            }

            function isVisible(elm) {
                var boxWidth = imageBox.innerWidth || screen.availWidth;
                var boxHeight = imageBox.innerHeight || screen.availHeight;

                var top = elm.getAttribute('data-top');
                var left = elm.getAttribute('data_left');
                if (top < boxHeight && left < boxWidth) {
                    return true;
                }
                else { return false; }
            }
        </script>
        ''')
    # for dice_path in dice_paths:


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", help="Path to an image file")
    args = parser.parse_args()
    image_path = args.image_file
    try:
        fileName, fileExtension = os.path.splitext(image_path.rsplit('/',1)[1])
    except IndexError:
        fileName, fileExtension = os.path.splitext(image_path)

    diced_images_dir = os.path.join(HTML_DIR, '_'.join([fileName, 'pieces']))
    if not os.path.exists(diced_images_dir):
        os.makedirs(diced_images_dir) 

    dice(
        image_path,
        fileName,
        fileExtension,
        diced_images_dir,
        10
        )

    print "Successfully diced %s" % image_path