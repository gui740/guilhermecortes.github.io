"""Mixagem: voz grave em primeiro plano (-16 LUFS), trilha infantil animada audível por baixo
(-12 LU em relação à voz, com ducking automático quando a voz fala), efeitos por cima. Saída: build/mix.wav"""
import subprocess, json

VOICE = "assets/narracao_grave.wav"

def lufs(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(json.loads(r[r.rindex("{"):r.rindex("}") + 1])["input_i"])

v, m, s = lufs(VOICE), lufs("build/music.wav"), lufs("build/sfx.wav")
gm = (v - 12) - m
gs = (v - 11) - s
print(f"voz {v:.1f} | trilha {m:.1f} -> {gm:+.1f} dB | sfx {s:.1f} -> {gs:+.1f} dB")
fc = (
    f"[0:a]asplit=2[v][vsc];"
    f"[1:a]volume={gm}dB[m];"
    f"[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=280:makeup=1[md];"
    f"[2:a]volume={gs}dB[s];"
    f"[v][md][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.89:attack=3:release=60[o]"
)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VOICE, "-i", "build/music.wav", "-i", "build/sfx.wav",
                "-filter_complex", fc, "-map", "[o]", "-ar", "48000", "build/mix.wav"], check=True)
print("mix", lufs("build/mix.wav"), "LUFS")
