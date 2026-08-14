#!/usr/bin/env python3
"""
add_console_commands.py — Adds 19 terminal commands to the terminal API route.

Target: .next/server/chunks/node_modules_next_dist_esm_build_templates_app-route_0-ahbvw.js

Commands added:
  Corporate Treasury (7): ebitda, wacc, npv, breakeven, dscr, cac-payback, working-cap
  Fintech (6): payments, neobank, defi-risk, compliance, lending-risk, wallet
  Logistics (6): supply-chain, freight, inventory, sc-risk, warehouse, ops

Each command parses --key value args, calculates, and returns NextResponse.json with blocks.
The help command is updated to list all new commands.

b() percentage fix: b() expects percentage like 25 (not 0.25). All b() calls use percentage values directly.
"""
import io
import os
import subprocess

TERMINAL = ".next/server/chunks/node_modules_next_dist_esm_build_templates_app-route_0-ahbvw.js"

# Each command definition: (key, help_text, case_body)
# case_body is the JS code for the case (without the leading `case"key":` and trailing `}`)
# The case_body should end with `return C.NextResponse.json(...)` so we close with `}`
COMMANDS = [
    # === Corporate Treasury ===
    ("ebitda",
     "Calculate EBITDA (--rev, --costs, --da)",
     '''case"ebitda":{let rev=1e7,costs=6e6,da=5e5;for(let e=1;e<u.length;e++){if("--rev"===u[e]&&u[e+1])rev=m(u[e+1]);else if("--costs"===u[e]&&u[e+1])costs=m(u[e+1]);else if("--da"===u[e]&&u[e+1])da=m(u[e+1])}let ebitda=rev-costs-da;let margin=rev>0?ebitda/rev*100:0;let bk=[];bk.push({type:"section",label:"EBITDA ANALYSIS"},{type:"divider"},{type:"row",label:"Revenue",value:f(rev,"USD")},{type:"row",label:"Operating Costs",value:f(costs,"USD")},{type:"row",label:"D&A",value:f(da,"USD")},{type:"divider"},{type:"row",label:"EBITDA",value:f(ebitda,"USD")},{type:"row",label:"Margin",value:b(margin)},{type:"divider"});if(margin>=30)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+b(margin)+" margin."});else if(margin>=15)bk.push({type:"verdict",verdict:"healthy",message:"HEALTHY: "+b(margin)+" margin."});else if(margin>=5)bk.push({type:"verdict",verdict:"warning",message:"MARGINAL: "+b(margin)+" margin."});else bk.push({type:"verdict",verdict:"danger",message:"POOR: "+b(margin)+" margin."});bk.push({type:"info",message:"EBITDA = Revenue - OpEx - D&A. Ref: GAAP standards."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("wacc",
     "Weighted Avg Cost of Capital (--equity, --debt, --re, --rd, --tax)",
     '''case"wacc":{let E=5e6,D=2e6,re=12,rd=6,tax=25;for(let e=1;e<u.length;e++){if("--equity"===u[e]&&u[e+1])E=m(u[e+1]);else if("--debt"===u[e]&&u[e+1])D=m(u[e+1]);else if("--re"===u[e]&&u[e+1])re=parseFloat(u[e+1].replace("%",""));else if("--rd"===u[e]&&u[e+1])rd=parseFloat(u[e+1].replace("%",""));else if("--tax"===u[e]&&u[e+1])tax=parseFloat(u[e+1].replace("%",""))}let V=E+D;let wE=E/V*100;let wD=D/V*100;let wacc=wE/100*re+wD/100*rd*(1-tax/100);let bk=[];bk.push({type:"section",label:"WACC CALCULATION"},{type:"divider"},{type:"row",label:"Equity",value:f(E,"USD")+" ("+b(wE)+")"},{type:"row",label:"Debt",value:f(D,"USD")+" ("+b(wD)+")"},{type:"row",label:"Cost of Equity",value:b(re)},{type:"row",label:"Cost of Debt (pre-tax)",value:b(rd)},{type:"row",label:"Tax Rate",value:b(tax)},{type:"divider"},{type:"row",label:"WACC",value:b(wacc)},{type:"divider"});if(wacc<8)bk.push({type:"verdict",verdict:"healthy",message:"LOW cost of capital: "+b(wacc)+"."});else if(wacc<12)bk.push({type:"verdict",verdict:"healthy",message:"MODERATE: "+b(wacc)+"."});else bk.push({type:"verdict",verdict:"warning",message:"HIGH: "+b(wacc)+" — capital intensive."});bk.push({type:"info",message:"WACC = E/V*Re + D/V*Rd*(1-T). Ref: Corporate finance theory."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("npv",
     "Net Present Value (--rate, --flows)",
     '''case"npv":{let rate=10,flowsStr="";for(let e=1;e<u.length;e++){if("--rate"===u[e]&&u[e+1])rate=parseFloat(u[e+1].replace("%",""));else if("--flows"===u[e]&&u[e+1])flowsStr=u[e+1]}if(!flowsStr)return C.NextResponse.json({output:null,blocks:[{type:"error",message:"Usage: npv --rate 10 --flows -10M,3M,4M,5M,6M"}]});let flows=flowsStr.split(",").map(function(x){return m(x)});let r=rate/100;let npv=0;for(let i=0;i<flows.length;i++)npv+=flows[i]/Math.pow(1+r,i);let bk=[];bk.push({type:"section",label:"NPV @ "+b(rate)+" DISCOUNT"},{type:"divider"},{type:"row",label:"Periods",value:String(flows.length-1)+" years"},{type:"row",label:"Initial Investment",value:f(Math.abs(flows[0]),"USD")},{type:"row",label:"Total Returns",value:f(flows.slice(1).reduce(function(a,b){return a+b},0),"USD")},{type:"divider"},{type:"row",label:"NPV",value:f(npv,"USD")},{type:"divider"});if(npv>0)bk.push({type:"verdict",verdict:"healthy",message:"ACCEPT: NPV positive at "+b(rate)+" discount."});else bk.push({type:"verdict",verdict:"danger",message:"REJECT: NPV negative at "+b(rate)+" discount."});bk.push({type:"info",message:"NPV = sum(Ft/(1+r)^t). Ref: GAAP, corporate finance."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("breakeven",
     "Breakeven units (--fixed, --price, --vc)",
     '''case"breakeven":{let fixed=1e6,price=100,vc=40;for(let e=1;e<u.length;e++){if("--fixed"===u[e]&&u[e+1])fixed=m(u[e+1]);else if("--price"===u[e]&&u[e+1])price=m(u[e+1]);else if("--vc"===u[e]&&u[e+1])vc=m(u[e+1])}if(price<=vc)return C.NextResponse.json({output:null,blocks:[{type:"error",message:"Price must exceed variable cost."}]});let be=fixed/(price-vc);let rev=be*price;let bk=[];bk.push({type:"section",label:"BREAKEVEN ANALYSIS"},{type:"divider"},{type:"row",label:"Fixed Costs",value:f(fixed,"USD")},{type:"row",label:"Price per Unit",value:f(price,"USD")},{type:"row",label:"Variable Cost/Unit",value:f(vc,"USD")},{type:"row",label:"Contribution Margin",value:f(price-vc,"USD")},{type:"divider"},{type:"row",label:"Breakeven Units",value:Math.ceil(be).toLocaleString()},{type:"row",label:"Breakeven Revenue",value:f(rev,"USD")},{type:"divider"});bk.push({type:"verdict",verdict:"healthy",message:"At "+Math.ceil(be).toLocaleString()+" units, total revenue covers all costs."});bk.push({type:"info",message:"BE = Fixed / (Price - VC). Ref: Managerial accounting."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("dscr",
     "Debt Service Coverage Ratio (--noi, --debt-service)",
     '''case"dscr":{let noi=1.2e6,ds=8e5;for(let e=1;e<u.length;e++){if("--noi"===u[e]&&u[e+1])noi=m(u[e+1]);else if("--debt-service"===u[e]&&u[e+1])ds=m(u[e+1])}if(ds<=0)return C.NextResponse.json({output:null,blocks:[{type:"error",message:"Debt service must be > 0."}]});let dscr=noi/ds;let bk=[];bk.push({type:"section",label:"DSCR ANALYSIS"},{type:"divider"},{type:"row",label:"Net Operating Income",value:f(noi,"USD")},{type:"row",label:"Annual Debt Service",value:f(ds,"USD")},{type:"divider"},{type:"row",label:"DSCR",value:dscr.toFixed(2)+"x"},{type:"divider"});if(dscr>=1.5)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+dscr.toFixed(2)+"x coverage."});else if(dscr>=1.25)bk.push({type:"verdict",verdict:"healthy",message:"ACCEPTABLE: "+dscr.toFixed(2)+"x."});else if(dscr>=1.0)bk.push({type:"verdict",verdict:"warning",message:"TIGHT: "+dscr.toFixed(2)+"x — minimal buffer."});else bk.push({type:"verdict",verdict:"danger",message:"INSUFFICIENT: "+dscr.toFixed(2)+"x — default risk."});bk.push({type:"info",message:"DSCR = NOI / Debt Service. Lenders typically require 1.25x+."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("cac-payback",
     "CAC Payback Period (--cac, --arpu, --gm)",
     '''case"cac-payback":{let cac=500,arpu=50,gm=80;for(let e=1;e<u.length;e++){if("--cac"===u[e]&&u[e+1])cac=m(u[e+1]);else if("--arpu"===u[e]&&u[e+1])arpu=m(u[e+1]);else if("--gm"===u[e]&&u[e+1])gm=parseFloat(u[e+1].replace("%",""))}let monthlyGP=arpu*gm/100;let months=monthlyGP>0?cac/monthlyGP:999;let bk=[];bk.push({type:"section",label:"CAC PAYBACK"},{type:"divider"},{type:"row",label:"CAC",value:f(cac,"USD")},{type:"row",label:"Monthly ARPU",value:f(arpu,"USD")},{type:"row",label:"Gross Margin",value:b(gm)},{type:"divider"},{type:"row",label:"Monthly Gross Profit/User",value:f(monthlyGP,"USD")},{type:"row",label:"Payback Period",value:months.toFixed(1)+" months"},{type:"divider"});if(months<12)bk.push({type:"verdict",verdict:"healthy",message:"FAST: "+months.toFixed(1)+" months payback."});else if(months<18)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+months.toFixed(1)+" months."});else if(months<24)bk.push({type:"verdict",verdict:"warning",message:"SLOW: "+months.toFixed(1)+" months."});else bk.push({type:"verdict",verdict:"danger",message:"UNHEALTHY: "+months.toFixed(1)+" months — capital inefficient."});bk.push({type:"info",message:"Payback = CAC / (ARPU * GM%). SaaS benchmark: <12 months."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("working-cap",
     "Working Capital (--ca, --cl)",
     '''case"working-cap":{let ca=2e6,cl=1.2e6;for(let e=1;e<u.length;e++){if("--ca"===u[e]&&u[e+1])ca=m(u[e+1]);else if("--cl"===u[e]&&u[e+1])cl=m(u[e+1])}let wc=ca-cl;let ratio=cl>0?ca/cl:0;let bk=[];bk.push({type:"section",label:"WORKING CAPITAL"},{type:"divider"},{type:"row",label:"Current Assets",value:f(ca,"USD")},{type:"row",label:"Current Liabilities",value:f(cl,"USD")},{type:"divider"},{type:"row",label:"Working Capital",value:f(wc,"USD")},{type:"row",label:"Current Ratio",value:ratio.toFixed(2)+"x"},{type:"divider"});if(ratio>=2)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+ratio.toFixed(2)+"x current ratio."});else if(ratio>=1.5)bk.push({type:"verdict",verdict:"healthy",message:"HEALTHY: "+ratio.toFixed(2)+"x."});else if(ratio>=1.0)bk.push({type:"verdict",verdict:"warning",message:"TIGHT: "+ratio.toFixed(2)+"x."});else bk.push({type:"verdict",verdict:"danger",message:"INSOLVENT: "+ratio.toFixed(2)+"x — current assets < liabilities."});bk.push({type:"info",message:"WC = CA - CL. Current Ratio = CA/CL. Benchmark: 1.5-2.0x."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    # === Fintech ===
    ("payments",
     "Payments net revenue (--tpv, --take, --refunds, --proc)",
     '''case"payments":{let tpv=1e7,take=2.5,ref=1.5,proc=1;for(let e=1;e<u.length;e++){if("--tpv"===u[e]&&u[e+1])tpv=m(u[e+1]);else if("--take"===u[e]&&u[e+1])take=parseFloat(u[e+1].replace("%",""));else if("--refunds"===u[e]&&u[e+1])ref=parseFloat(u[e+1].replace("%",""));else if("--proc"===u[e]&&u[e+1])proc=parseFloat(u[e+1].replace("%",""))}let gross=tpv*take/100;let refunds=tpv*ref/100;let fees=tpv*proc/100;let net=gross-refunds-fees;let margin=tpv>0?net/tpv*100:0;let bk=[];bk.push({type:"section",label:"PAYMENTS ECONOMICS"},{type:"divider"},{type:"row",label:"TPV",value:f(tpv,"USD")},{type:"row",label:"Take Rate",value:b(take)},{type:"row",label:"Gross Revenue",value:f(gross,"USD")},{type:"row",label:"Refunds",value:f(refunds,"USD")},{type:"row",label:"Processing Fees",value:f(fees,"USD")},{type:"divider"},{type:"row",label:"Net Revenue",value:f(net,"USD")},{type:"row",label:"Net Margin",value:b(margin)},{type:"divider"});if(margin>=1.5)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+b(margin)+" net margin."});else if(margin>=0.5)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+b(margin)+" margin."});else bk.push({type:"verdict",verdict:"warning",message:"THIN: "+b(margin)+" — sensitive to fee changes."});bk.push({type:"info",message:"Net = TPV*(take-refunds-proc)/100."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("neobank",
     "Neobank unit economics (--deposits, --nim, --cac, --ltv)",
     '''case"neobank":{let dep=1e8,nim=3,cac=50,ltv=5;for(let e=1;e<u.length;e++){if("--deposits"===u[e]&&u[e+1])dep=m(u[e+1]);else if("--nim"===u[e]&&u[e+1])nim=parseFloat(u[e+1].replace("%",""));else if("--cac"===u[e]&&u[e+1])cac=m(u[e+1]);else if("--ltv"===u[e]&&u[e+1])ltv=parseFloat(u[e+1])}let nii=dep*nim/100;let perUser=50;let users=dep/perUser;let ltvTotal=perUser*ltv;let ratio=ltvTotal/cac;let bk=[];bk.push({type:"section",label:"NEOBANK ECONOMICS"},{type:"divider"},{type:"row",label:"Deposits",value:f(dep,"USD")},{type:"row",label:"NIM",value:b(nim)},{type:"row",label:"Net Interest Income",value:f(nii,"USD")},{type:"row",label:"Est. Users",value:Math.round(users).toLocaleString()},{type:"divider"},{type:"row",label:"CAC",value:f(cac,"USD")},{type:"row",label:"LTV",value:f(ltvTotal,"USD")},{type:"row",label:"LTV/CAC",value:ratio.toFixed(2)+"x"},{type:"divider"});if(ratio>=3)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+ratio.toFixed(2)+"x LTV/CAC."});else if(ratio>=1.5)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+ratio.toFixed(2)+"x."});else bk.push({type:"verdict",verdict:"warning",message:"WEAK: "+ratio.toFixed(2)+"x — below 1.5x threshold."});bk.push({type:"info",message:"NII = Deposits * NIM%. LTV/CAC benchmark: 3x+."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("defi-risk",
     "DeFi protocol risk (--tvl, --util, --col, --vol)",
     '''case"defi-risk":{let tvl=5e7,util=70,col=150,vol=30;for(let e=1;e<u.length;e++){if("--tvl"===u[e]&&u[e+1])tvl=m(u[e+1]);else if("--util"===u[e]&&u[e+1])util=parseFloat(u[e+1].replace("%",""));else if("--col"===u[e]&&u[e+1])col=parseFloat(u[e+1].replace("%",""));else if("--vol"===u[e]&&u[e+1])vol=parseFloat(u[e+1].replace("%",""))}let borrowed=tvl*util/100;let liqThreshold=col>0?100/col*100:100;let riskScore=util*0.5+vol*0.3+(100-liqThreshold)*100*0.2;let bk=[];bk.push({type:"section",label:"DEFI RISK ANALYSIS"},{type:"divider"},{type:"row",label:"TVL",value:f(tvl,"USD")},{type:"row",label:"Utilization",value:b(util)},{type:"row",label:"Borrowed",value:f(borrowed,"USD")},{type:"row",label:"Collateralization",value:b(col)},{type:"row",label:"Volatility",value:b(vol)},{type:"divider"},{type:"row",label:"Liquidation Threshold",value:b(liqThreshold)},{type:"row",label:"Risk Score",value:riskScore.toFixed(1)+"/100"},{type:"divider"});if(riskScore>=70)bk.push({type:"verdict",verdict:"danger",message:"HIGH RISK: "+riskScore.toFixed(1)+" — reduce utilization or boost collateral."});else if(riskScore>=50)bk.push({type:"verdict",verdict:"warning",message:"ELEVATED: "+riskScore.toFixed(1)+" — monitor volatility."});else bk.push({type:"verdict",verdict:"healthy",message:"ACCEPTABLE: "+riskScore.toFixed(1)+" risk score."});bk.push({type:"info",message:"Risk = 0.5*util + 0.3*vol + 0.2*(100-liqThreshold)."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("compliance",
     "Compliance score (--total, --failed, --critical)",
     '''case"compliance":{let tot=50,failed=5,crit=1;for(let e=1;e<u.length;e++){if("--total"===u[e]&&u[e+1])tot=parseInt(u[e+1]);else if("--failed"===u[e]&&u[e+1])failed=parseInt(u[e+1]);else if("--critical"===u[e]&&u[e+1])crit=parseInt(u[e+1])}let passRate=tot>0?(tot-failed)/tot*100:0;let score=passRate-crit*5;let verdict=score>=90?"COMPLIANT":score>=75?"ACCEPTABLE":score>=60?"AT RISK":"NON-COMPLIANT";let bk=[];bk.push({type:"section",label:"COMPLIANCE SCORE"},{type:"divider"},{type:"row",label:"Total Controls",value:String(tot)},{type:"row",label:"Failed",value:String(failed)},{type:"row",label:"Critical Failures",value:String(crit)},{type:"divider"},{type:"row",label:"Pass Rate",value:b(passRate)},{type:"row",label:"Compliance Score",value:score.toFixed(1)+"/100"},{type:"row",label:"Verdict",value:verdict},{type:"divider"});if(score>=75)bk.push({type:"verdict",verdict:"healthy",message:verdict+": "+score.toFixed(1)+"/100."});else if(score>=60)bk.push({type:"verdict",verdict:"warning",message:verdict+": "+score.toFixed(1)+"/100."});else bk.push({type:"verdict",verdict:"danger",message:verdict+": "+score.toFixed(1)+"/100 — remediate immediately."});bk.push({type:"info",message:"Score = Pass Rate - 5*Critical. Ref: SOC2, ISO 27001."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("lending-risk",
     "Lending portfolio risk (--book, --rate, --default, --loss)",
     '''case"lending-risk":{let book=1e7,rate=8,def=3,sev=60;for(let e=1;e<u.length;e++){if("--book"===u[e]&&u[e+1])book=m(u[e+1]);else if("--rate"===u[e]&&u[e+1])rate=parseFloat(u[e+1].replace("%",""));else if("--default"===u[e]&&u[e+1])def=parseFloat(u[e+1].replace("%",""));else if("--loss"===u[e]&&u[e+1])sev=parseFloat(u[e+1].replace("%",""))}let interest=book*rate/100;let defaults=book*def/100;let lgd=defaults*sev/100;let netNII=interest-lgd;let bk=[];bk.push({type:"section",label:"LENDING PORTFOLIO RISK"},{type:"divider"},{type:"row",label:"Loan Book",value:f(book,"USD")},{type:"row",label:"Avg Rate",value:b(rate)},{type:"row",label:"Default Rate",value:b(def)},{type:"row",label:"Loss Severity",value:b(sev)},{type:"divider"},{type:"row",label:"Interest Income",value:f(interest,"USD")},{type:"row",label:"Expected Defaults",value:f(defaults,"USD")},{type:"row",label:"Loss Given Default",value:f(lgd,"USD")},{type:"divider"},{type:"row",label:"Net NII",value:f(netNII,"USD")},{type:"divider"});if(netNII>interest*0.7)bk.push({type:"verdict",verdict:"healthy",message:"HEALTHY: Net NII "+b(netNII/interest*100)+" of gross."});else if(netNII>interest*0.4)bk.push({type:"verdict",verdict:"warning",message:"PRESSURED: "+b(netNII/interest*100)+" of gross."});else bk.push({type:"verdict",verdict:"danger",message:"CRITICAL: "+b(netNII/interest*100)+" of gross — defaults eroding NII."});bk.push({type:"info",message:"EL = Book * Default% * Severity%."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("wallet",
     "Wallet unit economics (--mau, --arpu, --tx, --cac)",
     '''case"wallet":{let mau=5e5,arpu=2,tx=10,cac=10;for(let e=1;e<u.length;e++){if("--mau"===u[e]&&u[e+1])mau=m(u[e+1]);else if("--arpu"===u[e]&&u[e+1])arpu=m(u[e+1]);else if("--tx"===u[e]&&u[e+1])tx=parseFloat(u[e+1]);else if("--cac"===u[e]&&u[e+1])cac=m(u[e+1])}let mrr=mau*arpu;let arr=mrr*12;let totalTx=mau*tx;let ltv=arpu*24;let ratio=cac>0?ltv/cac:0;let bk=[];bk.push({type:"section",label:"WALLET UNIT ECONOMICS"},{type:"divider"},{type:"row",label:"MAU",value:mau.toLocaleString()},{type:"row",label:"ARPU ($/mo)",value:f(arpu,"USD")},{type:"row",label:"Tx per MAU",value:String(tx)},{type:"divider"},{type:"row",label:"Monthly Revenue",value:f(mrr,"USD")},{type:"row",label:"Annual Revenue",value:f(arr,"USD")},{type:"row",label:"Monthly Tx",value:Math.round(totalTx).toLocaleString()},{type:"divider"},{type:"row",label:"CAC",value:f(cac,"USD")},{type:"row",label:"LTV (24mo)",value:f(ltv,"USD")},{type:"row",label:"LTV/CAC",value:ratio.toFixed(2)+"x"},{type:"divider"});if(ratio>=3)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+ratio.toFixed(2)+"x LTV/CAC."});else if(ratio>=1.5)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+ratio.toFixed(2)+"x."});else bk.push({type:"verdict",verdict:"warning",message:"WEAK: "+ratio.toFixed(2)+"x — below threshold."});bk.push({type:"info",message:"LTV/CAC benchmark for wallets: 3x+."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    # === Logistics ===
    ("supply-chain",
     "Cash conversion cycle (--cogs, --inv, --lead, --pay)",
     '''case"supply-chain":{let cogs=5e6,inv=45,lead=30,pay=30;for(let e=1;e<u.length;e++){if("--cogs"===u[e]&&u[e+1])cogs=m(u[e+1]);else if("--inv"===u[e]&&u[e+1])inv=parseFloat(u[e+1]);else if("--lead"===u[e]&&u[e+1])lead=parseFloat(u[e+1]);else if("--pay"===u[e]&&u[e+1])pay=parseFloat(u[e+1])}let dailyCOGS=cogs/365;let invValue=dailyCOGS*inv;let inTransit=dailyCOGS*lead;let ccc=inv+lead-pay;let tied=invValue+inTransit;let bk=[];bk.push({type:"section",label:"SUPPLY CHAIN ANALYSIS"},{type:"divider"},{type:"row",label:"Annual COGS",value:f(cogs,"USD")},{type:"row",label:"Inventory Days",value:String(inv)},{type:"row",label:"Lead Time (days)",value:String(lead)},{type:"row",label:"Payment Terms (days)",value:String(pay)},{type:"divider"},{type:"row",label:"Inventory Value",value:f(invValue,"USD")},{type:"row",label:"In-Transit",value:f(inTransit,"USD")},{type:"row",label:"Cash Tied",value:f(tied,"USD")},{type:"divider"},{type:"row",label:"Cash Conversion Cycle",value:String(ccc)+" days"},{type:"divider"});if(ccc<30)bk.push({type:"verdict",verdict:"healthy",message:"EFFICIENT: "+ccc+" day CCC."});else if(ccc<60)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+ccc+" day CCC."});else bk.push({type:"verdict",verdict:"warning",message:"SLOW: "+ccc+" day CCC — cash trapped in inventory."});bk.push({type:"info",message:"CCC = Inventory Days + Lead Time - Payment Terms."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("freight",
     "Freight economics (--shipments, --price, --fuel, --margin)",
     '''case"freight":{let ship=1000,price=500,fuel=20,margin=15;for(let e=1;e<u.length;e++){if("--shipments"===u[e]&&u[e+1])ship=m(u[e+1]);else if("--price"===u[e]&&u[e+1])price=m(u[e+1]);else if("--fuel"===u[e]&&u[e+1])fuel=parseFloat(u[e+1].replace("%",""));else if("--margin"===u[e]&&u[e+1])margin=parseFloat(u[e+1].replace("%",""))}let rev=ship*price;let fuelCost=rev*fuel/100;let gross=rev*margin/100;let netMargin=margin-fuel;let bk=[];bk.push({type:"section",label:"FREIGHT ECONOMICS"},{type:"divider"},{type:"row",label:"Shipments/mo",value:ship.toLocaleString()},{type:"row",label:"Price/Shipment",value:f(price,"USD")},{type:"row",label:"Fuel Cost %",value:b(fuel)},{type:"row",label:"Target Margin",value:b(margin)},{type:"divider"},{type:"row",label:"Monthly Revenue",value:f(rev,"USD")},{type:"row",label:"Fuel Cost",value:f(fuelCost,"USD")},{type:"row",label:"Gross Profit",value:f(gross,"USD")},{type:"row",label:"Net Margin (post-fuel)",value:b(netMargin)},{type:"divider"});if(netMargin>=10)bk.push({type:"verdict",verdict:"healthy",message:"HEALTHY: "+b(netMargin)+" net margin."});else if(netMargin>=5)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+b(netMargin)+" margin."});else bk.push({type:"verdict",verdict:"warning",message:"THIN: "+b(netMargin)+" — fuel-sensitive."});bk.push({type:"info",message:"Net Margin = Target Margin - Fuel%."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("inventory",
     "Inventory optimization (--skus, --turnover, --cost, --holding)",
     '''case"inventory":{let sku=500,turn=6,cost=20,hold=25;for(let e=1;e<u.length;e++){if("--skus"===u[e]&&u[e+1])sku=parseInt(u[e+1]);else if("--turnover"===u[e]&&u[e+1])turn=parseFloat(u[e+1]);else if("--cost"===u[e]&&u[e+1])cost=m(u[e+1]);else if("--holding"===u[e]&&u[e+1])hold=parseFloat(u[e+1].replace("%",""))}let avgInv=sku*cost;let annualCOGS=avgInv*turn;let holdingCost=avgInv*hold/100;let days=turn>0?365/turn:0;let bk=[];bk.push({type:"section",label:"INVENTORY OPTIMIZATION"},{type:"divider"},{type:"row",label:"SKU Count",value:sku.toLocaleString()},{type:"row",label:"Annual Turnover",value:turn+"x"},{type:"row",label:"Avg Unit Cost",value:f(cost,"USD")},{type:"row",label:"Holding Cost %",value:b(hold)},{type:"divider"},{type:"row",label:"Avg Inventory Value",value:f(avgInv,"USD")},{type:"row",label:"Annual COGS",value:f(annualCOGS,"USD")},{type:"row",label:"Holding Cost/yr",value:f(holdingCost,"USD")},{type:"row",label:"Days of Supply",value:days.toFixed(0)},{type:"divider"});if(turn>=8)bk.push({type:"verdict",verdict:"healthy",message:"EFFICIENT: "+turn+"x turnover."});else if(turn>=4)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+turn+"x turnover."});else bk.push({type:"verdict",verdict:"warning",message:"SLOW: "+turn+"x — excess inventory."});bk.push({type:"info",message:"Days of Supply = 365 / Turnover. Benchmark: 6-8x for retail."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("sc-risk",
     "Supply chain risk exposure (--suppliers, --critical, --prob, --impact)",
     '''case"sc-risk":{let sup=100,crit=20,prob=15,impact=5e5;for(let e=1;e<u.length;e++){if("--suppliers"===u[e]&&u[e+1])sup=parseInt(u[e+1]);else if("--critical"===u[e]&&u[e+1])crit=parseFloat(u[e+1].replace("%",""));else if("--prob"===u[e]&&u[e+1])prob=parseFloat(u[e+1].replace("%",""));else if("--impact"===u[e]&&u[e+1])impact=m(u[e+1])}let critSup=sup*crit/100;let expectedLoss=critSup*prob/100*impact;let riskScore=prob*0.4+crit*0.3+Math.min(100,impact/1e4)*0.3;let bk=[];bk.push({type:"section",label:"SUPPLY CHAIN RISK"},{type:"divider"},{type:"row",label:"Total Suppliers",value:String(sup)},{type:"row",label:"Critical %",value:b(crit)},{type:"row",label:"Critical Suppliers",value:String(Math.round(critSup))},{type:"row",label:"Disruption Probability",value:b(prob)},{type:"row",label:"Avg Impact",value:f(impact,"USD")},{type:"divider"},{type:"row",label:"Expected Loss",value:f(expectedLoss,"USD")},{type:"row",label:"Risk Score",value:riskScore.toFixed(1)+"/100"},{type:"divider"});if(riskScore>=60)bk.push({type:"verdict",verdict:"danger",message:"HIGH RISK: "+riskScore.toFixed(1)+" — diversify suppliers."});else if(riskScore>=40)bk.push({type:"verdict",verdict:"warning",message:"MEDIUM: "+riskScore.toFixed(1)+" — monitor critical suppliers."});else bk.push({type:"verdict",verdict:"healthy",message:"LOW: "+riskScore.toFixed(1)+" risk score."});bk.push({type:"info",message:"EL = CriticalSuppliers * Prob% * Impact. Score = 0.4*prob + 0.3*crit + 0.3*impact_norm."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("warehouse",
     "Warehouse cost per unit (--sqft, --util, --rate, --throughput)",
     '''case"warehouse":{let sqft=5e4,util=70,rate=10,thru=1e6;for(let e=1;e<u.length;e++){if("--sqft"===u[e]&&u[e+1])sqft=m(u[e+1]);else if("--util"===u[e]&&u[e+1])util=parseFloat(u[e+1].replace("%",""));else if("--rate"===u[e]&&u[e+1])rate=m(u[e+1]);else if("--throughput"===u[e]&&u[e+1])thru=m(u[e+1])}let usedSpace=sqft*util/100;let annualCost=sqft*rate;let costPerUnit=thru>0?annualCost/thru:0;let headroom=100-util;let bk=[];bk.push({type:"section",label:"WAREHOUSE OPERATIONS"},{type:"divider"},{type:"row",label:"Total Sqft",value:sqft.toLocaleString()},{type:"row",label:"Utilization",value:b(util)},{type:"row",label:"Space Used",value:Math.round(usedSpace).toLocaleString()+" sqft"},{type:"row",label:"$ / sqft / yr",value:f(rate,"USD")},{type:"row",label:"Annual Throughput",value:thru.toLocaleString()+" units"},{type:"divider"},{type:"row",label:"Annual Cost",value:f(annualCost,"USD")},{type:"row",label:"Cost per Unit",value:f(costPerUnit,"USD")},{type:"row",label:"Capacity Headroom",value:b(headroom)},{type:"divider"});if(util>=85)bk.push({type:"verdict",verdict:"warning",message:"CONSTRAINED: "+b(util)+" utilization — expand or optimize."});else if(util>=60)bk.push({type:"verdict",verdict:"healthy",message:"OPTIMAL: "+b(util)+" utilization."});else bk.push({type:"verdict",verdict:"warning",message:"UNDERUTILIZED: "+b(util)+" — excess capacity."});bk.push({type:"info",message:"Cost/Unit = (Sqft * Rate) / Throughput."});return C.NextResponse.json({output:null,blocks:bk})}'''),

    ("ops",
     "Operations productivity (--headcount, --salary, --output, --rev)",
     '''case"ops":{let hc=50,sal=8e4,out=5e5,rev=20;for(let e=1;e<u.length;e++){if("--headcount"===u[e]&&u[e+1])hc=parseInt(u[e+1]);else if("--salary"===u[e]&&u[e+1])sal=m(u[e+1]);else if("--output"===u[e]&&u[e+1])out=m(u[e+1]);else if("--rev"===u[e]&&u[e+1])rev=m(u[e+1])}let laborCost=hc*sal;let revenue=out*rev;let costPerUnit=out>0?laborCost/out:0;let productivity=hc>0?out/hc:0;let margin=revenue-laborCost;let marginPct=revenue>0?margin/revenue*100:0;let bk=[];bk.push({type:"section",label:"OPERATIONS PRODUCTIVITY"},{type:"divider"},{type:"row",label:"Headcount",value:String(hc)},{type:"row",label:"Avg Salary",value:f(sal,"USD")},{type:"row",label:"Annual Output",value:out.toLocaleString()+" units"},{type:"row",label:"Revenue/Unit",value:f(rev,"USD")},{type:"divider"},{type:"row",label:"Total Labor Cost",value:f(laborCost,"USD")},{type:"row",label:"Total Revenue",value:f(revenue,"USD")},{type:"row",label:"Cost per Unit",value:f(costPerUnit,"USD")},{type:"row",label:"Productivity",value:Math.round(productivity).toLocaleString()+" units/head"},{type:"divider"},{type:"row",label:"Gross Margin",value:f(margin,"USD")},{type:"row",label:"Margin %",value:b(marginPct)},{type:"divider"});if(marginPct>=30)bk.push({type:"verdict",verdict:"healthy",message:"STRONG: "+b(marginPct)+" margin."});else if(marginPct>=15)bk.push({type:"verdict",verdict:"healthy",message:"OK: "+b(marginPct)+" margin."});else if(marginPct>=0)bk.push({type:"verdict",verdict:"warning",message:"THIN: "+b(marginPct)+" margin."});else bk.push({type:"verdict",verdict:"danger",message:"LOSS: "+b(marginPct)+" — labor exceeds revenue."});bk.push({type:"info",message:"Cost/Unit = Labor / Output. Productivity = Output / Headcount."});return C.NextResponse.json({output:null,blocks:bk})}'''),
]


def update_help(s):
    """Update the help command to list all new commands."""
    # The help command ends with: {type:"row",label:"brain",value:'Inject custom instructions (e.g. brain "Focus on SAFE traps")'}]});case"status"
    # We need to add new rows before the closing ]}
    help_end_marker = 'Inject custom instructions (e.g. brain \\"Focus on SAFE traps\\")\'}]});case"status"'
    # Actually the format is simpler - let me find the exact text
    help_old_end = '{type:"row",label:"brain",value:\'Inject custom instructions (e.g. brain "Focus on SAFE traps")\'}]});'
    if help_old_end not in s:
        print("  WARNING: help end marker not found")
        return s, False
    # Build new help rows
    new_rows = ""
    # Group header rows
    new_rows += ',{type:"row",label:"— CORPORATE TREASURY —",value:""}'
    for cmd in COMMANDS[:7]:
        new_rows += ',{type:"row",label:"' + cmd[0] + '",value:"' + cmd[1] + '"}'
    new_rows += ',{type:"row",label:"— FINTECH —",value:""}'
    for cmd in COMMANDS[7:13]:
        new_rows += ',{type:"row",label:"' + cmd[0] + '",value:"' + cmd[1] + '"}'
    new_rows += ',{type:"row",label:"— LOGISTICS —",value:""}'
    for cmd in COMMANDS[13:]:
        new_rows += ',{type:"row",label:"' + cmd[0] + '",value:"' + cmd[1] + '"}'

    # Insert before the closing ]}
    # The pattern is: ...brain..."}]});  ->  ...brain..."},NEW_ROWS]});
    # The exact text ends with: ']});  (close array, close object, close json call, semicolon)
    # We want to insert NEW_ROWS before the ]}
    help_new_end = '{type:"row",label:"brain",value:\'Inject custom instructions (e.g. brain "Focus on SAFE traps")\'}' + new_rows + ']});'
    s = s.replace(help_old_end, help_new_end)
    print("  Help command updated with 19 new commands")
    return s, True


def add_cases(s):
    """Add new case statements before case"clear"."""
    # Anchor: case"clear":return C.NextResponse.json({output:"CLEAR_SCREEN"});
    anchor = 'case"clear":return C.NextResponse.json({output:"CLEAR_SCREEN"});'
    if anchor not in s:
        print("  WARNING: clear case anchor not found")
        return s, False
    # Build all new cases
    new_cases = "".join(cmd[2] for cmd in COMMANDS)
    # Insert before case"clear"
    s = s.replace(anchor, new_cases + anchor)
    print("  Inserted 19 new case statements")
    return s, True


def main():
    os.chdir("/home/z/my-project")
    print("=== add_console_commands.py ===")
    with io.open(TERMINAL, 'r', encoding='utf-8') as f:
        s = f.read()
    original_size = len(s)

    # IDEMPOTENCY CHECK
    if 'case"ebitda":' in s:
        print("  CONSOLE COMMANDS ALREADY APPLIED — skipping")
        return

    print("\n--- Step 1: Add 19 new case statements ---")
    s, ok1 = add_cases(s)

    print("\n--- Step 2: Update help command ---")
    s, ok2 = update_help(s)

    with io.open(TERMINAL, 'w', encoding='utf-8') as f:
        f.write(s)
    print("\n  Wrote: " + TERMINAL + " (" + str(original_size) + " -> " + str(len(s)) + " bytes)")

    print("\n--- Syntax verification ---")
    r = subprocess.run(["node", "--check", TERMINAL], capture_output=True, text=True)
    if r.returncode == 0:
        print("  SYNTAX OK (node --check)")
    else:
        print("  SYNTAX ERROR:")
        err = r.stderr
        print(err[-800:] if len(err) > 800 else err)


if __name__ == "__main__":
    main()
