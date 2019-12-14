# PatternRecognition
2019년 2학기 패턴인식

# Reference

## official libraries

- [scikit learn](https://scikit-learn.org/)

- [scipy](https://www.scipy.org/)

---

### OpenCV BOWKmeansTrainer, BOWImageDesriptor

- [How exactly does BoVW work for Python-3 Open cv3?](https://answers.opencv.org/question/183596/how-exactly-does-bovw-work-for-python-3-open-cv3/)

- [Bow + SVM for front/back face determination](https://gist.github.com/autosquid/4c5b72b195a4d65008347c7920ef8273)

### non-opencvBOW

- [TrungTVo/spatial-pyramid-matching-scene-recognition](https://github.com/TrungTVo/spatial-pyramid-matching-scene-recognition/blob/master/spatial_pyramid.ipynb)

- [CyrusChiu/Image-recognition](https://github.com/CyrusChiu/Image-recognition)

- [wihoho/Image-Recognition](https://github.com/wihoho/Image-Recognition)

- [thundersvm(SVM GPU Accelation](https://github.com/Xtra-Computing/thundersvm.git)

### peer's kaggle discussion

- https://www.kaggle.com/c/2019-ml-finalproject/discussion

---

# Result

코드 설명은 노트북에 동봉되어 있습니다.

| Timeline    | image size  | L   | step size | K   | accuracy  | changes             |
| ----------- | ----------- | --- | --------- | --- | --------- | ------------------- |
|12/3 13/18/29|64           |  -  |8          |20   |0.04964    |weak feature, cv2.Bow|
|12/3 14/31/00|128          |  -  |8          |100  |0.07978    ||
|12/3 21/53/07|256          |  -  |8          |200  |0.16903    ||
|12/4 22/43/32|64           |  -  |2          |200  |0.22104    |strong feature, cv2.Bow|
|12/4 14/14/18|64           |  -  |2          |400  |0.26182    ||
|12/4 22/35/12|64           |  0  |2          |200  |0.21867    |SPM adapt|
|12/4 23/47/12|64           |  1  |2          |200  |0.27895    ||
|12/4 23/58/42|64           |  2  |2          |400  |0.42021    ||
|12/5 01/48/16|64           |  2  |2          |800  |**0.42080**||
|12/14 01/52/26|64          |  3  |2          |400  |0.36329    |train split 75%|
|12/14 09/57/54|64          |  4  |2          |400  |0.35342    |LDA adapt|
|12/14 10/47/56|64          |  4  |2          |400  |0.37352    |PCA adapt|
|12/14 11/33/54|256         |  2  |2          |400  |0.38356    ||
