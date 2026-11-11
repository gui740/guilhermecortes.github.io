"""Mixagem: voz -16 LUFS em primeiro plano, trilha 18 dB abaixo da voz, efeitos por cima. Saída: build/mix.wav"""
import subprocess, json, sys
def lufs(f):
    r = subprocess.run(["ffmpeg","-hide_banner","-i",f,"-af","loudnorm=print_format=json","-f","null","-"],capture_output=True,text=True).stderr
    return float(json.loads(r[r.rindex("{"):r.rindex("}")+1])["input_i"])
v, m, s = lufs("assets/narracao_limpa.wav"), lufs("build/music.wav"), lufs("build/sfx.wav")
gm = (v-18) - m          # trilha -18 dB em relação à voz
gs = (v-17) - s          # efeitos
print(f"voz {v:.1f} trilha {m:.1f} (+{gm:.1f}dB) sfx {s:.1f} (+{gs:.1f}dB)")
subprocess.run(["ffmpeg","-v","error","-y","-i","assets/narracao_limpa.wav","-i","build/music.wav","-i","build/sfx.wav","-filter_complex",
 f"[1:a]volume={gm}dB[m];[2:a]volume={gs}dB[s];[0:a][m][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.89:attack=3:release=50[o]",
 "-map","[o]","-ar","48000","build/mix.wav"],check=True)
print("mix", lufs("build/mix.wav"))
