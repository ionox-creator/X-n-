#!/bin/bash
# Restore Fintel app: extract zip, apply all patches, start server
set -e
cd /home/z/my-project

echo "=== 1. Re-extract .next + node_modules from zip ==="
unzip -o -q "upload/CPE-production-ready (2).zip" ".next/*" "node_modules/*" -d /home/z/my-project 2>&1 | tail -2
echo "Next version: $(cat node_modules/next/package.json | grep '\"version\"' | head -1)"
echo ".next BUILD_ID: $(cat .next/BUILD_ID 2>/dev/null)"

echo ""
echo "=== 2. Apply license key hash (FINTEL- prefix) ==="
python3 << 'PYEOF'
import io
p = ".next/server/chunks/[root-of-the-server]__0z2sns6._.js"
OLD = "let y=[70,39,24,65,108,168,195,113,31,74,186,221,44,40,37,72,109,215,186,244,100,114,26,187,26,203,65,229,137,254,30,135];"
NEW = "let y=[111,96,73,189,199,175,211,128,13,28,184,119,136,126,221,212,111,175,91,38,243,92,45,115,145,74,241,135,234,84,166,159];"
with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
s = s.replace(OLD, NEW)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("hash patched")
PYEOF

echo ""
echo "=== 3. Patch wallpaper upload API (GET handler + full path URL) ==="
python3 << 'PYEOF'
import io
p = ".next/server/chunks/[root-of-the-server]__02r4ny5._.js"
with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
old = "return await (0,m.writeFile)(i,a),f.NextResponse.json({url:o,name:t.name})"
new = 'return await (0,m.writeFile)(i,a),f.NextResponse.json({url:"/api/upload-wallpaper?file="+o,name:t.name})'
s = s.replace(old, new)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("upload API patched")

# Add GET handler
old2 = 'async function E(e){try{let t=(await e.formData()).get("wallpaper");if(!t)return f.NextResponse.json({error:"No file provided"},{status:400});let r=await t.arrayBuffer(),a=Buffer.from(r),n=process.env.VERCEL?"/tmp/cpe/uploads/wallpapers":g.default.join(process.cwd(),"public","uploads","wallpapers");await (0,m.mkdir)(n,{recursive:!0});let s=t.name.split(".").pop()?.toLowerCase()||"png",o=`wp_${Date.now()}_${Math.random().toString(36).substring(2,8)}.${s}`,i=g.default.join(n,o);return await (0,m.writeFile)(i,a),f.NextResponse.json({url:"/api/upload-wallpaper?file="+o,name:t.name})}catch(e){return console.error("[Wallpaper Upload] Error:",e),f.NextResponse.json({error:"Upload failed on serverless environment"},{status:500})}}e.s(["POST",0,E],4390);'
new2 = 'async function G(e){try{let file=new URL(e.url).searchParams.get("file");if(!file)return f.NextResponse.json({error:"No file specified"},{status:400});if(file.includes("..")||file.includes("/")||file.includes("\\\\"))return f.NextResponse.json({error:"Invalid file"},{status:400});let dir=g.default.join(process.cwd(),"public","uploads","wallpapers"),fp=g.default.join(dir,file),data=await (0,m.readFile)(fp),ext=file.split(".").pop()?.toLowerCase()||"png",ct={"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","gif":"image/gif","webp":"image/webp","svg":"image/svg+xml"}[ext]||"application/octet-stream";return new f.NextResponse(data,{headers:{"Content-Type":ct,"Cache-Control":"public, max-age=31536000, immutable"}})}catch(e){return f.NextResponse.json({error:"File not found"},{status:404})}}async function E(e){try{let t=(await e.formData()).get("wallpaper");if(!t)return f.NextResponse.json({error:"No file provided"},{status:400});let r=await t.arrayBuffer(),a=Buffer.from(r),n=process.env.VERCEL?"/tmp/cpe/uploads/wallpapers":g.default.join(process.cwd(),"public","uploads","wallpapers");await (0,m.mkdir)(n,{recursive:!0});let s=t.name.split(".").pop()?.toLowerCase()||"png",o=`wp_${Date.now()}_${Math.random().toString(36).substring(2,8)}.${s}`,i=g.default.join(n,o);return await (0,m.writeFile)(i,a),f.NextResponse.json({url:"/api/upload-wallpaper?file="+o,name:t.name})}catch(e){return console.error("[Wallpaper Upload] Error:",e),f.NextResponse.json({error:"Upload failed on serverless environment"},{status:500})}}e.s(["GET",0,G,"POST",0,E],4390);'
cnt = s.count(old2)
s = s.replace(old2, new2)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print(f"GET handler added ({cnt} match)")
PYEOF

