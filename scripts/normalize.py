import json,subprocess,sys
src,dst=sys.argv[1],sys.argv[2]
r=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-af","loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
d=json.loads(r[r.rindex("{"):r.rindex("}")+1])
f=f"loudnorm=I=-16:TP=-1.0:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true"
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-af",f,"-ar","48000",dst],check=True)
