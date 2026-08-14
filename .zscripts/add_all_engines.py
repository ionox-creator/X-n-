#!/usr/bin/env python3
"""
add_all_engines.py — Adds 18 calculator engines to the CLIENT chunk and applies
the SAFE mixing fix. Idempotent: skips if already applied.

Target: .next/static/chunks/1aed-jz3ypll2.js
  - Tab list: 6 original tabs + 18 new tabs = 24 total
  - Conditional chain: round?PRICED:safes?SAFE:waterfall?hT:...:termsheet?x4:
                       saas?e1:...:warehouse?e17:ops&&e18
  - SAFE mixing fix: convert comma chain to nested ternary chain
"""
import io
import os
import sys
import subprocess

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

# 18 new engines: (key, label, title, inputs, calc_js, result_html)
# inputs: list of (label, placeholder)
# calc_js: JS body that reads v[0..n-1] and sets html string in var 'html'
# result_html: initial HTML for the result div (usually empty)
ENGINES = [
    # 1. SaaS Economics
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
    # 2. Platform Valuation
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
    # 3. AI Monetization
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
    # 4. Tech TCO
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
    # 5. PMF Navigator
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
    # 6. War Gaming
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
    # 7. Payments
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
    # 8. Neobank
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
    # 9. DeFi Risk
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
    # 10. Compliance
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
    # 11. Lending Risk
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
    # 12. Wallet
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
    # 13. Supply Chain
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
    # 14. Freight
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
    # 15. Inventory
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
    # 16. SC Risk
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
    # 17. Warehouse
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
    # 18. Ops
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

INPUT_CLASS = "w-full text-xs bg-white/[0.03] border border-white/[0.06] rounded-lg px-3 py-1.5 outline-none text-white/80 focus:border-blue-400/20 transition"
LABEL_CLASS = "text-[10px] text-white/40 block mb-0.5"
BTN_CLASS = "bg-blue-500/10 border border-blue-400/15 text-blue-300 hover:bg-blue-500/20 text-[11px] py-2 px-3 rounded-lg font-semibold transition cursor-pointer"
RESULT_CLASS = "text-[11px] text-white/60 mt-2 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]"

def build_engine_jsx(engine, idx, J="u"):
    """Build the JSX for one engine. idx is 1-based (r1..r18)."""
    key, label, title, inputs, calc_js = engine
    rid = "r" + str(idx)
    parts = []
    parts.append(
        '(0,' + J + '.jsx)("div",{className:"p-4 space-y-3",children:['
    )
    # h3 title
    parts.append(
        '(0,' + J + '.jsx)("h3",{className:"text-[11px] font-bold text-white/30 uppercase tracking-wider",children:"' + title + '"}),'
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
    # Calculate button
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
    """Build the full conditional: "key"===A?(JSX) or "key"===A&&(JSX)"""
    key = engine[0]
    op = "&&" if use_and else "?"
    connector = ":" if not use_and else ""  # for ?, the next needs :
    jsx = build_engine_jsx(engine, idx, J)
    return '"' + key + '"===A' + op + jsx, connector


def apply_safe_fix(s):
    """Apply the SAFE mixing bug fix to the client chunk."""
    # Step 1: Insert "safes"===A? between round else-colon and SAFE_NOTES
    # The SAFE_NOTES block starts with an h3 saying "Configure Dilution Matrix".
    # We need to find the round's else-colon (":") that comes BEFORE this h3.
    safe_marker = 'children:"Configure Dilution Matrix"'
    safe_idx = s.find(safe_marker)
    if safe_idx == -1:
        print("  WARNING: SAFE marker not found")
        return s, False
    # Walk backward to find the round else-colon: pattern "):(" (close-paren, colon, open-paren)
    k = safe_idx
    found = -1
    while k > 0:
        if s[k:k+3] == '):(':
            found = k
            break
        k -= 1
    if found == -1:
        print("  WARNING: round else-colon not found")
        return s, False
    # Insert "safes"===A? at position found+2 (between ":" and "(")
    insert_pos = found + 2
    s = s[:insert_pos] + '"safes"===A?' + s[insert_pos:]
    print("  Inserted \"safes\"===A? before SAFE_NOTES at pos " + str(insert_pos))

    # Step 2: Convert comma chain to ternary chain
    reps = [
        ('),"waterfall"===A&&', '):"waterfall"===A?'),
        (',"vesting"===A&&', ':"vesting"===A?'),
        (',"antidilution"===A&&', ':"antidilution"===A?'),
        # termsheet may still use && or have been converted to ? by add_engines_to_chain
        (',"termsheet"===A&&', ':"termsheet"===A?'),
        (',"termsheet"===A?', ':"termsheet"===A?'),
        ('"termsheet"===A&&', '"termsheet"===A?'),
    ]
    for old, new in reps:
        if new is None:
            continue
        cnt = s.count(old)
        if cnt:
            s = s.replace(old, new)
            print("  Replaced: " + repr(old) + " -> " + repr(new) + " (" + str(cnt) + "x)")
    return s, True


def update_tab_list(s):
    """Add 18 new tabs to the tab list."""
    # Tab list: [["round","Priced Round"],...,["termsheet","Term Scanner"]]
    # We need to insert 18 new tabs before the closing "]"
    # Find the tab list pattern
    old = '[["round","Priced Round"],["safes","SAFE Radar"],["waterfall","Waterfall"],["vesting","Vesting"],["antidilution","Anti-Dilution"],["termsheet","Term Scanner"]]'
    if old not in s:
        print("  WARNING: tab list not found")
        return s, False
    # Build new tab entries
    new_entries = ','.join('["' + e[0] + '","' + e[1] + '"]' for e in ENGINES)
    # Remove last "]" from old, add new entries, then "]"
    new = old[:-1] + ',' + new_entries + ']'
    s = s.replace(old, new)
    print("  Tab list updated with 18 new tabs")
    return s, True


def add_engines_to_chain(s):
    """Add 18 engine conditions to the conditional chain.

    Before: ..."termsheet"===A?(0,u.jsx)(x4,{})]})}bI.displayName...
    After:  ..."termsheet"===A?(0,u.jsx)(x4,{}):"saas"===A?(e1):...:"ops"===A&&(e18)]})}bI.displayName...
    """
    # Find the termsheet content end - the `]})}` right after termsheet
    # The pattern is: "termsheet"===A?(0,u.jsx)(x4,{})]})}bI.displayName
    ts = '"termsheet"===A?(0,u.jsx)(x4,{})'
    if ts not in s:
        # Maybe already partially applied; check for any termsheet cond
        ts2 = '"termsheet"===A&&(0,u.jsx)(x4,{})'
        if ts2 in s:
            # termsheet still uses && - replace with ? for our chain
            s = s.replace(ts2, ts)
            print("  Converted termsheet && to ?")
        else:
            print("  WARNING: termsheet conditional not found")
            return s, False

    # Build the chain of 18 engines
    chain_parts = []
    for i, eng in enumerate(ENGINES):
        is_last = (i == len(ENGINES) - 1)
        cond, _ = build_engine_condition(eng, i + 1, J="u", use_and=is_last)
        chain_parts.append(":" if not is_last else ":")  # connector before each cond
        # For ?: chain, before each cond we have ":". The first one already comes from termsheet's ?
        # Actually the structure is: termsheet?x4:saas?e1:platform?e2:...:ops&&e18
        # So before saas, we have : (already added by termsheet?x4:)
        # Before platform, we have : (added by saas?e1:)
        # etc.
        # For the LAST (ops&&e18), we still need : before it (added by warehouse?e17:)
        # The && doesn't add a : for the next, but there's no next.
    # The first chain element comes right after termsheet's `?` content. We need `:` before each new cond.
    # termsheet?(x4):"saas"===A?(e1):"platform"===A?(e2):...:"warehouse"===A?(e17):"ops"===A&&(e18)

    # Build the chain string
    chain = ""
    for i, eng in enumerate(ENGINES):
        is_last = (i == len(ENGINES) - 1)
        cond, _ = build_engine_condition(eng, i + 1, J="u", use_and=is_last)
        chain += ":" + cond

    # Insert the chain right after the termsheet content, before the closing `]})}`
    # Pattern: (0,u.jsx)(x4,{})]})}bI.displayName
    # We want: (0,u.jsx)(x4,{})<CHAIN>]})}bI.displayName
    anchor = '(0,u.jsx)(x4,{})]})}bI.displayName'
    if anchor not in s:
        print("  WARNING: termsheet end anchor not found")
        return s, False
    s = s.replace(anchor, '(0,u.jsx)(x4,{})' + chain + ']})}bI.displayName')
    print("  Inserted 18 engine conditions into chain")
    return s, True


def verify_syntax(path):
    """Verify JS syntax with node --check."""
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if r.returncode == 0:
        print("  SYNTAX OK (node --check)")
        return True
    print("  SYNTAX ERROR:")
    print(r.stderr[:1500])
    return False


def main():
    os.chdir("/home/z/my-project")
    print("=== add_all_engines.py (CLIENT chunk) ===")
    with io.open(CLIENT, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    # IDEMPOTENCY CHECK
    if '["saas","SaaS Econ"]' in s:
        print("  ENGINES ALREADY APPLIED — skipping")
        verify_syntax(CLIENT)
        return

    # Step 1: Update tab list
    print("\n--- Step 1: Update tab list ---")
    s, ok1 = update_tab_list(s)

    # Step 2: Add 18 engines to conditional chain (this also converts termsheet && -> ?)
    print("\n--- Step 2: Add 18 engines to conditional chain ---")
    s, ok2 = add_engines_to_chain(s)

    # Step 3: Apply SAFE mixing fix (insert "safes"===A?, convert comma chain to ternary)
    print("\n--- Step 3: Apply SAFE mixing fix ---")
    s, ok3 = apply_safe_fix(s)

    # Write
    with io.open(CLIENT, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + CLIENT + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")

    # Verify syntax
    print("\n--- Syntax verification ---")
    verify_syntax(CLIENT)


if __name__ == "__main__":
    main()
