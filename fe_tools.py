import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
from scipy.signal import butter, sosfiltfilt

from array import array
import json
import base64
import glob
import gzip

def load_get_file_list(folderpath="./", extension="txt"):
    """
    폴더 내 특정 확장명의 파일목록을 반환합니다.
    folderpath: 폴더경로 (\ 쓰지 말것. /를 사용)
    extension: 확장명
    """
    flist = glob.glob(folderpath+f"/*.{extension}")
    return flist

def load_textfile(fname, skiprows=0, delimiter=","):
    """
    데이터 로드
    fname: 파일경로
    skiprows: 무시할 줄
    delimeter: 구분자 ("\t", " ", "," 등)
    return: 2D 어레이
    """
    data = np.loadtxt(fname=fname, skiprows=skiprows, delimiter=delimiter)
    return data

def load_AWSjson(fname):
    """
    AWS S3에 저장된 json 파일의 로딩
    return: dictionary(
        'version': str
        'mac_address': str
        'acq_time': int
        'sampling_rate': int
        'sample_size': int
        'current_u': 1d array
        'current_v': 1d array
        'current_w': 1d array
    )    
    """
    with open(fname, 'r') as f:
        data = json.load(f)
    
    data['current_u'] = np.array(list(array('f', gzip.decompress(base64.b64decode(data['current_u'])))))
    data['current_v'] = np.array(list(array('f', gzip.decompress(base64.b64decode(data['current_v'])))))
    data['current_w'] = np.array(list(array('f', gzip.decompress(base64.b64decode(data['current_w'])))))
    return data

def load_CT_TesterJson(fname):
    """
    CT tester 프로그램을 통해 얻은 json 파일의 로딩
    return: dictionary(
        'acq_time': str
        'sampling_rate': int
        'sample_size': int
        'AI0': 1d array
        'AI1': 1d array
        'AI2': 1d array
        'AI3': 1d array
        'AI4': 1d array
        'AI5': 1d array
    )    
    """
    with open(fname, 'r') as f:
        data = json.loads(f.read())
        data['AI0'] = np.array(data['AI0'])
        data['AI1'] = np.array(data['AI1'])
        data['AI2'] = np.array(data['AI2'])
        data['AI3'] = np.array(data['AI3'])
        data['AI4'] = np.array(data['AI4'])
        data['AI5'] = np.array(data['AI5'])
    return data

def save_list_to_file(_list, fname):
    """
    리스트의 내용을 파일로 저장합니다.
    _list: 리스트
    fname: 파일이름
    """
    with open(fname, 'w') as x:
        for _l in _list:
            x.write(str(_l))
            x.write("\n")

def save_figure(figname, fname):
    """
    figure 를 jpg로 저장합니다.
    figname: figure 이름
    fname: 파일 이름
    """
    plt.figure(figname)
    plt.savefig(fname if ".jpg" in fname else fname+".jpg")


def calc_power(u,v,w):
    power = np.sqrt((u**2+v**2+w**2)/3)
    return power

def process_split2D(arr2D):
    """
    2D 데이터를 컬럼별로 쪼개서 리스트를 반환
    arr2D: 2D 어레이 (컬럼수 N개)
    return [1Darr, 1Darr, 1Darr, ... xN 반복]
    """
    columns = arr2D.shape[-1]
    return [arr2D[i] for i in range(columns)]

def calc_smoothing(arr, windowLen, polyorder=1):
    """
    1D 어레이 스무딩
    arr: 1차원 어레이
    windowLen: 윈도우 길이(홀수)
    polyorder: 차수, 기본값 1
    return: 스무딩된 어레이
    """
    sm = savgol_filter(arr, window_length=windowLen, polyorder=polyorder)
    return sm

def process_threshold_index(arr, threshold):
    """
    threshold 기준값보다 높은 신호의 시작과 끝 인덱스를 반환합니다.
    arr: 1차원 어레이
    threshold: 기준값
    return: 2D 어레이
       [[시작인덱스, 종료인덱스], 
        [시작인덱스, 종료인덱스], 
        [시작인덱스, 종료인덱스], 
        ...
        [시작인덱스, 종료인덱스]]
    """
    newarr = np.concatenate([[threshold-1], arr, [threshold-1]])
    mask = newarr > threshold
    slist = np.where(np.diff(mask.astype(int)) == 1)[0]
    elist = np.where(np.diff(mask.astype(int)) == -1)[0]-1
    index = np.c_[slist, elist]
    return index

def process_windowing_index(array, window_size, step):
    """
    윈도우 처리를 위한 인덱스 생성 함수
    array: 1D 어레이
    window_size: 윈도우 크기
    step: 움직일 스텝 크기
    return: 2D 어레이
       [[시작인덱스, 종료인덱스], 
        [시작인덱스, 종료인덱스], 
        [시작인덱스, 종료인덱스], 
        ...
        [시작인덱스, 종료인덱스]]
    """
    array_len = len(array) # 1000
    index_list = []
    for i in range(int((array_len-window_size)/step)):
        s_index = i*step
        e_index = i*step+window_size
        if e_index <= array_len:
            index_list.append([s_index, e_index])
    return index_list

def calc_run_fft(x, fs):
    """
    fft 함수
    x: 1D array
    fs: 샘플레이트
    return: 주파수(x축), 값(y축)
    ex):
        x, y = run_fft(arr, 1000) 
        plt.plot(x, y)
    """
    Ts = 1/fs
    Nsamp = x.size
    xFreq = np.fft.rfftfreq(Nsamp, Ts)[:-1]
    yFFT = (np.fft.rfft(x)/Nsamp)[:-1]*2
    return xFreq, np.abs(yFFT)

def calc_apply_freq_filter(array, fs, cutoff, mode="lowpass", order=4):
    '''
    array: 적용할 신호
    fs: 샘플레이트
    cutoff: low/highpass 일경우는 cutoff 주파수(Hz), bandpass/notch 일 경우 리스트([low,high])
    mode: lowpass, highpass, bandpass, bandstop
    order: 필터 차수
    '''
    sos = butter(order, cutoff, btype=mode, fs=fs, output="sos")
    y = sosfiltfilt(sos, array)
    return y

def calc_curveFitting(originalFunc, xdata, ydata, p0=None):
    """
    커브피팅 적용 가정
    1. 내가 함수 원형을 알고 있다.
    2. 함수 원형의 계수를 어느정도 미리 알고 있다.
    originalFunc: 함수 원형
    xdata: x축데이터
    ydata: y축데이터
    p0: 초기 파라미터 추정값. 리스트 형태
    return: 최적 파라미터
    """
    popt, _ = curve_fit(originalFunc, xdata, ydata, p0=p0)
    return popt

