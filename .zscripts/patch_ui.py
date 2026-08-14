#!/usr/bin/env python3
"""
patch_ui.py — Applies UI patches to both client and SSR chunks.

Patches applied:
  1. Remove Production Build section (Settings)
  2. Add engine selector dropdown (replaces horizontal tab list)
  3. Update Export to individual format (client only)
  4. Disable service worker registration
  5. Welcome patches (SSR only — client already patched)

Target files:
  - .next/static/chunks/1aed-jz3ypll2.js (CLIENT)
  - .next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js (SSR)
"""
import io
import os
import re
import subprocess

CLIENT = ".next/static/chunks/1aed-jz3ypll2.js"
SSR = ".next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js"


# ====================================================================
# 1. Remove Production Build section (flexible: works for both client & SSR)
# ====================================================================

def remove_production_build(s, label):
    """Remove the Production Build section from settings.
    Works for both client (u.jsx) and SSR (d.jsx) chunks."""
    pb_idx = s.find('"Production Build"')
    if pb_idx == -1:
        print(f"  [{label}] Production Build not found")
        return s, False

    # Find the emerald badge preceding Production Build
    back_text = s[max(0, pb_idx - 600):pb_idx]
    m = re.search(r'\(0,\w\.jsx\)\(\w+,\{variant:"badge",color:"emerald"', back_text)
    if not m:
        print(f"  [{label}] emerald badge not found before Production Build")
        return s, False
    badge_pos = max(0, pb_idx - 600) + m.start()

    # Walk backward from badge to find the section's opening `,(0,?.jsxs)("div",{children:[(0,?.jsxs)("p"`
    back2 = s[max(0, badge_pos - 1500):badge_pos]
    section_starts = list(re.finditer(r',\(0,\w\.jsxs\)\("div",\{children:\[\(0,\w\.jsxs\)\("p"', back2))
    if not section_starts:
        # Try without leading comma (first element case)
        section_starts = list(re.finditer(r'\(0,\w\.jsxs\)\("div",\{children:\[\(0,\w\.jsxs\)\("p"', back2))
        if not section_starts:
            print(f"  [{label}] section start pattern not found")
            return s, False
    last_start = section_starts[-1]
    section_start = max(0, badge_pos - 1500) + last_start.start()

    # Find the end: next section's start after pb_idx
    forward_text = s[pb_idx + 100:pb_idx + 6000]
    next_matches = list(re.finditer(r',\(0,\w\.jsxs\)\("div",\{children:\[\(0,\w\.jsxs\)\("p"', forward_text))
    if not next_matches:
        print(f"  [{label}] next section not found after Production Build")
        return s, False
    next_match = next_matches[0]
    section_end = pb_idx + 100 + next_match.start()

    removed = s[section_start:section_end]
    s = s[:section_start] + s[section_end:]
    print(f"  [{label}] Removed Production Build section ({len(removed)} chars)")
    return s, True


# ====================================================================
# 2. Add engine selector dropdown
# ====================================================================

