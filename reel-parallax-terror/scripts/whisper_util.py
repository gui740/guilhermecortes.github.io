import subprocess, numpy as np
def load16k(path):
    raw = subprocess.run(["ffmpeg","-loglevel","error","-i",path,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)/32768.0
