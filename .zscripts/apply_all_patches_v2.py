#!/usr/bin/env python3
"""
apply_all_patches_v2.py — Apply ALL 8 patches to the Fintel client chunk.

Target: .next/static/chunks/1aed-jz3ypll2.js

Patches:
  1. Add 18 calculator engines + SAFE mixing fix
  2. Add engine selector dropdown (solid black bg)
  3. Add individual export
  4. Add chat features (icon-only Copy All + Share, per-message Copy)
  5. Remove Documentation link from Settings
  6. Remove Production Build section
  7. Improve calculator UI (professional, not boring)
  8. Disable service worker registration

Idempotent: each step checks if patch already applied and skips.
"""
import io
import os
import re
import subprocess
import sys

CLIENT = ".next/static/chunks/1aed-jz3ypll2.js"

# Existing 6 tabs
EXISTING_TABS = [
    ("round", "Priced Round"),
    ("safes", "SAFE Radar"),
    ("waterfall", "Waterfall"),
    ("vesting", "Vesting"),
    ("antidilution", "Anti-Dilution"),
    ("termsheet", "Term Scanner"),
]

# 18 new engines
ENGINES = [
    ("saas", "SaaS Econ", "SaaS Economics",
     [("Current ARR ($)", "1000000"), ("Annual Growth (%)", "50"),
      ("Churn (%)", "5"), ("Gross Margin (%)", "80")],
     "var arr=v[0];var g=v[1]/100;var ch=v[2]/100;var gm=v[3]/100;"
     "var y1=arr*(1+g-ch);var y5=arr*Math.pow(1+g-ch,5);var gp=y5*gm;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Year 1 ARR: <b>$'+Math.round(y1).toLocaleString()+'</b></div>'"
     "+'<div>Year 5 ARR: <b>$'+Math.round(y5).toLocaleString()+'</b></div>'"
     "+'<div>5yr Gross Profit: <b>$'+Math.round(gp).toLocaleString()+'</b></div>'"
     "+'<div>Net Growth: <b>'+((g-ch)*100).toFixed(1)+'%</b></div>'"
     "+'</div>'"),
    ("platform", "Platform Val", "Platform Valuation",
     [("API Calls (M/mo)", "10"), ("Price per Call ($)", "0.01"),
      ("Growth (%/mo)", "10")],
     "var calls=v[0]*1e6;var price=v[1];var growth=v[2]/100;"
     "var mrr=calls*price;var arr=mrr*12;var arr3=arr*Math.pow(1+growth,36);"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Monthly Revenue: <b>$'+Math.round(mrr).toLocaleString()+'</b></div>'"
     "+'<div>Annual Run-Rate: <b>$'+Math.round(arr).toLocaleString()+'</b></div>'"
     "+'<div>3yr Projected ARR: <b>$'+Math.round(arr3).toLocaleString()+'</b></div>'"
     "+'</div>'"),
    ("ai-monetize", "AI Monetize", "AI Monetization",
     [("Tokens (M/mo)", "100"), ("$ per 1M Tokens", "5"),
      ("Gross Margin (%)", "70")],
     "var tokens=v[0]*1e6;var rate=v[1];var gm=v[2]/100;"
     "var rev=tokens/1e6*rate;var gp=rev*gm;var arr=rev*12;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Monthly Revenue: <b>$'+Math.round(rev).toLocaleString()+'</b></div>'"
     "+'<div>Monthly Gross Profit: <b>$'+Math.round(gp).toLocaleString()+'</b></div>'"
     "+'<div>Annual Run-Rate: <b>$'+Math.round(arr).toLocaleString()+'</b></div>'"
     "+'</div>'"),
    ("tech-tco", "Tech TCO", "Technology TCO",
     [("Servers", "20"), ("$ per Server/mo", "500"),
      ("Engineers", "5"), ("$ per Engineer/yr", "150000")],
     "var servers=v[0];var serverCost=v[1];var eng=v[2];var engCost=v[3];"
     "var annualServer=servers*serverCost*12;var annualEng=eng*engCost;"
     "var tco=annualServer+annualEng;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Server Cost/yr: <b>$'+Math.round(annualServer).toLocaleString()+'</b></div>'"
     "+'<div>Engineering Cost/yr: <b>$'+Math.round(annualEng).toLocaleString()+'</b></div>'"
     "+'<div>Total Annual TCO: <b>$'+Math.round(tco).toLocaleString()+'</b></div>'"
     "+'</div>'"),
    ("pmf", "PMF Nav", "PMF Navigator",
     [("Retention (%)", "40"), ("NPS", "45"),
      ("Sessions/wk", "3"), ("Growth (%/wk)", "5")],
     "var ret=v[0];var nps=v[1];var ses=v[2];var g=v[3];"
     "var pmfScore=ret*0.4+Math.max(0,Math.min(100,nps+50))*0.3+Math.min(100,ses*20)*0.15+Math.min(100,g*10)*0.15;"
     "var verdict=pmfScore>=60?'Strong PMF':pmfScore>=40?'Developing':pmfScore>=25?'Weak':'No PMF';"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>PMF Score: <b>'+pmfScore.toFixed(1)+'/100</b></div>'"
     "+'<div>Verdict: <b>'+verdict+'</b></div>'"
     "+'</div>'"),
    ("war-game", "War Gaming", "Strategic War Gaming",
     [("Scenario Count", "3"), ("Probability (%)", "30"),
      ("Impact ($)", "1000000"), ("Mitigation Cost ($)", "100000")],
     "var sc=v[0];var prob=v[1]/100;var impact=v[2];var mit=v[3];"
     "var expectedLoss=prob*impact;var netLoss=expectedLoss-mit;"
     "var roi=(impact*prob-mit)/mit*100;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Expected Loss: <b>$'+Math.round(expectedLoss).toLocaleString()+'</b></div>'"
     "+'<div>Net (after mitigation): <b>$'+Math.round(netLoss).toLocaleString()+'</b></div>'"
     "+'<div>Mitigation ROI: <b>'+roi.toFixed(1)+'%</b></div>'"
     "+'</div>'"),
    ("payments", "Payments", "Payments Economics",
     [("TPV ($/mo)", "10000000"), ("Take Rate (%)", "2.5"),
      ("Refunds (%)", "1.5"), ("Processing Cost (%)", "1.0")],
     "var tpv=v[0];var take=v[1]/100;var ref=v[2]/100;var proc=v[3]/100;"
     "var gross=tpv*take;var refunds=tpv*ref;var fees=tpv*proc;var net=gross-refunds-fees;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Gross Revenue: <b>$'+Math.round(gross).toLocaleString()+'</b></div>'"
     "+'<div>Refunds: <b>-$'+Math.round(refunds).toLocaleString()+'</b></div>'"
     "+'<div>Processing Fees: <b>-$'+Math.round(fees).toLocaleString()+'</b></div>'"
     "+'<div>Net Revenue: <b>$'+Math.round(net).toLocaleString()+'</b></div>'"
     "+'<div>Net Margin: <b>'+(net/tpv*100).toFixed(2)+'%</b></div>'"
     "+'</div>'"),
    ("neobank", "Neobank", "Neobank Unit Economics",
     [("Deposits ($)", "100000000"), ("NIM (%)", "3"),
      ("CAC ($)", "50"), ("LTV (years)", "5")],
     "var dep=v[0];var nim=v[1]/100;var cac=v[2];var ltv=v[3];"
     "var nii=dep*nim;var perUser=50;var users=dep/perUser;"
     "var ltvTotal=perUser*ltv;var ratio=ltvTotal/cac;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Net Interest Income: <b>$'+Math.round(nii).toLocaleString()+'</b></div>'"
     "+'<div>Est. Users: <b>'+Math.round(users).toLocaleString()+'</b></div>'"
     "+'<div>LTV: <b>$'+Math.round(ltvTotal).toLocaleString()+'</b></div>'"
     "+'<div>LTV/CAC: <b>'+ratio.toFixed(2)+'x</b></div>'"
     "+'</div>'"),
    ("defi-risk", "DeFi Risk", "DeFi Risk Analysis",
     [("TVL ($)", "50000000"), ("Utilization (%)", "70"),
      ("Collateral (%)", "150"), ("Volatility (%)", "30")],
     "var tvl=v[0];var util=v[1]/100;var col=v[2]/100;var vol=v[3]/100;"
     "var liqThreshold=100/col*100;var riskScore=util*50+vol*30+(100-liqThreshold)*20;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Borrowed: <b>$'+Math.round(tvl*util).toLocaleString()+'</b></div>'"
     "+'<div>Liquidation Threshold: <b>'+liqThreshold.toFixed(1)+'%</b></div>'"
     "+'<div>Risk Score: <b>'+riskScore.toFixed(1)+'/100</b></div>'"
     "+'<div>Verdict: <b>'+(riskScore>=70?'HIGH RISK':riskScore>=50?'ELEVATED':'ACCEPTABLE')+'</b></div>'"
     "+'</div>'"),
    ("compliance", "Compliance", "Compliance Score",
     [("Total Controls", "50"), ("Failed", "5"),
      ("Critical Failed", "1"), ("Remediation Days", "30")],
     "var tot=v[0];var failed=v[1];var crit=v[2];var days=v[3];"
     "var passRate=(tot-failed)/tot*100;var score=passRate-crit*5-Math.min(20,days*0.5);"
     "var verdict=score>=90?'COMPLIANT':score>=75?'ACCEPTABLE':score>=60?'AT RISK':'NON-COMPLIANT';"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Pass Rate: <b>'+passRate.toFixed(1)+'%</b></div>'"
     "+'<div>Critical Failures: <b>'+crit+'</b></div>'"
     "+'<div>Compliance Score: <b>'+score.toFixed(1)+'/100</b></div>'"
     "+'<div>Verdict: <b>'+verdict+'</b></div>'"
     "+'</div>'"),
    ("lending", "Lending", "Lending Portfolio Risk",
     [("Loan Book ($)", "10000000"), ("Avg Rate (%)", "8"),
      ("Default Rate (%)", "3"), ("Loss Severity (%)", "60")],
     "var book=v[0];var rate=v[1]/100;var def=v[2]/100;var sev=v[3]/100;"
     "var interest=book*rate;var defaults=book*def;var lossGiven=defaults*sev;var netNII=interest-lossGiven;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Interest Income: <b>$'+Math.round(interest).toLocaleString()+'</b></div>'"
     "+'<div>Expected Defaults: <b>$'+Math.round(defaults).toLocaleString()+'</b></div>'"
     "+'<div>Loss Given Default: <b>$'+Math.round(lossGiven).toLocaleString()+'</b></div>'"
     "+'<div>Net NII: <b>$'+Math.round(netNII).toLocaleString()+'</b></div>'"
     "+'</div>'"),
    ("wallet", "Wallet", "Wallet Unit Economics",
     [("MAU", "500000"), ("ARPU ($/mo)", "2"),
      ("Tx per MAU", "10"), ("CAC ($)", "10")],
     "var mau=v[0];var arpu=v[1];var tx=v[2];var cac=v[3];"
     "var mrr=mau*arpu;var arr=mrr*12;var totalTx=mau*tx;var ltv=arpu*24;var ratio=ltv/cac;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Monthly Revenue: <b>$'+Math.round(mrr).toLocaleString()+'</b></div>'"
     "+'<div>Annual Revenue: <b>$'+Math.round(arr).toLocaleString()+'</b></div>'"
     "+'<div>Monthly Tx: <b>'+Math.round(totalTx).toLocaleString()+'</b></div>'"
     "+'<div>LTV/CAC: <b>'+ratio.toFixed(2)+'x</b></div>'"
     "+'</div>'"),
    ("supply-chain", "Supply Chain", "Supply Chain Analysis",
     [("COGS ($)", "5000000"), ("Inventory Days", "45"),
      ("Lead Time (days)", "30"), ("Payment Terms (days)", "30")],
     "var cogs=v[0];var inv=v[1];var lead=v[2];var pay=v[3];"
     "var dailyCOGS=cogs/365;var inventoryValue=dailyCOGS*inv;var inTransit=dailyCOGS*lead;"
     "var ccc=inv+lead-pay;var tied=inventoryValue+inTransit;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Inventory Value: <b>$'+Math.round(inventoryValue).toLocaleString()+'</b></div>'"
     "+'<div>In-Transit: <b>$'+Math.round(inTransit).toLocaleString()+'</b></div>'"
     "+'<div>Cash Tied: <b>$'+Math.round(tied).toLocaleString()+'</b></div>'"
     "+'<div>Cash Conversion Cycle: <b>'+ccc+' days</b></div>'"
     "+'</div>'"),
    ("freight", "Freight", "Freight Economics",
     [("Shipments/mo", "1000"), ("$ per Shipment", "500"),
      ("Fuel Cost (%)", "20"), ("Margin (%)", "15")],
     "var ship=v[0];var price=v[1];var fuel=v[2]/100;var margin=v[3]/100;"
     "var rev=ship*price;var fuelCost=rev*fuel;var gross=rev-margin*rev-fuelCost;"
     "var netMargin=(gross/rev*100);"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Monthly Revenue: <b>$'+Math.round(rev).toLocaleString()+'</b></div>'"
     "+'<div>Fuel Cost: <b>$'+Math.round(fuelCost).toLocaleString()+'</b></div>'"
     "+'<div>Gross Profit: <b>$'+Math.round(gross).toLocaleString()+'</b></div>'"
     "+'<div>Net Margin: <b>'+netMargin.toFixed(1)+'%</b></div>'"
     "+'</div>'"),
    ("inventory", "Inventory", "Inventory Optimization",
     [("SKU Count", "500"), ("Annual Turnover", "6"),
      ("Avg Unit Cost ($)", "20"), ("Holding Cost (%)", "25")],
     "var sku=v[0];var turn=v[1];var cost=v[2];var hold=v[3]/100;"
     "var avgInv=sku*cost;var annualCOGS=avgInv*turn;var holdingCost=avgInv*hold;"
     "var days=365/turn;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Avg Inventory Value: <b>$'+Math.round(avgInv).toLocaleString()+'</b></div>'"
     "+'<div>Annual COGS: <b>$'+Math.round(annualCOGS).toLocaleString()+'</b></div>'"
     "+'<div>Holding Cost/yr: <b>$'+Math.round(holdingCost).toLocaleString()+'</b></div>'"
     "+'<div>Days of Supply: <b>'+days.toFixed(0)+'</b></div>'"
     "+'</div>'"),
    ("sc-risk", "SC Risk", "Supply Chain Risk",
     [("Suppliers", "100"), ("Critical (%)", "20"),
      ("Disruption Prob (%)", "15"), ("Avg Impact ($)", "500000")],
     "var sup=v[0];var crit=v[1]/100;var prob=v[2]/100;var impact=v[3];"
     "var critSup=sup*crit;var expectedLoss=critSup*prob*impact;"
     "var riskScore=prob*100*0.4+crit*100*0.3+Math.min(100,impact/10000)*0.3;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Critical Suppliers: <b>'+Math.round(critSup)+'</b></div>'"
     "+'<div>Expected Loss: <b>$'+Math.round(expectedLoss).toLocaleString()+'</b></div>'"
     "+'<div>Risk Score: <b>'+riskScore.toFixed(1)+'/100</b></div>'"
     "+'<div>Verdict: <b>'+(riskScore>=60?'HIGH':riskScore>=40?'MEDIUM':'LOW')+'</b></div>'"
     "+'</div>'"),
    ("warehouse", "Warehouse", "Warehouse Operations",
     [("Sqft", "50000"), ("Utilization (%)", "70"),
      ("$ per Sqft/yr", "10"), ("Throughput (units/yr)", "1000000")],
     "var sqft=v[0];var util=v[1]/100;var rate=v[2];var thru=v[3];"
     "var usedSpace=sqft*util;var annualCost=sqft*rate;var costPerUnit=annualCost/thru;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Space Used: <b>'+Math.round(usedSpace).toLocaleString()+' sqft</b></div>'"
     "+'<div>Annual Cost: <b>$'+Math.round(annualCost).toLocaleString()+'</b></div>'"
     "+'<div>Cost per Unit: <b>$'+costPerUnit.toFixed(4)+'</b></div>'"
     "+'<div>Capacity Headroom: <b>'+((1-util)*100).toFixed(0)+'%</b></div>'"
     "+'</div>'"),
    ("ops", "Ops", "Operations Productivity",
     [("Headcount", "50"), ("Avg Salary ($)", "80000"),
      ("Output (units/yr)", "500000"), ("Revenue/Unit ($)", "20")],
     "var hc=v[0];var sal=v[1];var out=v[2];var rev=v[3];"
     "var laborCost=hc*sal;var revenue=out*rev;var costPerUnit=laborCost/out;var productivity=out/hc;var margin=revenue-laborCost;"
     "var html='<div class=\"space-y-1\">'"
     "+'<div>Total Labor Cost: <b>$'+Math.round(laborCost).toLocaleString()+'</b></div>'"
     "+'<div>Total Revenue: <b>$'+Math.round(revenue).toLocaleString()+'</b></div>'"
     "+'<div>Cost per Unit: <b>$'+costPerUnit.toFixed(2)+'</b></div>'"
     "+'<div>Productivity: <b>'+Math.round(productivity).toLocaleString()+' units/head</b></div>'"
     "+'<div>Gross Margin: <b>$'+Math.round(margin).toLocaleString()+'</b></div>'"
     "+'</div>'"),
]

