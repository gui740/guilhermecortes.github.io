import base64, json, os, sys, urllib.request
KEY=os.environ["GEMINI_API_KEY"]
for f in sys.argv[1:]:
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"audio/wav","data":base64.b64encode(open(f,'rb').read()).decode()}},
        {"text":"Transcreva exatamente o que é falado neste áudio, com marcações de tempo aproximadas [mm:ss]. Indique silêncios longos."}]}]}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/"+os.environ.get("M","gemini-3.8-flash")+":generateContent",
        data=json.dumps(body).encode(),headers={"Content-Type":"application/json","X-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=120))
    print(f, d["candidates"][0]["content"]["parts"][0]["text"])
