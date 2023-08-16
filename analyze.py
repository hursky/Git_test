import numpy as np
import matplotlib.pyplot as plt
import os

import fe_tools as fet

TEMP_FOLDER = "./temp"
BASE_PICTURE = "./data/base_picture.png"
ALGORITHM_VER = 1.0


def run_analysis(motor_name: str, aws_files: list):
    ret = {
        "name": motor_name,
        "driving_rst_pic": BASE_PICTURE,
        "driving_fft_pic": BASE_PICTURE,
        "driving_text": "",
        "driving_p2p_max_pic": BASE_PICTURE,
        "on_start_pic": BASE_PICTURE,
        "on_stop_pic": BASE_PICTURE,
        "stop_pic": BASE_PICTURE,
    }

    # begin analysis --------------------------------

    d1 = fet.load_AWSjson(aws_files[0])
    d1u = d1["current_u"]
    d1v = d1["current_v"]
    d1w = d1["current_w"]
    t = np.linspace(0, d1["sample_size"]/d1["sampling_rate"], d1["sample_size"])
    rms = np.sqrt((d1u**2 + d1v**2 + d1w**2)/3)
    p2p = rms.max() - rms.min()


    plt.figure(figsize=(6,3))
    plt.title(d1["acq_time"])
    plt.plot(t[:2000], d1u[:2000], "r", label="R")
    plt.plot(t[:2000], d1v[:2000], "b", label="S")
    plt.plot(t[:2000], d1w[:2000], "k", label="T")
    plt.plot(t[:2000], rms[:2000], "g", lw=4, label="RMS-A")
    plt.xlabel("seconds (s)")
    plt.ylabel("current (A)")
    plt.legend()
    plt.tight_layout()
    plt.grid()
    plt.savefig("./temp/rst_pic.png")
    plt.close()
    ret["driving_rst_pic"] = "./temp/rst_pic.png"

    # peak to peak
    plt.figure(figsize=(2,1))
    plt.plot(t[25000:25000+200], d1u[25000:25000+200], "r", label="R")
    plt.plot(t[25000:25000+200], d1v[25000:25000+200], "b", label="S")
    plt.plot(t[25000:25000+200], d1w[25000:25000+200], "k", label="T")
    plt.plot(t[25000:25000+200], rms[25000:25000+200], "g", lw=4, label="RMS-A")
    # plt.xlabel("point")
    # plt.ylabel("current (A)")
    # plt.legend()
    plt.tight_layout()
    plt.grid()
    plt.savefig("./temp/p2p_max_pic.png")
    plt.close()
    ret["driving_p2p_max_pic"] = "./temp/p2p_max_pic.png"

    # FFT
    fftxu, fftyu = fet.calc_run_fft(d1u, fs=d1["sampling_rate"])
    fftxv, fftyv = fet.calc_run_fft(d1v, fs=d1["sampling_rate"])
    fftxw, fftyw = fet.calc_run_fft(d1w, fs=d1["sampling_rate"])
    fftxr, fftyr = fet.calc_run_fft(rms, fs=d1["sampling_rate"])
    plt.figure(figsize=(6,3))
    plt.plot(fftxu, fftyu, "r", alpha=0.3, label="R")
    plt.plot(fftxv, fftyv, "b", alpha=0.3, label="S")
    plt.plot(fftxw, fftyw, "k", alpha=0.3, label="T")
    plt.plot(fftxr, fftyr, "g", alpha=0.3, lw=4, label="RMS-A")
    plt.xlabel("freq (Hz)")
    plt.ylabel("current (A)")
    # plt.semilogx()
    # plt.semilogy()
    plt.legend()
    plt.xlim([fftxu[fftyu.argmax()]-1.3, fftxu[fftyu.argmax()]+1.3])
    plt.tight_layout()
    plt.grid()
    plt.savefig("./temp/fft_pic.png")
    plt.close()
    ret["driving_fft_pic"] = "./temp/fft_pic.png"

    # THD
    fftyu_thd = np.sqrt((fftyu.sum() -fftyu.max())**2) / fftyu.max()
    fftyv_thd = np.sqrt((fftyv.sum() -fftyv.max())**2) / fftyv.max()
    fftyw_thd = np.sqrt((fftyw.sum() -fftyw.max())**2) / fftyw.max()


    

    ret["driving_text"] += f"총 분석 신호: {len(aws_files)} 개\n"
    ret["driving_text"] += f"RMS-A 평균값: {rms.mean():.2f} A, 표준편차: {rms.std():.2f}\n"
    ret["driving_text"] += f"RMS-A 최대 Peak-to-peak: {p2p:.2f} A\n"
    ret["driving_text"] += f"주파수 분석\n"
    ret["driving_text"] += f" - R상 main 주파수: {fftyu.max():.2f} A, {fftxu[fftyu.argmax()]:.2f} Hz. THD {fftyu_thd:.2f}%\n"
    ret["driving_text"] += f" - S상 main 주파수: {fftyv.max():.2f} A, {fftxv[fftyv.argmax()]:.2f} Hz. THD {fftyv_thd:.2f}%\n"
    ret["driving_text"] += f" - T상 main 주파수: {fftyw.max():.2f} A, {fftxw[fftyw.argmax()]:.2f} Hz. THD {fftyw_thd:.2f}%\n"

    # end of analysis -------------------------------

    return ret