# Professional UI classes
INPUT_CLASS = ("w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 "
               "outline-none text-white/90 focus:border-blue-400/40 font-mono text-xs "
               "transition-colors")
LABEL_CLASS = "text-[10px] text-white/50 block mb-1 font-semibold uppercase tracking-wider"
BTN_CLASS = ("bg-gradient-to-r from-blue-600/20 to-blue-500/10 border border-blue-400/25 "
             "text-blue-200 hover:from-blue-600/30 text-[11px] py-2.5 px-4 rounded-lg "
             "font-semibold transition cursor-pointer")
RESULT_CLASS = ("text-[11px] text-white/70 mt-3 p-3 rounded-lg bg-black/30 "
                "border border-white/[0.06]")

# Engine selector function (client variant — uses d.useState/useRef/useEffect, u.jsx/jsxs)
# Uses inline style backgroundColor:"#000000" for solid black dropdown panel
ENGINE_SELECTOR_CLIENT = (
    'function bQ_EngineSelector({tabs:t,activeTab:r,onSelect:n}){'
    'let[o,l]=(0,d.useState)(!1),s=(0,d.useRef)(null);'
    '(0,d.useEffect)(()=>{function e(t){s.current&&!s.current.contains(t.target)&&l(!1)}'
    'return document.addEventListener("mousedown",e),'
    '()=>document.removeEventListener("mousedown",e)},[]);'
    'let i=t.find(e=>e[0]===r);'
    'return(0,u.jsxs)("div",{ref:s,className:"relative shrink-0",children:['
    '(0,u.jsxs)("button",{onClick:()=>l(!o),'
    'className:"flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.04] '
    'border border-white/[0.06] hover:bg-white/[0.08] transition cursor-pointer",children:['
    '(0,u.jsx)("svg",{className:"w-3.5 h-3.5 text-white/60",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",'
    'children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",d:"M4 6h16M4 12h16M4 18h16"})}),'
    '(0,u.jsx)("span",{className:"text-[11px] font-semibold text-white/80",children:i?i[1]:"Select Engine"}),'
    '(0,u.jsx)("svg",{className:"w-3 h-3 text-white/40 transition-transform "+(o?"rotate-180":""),fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",'
    'children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2.5",d:"M19 9l-7 7-7-7"})})'
    ']}),'
    'o&&(0,u.jsx)("div",{'
    'className:"absolute top-full left-0 mt-1 max-h-80 overflow-y-auto border border-white/[0.08] rounded-lg shadow-2xl z-50 min-w-[200px] cosmic-scrollbar",'
    'style:{backgroundColor:"#000000"},'
    'children:t.map(e=>(0,u.jsx)("button",{onClick:()=>{n(e[0]),l(!1)},'
    'className:`block w-full text-left px-3 py-2 text-[11px] font-medium transition ${r===e[0]?"bg-blue-500/10 text-blue-300":"text-white/60 hover:bg-white/[0.04]"}`,'
    'children:e[1]},e[0]))})'
    ']})}'
)


