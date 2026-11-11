"""Mixagem: voz grave em primeiro plano (-16 LUFS); trilha infantil BEM audível por baixo, calibrada pelo
volume EFETIVO dentro da mix (depois de um ducking suave) para ficar ~8 LU abaixo da voz; efeitos por cima.
A trilha recebe realce de médios-altos/agudos para aparecer em alto-falante de celular e uma pequena
"abertura" (−5 dB por ~0,5 s) só nas palavras do título, para o nome "Buddy" ficar sempre claro.
Saída: build/mix.wav"""
import subprocess, json

VOICE = "assets/narracao_grave.wav"
DUR = 38.5
MUSIC_REL = -8.0   # trilha efetiva em relação à voz (LU)
SFX_REL = -10.0
MUSIC_EQ = "highpass=f=70,equalizer=f=1700:t=q:w=1.0:g=-5,equalizer=f=5200:t=q:w=1.0:g=5,treble=g=2:f=8000"  # abre espaço p/ voz (1,7 kHz) e realça brilho (5 kHz)
DUCK = "sidechaincompress=threshold=0.12:ratio=2:attack=20:release=300:makeup=1"

T = json.load(open("src/data/timeline.json")); B = T["blocks"]
def wt(i, j): return (B[i]["start"] + max(0, B[i]["words"][j]["f"])) / 30
KEY = [wt(4, 1), wt(8, 2), wt(6, 1), wt(16, 5), wt(18, 5), wt(18, 6)]   # "Buddy" x2, "cores", "Brasil", "Talking Horror"
dips = "+".join(f"between(t,{k-0.08:.2f},{k+0.45:.2f})" for k in KEY)
END = wt(18, 5) - 0.1   # "Talking Horror": trilha abaixa mais para o @ da página ficar claro
DIP = f"volume='if(gte(t,{END:.2f}),0.12,if({dips},0.56,1))':eval=frame"

def lufs(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(json.loads(r[r.rindex("{"):r.rindex("}") + 1])["input_i"])

def ff(args): subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)

v = lufs(VOICE)
gm = 0.0
for _ in range(3):
    ff(["-i", VOICE, "-i", "build/music.wav", "-filter_complex",
        f"[0:a]apad=whole_dur={DUR}[sc];[1:a]{MUSIC_EQ},volume={gm}dB[m];[m][sc]{DUCK},{DIP}[o]",
        "-map", "[o]", "-t", str(DUR), "-ar", "48000", "-c:a", "pcm_f32le", "build/music_in_mix.wav"])
    m_eff = lufs("build/music_in_mix.wav")
    gm += (v + MUSIC_REL) - m_eff
s = lufs("build/sfx.wav"); gs = (v + SFX_REL) - s
print(f"voz {v:.1f} LUFS | trilha efetiva na mix {m_eff:.1f} LUFS | sfx {gs:+.1f} dB")
ff(["-i", VOICE, "-i", "build/music_in_mix.wav", "-i", "build/sfx.wav", "-filter_complex",
    f"[0:a]apad=whole_dur={DUR}[v];[2:a]volume={gs}dB[s];"
    f"[v][1:a][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.79:attack=2:release=60:level=disabled[o]",
    "-map", "[o]", "-ar", "48000", "-t", str(DUR), "build/mix.wav"])
print("mix", lufs("build/mix.wav"), "LUFS")