ENGINE_SELECTOR_CLIENT = '''function bQ_EngineSelector({tabs:t,activeTab:r,onSelect:n}){let[o,l]=(0,d.useState)(!1),s=(0,d.useRef)(null);(0,d.useEffect)(()=>{function e(t){s.current&&!s.current.contains(t.target)&&l(!1)}return document.addEventListener("mousedown",e),()=>document.removeEventListener("mousedown",e)},[]);let i=t.find(e=>e[0]===r);return(0,u.jsxs)("div",{ref:s,className:"relative shrink-0",children:[(0,u.jsxs)("button",{onClick:()=>l(!o),className:"flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.06] hover:bg-white/[0.08] transition cursor-pointer",children:[(0,u.jsx)("svg",{className:"w-3.5 h-3.5 text-white/60",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",d:"M4 6h16M4 12h16M4 18h16"})}),(0,u.jsx)("span",{className:"text-[11px] font-semibold text-white/80",children:i?i[1]:"Select Engine"}),(0,u.jsx)("svg",{className:"w-3 h-3 text-white/40 transition-transform "+(o?"rotate-180":""),fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2.5",d:"M19 9l-7 7-7-7"})})]}),o&&(0,u.jsx)("div",{className:"absolute top-full left-0 mt-1 max-h-80 overflow-y-auto bg-[#0a0512] border border-white/[0.08] rounded-lg shadow-2xl z-50 min-w-[180px] cosmic-scrollbar",children:t.map(e=>(0,u.jsx)("button",{onClick:()=>{n(e[0]),l(!1)},className:`block w-full text-left px-3 py-2 text-[11px] font-medium transition ${r===e[0]?"bg-blue-500/10 text-blue-300":"text-white/60 hover:bg-white/[0.04]"}`,children:e[1]},e[0]))})]})}'''

ENGINE_SELECTOR_SSR = '''function bQ_EngineSelector({tabs:t,activeTab:r,onSelect:n}){let[o,l]=(0,e.useState)(!1),s=(0,e.useRef)(null);(0,e.useEffect)(()=>{function i(t){s.current&&!s.current.contains(t.target)&&l(!1)}return document.addEventListener("mousedown",i),()=>document.removeEventListener("mousedown",i)},[]);let a=t.find(e=>e[0]===r);return(0,d.jsxs)("div",{ref:s,className:"relative shrink-0",children:[(0,d.jsxs)("button",{onClick:()=>l(!o),className:"flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.06] hover:bg-white/[0.08] transition cursor-pointer",children:[(0,d.jsx)("svg",{className:"w-3.5 h-3.5 text-white/60",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:(0,d.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",d:"M4 6h16M4 12h16M4 18h16"})}),(0,d.jsx)("span",{className:"text-[11px] font-semibold text-white/80",children:a?a[1]:"Select Engine"}),(0,d.jsx)("svg",{className:"w-3 h-3 text-white/40 transition-transform "+(o?"rotate-180":""),fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",children:(0,d.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2.5",d:"M19 9l-7 7-7-7"})})]}),o&&(0,d.jsx)("div",{className:"absolute top-full left-0 mt-1 max-h-80 overflow-y-auto bg-[#0a0512] border border-white/[0.08] rounded-lg shadow-2xl z-50 min-w-[180px] cosmic-scrollbar",children:t.map(e=>(0,d.jsx)("button",{onClick:()=>{n(e[0]),l(!1)},className:`block w-full text-left px-3 py-2 text-[11px] font-medium transition ${r===e[0]?"bg-blue-500/10 text-blue-300":"text-white/60 hover:bg-white/[0.04]"}`,children:e[1]},e[0]))})]})}'''


