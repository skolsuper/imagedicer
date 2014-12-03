import Image
import os
import math
import argparse

# Set the root directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HTML_DIR = os.path.join(BASE_DIR, 'diced_images')

def dice(image_path, out_name, out_ext, outdir, slices):
    img = Image.open(image_path) # Load image 
    imgdir = os.path.join(outdir, out_name)
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)
    imageWidth, imageHeight = img.size # Get image dimensions

    # Make sure the integer widths are bigger than the floats to avoid
    # making 1px wide slices at the edges 
    sliceWidth = int(math.ceil(float(imageWidth) / slices))
    sliceHeight = int(math.ceil(float(imageHeight) / slices))

    percent = 100.0 / slices
    
    html_file = open(os.path.join(HTML_DIR, out_name + '.html'), 'w+')
    html_file.write('''
        <style>
            .dicedimage {
                padding: 0; margin: 0; border-width: 0;
            }
            .dicedimage table {
                border-collapse: collapse; width: 100%%; height: 100%%;
            }
            .dicedimage tr {
                width: 100%%; height:%(percent)s%%;
            }
            .dicedimage td {
                width: %(percent)s%%; height: 100%%;
            }
            .dicedimage img {
                width: 100%%; height: 100%%;
            }
        </style>
        <div class="dicedimage">
            <table>
        ''' % locals())

    left = 0 # Set the left-most edge
    upper = 0 # Set the top-most edge
    while (upper < imageHeight):

        html_file.write('<tr>\n')
        
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
            dice_filename = '_'.join(['dice', str(upper), str(left)]) + out_ext
            dice_path = os.path.join(imgdir, dice_filename)
            working_slice.save(dice_path)
            
            html_file.write('<td>\n')
            html_file.write(
                '''
                <img src="%s/%s"></td>\n
                ''' % (
                    diced_images_dir.split('/', 1)[1],
                    '/'.join([out_name, dice_filename])
                    )
                )

            left += sliceWidth # Increment the horizontal position
        html_file.write('</tr>\n')
        upper += sliceHeight # Increment the vertical position
        left = 0
    html_file.write('</table></div>')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", help="Path to an image file")
    args = parser.parse_args()
    image_path = args.image_file
    fileName, fileExtension = os.path.splitext(image_path.rsplit('/',1)[1])

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