# CSS injected for result cards
RESULT_CSS = (
    '[id^=r] > div > div{background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.06);'
    'border-radius:8px;padding:10px 14px;margin-bottom:6px;display:flex;'
    'justify-content:space-between;align-items:center}'
    '[id^=r] b{color:#4ade80;font-family:monospace;font-size:13px;font-weight:700}'
)


# ===================================================================
# Helpers
# ===================================================================

def find_matching(s, start_idx, open_char, close_char):
    """Find the matching close char for the open char at start_idx (which must point to open_char)."""
    assert s[start_idx] == open_char
    depth = 0
    in_str = None
    i = start_idx
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
        else:
            if c in ('"', "'", '`'):
                in_str = c
            elif c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def verify_syntax(path):
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if r.returncode == 0:
        print("  SYNTAX OK (node --check)")
        return True
    print("  SYNTAX ERROR:")
    err = r.stderr
    print(err[-1500:] if len(err) > 1500 else err)
    return False


# ===================================================================
# Patch 1: Add 18 engines + SAFE mixing fix
# ===================================================================

def build_engine_jsx(engine, idx, J="u"):
    key, label, title, inputs, calc_js = engine
    rid = "r" + str(idx)
    parts = []
    parts.append(
        '(0,' + J + '.jsx)("div",{className:"p-4 space-y-3",children:['
    )
    # title with professional class
    parts.append(
        '(0,' + J + '.jsx)("h3",{className:"text-xs font-bold text-blue-400/80 uppercase tracking-wider pb-2 border-b border-white/5 mb-3",children:"' + title + '"}),'
    )
    # inputs container
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
    # Calculate button with professional class
    onclick = (
        "function(){var inp=document.getElementById('" + rid + "').parentNode.querySelectorAll('input[type=number]');"
        "var v=Array.from(inp).map(function(x){return parseFloat(x.value)||0});"
        + calc_js + ";"
        "document.getElementById('" + rid + "').innerHTML=html;}"
    )
    parts.append(
        '(0,' + J + '.jsx)("button",{onClick:' + onclick + ',className:"' + BTN_CLASS + '",children:"Calculate"}),'
    )
    # result div
    parts.append(
        '(0,' + J + '.jsx)("div",{id:"' + rid + '",className:"' + RESULT_CLASS + '"})'
    )
    parts.append("]})")
    return "".join(parts)


