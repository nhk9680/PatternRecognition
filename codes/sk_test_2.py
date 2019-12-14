# -*- coding: utf-8 -*-
"""패턴인식_data_augmentation.ipynb의 사본

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10Fe1PaW8bM9FfL0UeQkMuppc_uWHP4c_
"""

k=400
L=2
imgsize = 256
step_size = 8

import zipfile
import os
from pandas import read_csv
import cv2
import numpy as np
import time
import pickle
import math
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
#from sklearn.svm import SVC, LinearSVC
from thundersvm import *
from sklearn.model_selection import GridSearchCV
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import classification_report
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
import kmc2
from google.colab import files
from tqdm import tqdm
from scipy.cluster.vq import vq
from keras.preprocessing.image import ImageDataGenerator, array_to_img

os.makedirs('./input', exist_ok=True)

zip_ref = zipfile.ZipFile("2019-ml-finalproject.zip", 'r')
zip_ref.extractall("./input")
zip_ref.close()

df_data = read_csv('/input/Label2Names.csv', header=None)

#train
train_dir = "/input/train"

train_data = []
train_label = []

i=1
for cls in os.listdir(train_dir):
  img_list = os.listdir(train_dir + "/" + cls)

  if cls == 'BACKGROUND_Google' :
    label = 102
    #continue
  else:
    label = (df_data.index[df_data[1]==cls]+1).tolist()[0]

  #sift

  for img in img_list:

    image = cv2.imread(train_dir +'/'+cls+'/'+img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256))
    train_data.append(gray)
    train_label.append(label)

#test
test_dir = "/input/testAll_v2"
test_data = []

img_list = os.listdir(test_dir)

i=1
for img in img_list:
  image = cv2.imread(test_dir+'/'+img)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  gray = cv2.resize(gray, (256, 256))
  test_data.append(gray)

# Importing necessary functions 
from keras.preprocessing.image import ImageDataGenerator, array_to_img
   
# Initialising the ImageDataGenerator class. 
# We will pass in the augmentation parameters in the constructor. 
datagen = ImageDataGenerator( 
        rotation_range = 40, 
        shear_range = 0.2, 
        zoom_range = 0.2, 
        horizontal_flip = True, 
        vertical_flip = True, 
        brightness_range = (0.5, 1.5)) 

x_reshape = []
train_data = np.asarray(train_data)
for i, img in enumerate(train_data):
  img = img.reshape((1,) + (img.shape) + (1, ))
  x_reshape.append(img)

gray_train_data = []
gray_train_label = []

for img, label in tqdm(zip(x_reshape, train_label), total=len(train_label)):
  # Generating and saving 3 augmented samples  
  # using the above defined parameters.  
  for i, batch_x in enumerate(datagen.flow(img, batch_size = 1)):
      #gray = np.squeeze(batch_x, axis=0)
      #gray = np.squeeze(gray, axis=2)
      gray = cv2.resize(gray, (256, 256))
      gray_train_data.append(gray)
      gray_train_label.append(label)
      if i == 3-1 :
        break

train_data = gray_train_data
train_label = gray_train_label

def extract_denseSIFT(img):
    disft_step_size = 8
    sift = cv2.xfeatures2d.SIFT_create()
    keypoints = [cv2.KeyPoint(x, y, disft_step_size)
            for y in range(0, img.shape[0], disft_step_size)
                for x in range(0, img.shape[1], disft_step_size)]

    _, descriptors = sift.compute(img, keypoints)
    
    #keypoints, descriptors = sift.detectAndCompute(gray, None)
    return descriptors

# compute dense SIFT 
def computeSIFT(data):
    x = []
    for i in tqdm(range(0, len(data))):
        img = data[i]
        '''
        sift = cv2.xfeatures2d.SIFT_create()
        step_size = 15
        kp = [cv2.KeyPoint(x, y, step_size) \
              for x in range(0, img.shape[0], step_size) \
              for y in range(0, img.shape[1], step_size)]
        dense_feat = sift.compute(img, kp)
        x.append(dense_feat[1])
        '''

        des = extract_denseSIFT(img)
        x.append(des)
        
    return x

x_train = computeSIFT(train_data)

len(x_train)

x_test = computeSIFT(test_data)

# extract dense sift features from training images

with open("voca_"+str(k)+".pkl", "rb") as f:
  voc = pickle.load(f)

# form histogram with Spatial Pyramid Matching upto level L with codebook kmeans and k codewords
def getImageFeaturesSPM2(L, des, voc, k):
    W = 256
    H = 256
    step_size = 8
    h = []

    W_des = int(W/step_size)
    H_des = int(H/step_size)

    des = np.reshape(des, (W_des, H_des, 128))

    for l in range(L+1):
        w_step = math.floor(W/(2**l))
        h_step = math.floor(H/(2**l))
        x, y = 0, 0
        for i in range(1,2**l + 1):
            x = 0
            for j in range(1, 2**l + 1):                
                desc = des[y:y+h_step, x:x+w_step, :].reshape(-1, 128)
                #predict = kmeans.predict(desc)
                predict = vq(desc, voc)
                histo = np.bincount(predict[0], minlength=k).reshape(1,-1).ravel()
                weight = 2**(l-L)
                h.append(weight*histo)
                x = x + w_step
            y = y + h_step
            
    hist = np.array(h).ravel()
    # normalize hist
    dev = np.std(hist)
    mean = np.mean(hist)
    hist = hist - mean
    hist /= dev
    return hist


# get histogram representation for training/testing data
def getHistogramSPM2(L, data, voc, k):    
    x = []
    for i in tqdm(range(len(data))):        
        hist = getImageFeaturesSPM2(L, data[i], voc, k)        
        x.append(hist)
    return np.array(x)

train_histo = getHistogramSPM2(2, x_train, voc, k)
test_histo = getHistogramSPM2(2, x_test, voc, k)

split_xtrain, split_xtest, split_ytrain, split_ytest = train_test_split(train_histo, train_label, test_size=0.25, random_state=42)

#Kmeans-GPU

now = time.gmtime(time.time())
print(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour+9, now.tm_min, now.tm_sec)
start=time.time()

clf = SVC(verbose=False)

##########################################
clf.fit(split_xtrain, split_ytrain)
##########################################

print(time.time()-start, "sec")

#result = clf.predict(test_histo)

print(classification_report(clf.predict(split_xtest), split_ytest))

result = clf.predict(test_histo)

'''
#GridSearch
parameters = {'kernel':('linear', 'rbf'), 'C':[0.1, 1, 10]}
svc = SVC()
svm = GridSearchCV(svc, parameters)

now = time.gmtime(time.time())
print(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour+9, now.tm_min, now.tm_sec)
start=time.time()

##########################################
svm.fit(train_histo, train_label)
##########################################

print(time.time()-start, "sec")
'''

# numpy 를 Pandas 이용하여 결과 파일로 저장

import pandas as pd

print(result.shape)
df = pd.DataFrame(result, columns=['Category'])
df.index = img_list
df.index.name = 'Id'
df.to_csv('result_namhun_kim_gpusvm.csv',index=True, header=True)

! kaggle competitions submit -c 2019-ml-finalproject -f result_namhun_kim_gpusvm.csv -m "Namhun Kim"