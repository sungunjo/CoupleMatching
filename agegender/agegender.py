import os
import cv2
import numpy as np
import argparse
from SSRNET.SSRNET_model import SSR_net, SSR_net_general
import sys
from keras import backend as K
import datetime

class AgeGenderDetector:
    def __init__(self, ad = 0.5, gender_factor = 0.5, scale_factor = 1.1, img_size = 64):
        self.ad = 0.5
        self.gender_factor = gender_factor
        self.scale_factor = scale_factor
        self.img_size = img_size 

        self.model = SSR_net(self.img_size, [3, 3, 3], 1, 1)()
        self.model.load_weights("./SSRNET/pre-trained/age_model/ssrnet_3_3_3_64_1.0_1.0.h5")

        self.model_gender = SSR_net_general(self.img_size, [3, 3, 3], 1, 1)()
        self.model_gender.load_weights("./SSRNET/pre-trained/gender_model/ssrnet_3_3_3_64_1.0_1.0.h5")

        self.face_cascade = cv2.CascadeClassifier('./SSRNET/pre-trained/face_model/lbpcascade_frontalface_improved.xml')

    def run(self, folder_path, image_path, idx):
        print('\nchecking ' + image_path + ' now...')

        if not os.path.isfile(image_path):
            return -5

        input_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        img_h, img_w, _ = np.shape(input_img)

        # detect faces using LBP detector
        detected = ''
        gray_img = cv2.cvtColor(input_img,cv2.COLOR_BGR2GRAY)
        detected = self.face_cascade.detectMultiScale(gray_img, self.scale_factor)
    
        if len(detected) != 2:
            print(str(len(detected)) + " people detected")
            return -1

        faces = np.empty((len(detected), self.img_size, self.img_size, 3))

        for i, (x,y,w,h) in enumerate(detected):
            
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h

            xw1 = max(int(x1 - self.ad * w), 0)
            yw1 = max(int(y1 - self.ad * h), 0)
            xw2 = min(int(x2 + self.ad * w), img_w - 1)
            yw2 = min(int(y2 + self.ad * h), img_h - 1)
            
            faces[i,:,:,:] = cv2.resize(input_img[yw1:yw2 + 1, xw1:xw2 + 1, :], (self.img_size, self.img_size))
            
            faces[i,:,:,:] = cv2.normalize(faces[i,:,:,:], None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        predict_ages = self.model.predict(faces)

        if int(predict_ages[0]) < 10 or int(predict_ages[1]) < 10:
            print("baby(" + str(min(predict_ages[0], predict_ages[1])) + " detected -> " + str(predict_ages[0]) + ", " + str(predict_ages[1]))
            return -2


        # if gender < 0.5 -> female
        # else gender >= 0.5 -> male
        predict_genders = self.model_gender.predict(faces)
        if predict_genders[0] == predict_genders[1]:
            gender = 'male'
            if predict_genders[0] < self.gender_factor:
                gender = 'female'
            print("same gender(" + gender + ") detected")
            return -3

        for i in range(2):
            cv2.imwrite(folder_path + "/temp.jpg", faces[i])
            img = cv2.imread(folder_path + "/temp.jpg", cv2.IMREAD_GRAYSCALE)

            img_mean = img.sum() / (64 * 64)
            img_diff = np.uint8(128 - img_mean)
            if img_diff > 0:
                img_mask = (img <= 255 - img_diff)
                img[img_mask] += img_diff
            else:
                img_mask = (img >= img_diff)
                img[img_mask] -= img_diff

            '''
            img_mask = (img < 32)
            img[img_mask] = 32

            img_mask = (32 <= img)
            img[img_mask] -= 32

            img_mask = (img < 16)
            img[img_mask] = 0

            img_mask = (64 <= img)
            img[img_mask] += 32

            img_mask = (191 <= img)
            img[img_mask] = 191

            img_mask = (95 <= img)
            img[img_mask] -= 32 

            img_mask = (95 <= img)
            img[img_mask] += 64 

            img_mask = (191 <= img)
            img[img_mask] = 255
            '''

            if predict_genders[i] < self.gender_factor:
                cv2.imwrite("female/img_" + str(idx) + ".jpg", img)
            else:
                cv2.imwrite("male/img_" + str(idx) + ".jpg", img)
            os.remove(folder_path + "/temp.jpg")


        if os.path.isfile("female/img_" + str(idx) + ".jpg") == False:
            if os.path.isfile("male/img_" + str(idx) + ".jpg"):
                os.remove("male/img_" + str(idx) + ".jpg")
            return -4
        if os.path.isfile("male/img_" + str(idx) + ".jpg") == False:
            if os.path.isfile("female/img_" + str(idx) + ".jpg") == False:
                os.remove("female/img_" + str(idx) + ".jpg")
            return -4
        
        return idx
    
def main(args):
    try:
        os.mkdir('male')
        os.mkdir('female')
    except:
        pass

    try:
        log = open(args.folder + '/run.log', 'a')
        log.write('\n' + str(datetime.datetime.now()) + " | program start\n")
    except:
        print("ERROR: log file open failed")
        pass

    detector = AgeGenderDetector()
    idx = 0
    if args.index != None:
        idx = int(args.index)
    for i in range(int(args.start), int(args.end) + 1):
        try:
            ret = detector.run(args.folder, args.folder + '/img_' + str(i) + '.jpg', idx)
        except KeyboardInterrupt:
            log.write(str(datetime.datetime.now()) + " | program exit by interrypt\n")
            sys.exit()
        if ret >= 0:
            print("save complete")
            log.write(str(datetime.datetime.now()) + " | split img_" + str(i) + " to img_" + str(idx) + '\n')
            idx = ret + 1
        if ret == -1:
            print("SKIP: more/less than 2 people")
            log.write(str(datetime.datetime.now()) + " | skip img_" + str(i) + " because more less than 2 people detected\n")
        if ret == -2 or ret == -3:
            print("SKIP: not a couple")
            log.write(str(datetime.datetime.now()) + " | skip img_" + str(i) + " because couple not detected\n")
        if ret == -4:
            print("ERROR: save failed")
            log.write(str(datetime.datetime.now()) + " | ERROR OCCUR: img_" + str(i) + " save failed\n")
        if ret == -5:
            print("ERROR: img not found")
            log.write(str(datetime.datetime.now()) + " | ERROR OCCUR img_" + str(i) + " not exist\n")

    print("\nnext index must be " + str(idx) + "\n")

    log.write(str(datetime.datetime.now()) + " | program end\n")
    log.close()

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', required=True, help='folder to process.')
    parser.add_argument('--start', required=True, help='start num of image')
    parser.add_argument('--end', required=True, help='end num of image')
    parser.add_argument('--index', required=False, help='start index num')

    return parser.parse_args(argv)
        
if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
