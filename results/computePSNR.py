import cv2
import os
from skimage.metrics import structural_similarity as compare_ssim

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


def computePSNR_avi(srframe_dir, client_avi_path, outcsvfile):

    # empty dictionary
    psnr_dict = {}
    psnrlist = []
    reader_1920_1080 = cv2.VideoCapture(srframe_dir )  # cv2.VideoCapture(srframe_dir+'output_1920_1080.ivf')
    avi_reader = cv2.VideoCapture(client_avi_path)

    frameno = 0
    while True:

        # Loading images (original image and compressed image)
        success, original = reader_1920_1080.read()
        success, compressed =  avi_reader.read()

        if not success:
            break;

        framepsnr = cv2.PSNR(original, compressed)
        cv2.imshow('original', original)
        cv2.imshow('compressed', compressed)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        psnrlist.append(framepsnr)

        # add key value pair to <frameno,psnr> dict
        frameno += 1
        psnr_dict[frameno] = framepsnr

        if frameno >= 1800:
            break

    # print("frame no:", frameno, ", res:", width, "X", height)
    print(psnrlist)
    print(psnr_dict.keys())
    print(psnr_dict.values())
    print(frameno)
    with open(outcsvfile, 'w') as f:
        for key in psnr_dict.keys():
            f.write("%s,%s\n" % (key, psnr_dict[key]))

def computePSNR_Paths(srframe_dir, clframe_dir, outcsvfile):

    _, clientfilenames = get_filepaths(clframe_dir)
    print(clientfilenames)

    # empty dictionary
    psnr_dict = {}
    psnrlist = []
    reader_1920_1080 = cv2.VideoCapture(srframe_dir+'hq4.mp4') #cv2.VideoCapture(srframe_dir+'output_1920_1080.ivf')
    
    frameno=0
    while True:

        # Loading images (original image and compressed image)
        success, original_1920_1080 = reader_1920_1080.read()

        if not success:
            break;

        original = original_1920_1080
        if(str(frameno)+".jpg" in clientfilenames):
            compressed = cv2.imread(clframe_dir + str(frameno) + ".jpg")
            framepsnr = cv2.PSNR(original, compressed)
            # cv2.imshow('original', original)
            # cv2.imshow('compressed', compressed)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        else:
            framepsnr = 1
        #framepsnr=ssim(original,compressed)
        psnrlist.append(framepsnr)

        # add key value pair to <frameno,psnr> dict
        frameno +=1
        psnr_dict[frameno] = framepsnr

        if frameno>1800:
            break

    # print("frame no:", frameno, ", res:", width, "X", height)
    print(psnrlist)
    print(psnr_dict.keys())
    print(psnr_dict.values())
    print(frameno)
    with open(outcsvfile, 'w') as f:
        for key in psnr_dict.keys():
            f.write("%s,%s\n" % (key, psnr_dict[key]))

def main():
    # Put video hq4 in folder named "videos" and frames in folder named "subfolder"
    # computePSNR_Paths('../inout_data/', '../inout_data/tcpframes/', 'tcppsnr.csv')
    # computePSNR_Paths('../inout_data/', '../inout_data/boframes/', 'bopsnr.csv')
    computePSNR_Paths('../inout_data/', '../inout_data/nebulaframes/', 'nebulapsnr.csv')
    # computePSNR_Paths('../inout_data/', '../inout_data/gopframes/', 'goppsnr.csv')

if __name__ == '__main__':
    main()