def add_engine_selector(s, label, J, setActive_var, engine_selector_fn, active_var):
    """Replace the horizontal tab list with a dropdown.

    J: 'u' for client, 'd' for SSR
    setActive_var: 'E' for client, 'D' for SSR
    active_var: 'A' for client, 'C' for SSR
    """
    # Find tab list start
    tab_list_start = '[["round","Priced Round"]'
    if tab_list_start not in s:
        print(f"  [{label}] tab list start not found")
        return s, False
    t_idx = s.find(tab_list_start)

    # Find end of tab list: pattern is `},KEY))` where KEY is the map's key var (e for client, a for SSR)
    end_match = re.search(r'\},(\w)\)\)', s[t_idx:])
    if not end_match:
        print(f"  [{label}] tab list end not found")
        return s, False
    e_idx = t_idx + end_match.end()

    # Extract tab list array (everything before .map()
    tab_list_text = s[t_idx:e_idx]
    map_idx = tab_list_text.find('.map(')
    if map_idx == -1:
        print(f"  [{label}] .map( not found in tab list")
        return s, False
    tabs_array = tab_list_text[:map_idx]

    # Replace .map(...) with EngineSelector jsx
    replacement = '(0,' + J + '.jsx)(bQ_EngineSelector,{tabs:' + tabs_array + ',activeTab:' + active_var + ',onSelect:' + setActive_var + '})'
    s = s[:t_idx] + replacement + s[e_idx:]
    print(f"  [{label}] Replaced tab list .map with EngineSelector dropdown")

    # Insert EngineSelector function definition
    if J == 'u':
        anchor = 'function bR('
    else:
        anchor = 't4.displayName="CartesianGrid";'
    if anchor in s:
        s = s.replace(anchor, engine_selector_fn + ';' + anchor, 1)
        print(f"  [{label}] Inserted EngineSelector function definition")
    else:
        # Fallback: insert after "use strict"
        us = s.find('"use strict"')
        if us > 0:
            us_end = s.find(';', us)
            if us_end > 0:
                s = s[:us_end + 1] + engine_selector_fn + ';' + s[us_end + 1:]
                print(f"  [{label}] Inserted EngineSelector after 'use strict'")

    return s, True


# ====================================================================
# 3. Update Export to individual format (client only)
# ====================================================================

def update_export_individual(s):
    """Update the export button to send individual format."""
    old = 'type:"combined",format:e,dilutionData:n,safes:[],currency:i'
    if old not in s:
        print("  [CLIENT] combined export anchor not found")
        return s, False
    new = ('type:"individual",engine:(function(){var m={"round":"Priced Round","safes":"SAFE Radar","waterfall":"Waterfall","vesting":"Vesting","antidilution":"Anti-Dilution","termsheet":"Term Scanner","saas":"SaaS Econ","platform":"Platform Val","ai-monetize":"AI Monetize","tech-tco":"Tech TCO","pmf":"PMF Nav","war-game":"War Gaming","payments":"Payments","neobank":"Neobank","defi-risk":"DeFi Risk","compliance":"Compliance","lending":"Lending","wallet":"Wallet","supply-chain":"Supply Chain","freight":"Freight","inventory":"Inventory","sc-risk":"SC Risk","warehouse":"Warehouse","ops":"Ops"};return m[A]||A})(),format:e,resultHtml:(function(){var el=document.querySelector(".glass-panel-cosmic");return el?el.innerText:""})(),inputs:(function(){var ins=document.querySelectorAll(".glass-panel-cosmic input[type=number]");var arr=[];ins.forEach(function(inp){var lbl=inp.previousElementSibling;var label=lbl&&lbl.tagName==="LABEL"?lbl.innerText:(inp.placeholder||"input");arr.push({label:label,value:inp.value})});return arr})(),currency:i')
    s = s.replace(old, new)
    print("  [CLIENT] Updated export to individual format")
    return s, True


# ====================================================================
# 4. Disable service worker registration
# ====================================================================

def disable_service_worker(s, label):
    old = 'navigator.serviceWorker.register("/sw.js",{updateViaCache:"none"})'
    new = 'false&&null'
    if old not in s:
        print(f"  [{label}] serviceWorker.register not found")
        return s, False
    s = s.replace(old, new)
    print(f"  [{label}] Disabled service worker registration")
    return s, True


# ====================================================================
# 5. Welcome patches (SSR only)
# ====================================================================