def build_engine_condition(engine, idx, J="u", use_and=False):
    key = engine[0]
    op = "&&" if use_and else "?"
    jsx = build_engine_jsx(engine, idx, J)
    return '"' + key + '"===A' + op + jsx


def apply_engines_patch(s):
    """Add 18 tabs, add 18 engine conditionals, apply SAFE mixing fix."""
    changes = []

    # Step 1a: Update tab list
    old_tab_list = '[["round","Priced Round"],["safes","SAFE Radar"],["waterfall","Waterfall"],["vesting","Vesting"],["antidilution","Anti-Dilution"],["termsheet","Term Scanner"]]'
    if old_tab_list in s:
        new_entries = ','.join('["' + e[0] + '","' + e[1] + '"]' for e in ENGINES)
        # remove 1 char (the last "]"), add new entries, then "]"
        new_tab_list = old_tab_list[:-1] + ',' + new_entries + ']'
        s = s.replace(old_tab_list, new_tab_list)
        print("  [Step 1a] Tab list updated: 6 -> 24 tabs")
        changes.append("tab_list")
    else:
        # Check if tabs are already there
        if '["saas","SaaS Econ"]' in s:
            print("  [Step 1a] Tab list already updated — skipping")
        else:
            print("  [Step 1a] WARNING: tab list not found, skipping")

    # Step 1b: Add 18 engines to conditional chain
    # First convert termsheet from && to ? if needed
    ts_old_and = '"termsheet"===A&&(0,u.jsx)(x4,{})'
    ts_new_q = '"termsheet"===A?(0,u.jsx)(x4,{})'
    if ts_old_and in s:
        s = s.replace(ts_old_and, ts_new_q)
        print("  [Step 1b] Converted termsheet && to ?")
        changes.append("termsheet_&&->?")

    # Build the chain
    chain = ""
    for i, eng in enumerate(ENGINES):
        is_last = (i == len(ENGINES) - 1)
        cond = build_engine_condition(eng, i + 1, J="u", use_and=is_last)
        chain += ":" + cond

    # Anchor: termsheet content end
    anchor = '(0,u.jsx)(x4,{})]})}bI.displayName'
    if anchor in s:
        s = s.replace(anchor, '(0,u.jsx)(x4,{})' + chain + ']})}bI.displayName')
        print("  [Step 1b] Inserted 18 engine conditions into chain")
        changes.append("engines_chain")
    else:
        # Check if already applied
        if '"saas"===A?' in s and '"ops"===A&&' in s:
            print("  [Step 1b] Engines chain already present — skipping")
        else:
            print("  [Step 1b] WARNING: anchor not found")
            print("    anchor was:", repr(anchor))

    # Step 1c: SAFE mixing fix
    # Insert "safes"===A? between round's else-colon and SAFE_NOTES block
    safe_marker = 'children:"Configure Dilution Matrix"'
    if safe_marker in s:
        safe_idx = s.find(safe_marker)
        # Walk backward to find pattern "):(" (round else-colon)
        k = safe_idx
        found = -1
        while k > 0:
            if s[k:k+3] == '):(':
                found = k
                break
            k -= 1
        if found != -1:
            insert_pos = found + 2
            # Check if "safes"===A? is already there
            if s[insert_pos:insert_pos+15] != '"safes"===A?':
                s = s[:insert_pos] + '"safes"===A?' + s[insert_pos:]
                print("  [Step 1c] Inserted \"safes\"===A? before SAFE_NOTES at pos " + str(insert_pos))
                changes.append("safe_insert")
            else:
                print("  [Step 1c] \"safes\"===A? already inserted — skipping")
        else:
            print("  [Step 1c] WARNING: round else-colon not found")
    else:
        print("  [Step 1c] WARNING: SAFE marker 'Configure Dilution Matrix' not found")

    # Step 1d: Convert comma chain to ternary chain
    reps = [
        ('),"waterfall"===A&&', '):"waterfall"===A?'),
        (',"vesting"===A&&', ':"vesting"===A?'),
        (',"antidilution"===A&&', ':"antidilution"===A?'),
        (',"termsheet"===A&&', ':"termsheet"===A?'),
        (',"termsheet"===A?', ':"termsheet"===A?'),
    ]
    for old, new in reps:
        cnt = s.count(old)
        if cnt:
            s = s.replace(old, new)
            print("  [Step 1d] Replaced " + repr(old) + " -> " + repr(new) + " (" + str(cnt) + "x)")
            changes.append("ternary:" + old[:20])

    return s, changes


