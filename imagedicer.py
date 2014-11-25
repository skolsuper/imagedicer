import Image
import os
import math

# Set the root directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
HTML_DIR = os.path.join(BASE_DIR, 'html_snippets')
DICED_IMAGES_DIR = os.path.join(HTML_DIR, 'diced_images')

STYLE = 'padding: 0; margin: 0; border-width: 0;'

def dice(image_path, out_name, out_ext, outdir, slices):
    try:
        img = Image.open(image_path) # Load image
    except:
        return
    imgdir = os.path.join(outdir, out_name)
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)
    imageWidth, imageHeight = img.size # Get image dimensions

    # Make sure the integer widths are bigger than the floats to avoid
    # making 1px wide slices at the edges 
    sliceWidth = int(math.ceil(float(imageWidth) / slices))
    sliceHeight = int(math.ceil(float(imageHeight) / slices))

    html_file = open(os.path.join(HTML_DIR, out_name + '.html'), 'w+')
    html_file.write(
        '<table style="%s border-collapse: collapse; width: 100%%">\n' % STYLE
        )

    left = 0 # Set the left-most edge
    upper = 0 # Set the top-most edge
    while (upper < imageHeight):
        html_file.write(
            '<tr style="%s width: 100%%; height:20%%;">\n' % STYLE
            )
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
            
            html_file.write(
                '<td style="%s width: 20%%; height: 100%%;">\n' % STYLE
                )
            html_file.write(
                '''
                <img src="diced_images/%s"
                style="width: 100%%; height: 100%%;"></td>\n
                ''' % '/'.join([out_name, dice_filename])
                )

            left += sliceWidth # Increment the horizontal position
        html_file.write('</tr>\n')
        upper += sliceHeight # Increment the vertical position
        left = 0
    html_file.write('</table>')

if __name__ == '__main__':
    if not os.path.exists(DICED_IMAGES_DIR):
        os.makedirs(DICED_IMAGES_DIR)
    # Iterate through all the files in a set of directories.
    file_count = 0
    for subdir, dirs, files in os.walk(IMAGES_DIR):
        for imgfile in files:
            fileName, fileExtension = os.path.splitext(imgfile)
            dice(
                '/'.join([subdir, imgfile]),
                fileName,
                fileExtension,
                DICED_IMAGES_DIR,
                5
                )
            file_count += 1

    print "Successfully diced %s images" % str(file_count)