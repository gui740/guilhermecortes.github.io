import sys, json
from faster_whisper import WhisperModel
_m = None
def model():
    global _m
    if _m is None:
        _m = WhisperModel("small", device="cpu", compute_type="int8")
    return _m
def load16k(path):
    import subprocess, numpy as np
    raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def words(path, prompt=None):
    segs, info = model().transcribe(load16k(path), language="pt", word_timestamps=True, initial_prompt=prompt, vad_filter=False)
    out = []
    for s in segs:
        for w in s.words:
            out.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 2)})
    return out
if __name__ == "__main__":
    for p in sys.argv[1:]:
        ws = words(p)
        print(p, " ".join(w["w"] for w in ws))
        print("   avg prob %.2f" % (sum(w["p"] for w in ws) / max(1, len(ws))))