# ===================================================================
# Patch 2: Add engine selector dropdown
# ===================================================================

def add_engine_selector(s):
    """Replace horizontal tab list with dropdown, inject bQ_EngineSelector fn."""
    if 'function bQ_EngineSelector' in s:
        print("  bQ_EngineSelector already defined — skipping function injection")
        fn_inserted = True
    else:
        anchor = 'function bR('
        if anchor in s:
            s = s.replace(anchor, ENGINE_SELECTOR_CLIENT + ';' + anchor, 1)
            print("  Injected bQ_EngineSelector function definition before bR")
            fn_inserted = True
        else:
            print("  WARNING: bR anchor not found for EngineSelector injection")
            fn_inserted = False

    # Replace tab list .map(...) with EngineSelector JSX
    tab_list_start = '[["round","Priced Round"]'
    if tab_list_start not in s:
        print("  Tab list start anchor not found — already replaced?")
        # Check if EngineSelector JSX already in place
        if 'bQ_EngineSelector,{tabs:' in s:
            print("  EngineSelector JSX already in place — skipping")
            return s, fn_inserted
        return s, fn_inserted

    t_idx = s.find(tab_list_start)
    # Find end of tab list .map() — pattern `},e))` (close attr `}`, comma, key `e`, `)` u.jsx, `)` .map)
    end_match = re.search(r'\},(\w)\)\)', s[t_idx:])
    if not end_match:
        print("  Tab list end pattern not found")
        return s, fn_inserted
    e_idx = t_idx + end_match.end()

    tab_list_text = s[t_idx:e_idx]
    map_idx = tab_list_text.find('.map(')
    if map_idx == -1:
        print("  .map( not found in tab list")
        return s, fn_inserted
    tabs_array = tab_list_text[:map_idx]

    replacement = '(0,u.jsx)(bQ_EngineSelector,{tabs:' + tabs_array + ',activeTab:A,onSelect:E})'
    s = s[:t_idx] + replacement + s[e_idx:]
    print("  Replaced horizontal tab list .map with EngineSelector dropdown")
    return s, True


# ===================================================================
# Patch 3: Individual export
# ===================================================================

def update_export_individual(s):
    old = 'type:"combined",format:e,dilutionData:n,safes:[],currency:i'
    if old not in s:
        if 'type:"individual"' in s:
            print("  Export already individual — skipping")
            return s, True
        print("  WARNING: combined export anchor not found")
        return s, False

    engine_map = ("(function(){var m={"
                  '"round":"Priced Round","safes":"SAFE Radar","waterfall":"Waterfall",'
                  '"vesting":"Vesting","antidilution":"Anti-Dilution","termsheet":"Term Scanner",'
                  '"saas":"SaaS Econ","platform":"Platform Val","ai-monetize":"AI Monetize",'
                  '"tech-tco":"Tech TCO","pmf":"PMF Nav","war-game":"War Gaming","payments":"Payments",'
                  '"neobank":"Neobank","defi-risk":"DeFi Risk","compliance":"Compliance",'
                  '"lending":"Lending","wallet":"Wallet","supply-chain":"Supply Chain",'
                  '"freight":"Freight","inventory":"Inventory","sc-risk":"SC Risk",'
                  '"warehouse":"Warehouse","ops":"Ops"};return m[A]||A})()')

    # Get result HTML from the active engine's rN div
    result_html_fn = ('(function(){var ridMap={"round":null,"safes":null,"waterfall":null,'
                      '"vesting":null,"antidilution":null,"termsheet":null,'
                      '"saas":"r1","platform":"r2","ai-monetize":"r3","tech-tco":"r4",'
                      '"pmf":"r5","war-game":"r6","payments":"r7","neobank":"r8",'
                      '"defi-risk":"r9","compliance":"r10","lending":"r11","wallet":"r12",'
                      '"supply-chain":"r13","freight":"r14","inventory":"r15","sc-risk":"r16",'
                      '"warehouse":"r17","ops":"r18"};'
                      'var rid=ridMap[A];'
                      'if(rid){var el=document.getElementById(rid);if(el)return el.innerHTML}'
                      'var panel=document.querySelector(".glass-panel-cosmic");'
                      'return panel?panel.innerText:""})()')

    # Get inputs from sibling spans
    inputs_fn = ('(function(){var ridMap={"saas":"r1","platform":"r2","ai-monetize":"r3",'
                 '"tech-tco":"r4","pmf":"r5","war-game":"r6","payments":"r7","neobank":"r8",'
                 '"defi-risk":"r9","compliance":"r10","lending":"r11","wallet":"r12",'
                 '"supply-chain":"r13","freight":"r14","inventory":"r15","sc-risk":"r16",'
                 '"warehouse":"r17","ops":"r18"};'
                 'var rid=ridMap[A];var arr=[];'
                 'if(rid){var el=document.getElementById(rid);'
                 'if(el){var ins=el.parentNode.querySelectorAll("input[type=number]");'
                 'ins.forEach(function(inp){var lbl=inp.previousElementSibling;'
                 'var label=lbl&&lbl.tagName==="LABEL"?lbl.innerText:(inp.placeholder||"input");'
                 'arr.push({label:label,value:inp.value})})}}'
                 'return arr})()')

    new = ('type:"individual",engine:' + engine_map + ','
           'format:"xlsx"===e?"xlsx":"html",'
           'resultHtml:' + result_html_fn + ','
           'inputs:' + inputs_fn + ','
           'currency:i')

    s = s.replace(old, new)
    print("  Updated export to individual format")
    return s, True


