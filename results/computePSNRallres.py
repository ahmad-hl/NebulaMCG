import math
import  cv2
import numpy as np
import os
from skimage.measure import compare_ssim
import PIL
from PIL import Image

def ssim(original,compressed):
    # 4. Convert the images to grayscale
    #compressed = cv2.resize(compressed,(1920,1080))
    grayA = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(compressed, cv2.COLOR_BGR2GRAY)

    # 5. Compute the Structural Similarity Index (SSIM) between the two
    #    images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    return score


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.
    file_names = [] # List which will store all of the filenames
    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.
            file_names.append(filename)

    return file_paths,file_names  # Self-explanatory.



def  computeResolutionofJPG(filename):
    """"This function prints the resolution of the jpeg image file passed into it"""
    # loading the image
    with PIL.Image.open(filename) as img_file:
        # fetching the dimensions
        width, height = img_file.size
        # print("The resolution of the image is", width, "x", height)
        return width, height


def computePSNR_Paths(srframe_dir, clframe_dir, outcsvfile):

    _, clientfilenames = get_filepaths(clframe_dir)
    print(clientfilenames)

    # empty dictionary
    psnr_dict = {}
    psnrlist = []
    reader_176_144 = cv2.VideoCapture(srframe_dir+'output_176_144.ivf')
    reader_352_288 = cv2.VideoCapture(srframe_dir+'output_352_288.ivf')
    reader_480_270 = cv2.VideoCapture(srframe_dir+'output_480_270.ivf')
    reader_504_376 = cv2.VideoCapture(srframe_dir+'output_504_376.ivf')
    reader_640_360 = cv2.VideoCapture(srframe_dir+'output_640_360.ivf')
    reader_854_480 = cv2.VideoCapture(srframe_dir+'output_854_480.ivf')
    reader_960_540 = cv2.VideoCapture(srframe_dir+'output_960_540.ivf')
    reader_1280_720 = cv2.VideoCapture(srframe_dir+'output_1280_720.ivf')
    reader_1920_1080 = cv2.VideoCapture(srframe_dir+'output_1920_1080.ivf')
    
    frameno=0
    while True:

        # Loading images (original image and compressed image)
        success, original_1920_1080 = reader_1920_1080.read()
        success, original_1280_720 = reader_1280_720.read()
        success, original_960_540 = reader_960_540.read()
        success, original_854_480 = reader_854_480.read()
        success, original_640_360 = reader_640_360.read()
        success, original_504_376 = reader_504_376.read()
        success, original_480_270 = reader_480_270.read()
        success, original_352_288= reader_352_288.read()
        success, original_176_144 = reader_176_144.read()

        if not success:
            break;

        original = original_1920_1080

        if(str(frameno)+".jpg" in clientfilenames):
            width, height = computeResolutionofJPG(clframe_dir + str(frameno) + ".jpg")
            if width == 1920 and height == 1080:
                original = original_1920_1080

            elif width == 1280 and height == 720:
                original = original_1280_720

            elif width == 960 and height == 540:
                original = original_960_540

            elif width == 854 and height == 480:
                original = original_854_480

            elif width == 640 and height == 360:
                original = original_640_360

            elif width == 504 and height == 376:
                original = original_504_376

            elif width == 480 and height == 270:
                original = original_480_270

            elif width == 352 and height == 288:
                original = original_352_288

            elif width == 176 and height == 144:
                original = original_176_144

            else:
                print("res: {} X {} doesn't belong to any reader".format(width,height))


            compressed = cv2.imread(clframe_dir + str(frameno) + ".jpg")
            framepsnr = cv2.PSNR(original, compressed)
            # print('SIMM:',ssim(original,compressed))
            # cv2.imshow('original', original)
            # cv2.imshow('compressed', compressed)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            framepsnr = 1
        #framepsnr=ssim(original,compressed)
        psnrlist.append(framepsnr)

        # add key value pair to <frameno,psnr> dict
        frameno +=1
        psnr_dict[frameno] = framepsnr

        if frameno>1800:
            break

    print("frame no:", frameno, ", res:", width, "X", height)
    print(psnrlist)
    print(psnr_dict.keys())
    print(psnr_dict.values())
    print(frameno)
    with open(outcsvfile, 'w') as f:
        for key in psnr_dict.keys():
            f.write("%s,%s\n" % (key, psnr_dict[key]))

def main():
    # Put video hq4 in folder named "videos" and frames in folder named "subfolder"
    computePSNR_Paths('../MCGserver/ivfvideos/', '../MCGserver/varbw20ms1plr/recframes_abr/', 'abrPSNR_varbw.csv')



if __name__ == '__main__':
    main()
