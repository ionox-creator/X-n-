#!/usr/bin/env python3
"""
add_chat_features.py — Adds chat features to the client chunk.

Target: .next/static/chunks/1aed-jz3ypll2.js

Features added:
  1. Per-message Copy button on AI (assistant) responses
  2. Copy All button in chat header
  3. Share button in chat header

Event handling uses ev.currentTarget pattern:
  - Label changes to "Copied!" FIRST (before copy logic)
  - Then navigator.clipboard.writeText
  - Reset label after 1500ms timeout
"""
import io
import os
import subprocess

CLIENT = ".next/static/chunks/1aed-jz3ypll2.js"


def add_header_buttons(s):
    """Add Copy All and Share buttons to chat header."""
    # Current header ends with:
    # (0,u.jsx)("span",{className:"text-[10px] font-semibold text-white/25 font-mono",children:"Precision: 0.2t"})]})
    old = '(0,u.jsx)("span",{className:"text-[10px] font-semibold text-white/25 font-mono",children:"Precision: 0.2t"})]})'
    if old not in s:
        print("  WARNING: header span anchor not found")
        return s, False
    # Build new header with Copy All + Share buttons
    # The 'e' variable here refers to the messages array (outer scope of b1 component)
    copy_all_btn = (
        '(0,u.jsx)("button",{onClick:function(ev){'
        'var allText=e.filter(function(m){return m.role==="assistant"&&m.content}).map(function(m){return m.content}).join("\\n\\n---\\n\\n");'
        'ev.currentTarget.innerText="Copied!";'
        'setTimeout(function(){ev.currentTarget.innerText="Copy All"},1500);'
        'navigator.clipboard.writeText(allText)},'
        'className:"text-[10px] text-white/40 hover:text-white/70 transition px-2 py-1 rounded border border-white/[0.06] hover:border-white/[0.12]",children:"Copy All"})'
    )
    share_btn = (
        '(0,u.jsx)("button",{onClick:function(ev){'
        'var shareText=e.map(function(m){return (m.role==="user"?"You: ":"Fintel: ")+(typeof m.content==="string"?m.content:"")}).join("\\n\\n");'
        'if(navigator.share){navigator.share({title:"Fintel Chat",text:shareText}).catch(function(){})}else{'
        'ev.currentTarget.innerText="Copied!";'
        'setTimeout(function(){ev.currentTarget.innerText="Share"},1500);'
        'navigator.clipboard.writeText(shareText)}},'
        'className:"text-[10px] text-white/40 hover:text-white/70 transition px-2 py-1 rounded border border-white/[0.06] hover:border-white/[0.12]",children:"Share"})'
    )
    # Wrap in a div with the precision span and the two buttons
    new = (
        '(0,u.jsxs)("div",{className:"flex items-center gap-2",children:['
        '(0,u.jsx)("span",{className:"text-[10px] font-semibold text-white/25 font-mono",children:"Precision: 0.2t"}),'
        + copy_all_btn + ',' + share_btn +
        ']})]})'
    )
    s = s.replace(old, new)
    print("  Added Copy All + Share buttons to chat header")
    return s, True


def add_per_message_copy(s):
    """Add a Copy button to each AI (assistant) message."""
    # Anchor: the assistant content div ends with:
    # :(0,u.jsx)("div",{className:"markdown-body",children:(0,u.jsx)(b0,{content:e.content})})}),!a&&o.length>0&&
    old = ':(0,u.jsx)("div",{className:"markdown-body",children:(0,u.jsx)(b0,{content:e.content})})}),!a&&o.length>0&&'
    if old not in s:
        print("  WARNING: assistant message anchor not found")
        return s, False
    # Insert Copy button between content div and citations
    # Inside the map callback, 'e' is the message, 'e.content' is its content
    copy_btn = (
        ',!a&&(0,u.jsx)("button",{onClick:function(ev){'
        'var txt=typeof e.content==="string"?e.content:"";'
        'ev.currentTarget.innerText="Copied!";'
        'setTimeout(function(){ev.currentTarget.innerText="Copy"},1500);'
        'navigator.clipboard.writeText(txt)},'
        'className:"self-start text-[10px] text-white/30 hover:text-white/60 transition px-2 py-0.5",children:"Copy"})'
    )
    # Insert the Copy button right after the content div close, before citations
    new = ':(0,u.jsx)("div",{className:"markdown-body",children:(0,u.jsx)(b0,{content:e.content})})})' + copy_btn + ',!a&&o.length>0&&'
    s = s.replace(old, new)
    print("  Added per-message Copy button on AI responses")
    return s, True


def main():
    os.chdir("/home/z/my-project")
    print("=== add_chat_features.py ===")
    with io.open(CLIENT, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    # IDEMPOTENCY CHECK
    if 'Copy All' in s:
        print("  CHAT FEATURES ALREADY APPLIED — skipping")
        return

    print("\n--- Step 1: Add Copy All + Share to chat header ---")
    s, ok1 = add_header_buttons(s)

    print("\n--- Step 2: Add per-message Copy button ---")
    s, ok2 = add_per_message_copy(s)

    with io.open(CLIENT, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + CLIENT + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")

    print("\n--- Syntax verification ---")
    r = subprocess.run(["node", "--check", CLIENT], capture_output=True, text=True)
    if r.returncode == 0:
        print("  SYNTAX OK (node --check)")
    else:
        print("  SYNTAX ERROR:")
        err = r.stderr
        print(err[-800:] if len(err) > 800 else err)


if __name__ == "__main__":
    main()