def apply_welcome_patches_ssr(s):
    changes = 0
    if '"welcome.headline":"PRECISION ENGINE"' in s:
        s = s.replace('"welcome.headline":"PRECISION ENGINE"', '"welcome.headline":"Fintel"')
        changes += 1
        print("  [SSR] Patched welcome.headline: PRECISION ENGINE -> Fintel")
    s_before = s
    s = s.replace('"PRECISION ENGINE"', '"Fintel"')
    if s != s_before:
        changes += 1
        print("  [SSR] Patched standalone PRECISION ENGINE strings")
    if 'setTimeout(()=>h("hold"),800)' in s:
        s = s.replace('setTimeout(()=>h("hold"),800)', 'setTimeout(()=>h("key"),800)')
        changes += 1
        print("  [SSR] Patched setTimeout: hold -> key")
    old_pwa = 'controllerchange",()=>{console.log("[PWA] New controller — page reloading"),window.location.reload()})'
    new_pwa = 'controllerchange",()=>{console.log("[PWA] controllerchange — no reload (patched)")})'
    if old_pwa in s:
        s = s.replace(old_pwa, new_pwa)
        changes += 1
        print("  [SSR] Patched PWA controllerchange: no reload")
    return s, changes > 0


def verify_syntax(path, label):
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  [{label}] SYNTAX OK (node --check)")
        return True
    print(f"  [{label}] SYNTAX ERROR:")
    err = r.stderr
    print(err[-800:] if len(err) > 800 else err)
    return False


def main():
    os.chdir("/home/z/my-project")

    # ========= CLIENT =========
    print("=== patch_ui.py: CLIENT chunk ===")
    with io.open(CLIENT, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    needs_pb = ('"Production Build"' in s)
    needs_es = ('bQ_EngineSelector' not in s)
    needs_exp = ('type:"combined",format:e,dilutionData:n' in s)
    needs_sw = ('navigator.serviceWorker.register("/sw.js"' in s)

    print("\n--- Step 1: Remove Production Build section ---")
    if needs_pb:
        s, _ = remove_production_build(s, "CLIENT")
    else:
        print("  [CLIENT] Already removed")

    print("\n--- Step 2: Add engine selector dropdown ---")
    if needs_es:
        s, _ = add_engine_selector(s, "CLIENT", "u", "E", ENGINE_SELECTOR_CLIENT, "A")
    else:
        print("  [CLIENT] Engine selector already added")

    print("\n--- Step 3: Update export to individual ---")
    if needs_exp:
        s, _ = update_export_individual(s)
    else:
        print("  [CLIENT] Export already updated")

    print("\n--- Step 4: Disable service worker ---")
    if needs_sw:
        s, _ = disable_service_worker(s, "CLIENT")
    else:
        print("  [CLIENT] Service worker already disabled")

    with io.open(CLIENT, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + CLIENT + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")
    verify_syntax(CLIENT, "CLIENT")

    # ========= SSR =========
    print("\n\n=== patch_ui.py: SSR chunk ===")
    with io.open(SSR, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    needs_pb_s = ('"Production Build"' in s)
    needs_es_s = ('bQ_EngineSelector' not in s)
    needs_sw_s = ('navigator.serviceWorker.register("/sw.js"' in s)
    needs_welcome_s = ('"welcome.headline":"PRECISION ENGINE"' in s or
                       'setTimeout(()=>h("hold"),800)' in s or
                       '[PWA] New controller' in s)

    print("\n--- Step 1: Remove Production Build section ---")
    if needs_pb_s:
        s, _ = remove_production_build(s, "SSR")
    else:
        print("  [SSR] Already removed")

    print("\n--- Step 2: Add engine selector dropdown ---")
    if needs_es_s:
        s, _ = add_engine_selector(s, "SSR", "d", "D", ENGINE_SELECTOR_SSR, "C")
    else:
        print("  [SSR] Engine selector already added")

    print("\n--- Step 3: Disable service worker ---")
    if needs_sw_s:
        s, _ = disable_service_worker(s, "SSR")
    else:
        print("  [SSR] Service worker already disabled")

    print("\n--- Step 4: Apply welcome patches ---")
    if needs_welcome_s:
        s, _ = apply_welcome_patches_ssr(s)
    else:
        print("  [SSR] Welcome patches already applied")

    with io.open(SSR, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + SSR + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")
    verify_syntax(SSR, "SSR")


if __name__ == "__main__":
    main()