# ===================================================================
# Patch 4: Chat features (icon-only Copy All + Share + per-message Copy)
# ===================================================================

def add_chat_features(s):
    """Add Copy All + Share (icon-only) to chat header, plus per-message Copy."""
    changes = []

    # ---- 4a: Header buttons (icon-only with sr-only labels) ----
    # Anchor: precision span at end of chat header
    # The 'e' var here is the messages array (outer scope of the chat component)
    header_old = '(0,u.jsx)("span",{className:"text-[10px] font-semibold text-white/25 font-mono",children:"Precision: 0.2t"})]})'
    if header_old not in s:
        if 'Copy All' in s or 'copy-all-btn' in s:
            print("  Header buttons already present — skipping")
        else:
            print("  WARNING: header precision span anchor not found")
    else:
        # Icon-only buttons with sr-only labels
        # Copy All: copies all assistant messages
        # Share: uses navigator.share if available, else copies
        copy_icon = ('(0,u.jsx)("svg",{className:"w-3.5 h-3.5",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",'
                     'children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",'
                     'd:"M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3"})})')
        share_icon = ('(0,u.jsx)("svg",{className:"w-3.5 h-3.5",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",'
                      'children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",'
                      'd:"M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"})})')

        copy_all_btn = (
            '(0,u.jsx)("button",{onClick:function(ev){'
            'var allText=e.filter(function(m){return m.role==="assistant"&&m.content}).'
            'map(function(m){return m.content}).join("\\n\\n---\\n\\n");'
            'navigator.clipboard.writeText(allText);'
            'var ic=ev.currentTarget.querySelector("svg");'
            'if(ic){ic.style.color="#4ade80"}'
            'setTimeout(function(){if(ic)ic.style.color=""},1500)},'
            'className:"text-white/40 hover:text-white/70 transition p-1 rounded border border-white/[0.06] hover:border-white/[0.12] cursor-pointer",'
            'title:"Copy All",children:[' + copy_icon + ','
            '(0,u.jsx)("span",{className:"sr-only",children:"Copy All"})]})'
        )
        share_btn = (
            '(0,u.jsx)("button",{onClick:function(ev){'
            'var shareText=e.map(function(m){return (m.role==="user"?"You: ":"Fintel: ")+(typeof m.content==="string"?m.content:"")}).join("\\n\\n");'
            'if(navigator.share){navigator.share({title:"Fintel Chat",text:shareText}).catch(function(){})}else{'
            'navigator.clipboard.writeText(shareText);'
            'var ic=ev.currentTarget.querySelector("svg");'
            'if(ic){ic.style.color="#4ade80"}'
            'setTimeout(function(){if(ic)ic.style.color=""},1500)}},'
            'className:"text-white/40 hover:text-white/70 transition p-1 rounded border border-white/[0.06] hover:border-white/[0.12] cursor-pointer",'
            'title:"Share",children:[' + share_icon + ','
            '(0,u.jsx)("span",{className:"sr-only",children:"Share"})]})'
        )

        header_new = (
            '(0,u.jsxs)("div",{className:"flex items-center gap-2",children:['
            '(0,u.jsx)("span",{className:"text-[10px] font-semibold text-white/25 font-mono",children:"Precision: 0.2t"}),'
            + copy_all_btn + ',' + share_btn +
            ']})]})'
        )
        s = s.replace(header_old, header_new)
        print("  Added icon-only Copy All + Share to chat header")
        changes.append("header_buttons")

    # ---- 4b: Per-message Copy button ----
    msg_old = ':(0,u.jsx)("div",{className:"markdown-body",children:(0,u.jsx)(b0,{content:e.content})})}),!a&&o.length>0&&'
    if msg_old not in s:
        if 'self-start text-[10px] text-white/30 hover:text-white/60' in s or 'per-msg-copy' in s:
            print("  Per-message Copy already present — skipping")
        else:
            print("  WARNING: per-message anchor not found")
    else:
        copy_btn = (
            ',!a&&(0,u.jsx)("button",{onClick:function(ev){'
            'var txt=typeof e.content==="string"?e.content:"";'
            'navigator.clipboard.writeText(txt);'
            'var ic=ev.currentTarget.querySelector("svg");'
            'if(ic){ic.style.color="#4ade80"}'
            'setTimeout(function(){if(ic)ic.style.color=""},1500)},'
            'className:"self-start text-white/30 hover:text-white/60 transition p-1",'
            'title:"Copy",children:['
            '(0,u.jsx)("svg",{className:"w-3 h-3",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24",'
            'children:(0,u.jsx)("path",{strokeLinecap:"round",strokeLinejoin:"round",strokeWidth:"2",'
            'd:"M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3"})})'
            ',(0,u.jsx)("span",{className:"sr-only",children:"Copy"})]'
            '})'
        )
        new_str = (':(0,u.jsx)("div",{className:"markdown-body",children:(0,u.jsx)(b0,{content:e.content})})})'
                   + copy_btn + ',!a&&o.length>0&&')
        s = s.replace(msg_old, new_str)
        print("  Added per-message Copy button (icon-only)")
        changes.append("per_msg_copy")

    return s, changes


