import cv2
import datetime
import argparse
import os
import sys
import numpy as np

def L2Distance(a, b):
    temp = (a - b)**2
    diff = np.sqrt(temp.sum())

    return diff
 

class KNear:
    def __init__(self, k, basis, folder_path):
        self.k = k
        self.norm = 1.1
        self.folder_path = folder_path

        self.img_size = 64
        self.num_of_cluster = 0
        self.basis = basis
        self.init_basis_rate = 0.95

        self.cluster_size = []

        self.log = open("./run_" + str(datetime.datetime.now()) + ".log", 'a')
        self.log.write("\n\n\nprogram start\n\n")

    def initBasis(self, start, end):
        diff_sum = 0
        count = 0

        for i in range(start, end + 1):
            input_img = cv2.imread(self.folder_path + "/img_" + str(i) + ".jpg", cv2.IMREAD_GRAYSCALE) / self.norm

            for j in range(i+1, end + 1):
                input_img2 = cv2.imread(self.folder_path + "/img_" + str(j) + ".jpg", cv2.IMREAD_GRAYSCALE) / self.norm

                diff = L2Distance(input_img, input_img2)
                diff_sum += diff
                count += 1

        self.basis = diff_sum / count * self.init_basis_rate
        self.log.write("init basis to " + str(self.basis) + "\n")

    def run(self, idx):
        input_img = cv2.imread(self.folder_path + "/img_" + str(idx) + ".jpg", cv2.IMREAD_GRAYSCALE) / self.norm

        if self.num_of_cluster == 0:
            try:
                os.mkdir(self.folder_path + "/" + self.folder_path + "_0")
            except:
                pass
            cv2.imwrite(self.folder_path + "/" + self.folder_path + "_0/img_0.jpg", input_img)
            self.cluster_size.append(1)
            self.num_of_cluster += 1
            self.log.write("img_" + str(idx) + " make new cluster 0\n\n")
            return idx

        min_diff_pair = (1000000000000000000, -1)
        for i in range(0, self.num_of_cluster):
            diff_sum = 0
            for j in range(0, self.cluster_size[i]):
                input_img2 = cv2.imread(self.folder_path + "/" + self.folder_path + "_" + str(i) + "/img_" + str(j) + ".jpg", cv2.IMREAD_GRAYSCALE) / self.norm
                diff = L2Distance(input_img, input_img2)
                diff_sum += diff
            diff_avg = diff_sum / self.cluster_size[i]

            if min_diff_pair[0] > diff_avg:
                min_diff_pair = (diff_avg, i)

        self.log.write("img_" + str(idx) + " different " + str(min_diff_pair[0]) + " with cluster " + str(min_diff_pair[1]) + "\n")
        
        if min_diff_pair[0] > self.basis:
            try:
                os.mkdir(self.folder_path + "/" + self.folder_path + "_" + str(self.num_of_cluster))
            except:
                pass
            cv2.imwrite(self.folder_path + "/" + self.folder_path + "_" + str(self.num_of_cluster) + "/img_0.jpg", input_img)
            self.cluster_size.append(1)
            self.num_of_cluster += 1
            self.basis *= 1.01
            self.log.write("img_" + str(idx) + " make new cluster " + str(self.num_of_cluster-1) + "\n\n")
        else:

            cv2.imwrite(self.folder_path + "/" + self.folder_path + "_" + str(min_diff_pair[1]) + "/img_" + str(self.cluster_size[min_diff_pair[1]]) + ".jpg", input_img)
            self.cluster_size[min_diff_pair[1]] += 1
            self.log.write("img_" + str(idx) + " go to cluster " + str(min_diff_pair[1]) + "\n\n")
        return idx

    def printResult(self):
        self.log.write("K-nearest neighbor result\n")
        for i in range(0, self.num_of_cluster):
            self.log.write("img at cluster " + str(i) + " = " + str(self.cluster_size[i]) + "\n")
            




def main(args):
    input_k = 3
    input_basis = 5000
    knear = KNear(k = input_k, basis = input_basis, folder_path = args.folder)
    knear.initBasis(int(args.start), int(args.end))
    for i in range(int(args.start), int(args.end) + 1):
        try:
            ret = knear.run(i)
        except KeyboardInterrupt:
            sys.exit()

    knear.printResult()

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', required=True, help='folder to process')
    parser.add_argument('--start', required=True, help='start num of image')
    parser.add_argument('--end', required=True, help='end num of image')

    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
