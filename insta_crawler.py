from urllib.request import urlopen
import argparse
from selenium import webdriver
import urllib.request
import os
import time
import datetime

parser = argparse.ArgumentParser()

parser.add_argument('-t', '--tag', required=False, help='Tag')
parser.add_argument('-f', '--folder', required=True, help='Folder name')
parser.add_argument('-o', '--os', required=False, help='linux or mac')
args = parser.parse_args()
tag = args.tag
folder = args.folder
run_at = args.os

try:
    if not(os.path.isdir(folder)):
        os.makedirs(os.path.join(folder))
except OSError as e:
    if e.errno != e.errno.EEXIST:
        print("Failed to create directory: " + e.errno)
        raise

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

####
if run_at != None and run_at == "linux":
    driver = webdriver.Chrome('/home/jo/Documents/Resource/chromedriver')                                       # driver for linux
else:
    driver = webdriver.Chrome('/Users/jo/Documents/Resource/chromedriver')                                      # driver for mac
####

driver.implicitly_wait(5)

####
if tag == None:
    driver.get('https://www.instagram.com/explore/tags/럽스타그램/')                                              # static tag search
else:
    driver.get('https://www.instagram.com/explore/tags/'+str(tag)+'/')                                         # dynamic tag search
####

driver.implicitly_wait(3)

driver.execute_script("window.scrollBy(0, 10000);")
idx = 0
cache_size = 24
cache = []
dup_count = 0

f = open("./" + str(folder) + "/log", 'w')
f.write("program start at" + str(datetime.datetime.now()))
f.close()

isEnd = False

for i in range(100000000):
    if isEnd == True:
        break
    line = 4
    if i == 0:
        line = 2

    time.sleep(3)
    print("check " + str(i * 12 - 2) + " images")
    try:
        for j in range(line):
            for k in range(3):
                img_data = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[2]/div/div[' + str(j + 1) + ']/div[' + str(k + 1)+']/a/div/div[1]/img')
                alt = img_data.get_attribute('alt')

                if "사람 1명 이상" in alt or "사람 2명" in alt:
                    if "아기" not in alt and "아이" not in alt and "어린이" not in alt and "결혼" not in alt and "텍스트" not in alt:
                        src = img_data.get_attribute('src')
                        if src in cache:
                            print("duplicated")
                            dup_count += 1
                            if dup_count > cache_size * 1000:
                                isEnd = True
                                break
                        else:
                            urllib.request.urlretrieve(src, str(folder)+"/img_"+str(idx)+".jpg")
                            print(alt)
                            print("img " + str(idx) + " saved")
                            idx += 1
                            cache.append(src)
                            if len(cache) > cache_size:
                                cache.pop(0)
                            dup_count = 0
                    else:
                        print("not couple")
                else:
                    print("more/less than 2 people")
    except:
        print("EXCEPTION OCCUR\nwait 5 sec...")
        f = open("./" + str(folder) + "/error.log", "a")
        f.write("EXCEPTION OCCUR:" + str(datetime.datetime.now()))

        time.sleep(5)
    try:
        driver.execute_script("window.scrollBy(0, 10000);")
    except:
        f.write("program end at " + str(datetime.datetime.now()))
        break
        
driver.close()