echo ""
echo "=== 4. Patch PDF export (HTML -> real PDF via chrome) ==="
python3 << 'PYEOF'
import io
p = ".next/server/chunks/node_modules_next_dist_esm_build_templates_app-route_1a5o629.js"
with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
# vars
s = s.replace('87578,e=>{"use strict";let t;var r,n,a,s,i',
              '87578,e=>{"use strict";let t;var CP=e.i(555001),FSP=e.i(555002),CHROME="/home/z/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome";var r,n,a,s,i')
# return + conversion
old_ret = '}}return new Q.NextResponse(a,{headers:{"Content-Type":n,"Content-Disposition":`attachment; filename="${r}"`}})'
new_ret = '''}}if("pdf"===o&&"string"==typeof a){let th=`/tmp/cpe_${Date.now()}_${Math.random().toString(36).slice(2,8)}.html`,tp=th.replace(/\\.html$/,".pdf");try{await FSP.writeFile(th,a);CP.execFileSync(CHROME,["--headless","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--no-pdf-header-footer",`--print-to-pdf=${tp}`,th],{timeout:30000,stdio:"ignore"});let pdf=await FSP.readFile(tp);if(pdf&&pdf.length>100){a=Buffer.from(pdf);r=r.replace(/\\.html$/,".pdf");n="application/pdf"}else{console.error("[PDF] empty pdf output")}}catch(e){console.error("[PDF] conversion error:",e.message)}try{await FSP.unlink(th)}catch(e){}try{await FSP.unlink(tp)}catch(e){}}return new Q.NextResponse(a,{headers:{"Content-Type":n,"Content-Disposition":`attachment; filename="${r}"`}})'''
s = s.replace(old_ret, new_ret)
# modules
old_mods = 'sR],87578)}];\n\n'
new_mods = 'sR],87578)},555001,(e,t,r)=>{t.exports=e.x("child_process",()=>require("child_process"))},555002,(e,t,r)=>{t.exports=e.x("fs/promises",()=>require("fs/promises"))}];\n\n'
s = s.replace(old_mods, new_mods)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("PDF export patched")
PYEOF

echo ""
echo "=== 5. Patch client: PWA controllerchange no-op ==="
python3 << 'PYEOF'
import io
p = ".next/static/chunks/1aed-jz3ypll2.js"
with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
old = 'navigator.serviceWorker.addEventListener("controllerchange",()=>{console.log("[PWA] New controller — page reloading"),window.location.reload()})'
new = 'navigator.serviceWorker.addEventListener("controllerchange",()=>{console.log("[PWA] controllerchange — no reload (patched)")})'
s = s.replace(old, new)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("client PWA patched")
PYEOF

echo ""
echo "=== 6. Patch public/sw.js (remove force-reload) ==="
python3 << 'PYEOF'
import io
p = "public/sw.js"
with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
old = '''self.clients.claim();
  // Tell all clients to reload so they get fresh content
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => client.postMessage({ type: 'FORCE_RELOAD' }));
  });'''
new = '''self.clients.claim();
  // Note: force-reload on activate removed — it raced with license activation
  // and wiped sessionStorage writes. Clients refresh naturally on demand.'''
s = s.replace(old, new)
with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("sw.js patched")
PYEOF

echo ""
echo "=== 7. Apply Fintel rebrand ==="
python3 .zscripts/rename-fintel.py 2>&1 | tail -20

