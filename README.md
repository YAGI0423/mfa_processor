<br><br>

### 이 저장소(Repository)는 「Python을 이용한 MFA(Montreal Forced Aligner) 수행」에 대한 내용을 다루고 있습니다.

***
작성자: YAGI<br>

최종 수정일: 2025-12-22
***

<br>

***
+ 프로젝트 기간: 2025-12-20 ~ 2025-12-22
***
<br>

## 프로젝트 요약
&nbsp;&nbsp;
음원 데이터셋 폴더를 MFA 수행에 요구되는 구조로 재구성한 후, TextGrid 파일을 생성합니다.
본 프로젝트는 다음과 같은 기능을 제공합니다. 
<br>

> 1. audio-script로 구성된 `transcript.txt` 자체 식별
> 2. 경로 기반 발화자(speaker) 구분
> 3. MFA 요구 폴더 구조로 재구성
> 4. MFA를 통한 TextGrid 파일 생성

<br><br>

## Getting Start

### Building an environment
```python
$ conda create -n mfa_processor -c conda-forge montreal-forced-aligner==2.2.17  #Create env
$ conda activate mfa_processor  #activate env

$ conda update montreal-forced-aligner -c conda-forge   #install `montreal-forced-aligner`
$ mfa version   #Check `mfa` version
>>> 3.3.8

#install library
$ pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124   #install pytorch
$ pip install questionary

$ mfa model download acoustic [MODEL_NAME]          #install model, ex) `japanese_mfa`
$ mfa model download dictionary [DICTIONARY_NAME]   #install dictionary
```

<br>

### Edit 'hparams.py'
```python
#Get mfa model & dictionary
$ mfa model list acoustic
>>> ['japanese_mfa']

$ mfa model list dictionary
>>> ['japanese_mfa']


#Edit `hparams.py`
DATA_DIR = 'C:/translator/dataset'
...
DICT_NAME = 'japanese_mfa' 
MODEL_NAME = 'japanese_mfa'
```

<br>

### Get TextGrid
```python
$ python audio_preprocessor.py
#1. Self-identifying transcript.txt consisting of `audio-script`
#2. Path-based speaker classification function
#3. Folder structure for performing MFA
'''
mfa_result/
    |--- speaker1/
    |       |--- audio1.wav
    |       |--- audio1.txt
    |       |--- audio2.wav
    |       |--- audio2.txt
    |--- speaker2/
'''



$ python mfa_processor.py   #Get TextGrid
'''
Error About mecab
1. pip install python-mecab-[LANG] jamo
2. conda install -c conda-forge spacy sudachipy sudachidict-core

mfa_result/
    |--- speaker1/
    |       |--- audio1.wav
    |       |--- audio1.txt
    |       |--- audio1.TextGrid <<<
    |       |--- audio2.wav
    |       |--- audio2.txt
    |       |--- audio2.TextGrid <<<
    |--- speaker2/
'''
```
***
<br><br>


## 개발 환경
**Language**

    + Python 3.10.19


<br><br>

## License
This project is licensed under the terms of the [MIT license](https://github.com/YAGI0423/mfa_processor/blob/main/LICENSE).