# ===================================================================
# Patch 5: Remove Documentation link
# ===================================================================

def remove_documentation(s):
    """Remove the DOCUMENTATION section from settings."""
    doc_idx = s.find('"DOCUMENTATION"')
    if doc_idx == -1:
        if 'Full app guide' not in s and 'docs.html' not in s:
            print("  Documentation section not found — already removed?")
        return s, False

    # The section starts with `,(0,u.jsxs)("div",{children:[(0,u.jsxs)("p",{...,"DOCUMENTATION"]}),...`
    # We need to find this start. Walk backward to find `,(0,u.jsxs)("div",{children:[(0,u.jsxs)("p"`
    back_text = s[max(0, doc_idx - 2000):doc_idx]
    starts = list(re.finditer(r',\(0,u\.jsxs\)\("div",\{children:\[\(0,u\.jsxs\)\("p"', back_text))
    if not starts:
        # Try without leading comma (first section case)
        starts = list(re.finditer(r'\(0,u\.jsxs\)\("div",\{children:\[\(0,u\.jsxs\)\("p"', back_text))
        if not starts:
            print("  Section start pattern not found")
            return s, False
    last_start = starts[-1]
    section_start = max(0, doc_idx - 2000) + last_start.start()
    # If matched without leading comma, we need to remove the leading comma too
    has_leading_comma = (last_start.group(0)[0] == ',')

    # Find the end: the closing `]})})})]}),` pattern after the docs.html link
    # We need to find the closing of the outer (0,u.jsxs)("div",{children:[...]
    # Pattern after the docs section: closes with `]})})})]}),`
    forward_text = s[doc_idx:doc_idx + 3000]
    # The structure: ...docs.html..."Documentation & Guide"...}]})})})]}),
    # Find the first `]})})})]})` pattern that closes the outer div
    # We'll use bracket matching instead for reliability

    # Find the outer div open paren position
    # The outer (0,u.jsxs)("div",{children:[ starts at section_start (after comma)
    div_open = section_start + (1 if has_leading_comma else 0)
    # Find the children:[ position
    children_idx = s.find('children:[', div_open)
    if children_idx == -1 or children_idx > doc_idx + 200:
        print("  children:[ not found after section start")
        return s, False
    # Find the matching `]` for the `[` at children_idx + len('children:')
    bracket_open = children_idx + len('children:')
    assert s[bracket_open] == '['
    bracket_close = find_matching(s, bracket_open, '[', ']')
    if bracket_close == -1:
        print("  Could not find matching ] for children:[")
        return s, False
    # After the close `]`, the next chars should be `})` for the div attrs + u.jsx call
    # Pattern: `]})` then possibly `)` for outer u.jsx call
    # Actually the outer is (0,u.jsxs)("div",{children:[...]})  -> ends with `]})`
    # But there may also be additional wrapper, so we look for `]})` after bracket_close
    # Looking at the actual code: `...})})})]}),,(0,u.jsxs)("div",{...`
    # The pattern is: ...]})})})]}),  - this is the close of: div > vP > div > a > inner divs
    # The outer (0,u.jsxs)("div",{children:[SECTION_DIV]) -> close is ]})
    # But the SECTION_DIV itself is (0,u.jsx)(vP,{...}) which contains (0,u.jsx)("div",{...})
    # So the full close pattern after our anchor is: ]})}  (close children, close vP attrs, close vP u.jsx, close div attrs)
    # Wait, let me re-look at the actual code:
    # (0,u.jsxs)("div",{children:[(0,u.jsxs)("p",{...,"DOCUMENTATION"]}),  <- this is the section title
    #            (0,u.jsx)(vP,{children:(0,u.jsx)("div",{className:"p-5",children:(0,u.jsxs)("a",{...})})})]})
    # So after the title close `]})` and the vP close `)`, the children:[ closes with `]})` for the outer div
    # Pattern: ...,]})})})]})

    # Find the close of the outer (0,u.jsxs)("div",{children:[...])  - which is `]})`
    # This should be right after bracket_close
    # Verify by checking what's after bracket_close
    after = s[bracket_close:bracket_close+10]
    if not after.startswith(']})'):
        # bracket_close might be wrong - the children:[ contains items separated by commas
        # Each item is balanced, so bracket_close should be the position of the outer ]
        pass

    # Actually we need bracket_close to be the position of the ] that closes children:[
    # Let's verify: after that we should see `})`  for closing the attrs and the u.jsx call
    # So total close: `]})` (close children [, close attrs }, close u.jsx ))

    # Move past `]})`
    end_pos = bracket_close + 1  # position of ]
    # Skip past `]})`
    if s[end_pos:end_pos+3] == ']})':
        end_pos += 3
    else:
        # Hmm, let's just find `]})` after bracket_close
        m = re.search(r'\]\}\)', s[bracket_close:bracket_close+200])
        if m:
            end_pos = bracket_close + m.end()
        else:
            print("  Could not find ]}) close pattern")
            return s, False

    # If there's a leading comma, we want to remove from `section_start` (including comma)
    # Otherwise remove from section_start (the (0,u.jsxs)("div"...) itself)
    remove_start = section_start if has_leading_comma else section_start
    # Also remove the trailing comma if present (to avoid `]),,(0,u.jsxs)("div"...`)
    # After end_pos, the next char should be `,` (separator) — remove it too if has_leading_comma is False
    if not has_leading_comma:
        # Remove trailing comma after the section
        if s[end_pos:end_pos+1] == ',':
            end_pos += 1
    # else: leading comma was removed, so trailing comma stays

    removed = s[remove_start:end_pos]
    s = s[:remove_start] + s[end_pos:]
    print("  Removed DOCUMENTATION section (" + str(len(removed)) + " chars)")

    # Fix double commas if any
    s2 = s.replace(']),,(', ']),(')
    if s2 != s:
        n = s.count(']),,(')
        s = s2
        print("  Fixed " + str(n) + " double comma(s)")

    return s, True


# ===================================================================
# Patch 6: Remove Production Build section
# ===================================================================