echo ""
echo "=== 8. Apply welcome screen design ==="
python3 .zscripts/patch-welcome.py 2>&1 | tail -10

echo ""
echo "=== 9. Replace wallpapers (6 png -> 7 jpg) ==="
python3 << 'PYEOF'
import io
OLD_ARRAY = '["/uploads/wallpapers/wp_1.png","/uploads/wallpapers/wp_2.png","/uploads/wallpapers/wp_3.png","/uploads/wallpapers/wp_4.png","/uploads/wallpapers/wp_5.png","/uploads/wallpapers/wp_6.png"]'
NEW_ARRAY = '["/uploads/wallpapers/wp_1.jpg","/uploads/wallpapers/wp_2.jpg","/uploads/wallpapers/wp_3.jpg","/uploads/wallpapers/wp_4.jpg","/uploads/wallpapers/wp_5.jpg","/uploads/wallpapers/wp_6.jpg","/uploads/wallpapers/wp_7.jpg"]'
for path in ['.next/static/chunks/1aed-jz3ypll2.js', '.next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js']:
    with io.open(path, 'r', encoding='utf-8') as f: s = f.read()
    s = s.replace(OLD_ARRAY, NEW_ARRAY)
    s = s.replace('="/uploads/wallpapers/wp_1.png"', '="/uploads/wallpapers/wp_1.jpg"')
    with io.open(path, 'w', encoding='utf-8') as f: f.write(s)
print("wallpaper arrays patched")
PYEOF

echo ""
echo "=== 10. Fix welcome headline (CAPITAL<br>Fintel -> Fintel) ==="
python3 << 'PYEOF'
import io
for p, J in [('.next/static/chunks/1aed-jz3ypll2.js','u'), ('.next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js','d')]:
    with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
    s = s.replace(f'["CAPITAL",(0,{J}.jsx)("br",{{}}),"Fintel"]', '["Fintel"]')
    # status pill -> direct key input (phase hold->key, remove conditional)
    s = s.replace(f'let t=setTimeout(()=>a("hold"),800)' if J=='u' else 'let b=setTimeout(()=>h("hold"),800)',
                  f'let t=setTimeout(()=>a("key"),800)' if J=='u' else 'let b=setTimeout(()=>h("key"),800)')
    with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
print("headline + phase patched")
PYEOF

echo ""
echo "=== 11. Replace status-pill with direct key input ==="
python3 << 'PYEOF'
import io

