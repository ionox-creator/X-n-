#!/usr/bin/env python3
"""
add_engines_ssr.py — Adds 18 calculator engines to the SSR chunk and applies
the SAFE mixing fix. Idempotent: skips if already applied.

Target: .next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js
  - Uses d.jsx instead of u.jsx
  - Uses variable C (active tab) instead of A
  - Uses function D (tab setter) instead of E
  - Engine components: o3 (waterfall), t6 (vesting), tz (antidilution), tu (termsheet)
  - t4.displayName instead of bI.displayName
"""
import io
import os
import sys
import subprocess

# Path with escaped brackets
SSR = ".next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js"

# Import engine specs from add_all_engines
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_all_engines import ENGINES, INPUT_CLASS, LABEL_CLASS, BTN_CLASS, RESULT_CLASS


def build_engine_jsx_ssr(engine, idx):
    """Build JSX for one engine using d.jsx (SSR)."""
    key, label, title, inputs, calc_js = engine
    rid = "r" + str(idx)
    J = "d"
    parts = []
    parts.append(
        '(0,' + J + '.jsx)("div",{className:"p-4 space-y-3",children:['
    )
    parts.append(
        '(0,' + J + '.jsx)("h3",{className:"text-[11px] font-bold text-white/30 uppercase tracking-wider",children:"' + title + '"}),'
    )
    parts.append('(' + J + '.jsxs)("div",{className:"space-y-2",children:[')
    input_divs = []
    for lbl, ph in inputs:
        input_divs.append(
            '(0,' + J + '.jsxs)("div",{children:['
            '(0,' + J + '.jsx)("label",{className:"' + LABEL_CLASS + '",children:"' + lbl + '"}),'
            '(0,' + J + '.jsx)("input",{type:"number",placeholder:"' + str(ph) + '",className:"' + INPUT_CLASS + '"})'
            ']})'
        )
    parts.append(",".join(input_divs))
    parts.append("]}),")
    onclick = (
        "function(){var inp=document.getElementById('" + rid + "').parentNode.querySelectorAll('input[type=number]');"
        "var v=Array.from(inp).map(function(x){return parseFloat(x.value)||0});"
        + calc_js + ";"
        "document.getElementById('" + rid + "').innerHTML=html;}"
    )
    parts.append(
        '(0,' + J + '.jsx)("button",{onClick:' + onclick + ',className:"' + BTN_CLASS + '",children:"Calculate"}),'
    )
    parts.append(
        '(0,' + J + '.jsx)("div",{id:"' + rid + '",className:"' + RESULT_CLASS + '"})'
    )
    parts.append("]})")
    return "".join(parts)


def update_tab_list_ssr(s):
    """Add 18 new tabs to the SSR tab list."""
    old = '[["round","Priced Round"],["safes","SAFE Radar"],["waterfall","Waterfall"],["vesting","Vesting"],["antidilution","Anti-Dilution"],["termsheet","Term Scanner"]]'
    if old not in s:
        print("  WARNING: SSR tab list not found")
        return s, False
    new_entries = ','.join('["' + e[0] + '","' + e[1] + '"]' for e in ENGINES)
    new = old[:-1] + ',' + new_entries + ']'
    s = s.replace(old, new)
    print("  SSR tab list updated with 18 new tabs")
    return s, True


def add_engines_to_chain_ssr(s):
    """Add 18 engine conditions to SSR conditional chain."""
    # Convert termsheet && to ?
    ts_old = '"termsheet"===C&&(0,d.jsx)(tu,{})'
    ts_new = '"termsheet"===C?(0,d.jsx)(tu,{})'
    if ts_old in s:
        s = s.replace(ts_old, ts_new)
        print("  Converted SSR termsheet && to ?")
    elif ts_new not in s:
        print("  WARNING: SSR termsheet conditional not found")
        return s, False

    # Build chain
    chain = ""
    for i, eng in enumerate(ENGINES):
        is_last = (i == len(ENGINES) - 1)
        key = eng[0]
        op = "&&" if is_last else "?"
        jsx = build_engine_jsx_ssr(eng, i + 1)
        chain += ":" + '"' + key + '"===C' + op + jsx

    # Insert chain after termsheet content, before ]})}t4.displayName
    anchor = '(0,d.jsx)(tu,{})]})}t4.displayName'
    if anchor not in s:
        print("  WARNING: SSR termsheet end anchor not found")
        return s, False
    s = s.replace(anchor, '(0,d.jsx)(tu,{})' + chain + ']})}t4.displayName')
    print("  Inserted 18 engine conditions into SSR chain")
    return s, True


def apply_safe_fix_ssr(s):
    """Apply SAFE mixing fix to SSR chunk."""
    # Step 1: Insert "safes"===C? between round else-colon and SAFE_NOTES
    safe_marker = 'children:"Configure Dilution Matrix"'
    safe_idx = s.find(safe_marker)
    if safe_idx == -1:
        print("  WARNING: SSR SAFE marker not found")
        return s, False
    k = safe_idx
    found = -1
    while k > 0:
        if s[k:k+3] == '):(':
            found = k
            break
        k -= 1
    if found == -1:
        print("  WARNING: SSR round else-colon not found")
        return s, False
    insert_pos = found + 2
    s = s[:insert_pos] + '"safes"===C?' + s[insert_pos:]
    print("  Inserted \"safes\"===C? before SSR SAFE_NOTES at pos " + str(insert_pos))

    # Step 2: Convert comma chain to ternary chain
    reps = [
        ('),"waterfall"===C&&', '):"waterfall"===C?'),
        (',"vesting"===C&&', ':"vesting"===C?'),
        (',"antidilution"===C&&', ':"antidilution"===C?'),
        (',"termsheet"===C&&', ':"termsheet"===C?'),
        (',"termsheet"===C?', ':"termsheet"===C?'),
        ('"termsheet"===C&&', '"termsheet"===C?'),
    ]
    for old, new in reps:
        cnt = s.count(old)
        if cnt:
            s = s.replace(old, new)
            print("  Replaced: " + repr(old) + " -> " + repr(new) + " (" + str(cnt) + "x)")
    return s, True


def verify_syntax(path):
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if r.returncode == 0:
        print("  SYNTAX OK (node --check)")
        return True
    print("  SYNTAX ERROR:")
    # Show just the last few lines (error summary)
    err = r.stderr
    print(err[-500:] if len(err) > 500 else err)
    return False


def main():
    os.chdir("/home/z/my-project")
    print("=== add_engines_ssr.py (SSR chunk) ===")
    with io.open(SSR, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    # IDEMPOTENCY CHECK
    if '["saas","SaaS Econ"]' in s:
        print("  ENGINES ALREADY APPLIED — skipping")
        verify_syntax(SSR)
        return

    print("\n--- Step 1: Update SSR tab list ---")
    s, ok1 = update_tab_list_ssr(s)

    print("\n--- Step 2: Add 18 engines to SSR conditional chain ---")
    s, ok2 = add_engines_to_chain_ssr(s)

    print("\n--- Step 3: Apply SSR SAFE mixing fix ---")
    s, ok3 = apply_safe_fix_ssr(s)

    with io.open(SSR, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + SSR + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")

    print("\n--- Syntax verification ---")
    verify_syntax(SSR)


if __name__ == "__main__":
    main()