def remove_production_build(s):
    pb_idx = s.find('"Production Build"')
    if pb_idx == -1:
        print("  Production Build not found — already removed?")
        return s, False

    # Find the emerald badge preceding Production Build
    back_text = s[max(0, pb_idx - 600):pb_idx]
    m = re.search(r'\(0,u\.jsx\)\(\w+,\{variant:"badge",color:"emerald"', back_text)
    if not m:
        print("  emerald badge not found before Production Build")
        return s, False
    badge_pos = max(0, pb_idx - 600) + m.start()

    # Walk backward to find section start: `,(0,u.jsxs)("div",{children:[(0,u.jsxs)("p"`
    back2 = s[max(0, badge_pos - 1500):badge_pos]
    section_starts = list(re.finditer(r',\(0,u\.jsxs\)\("div",\{children:\[\(0,u\.jsxs\)\("p"', back2))
    if not section_starts:
        section_starts = list(re.finditer(r'\(0,u\.jsxs\)\("div",\{children:\[\(0,u\.jsxs\)\("p"', back2))
        if not section_starts:
            print("  Section start pattern not found")
            return s, False
    last_start = section_starts[-1]
    section_start = max(0, badge_pos - 1500) + last_start.start()
    has_leading_comma = (last_start.group(0)[0] == ',')

    # Use bracket matching to find end of children:[...]
    div_open = section_start + (1 if has_leading_comma else 0)
    children_idx = s.find('children:[', div_open)
    if children_idx == -1 or children_idx > pb_idx + 200:
        print("  children:[ not found")
        return s, False
    bracket_open = children_idx + len('children:')
    bracket_close = find_matching(s, bracket_open, '[', ']')
    if bracket_close == -1:
        print("  Could not find matching ] for production build children:[")
        return s, False

    end_pos = bracket_close + 1
    # Skip past `]})` for the div attrs + u.jsx call
    if s[end_pos:end_pos+3] == ']})':
        end_pos += 3
    else:
        m = re.search(r'\]\}\)', s[bracket_close:bracket_close+200])
        if m:
            end_pos = bracket_close + m.end()
        else:
            print("  Could not find ]}) close for production build")
            return s, False

    remove_start = section_start
    if not has_leading_comma:
        if s[end_pos:end_pos+1] == ',':
            end_pos += 1

    removed = s[remove_start:end_pos]
    s = s[:remove_start] + s[end_pos:]
    print("  Removed Production Build section (" + str(len(removed)) + " chars)")

    # Fix double commas
    s2 = s.replace(']),,(', ']),(')
    if s2 != s:
        n = s.count(']),,(')
        s = s2
        print("  Fixed " + str(n) + " double comma(s) after PB removal")

    return s, True


# ===================================================================
# Patch 7: Improve calculator UI (inject CSS, professional classes)
# ===================================================================

def inject_css(s):
    """Inject CSS for result cards via a useEffect or a style tag injection."""
    # Strategy: inject a style tag at the start of the calculator component
    # Or use document.head injection. Simplest: inject a <style> tag via a script-like IIFE.
    css_marker = '/* fintel-pro-ui */'
    if css_marker in s:
        print("  CSS already injected — skipping")
        return s, True
    # Inject as a side-effect: insert a (0,d.useEffect)(()=>{...},[]) right after function bR({...
    # But that's risky. Better: inject via an IIFE that runs once at module load.
    # Find a good injection point: after the "use strict" directive
    us = s.find('"use strict"')
    if us == -1:
        print("  'use strict' not found for CSS injection")
        return s, False
    us_end = s.find(';', us)
    if us_end == -1:
        return s, False
    # Build the CSS injection IIFE
    css_js = (
        ';(function(){if(document.getElementById("fintel-pro-ui"))return;'
        'var s=document.createElement("style");s.id="fintel-pro-ui";'
        's.textContent=' + repr(RESULT_CSS) + ';'
        'document.head.appendChild(s)})();'
    )
    s = s[:us_end+1] + css_js + s[us_end+1:]
    print("  Injected professional UI CSS (" + str(len(RESULT_CSS)) + " chars)")
    return s, True


# ===================================================================
# Patch 8: Disable service worker
# ===================================================================

def disable_service_worker(s):
    old = 'navigator.serviceWorker.register("/sw.js",{updateViaCache:"none"})'
    if old not in s:
        if 'false&&null' in s:
            print("  Service worker already disabled — skipping")
            return s, True
        print("  WARNING: serviceWorker.register not found")
        return s, False
    s = s.replace(old, 'false&&null')
    print("  Disabled service worker registration")
    return s, True


# ===================================================================
# Main
# ===================================================================

def main():
    os.chdir("/home/z/my-project")
    print("=" * 70)
    print("apply_all_patches_v2.py — Apply ALL 8 patches to client chunk")
    print("=" * 70)
    with io.open(CLIENT, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)
    print("\nOriginal size: " + str(original_size) + " bytes")

    print("\n--- Patch 1: 18 engines + SAFE mixing fix ---")
    s, _ = apply_engines_patch(s)

    print("\n--- Patch 2: Engine selector dropdown ---")
    s, _ = add_engine_selector(s)

    print("\n--- Patch 3: Individual export ---")
    s, _ = update_export_individual(s)

    print("\n--- Patch 4: Chat features (icon-only) ---")
    s, _ = add_chat_features(s)

    print("\n--- Patch 5: Remove Documentation link ---")
    s, _ = remove_documentation(s)

    print("\n--- Patch 6: Remove Production Build section ---")
    s, _ = remove_production_build(s)

    print("\n--- Patch 7: Improve calculator UI (CSS) ---")
    s, _ = inject_css(s)

    print("\n--- Patch 8: Disable service worker ---")
    s, _ = disable_service_worker(s)

    with io.open(CLIENT, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + CLIENT + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")

    print("\n--- Syntax verification (node --check) ---")
    ok = verify_syntax(CLIENT)

    print("\n--- Syntax verification (acorn) ---")
    try:
        r = subprocess.run(
            ["node", "-e",
             'require("acorn").parse(require("fs").readFileSync("' + CLIENT + '","utf8"),{ecmaVersion:2022,sourceType:"script"});console.log("ACORN OK")'],
            capture_output=True, text=True
        )
        print(r.stdout)
        if r.stderr:
            print("STDERR:", r.stderr[:1500])
        acorn_ok = (r.returncode == 0)
    except Exception as e:
        print("  acorn check failed:", e)
        acorn_ok = False

    return ok and acorn_ok


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