# CLIENT
p1 = '.next/static/chunks/1aed-jz3ypll2.js'
with io.open(p1, 'r', encoding='utf-8') as f: s = f.read()
old = '(0,u.jsxs)("div",{className:"actions",children:[\n(0,u.jsx)("div",{className:"status-pill",children:"success"===s?"ACCESS GRANTED":"loading"===s?"Validating…":"Enter Licence Key…"}),\n"key"===i?(0,u.jsxs)("div",{className:"cpe-ws-keybox",onClick:function(e){e.stopPropagation()},children:[\n(0,u.jsx)("input",{ref:y,type:"text",value:o,onChange:function(e){l(e.target.value.toUpperCase()),c("idle"),f("")},onKeyDown:j,placeholder:"XXXX-XXXX-XXXX-XXXX",disabled:"loading"===s||"success"===s,className:"cpe-ws-input"}),\np?(0,u.jsx)("p",{className:"cpe-ws-err",children:p}):null,\n(0,u.jsx)("button",{onClick:b,disabled:"loading"===s||"success"===s||!o.trim(),className:"activate-btn",children:"loading"===s?"Validating…":"success"===s?"Access Granted":"Activate"})\n]}):(0,u.jsx)("button",{className:"activate-btn",onClick:function(){a("key")},children:"Activate"}),\n(0,u.jsxs)("p",{className:"terms",children:["By continuing you ",(0,u.jsx)("a",{href:"#",onClick:function(e){e.preventDefault(),m(!0)},children:"agree to the Terms & conditions"})]})\n]})'
new = '(0,u.jsxs)("div",{className:"actions",children:[\n(0,u.jsxs)("div",{className:"cpe-ws-keybox",onClick:function(e){e.stopPropagation()},children:[\n(0,u.jsx)("label",{style:{fontFamily:"\'Space Grotesk\',sans-serif",fontSize:".72rem",letterSpacing:".18em",textTransform:"uppercase",color:"rgba(201,174,247,0.85)",marginBottom:".3rem",alignSelf:"flex-start"},children:"Enter Licence Key"}),\n(0,u.jsx)("input",{ref:y,type:"text",value:o,onChange:function(e){l(e.target.value.toUpperCase()),c("idle"),f("")},onKeyDown:j,placeholder:"XXXX-XXXX-XXXX-XXXX",disabled:"loading"===s||"success"===s,className:"cpe-ws-input",autoFocus:!0}),\np?(0,u.jsx)("p",{className:"cpe-ws-err",children:p}):null,\n(0,u.jsx)("button",{onClick:b,disabled:"loading"===s||"success"===s||!o.trim(),className:"activate-btn",children:"loading"===s?"Validating…":"success"===s?"Access Granted":"Activate"})\n]}),\n(0,u.jsxs)("p",{className:"terms",children:["By continuing you ",(0,u.jsx)("a",{href:"#",onClick:function(e){e.preventDefault(),m(!0)},children:"agree to the Terms & conditions"})]})\n]})'
cnt = s.count(old)
s = s.replace(old, new)
with io.open(p1, 'w', encoding='utf-8') as f: f.write(s)
print(f"client: {cnt} actions block patched")

# SSR
p2 = '.next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js'
with io.open(p2, 'r', encoding='utf-8') as f: s = f.read()
old2 = '(0,d.jsxs)("div",{className:"actions",children:[\n(0,d.jsx)("div",{className:"status-pill",children:"success"===l?"ACCESS GRANTED":"loading"===l?"Validating…":"Enter Licence Key…"}),\n"key"===g?(0,d.jsxs)("div",{className:"cpe-ws-keybox",onClick:function(e){e.stopPropagation()},children:[\n(0,d.jsx)("input",{ref:r,type:"text",value:i,onChange:function(e){k(e.target.value.toUpperCase()),m("idle"),o("")},onKeyDown:w,placeholder:"XXXX-XXXX-XXXX-XXXX",disabled:"loading"===l||"success"===l,className:"cpe-ws-input"}),\nn?(0,d.jsx)("p",{className:"cpe-ws-err",children:n}):null,\n(0,d.jsx)("button",{onClick:t,disabled:"loading"===l||"success"===l||!i.trim(),className:"activate-btn",children:"loading"===l?"Validating…":"success"===l?"Access Granted":"Activate"})\n]}):(0,d.jsx)("button",{className:"activate-btn",onClick:function(){h("key")},children:"Activate"}),\n(0,d.jsxs)("p",{className:"terms",children:["By continuing you ",(0,d.jsx)("a",{href:"#",onClick:function(e){e.preventDefault(),q(!0)},children:"agree to the Terms & conditions"})]})\n]})'
new2 = '(0,d.jsxs)("div",{className:"actions",children:[\n(0,d.jsxs)("div",{className:"cpe-ws-keybox",onClick:function(e){e.stopPropagation()},children:[\n(0,d.jsx)("label",{style:{fontFamily:"\'Space Grotesk\',sans-serif",fontSize:".72rem",letterSpacing:".18em",textTransform:"uppercase",color:"rgba(201,174,247,0.85)",marginBottom:".3rem",alignSelf:"flex-start"},children:"Enter Licence Key"}),\n(0,d.jsx)("input",{ref:r,type:"text",value:i,onChange:function(e){k(e.target.value.toUpperCase()),m("idle"),o("")},onKeyDown:w,placeholder:"XXXX-XXXX-XXXX-XXXX",disabled:"loading"===l||"success"===l,className:"cpe-ws-input",autoFocus:!0}),\nn?(0,d.jsx)("p",{className:"cpe-ws-err",children:n}):null,\n(0,d.jsx)("button",{onClick:t,disabled:"loading"===l||"success"===l||!i.trim(),className:"activate-btn",children:"loading"===l?"Validating…":"success"===l?"Access Granted":"Activate"})\n]}),\n(0,d.jsxs)("p",{className:"terms",children:["By continuing you ",(0,d.jsx)("a",{href:"#",onClick:function(e){e.preventDefault(),q(!0)},children:"agree to the Terms & conditions"})]})\n]})'
cnt2 = s.count(old2)
s = s.replace(old2, new2)
with io.open(p2, 'w', encoding='utf-8') as f: f.write(s)
print(f"SSR: {cnt2} actions block patched")
PYEOF

