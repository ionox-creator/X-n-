import io

CSS = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
.cpe-ws-stage{--bg-0:#0a0512;--bg-1:#120a1f;--violet-900:#2a1250;--violet-700:#5b2fb8;--violet-500:#8f5cf0;--violet-300:#c9aef7;--lilac-100:#efe6fb;--grid-line:rgba(180,150,230,0.09);--grid-dot:rgba(200,175,240,0.35);--text-dim:rgba(230,220,245,0.55);--text-mid:rgba(235,225,248,0.78);position:fixed;inset:0;z-index:200;width:100%;min-height:100vh;min-height:100dvh;background:radial-gradient(ellipse 900px 500px at 78% 8%,rgba(120,70,200,0.20),transparent 60%),linear-gradient(180deg,var(--bg-1) 0%,var(--bg-0) 55%,#050208 100%);display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;color:var(--lilac-100);font-family:'Inter',sans-serif;}
.cpe-ws-stage *{margin:0;padding:0;box-sizing:border-box;}
.cpe-ws-stage .grid-layer{position:absolute;inset:0;background-image:linear-gradient(var(--grid-line) 1px,transparent 1px),linear-gradient(90deg,var(--grid-line) 1px,transparent 1px);background-size:84px 84px;-webkit-mask-image:radial-gradient(ellipse 90% 80% at 60% 30%,black 30%,transparent 85%);mask-image:radial-gradient(ellipse 90% 80% at 60% 30%,black 30%,transparent 85%);pointer-events:none;}
.cpe-ws-stage .grid-dots span{position:absolute;width:5px;height:5px;border-radius:50%;background:var(--grid-dot);box-shadow:0 0 6px rgba(200,175,240,0.6);opacity:.55;}
.cpe-ws-stage .market-line{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:.5;}
.cpe-ws-stage .orb{position:absolute;left:50%;width:min(1000px,145vw);aspect-ratio:1.9/1;border-radius:50%;pointer-events:none;}
.cpe-ws-stage .orb-top{top:-18%;background:radial-gradient(closest-side at 50% 85%,rgba(255,255,255,0.55),rgba(200,170,240,0.28) 38%,rgba(120,70,200,0.05) 62%,transparent 72%);transform:translateX(-50%);filter:blur(0.5px);animation:drift-a 14s ease-in-out infinite;}
.cpe-ws-stage .orb-bottom{bottom:-46%;left:38%;width:min(760px,110vw);background:radial-gradient(closest-side at 50% 15%,rgba(255,255,255,0.4),rgba(180,140,235,0.30) 40%,rgba(90,45,170,0.08) 65%,transparent 75%);transform:translateX(-50%);animation:drift-b 16s ease-in-out infinite;}
.cpe-ws-stage .orb-noise{position:absolute;inset:0;background-image:radial-gradient(1px 1px at 20% 30%,rgba(255,255,255,0.9),transparent),radial-gradient(1px 1px at 60% 15%,rgba(255,255,255,0.7),transparent),radial-gradient(1.5px 1.5px at 80% 40%,rgba(255,255,255,0.8),transparent),radial-gradient(1px 1px at 35% 60%,rgba(255,255,255,0.6),transparent),radial-gradient(1px 1px at 90% 70%,rgba(255,255,255,0.5),transparent);background-size:200px 200px;opacity:.5;mix-blend-mode:screen;}
@keyframes drift-a{0%,100%{transform:translateX(-50%) translateY(0);}50%{transform:translateX(-50%) translateY(10px);}}
@keyframes drift-b{0%,100%{transform:translateX(-50%) translateY(0);}50%{transform:translateX(-50%) translateY(-8px);}}
@media (prefers-reduced-motion:reduce){.cpe-ws-stage .orb-top,.cpe-ws-stage .orb-bottom{animation:none;}}
.cpe-ws-stage header{position:relative;z-index:5;display:flex;align-items:center;gap:.6rem;padding:2.4rem clamp(1.5rem,5vw,4rem) 0;}
.cpe-ws-stage .mark{width:30px;height:30px;display:block;}
.cpe-ws-stage .wordmark{font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:1.35rem;letter-spacing:0.01em;color:#f5f0fc;}
.cpe-ws-stage main{position:relative;z-index:5;flex:1;display:flex;align-items:flex-end;justify-content:space-between;gap:2rem;padding:0 clamp(1.5rem,5vw,4rem) clamp(2.2rem,6vw,4rem);flex-wrap:wrap;}
.cpe-ws-stage .copy{max-width:640px;}
.cpe-ws-stage .eyebrow{font-family:'Space Grotesk',sans-serif;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--violet-300);margin-bottom:1rem;display:flex;align-items:center;gap:.5rem;}
.cpe-ws-stage .eyebrow::before{content:"";width:16px;height:1px;background:var(--violet-300);display:inline-block;}
.cpe-ws-stage h1{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:clamp(2.4rem,5.6vw,4.4rem);line-height:1.02;letter-spacing:-0.01em;background:linear-gradient(180deg,#ffffff 0%,#e7d9fb 55%,#b892ea 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.cpe-ws-stage .subline{margin-top:1.1rem;font-size:clamp(1rem,1.6vw,1.25rem);color:var(--text-mid);font-weight:400;}
.cpe-ws-stage .subline strong{color:var(--lilac-100);font-weight:600;}
.cpe-ws-stage .actions{display:flex;flex-direction:column;align-items:flex-end;gap:1rem;min-width:280px;}
.cpe-ws-stage .status-pill{width:100%;max-width:340px;padding:.95rem 1.4rem;border-radius:999px;text-align:center;font-family:'Space Grotesk',sans-serif;font-size:.92rem;letter-spacing:.03em;color:rgba(230,222,245,0.75);background:linear-gradient(180deg,rgba(255,255,255,0.14),rgba(255,255,255,0.03));border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);}
.cpe-ws-stage .activate-btn{width:100%;max-width:340px;padding:1.05rem 1.4rem;border-radius:999px;border:1px solid rgba(200,160,255,0.4);background:linear-gradient(135deg,#7c2fe0 0%,#5a1fc4 55%,#3d1499 100%);color:#fff;font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:1.02rem;letter-spacing:.02em;cursor:pointer;box-shadow:0 0 0 1px rgba(255,255,255,0.05) inset,0 8px 30px rgba(110,40,220,0.45);transition:transform .18s ease,box-shadow .18s ease,filter .18s ease;}
.cpe-ws-stage .activate-btn:hover{transform:translateY(-1px);filter:brightness(1.08);box-shadow:0 0 0 1px rgba(255,255,255,0.08) inset,0 10px 36px rgba(120,50,235,0.6);}
.cpe-ws-stage .activate-btn:active{transform:translateY(0);filter:brightness(0.96);}
.cpe-ws-stage .activate-btn:focus-visible{outline:2px solid var(--violet-300);outline-offset:3px;}
.cpe-ws-stage .activate-btn:disabled{opacity:.5;cursor:not-allowed;transform:none;}
.cpe-ws-stage .terms{font-size:.78rem;color:var(--text-dim);text-align:right;}
.cpe-ws-stage .terms a{color:var(--violet-300);text-decoration:none;border-bottom:1px solid rgba(201,174,247,0.35);cursor:pointer;}
.cpe-ws-stage .terms a:hover{color:var(--lilac-100);}
.cpe-ws-stage .cpe-ws-keybox{width:100%;max-width:340px;display:flex;flex-direction:column;gap:.6rem;}
.cpe-ws-stage .cpe-ws-input{width:100%;padding:.95rem 1.2rem;border-radius:14px;border:1px solid rgba(200,160,255,0.3);background:rgba(20,10,35,0.65);color:#f5f0fc;font-family:'Space Grotesk',monospace;font-size:.95rem;text-align:center;letter-spacing:.12em;outline:none;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);transition:border-color .2s,box-shadow .2s;}
.cpe-ws-stage .cpe-ws-input:focus{border-color:rgba(200,160,255,0.6);box-shadow:0 0 0 3px rgba(143,92,240,0.15);}
.cpe-ws-stage .cpe-ws-input::placeholder{color:rgba(200,175,240,0.4);letter-spacing:.15em;}
.cpe-ws-stage .cpe-ws-input:disabled{opacity:.6;}
.cpe-ws-stage .cpe-ws-err{color:#f87171;font-size:.78rem;text-align:center;margin:0;}
.cpe-ws-stage.cpe-ws-fadeout{animation:cpeWsFadeOut .6s ease-in forwards;}
@keyframes cpeWsFadeOut{from{opacity:1;}to{opacity:0;}}
@media (max-width:760px){.cpe-ws-stage main{flex-direction:column;align-items:flex-start;gap:1.6rem;}.cpe-ws-stage .actions{align-items:flex-start;width:100%;}.cpe-ws-stage .status-pill,.cpe-ws-stage .activate-btn{max-width:100%;}.cpe-ws-stage .terms{text-align:left;}}
@media (max-width:480px){.cpe-ws-stage header{padding:1.6rem 1.25rem 0;gap:.45rem;}.cpe-ws-stage .mark{width:24px;height:24px;}.cpe-ws-stage .wordmark{font-size:1.1rem;}.cpe-ws-stage main{padding:0 1.25rem 1.8rem;}.cpe-ws-stage .copy{max-width:100%;}.cpe-ws-stage .eyebrow{font-size:.62rem;letter-spacing:.16em;margin-bottom:.75rem;}.cpe-ws-stage .eyebrow::before{width:12px;}.cpe-ws-stage h1{font-size:clamp(2rem,9vw,2.6rem);line-height:1.05;}.cpe-ws-stage .subline{margin-top:.85rem;font-size:.95rem;line-height:1.5;}.cpe-ws-stage .actions{gap:.75rem;}.cpe-ws-stage .status-pill{padding:.8rem 1.1rem;font-size:.82rem;}.cpe-ws-stage .activate-btn{padding:.9rem 1.1rem;font-size:.95rem;}.cpe-ws-stage .terms{font-size:.72rem;}.cpe-ws-stage .grid-layer{background-size:56px 56px;}.cpe-ws-stage .orb-top{top:-10%;}.cpe-ws-stage .orb-bottom{bottom:-38%;}}
@media (max-width:360px){.cpe-ws-stage h1{font-size:1.75rem;}.cpe-ws-stage .subline{font-size:.88rem;}}"""

css_literal = '`' + CSS + '`'

def build_return(J, phase, key, setkey, status, setstatus, err, seterr, showterms, setterms, setphase, validateBtn, actualVal, declineCb, keydownCb, refvar, rtlvar, termsModal):
    """Build the new return JSX with the given variable names."""
    return (
f'''return(0,{J}.jsxs)("div",{{className:"cpe-ws-stage"+("exit"==={phase}?" cpe-ws-fadeout":""),dir:{rtlvar}?"rtl":void 0,children:[
(0,{J}.jsx)("style",{{dangerouslySetInnerHTML:{{__html:{css_literal}}}}}),
(0,{J}.jsx)("div",{{className:"grid-layer"}}),
(0,{J}.jsx)("svg",{{className:"market-line",viewBox:"0 0 1400 800",preserveAspectRatio:"none",children:(0,{J}.jsx)("polyline",{{points:"0,470 140,430 280,510 420,380 560,460 700,300 840,360 980,220 1120,260 1260,150 1400,190",fill:"none",stroke:"rgba(190,165,235,0.28)","strokeWidth":"1.5"}})}}),
(0,{J}.jsxs)("div",{{className:"grid-dots",children:[(0,{J}.jsx)("span",{{style:{{top:"47%",left:"10%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"57%",left:"24%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"38%",left:"40%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"45%",left:"58%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"27%",left:"70%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"32%",left:"80%"}}}}),(0,{J}.jsx)("span",{{style:{{top:"19%",left:"90%"}}}})]}}),
(0,{J}.jsx)("div",{{className:"orb orb-top",children:(0,{J}.jsx)("div",{{className:"orb-noise"}})}}),
(0,{J}.jsx)("div",{{className:"orb orb-bottom",children:(0,{J}.jsx)("div",{{className:"orb-noise"}})}}),
(0,{J}.jsxs)("header",{{children:[(0,{J}.jsx)("svg",{{className:"mark",viewBox:"0 0 40 40",fill:"none",children:(0,{J}.jsx)("path",{{d:"M28 4L14 18H24L12 36L34 16H22L28 4Z",fill:"#F5F0FC"}})}}),(0,{J}.jsx)("span",{{className:"wordmark",children:"ionox"}})]}}),
(0,{J}.jsxs)("main",{{children:[
(0,{J}.jsxs)("div",{{className:"copy",children:[
(0,{J}.jsx)("div",{{className:"eyebrow",children:"Venture Capitalists / Financial Intel Hub"}}),
(0,{J}.jsxs)("h1",{{children:["CAPITAL",(0,{J}.jsx)("br",{{}}),"PRECISION ENGINE"]}}),
(0,{J}.jsxs)("p",{{className:"subline",children:["Where ",(0,{J}.jsx)("strong",{{children:"signal outruns noise"}})," \u2014 precision intelligence for capital that moves first."]}})
]}}),
(0,{J}.jsxs)("div",{{className:"actions",children:[
(0,{J}.jsx)("div",{{className:"status-pill",children:"success"==={status}?"ACCESS GRANTED":"loading"==={status}?"Validating\u2026":"System Syncing\u2026"}}),
"key"==={phase}?(0,{J}.jsxs)("div",{{className:"cpe-ws-keybox",onClick:function(e){{e.stopPropagation()}},children:[
(0,{J}.jsx)("input",{{ref:{refvar},type:"text",value:{key},onChange:function(e){{{setkey}(e.target.value.toUpperCase()),{setstatus}("idle"),{seterr}("")}},onKeyDown:{keydownCb},placeholder:"XXXX-XXXX-XXXX-XXXX",disabled:"loading"==={status}||"success"==={status},className:"cpe-ws-input"}}),
{err}?(0,{J}.jsx)("p",{{className:"cpe-ws-err",children:{err}}}):null,
(0,{J}.jsx)("button",{{onClick:{validateBtn},disabled:"loading"==={status}||"success"==={status}||!{key}.trim(),className:"activate-btn",children:"loading"==={status}?"Validating\u2026":"success"==={status}?"Access Granted":"Activate"}})
]}}):(0,{J}.jsx)("button",{{className:"activate-btn",onClick:function(){{{setphase}("key")}},children:"Activate"}}),
(0,{J}.jsxs)("p",{{className:"terms",children:["By continuing you ",(0,{J}.jsx)("a",{{href:"#",onClick:function(e){{e.preventDefault(),{setterms}(!0)}},children:"agree to the Terms & conditions"}})]}})
]}})
]}}),
(0,{J}.jsx)({termsModal},{{open:{showterms},onAgree:{actualVal},onDecline:{declineCb}}})
]}})'''
    )

# Client chunk: J=u, phase=i, key=o, setkey=l, status=s, setstatus=c, err=p, seterr=f, showterms=h, setterms=m, setphase=a, validateBtn=b, actualVal=v, declineCb=w, keydownCb=j, refvar=y, rtlvar=r, termsModal=vH
client_return = build_return('u', 'i', 'o', 'l', 's', 'c', 'p', 'f', 'h', 'm', 'a', 'b', 'v', 'w', 'j', 'y', 'r', 'vH') + "}"

# SSR chunk: J=d, phase=g, key=i, setkey=k, status=l, setstatus=m, err=n, seterr=o, showterms=p, setterms=q, setphase=h, validateBtn=t, actualVal=u, declineCb=v, keydownCb=w, refvar=r, rtlvar=f, termsModal=ve
ssr_return = build_return('d', 'g', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'h', 't', 'u', 'v', 'w', 'r', 'f', 've') + "}"

OLD_END = "@keyframes welcomeIconIn {\n          from { opacity: 0; transform: scale(0.7); }\n          to { opacity: 1; transform: scale(1); }\n        }\n      `}})]})}"

def patch_file(path, old_start, new_return):
    with io.open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    si = s.find(old_start)
    sj = s.find(OLD_END)
    if si == -1:
        print(f"  ERROR: start anchor not found in {path}")
        return False
    if sj == -1:
        print(f"  ERROR: end anchor not found in {path}")
        return False
    sj_end = sj + len(OLD_END)
    old_len = sj_end - si
    print(f"  Found return block: {old_len} chars (start at {si})")
    s = s[:si] + new_return + s[sj_end:]
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print(f"  PATCHED {path} ({old_len} -> {len(new_return)} chars)")
    return True

print("=== Patching client chunk ===")
patch_file(".next/static/chunks/1aed-jz3ypll2.js",
           'return(0,u.jsxs)("div",{onClick:"hold"===i?x:void 0,', client_return)

print("=== Patching SSR chunk ===")
patch_file(".next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js",
           'return(0,d.jsxs)("div",{onClick:"hold"===g?s:void 0,', ssr_return)

print("\nDONE")