echo ""
echo "=== 12. Patch RSC segments + HTML (Fintel name) ==="
python3 << 'PYEOF'
import io, os, re
files = [
    '.next/server/app/index.segments/_full.segment.rsc',
    '.next/server/app/index.segments/_head.segment.rsc',
    '.next/server/app/index.html',
    '.next/server/app/_not-found.segments/_full.segment.rsc',
    '.next/server/app/_not-found.segments/_head.segment.rsc',
    '.next/server/app/_not-found.rsc',
    '.next/server/app/_not-found.html',
    '.next/server/app/index.rsc',
    '.next/server/pages/404.html',
    '.next/server/app/_global-error.html',
]
for p in files:
    if not os.path.exists(p): continue
    with io.open(p, 'r', encoding='utf-8') as f: s = f.read()
    orig = s
    s = s.replace('Capital Precision Engine', 'Fintel')
    s = s.replace('Capital Auditor Engine', 'Fintel')
    s = s.replace('(CPE)', '')
    s = re.sub(r'\bCPE\b', 'Fintel', s)
    if s != orig:
        with io.open(p, 'w', encoding='utf-8') as f: f.write(s)
        print(f"patched: {p}")
PYEOF

echo ""
echo "=== 13. Update manifest.json ==="
python3 << 'PYEOF'
import io, json
p = 'public/manifest.json'
with io.open(p, 'r', encoding='utf-8') as f: d = json.load(f)
d['name'] = 'Fintel'
d['short_name'] = 'Fintel'
if 'description' in d:
    d['description'] = d['description'].replace('Capital Precision Engine', 'Fintel').replace('CPE', 'Fintel')
with io.open(p, 'w', encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)
print("manifest updated")
PYEOF

echo ""
echo "=== 14. Syntax check ==="
node --check .next/static/chunks/1aed-jz3ypll2.js 2>&1 && echo "CLIENT OK" || echo "CLIENT FAIL"

echo ""
echo "=== 15. Ensure wallpapers exist ==="
ls -la public/uploads/wallpapers/wp_[1-7].jpg 2>/dev/null | wc -l

echo ""
echo "=== 16. Update package.json dev script ==="
python3 << 'PYEOF'
import io, json
p = 'package.json'
with io.open(p, 'r', encoding='utf-8') as f: d = json.load(f)
d['scripts']['dev'] = 'node server.js'
with io.open(p, 'w', encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)
print("package.json dev script: node server.js")
PYEOF

echo ""
echo "=== 17. Start server ==="
> dev.log
( setsid bash -c 'cd /home/z/my-project && PORT=3000 HOSTNAME=0.0.0.0 exec node server.js' </dev/null >/home/z/my-project/dev.log 2>&1 & ) 2>/dev/null
sleep 7
ss -ltn 2>/dev/null | grep :3000 && echo "PORT 3000 LISTENING" || echo "PORT NOT LISTENING"
curl -s --max-time 6 -o /dev/null -w "home HTTP %{http_code}\n" http://127.0.0.1:3000/
cat dev.log

echo ""
echo "=== 18. Verify key ==="
curl -s --max-time 5 -X POST http://127.0.0.1:3000/api/validate-key -H "Content-Type: application/json" -d '{"key":"FINTEL-X7K9-M2P4-Q8W3"}'
