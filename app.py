from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf
import time, socket
socket.setdefaulttimeout(4)

app = Flask(__name__)
CORS(app)

# ── ALL NSE/BSE TRACKED STOCKS (100+) ─────────────────────────────────────────
TRACKED_STOCKS = {
  "RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","HDFCBANK":"HDFCBANK.NS","INFY":"INFY.NS",
  "ICICIBANK":"ICICIBANK.NS","KOTAKBANK":"KOTAKBANK.NS","HINDUNILVR":"HINDUNILVR.NS",
  "SBIN":"SBIN.NS","BHARTIARTL":"BHARTIARTL.NS","ITC":"ITC.NS","BAJFINANCE":"BAJFINANCE.NS",
  "WIPRO":"WIPRO.NS","HCLTECH":"HCLTECH.NS","ASIANPAINT":"ASIANPAINT.NS","AXISBANK":"AXISBANK.NS",
  "TATAMOTORS":"TATAMOTORS.NS","MARUTI":"MARUTI.NS","SUNPHARMA":"SUNPHARMA.NS",
  "ULTRACEMCO":"ULTRACEMCO.NS","TITAN":"TITAN.NS","NESTLEIND":"NESTLEIND.NS",
  "TATASTEEL":"TATASTEEL.NS","TECHM":"TECHM.NS","ONGC":"ONGC.NS","NTPC":"NTPC.NS",
  "POWERGRID":"POWERGRID.NS","M&M":"M&M.NS","BAJAJFINSV":"BAJAJFINSV.NS",
  "HDFCLIFE":"HDFCLIFE.NS","SBILIFE":"SBILIFE.NS","ADANIPORTS":"ADANIPORTS.NS",
  "ADANIENT":"ADANIENT.NS","JSWSTEEL":"JSWSTEEL.NS","GRASIM":"GRASIM.NS",
  "COALINDIA":"COALINDIA.NS","BPCL":"BPCL.NS","IOC":"IOC.NS","INDUSINDBK":"INDUSINDBK.NS",
  "CIPLA":"CIPLA.NS","DRREDDY":"DRREDDY.NS","DIVISLAB":"DIVISLAB.NS","EICHERMOT":"EICHERMOT.NS",
  "HEROMOTOCO":"HEROMOTOCO.NS","BAJAJ-AUTO":"BAJAJ-AUTO.NS","LT":"LT.NS","LTIM":"LTIM.NS",
  "HAVELLS":"HAVELLS.NS","PIDILITIND":"PIDILITIND.NS","DMART":"DMART.NS","NYKAA":"NYKAA.NS",
  "PAYTM":"PAYTM.NS","ZOMATO":"ZOMATO.NS","POLICYBZR":"POLICYBZR.NS","IRCTC":"IRCTC.NS",
  "HAL":"HAL.NS","BEL":"BEL.NS","BHEL":"BHEL.NS","SAIL":"SAIL.NS",
  "VEDL":"VEDL.NS","HINDALCO":"HINDALCO.NS","NMDC":"NMDC.NS","RECLTD":"RECLTD.NS",
  "PFC":"PFC.NS","IRFC":"IRFC.NS","HUDCO":"HUDCO.NS","RVNL":"RVNL.NS",
  "TATAPOWER":"TATAPOWER.NS","TORNTPOWER":"TORNTPOWER.NS","CESC":"CESC.NS",
  "APOLLOHOSP":"APOLLOHOSP.NS","MAXHEALTH":"MAXHEALTH.NS","FORTIS":"FORTIS.NS",
  "LUPIN":"LUPIN.NS","AUROPHARMA":"AUROPHARMA.NS","BIOCON":"BIOCON.NS",
  "TATACOMM":"TATACOMM.NS","MTNL":"MTNL.NS","INDUSTOWER":"INDUSTOWER.NS",
  "OBEROIRLTY":"OBEROIRLTY.NS","DLF":"DLF.NS","GODREJPROP":"GODREJPROP.NS",
  "PRESTIGE":"PRESTIGE.NS","SOBHA":"SOBHA.NS","BRIGADE":"BRIGADE.NS",
  "BANKBARODA":"BANKBARODA.NS","PNB":"PNB.NS","CANBK":"CANBK.NS","UNIONBANK":"UNIONBANK.NS",
  "IDBI":"IDBI.NS","FEDERALBNK":"FEDERALBNK.NS","IDFCFIRSTB":"IDFCFIRSTB.NS",
  "MUTHOOTFIN":"MUTHOOTFIN.NS","CHOLAFIN":"CHOLAFIN.NS","MANAPPURAM":"MANAPPURAM.NS",
  "PERSISTENT":"PERSISTENT.NS","MPHASIS":"MPHASIS.NS","COFORGE":"COFORGE.NS",
  "KPIT":"KPIT.NS","TRENT":"TRENT.NS","ABFRL":"ABFRL.NS","PAGEIND":"PAGEIND.NS",
  "JUBLFOOD":"JUBLFOOD.NS","DEVYANI":"DEVYANI.NS","SAPPHIRE":"SAPPHIRE.NS",
  "DIXON":"DIXON.NS","AMBER":"AMBER.NS","VOLTAS":"VOLTAS.NS","BLUESTAR":"BLUESTAR.NS",
}

# ── UNLIMITED WHALES (25) ──────────────────────────────────────────────────────
WHALES = [
  {"id":"w1","name":"Rakesh Jhunjhunwala Estate","type":"Legendary Investor","aum":"₹45,000 Cr","avatar":"🐋","style":"Value + Growth","returns":"35%+ CAGR"},
  {"id":"w2","name":"Radhakishan Damani","type":"Retail Billionaire","aum":"₹2,10,000 Cr","avatar":"🦈","style":"Deep Value","returns":"40%+ CAGR"},
  {"id":"w3","name":"Ashish Kacholia","type":"Smallcap Hunter","aum":"₹3,200 Cr","avatar":"🦁","style":"High Growth Smallcap","returns":"45%+ CAGR"},
  {"id":"w4","name":"Dolly Khanna","type":"Contrarian Investor","aum":"₹1,800 Cr","avatar":"🐘","style":"Contrarian Value","returns":"30%+ CAGR"},
  {"id":"w5","name":"Porinju Veliyath","type":"Micro/Smallcap","aum":"₹900 Cr","avatar":"🐯","style":"Turnaround Plays","returns":"38%+ CAGR"},
  {"id":"w6","name":"Vijay Kedia","type":"Growth Investor","aum":"₹1,200 Cr","avatar":"🦅","style":"SMILE Strategy","returns":"32%+ CAGR"},
  {"id":"w7","name":"Mohnish Pabrai","type":"Dhandho Investor","aum":"₹2,500 Cr","avatar":"🧠","style":"Concentrated Value","returns":"28%+ CAGR"},
  {"id":"w8","name":"Nemish Shah","type":"ENAM Founder","aum":"₹5,000 Cr","avatar":"🏦","style":"Quality at Price","returns":"25%+ CAGR"},
  {"id":"w9","name":"FII - Goldman Sachs","type":"Foreign Institution","aum":"₹85,000 Cr","avatar":"🌐","style":"Index + Momentum","returns":"18%+ CAGR"},
  {"id":"w10","name":"LIC of India","type":"Domestic Institution","aum":"₹12,00,000 Cr","avatar":"🏛️","style":"Long-term Bluechip","returns":"14%+ CAGR"},
  {"id":"w11","name":"SBI Mutual Fund","type":"Domestic MF","aum":"₹9,50,000 Cr","avatar":"🏦","style":"Diversified","returns":"16%+ CAGR"},
  {"id":"w12","name":"Mirae Asset MF","type":"Foreign MF","aum":"₹1,40,000 Cr","avatar":"🌏","style":"Growth at Value","returns":"20%+ CAGR"},
  {"id":"w13","name":"Rekha Jhunjhunwala","type":"Portfolio Inheritor","aum":"₹20,000 Cr","avatar":"👑","style":"Value + Momentum","returns":"30%+ CAGR"},
  {"id":"w14","name":"Sunil Singhania","type":"Abakkus Fund","aum":"₹3,800 Cr","avatar":"🔭","style":"GARP Strategy","returns":"28%+ CAGR"},
  {"id":"w15","name":"Kenneth Andrade","type":"Old Bridge Capital","aum":"₹2,100 Cr","avatar":"🌉","style":"Asset Light","returns":"22%+ CAGR"},
  {"id":"w16","name":"Prashant Jain","type":"Ex-HDFC MF CIO","aum":"₹3F,500 Cr","avatar":"⚖️","style":"Value Cyclicals","returns":"20%+ CAGR"},
  {"id":"w17","name":"FII - Morgan Stanley","type":"Foreign Institution","aum":"₹62,000 Cr","avatar":"🏢","style":"Quant + Growth","returns":"17%+ CAGR"},
  {"id":"w18","name":"FII - Norges Bank","type":"Sovereign Fund","aum":"₹55,000 Cr","avatar":"🇳🇴","style":"ESG + Index","returns":"15%+ CAGR"},
  {"id":"w19","name":"Akash Prakash","type":"Amansa Capital","aum":"₹4,200 Cr","avatar":"💎","style":"Quality Growth","returns":"26%+ CAGR"},
  {"id":"w20","name":"Ramesh Damani","type":"BSE Veteran","aum":"₹2,800 Cr","avatar":"📊","style":"Multibagger Hunt","returns":"33%+ CAGR"},
  {"id":"w21","name":"Madhusudan Kela","type":"MK Ventures","aum":"₹1,500 Cr","avatar":"🎯","style":"Special Situations","returns":"35%+ CAGR"},
  {"id":"w22","name":"Shankar Sharma","type":"First Global","aum":"₹1,100 Cr","avatar":"⚡","style":"Momentum Trading","returns":"40%+ CAGR"},
  {"id":"w23","name":"HDFC MF","type":"Domestic MF","aum":"₹6,80,000 Cr","avatar":"🔵","style":"Quality Largecap","returns":"16%+ CAGR"},
  {"id":"w24","name":"Nippon India MF","type":"Domestic MF","aum":"₹4,20,000 Cr","avatar":"🟠","style":"Multi-asset","returns":"15%+ CAGR"},
  {"id":"w25","name":"FII - Blackrock","type":"Global Giant","aum":"₹1,20,000 Cr","avatar":"🌑","style":"Passive + Active","returns":"14%+ CAGR"},
]

WHALE_INVESTMENTS = {
  "w1":[{"date":"2026-05-01","stock":"TATAMOTORS","action":"BUY","qty":"5,00,000","price":"₹612","value":"₹306 Cr","potential":"EV expansion — Target ₹800+","pattern":"Bought dip, +35% historically"},{"date":"2026-04-15","stock":"TITAN","action":"BUY","qty":"2,00,000","price":"₹3,210","value":"₹642 Cr","potential":"Jewellery boom + wedding season","pattern":"Accumulated over 3 months"},{"date":"2026-03-20","stock":"CRISIL","action":"BUY","qty":"80,000","price":"₹4,800","value":"₹384 Cr","potential":"Rating upgrade cycle — Target ₹6,000","pattern":"Bought before earnings"},{"date":"2026-02-10","stock":"NAZARA","action":"BUY","qty":"3,50,000","price":"₹780","value":"₹273 Cr","potential":"Gaming sector growth","pattern":"Early mover in gaming"},{"date":"2026-01-05","stock":"ESCORTS","action":"SELL","qty":"1,20,000","price":"₹3,900","value":"₹468 Cr","potential":"Book profit after 60% gain","pattern":"Exit on valuation"}],
  "w2":[{"date":"2026-05-03","stock":"DMART","action":"BUY","qty":"1,00,000","price":"₹4,200","value":"₹420 Cr","potential":"Retail expansion 500+ stores — Target ₹5,500","pattern":"Promoter increased stake"},{"date":"2026-04-20","stock":"VSTIND","action":"BUY","qty":"50,000","price":"₹3,800","value":"₹190 Cr","potential":"Cigarette volume recovery","pattern":"Value buy at 5yr low PE"},{"date":"2026-03-15","stock":"TRENT","action":"BUY","qty":"2,00,000","price":"₹5,100","value":"₹1,020 Cr","potential":"Zudio expansion — Target ₹7,000","pattern":"Bought on correction"},{"date":"2026-02-25","stock":"BAJFINANCE","action":"BUY","qty":"50,000","price":"₹6,800","value":"₹340 Cr","potential":"NBFC growth story intact","pattern":"Added on dip"}],
  "w3":[{"date":"2026-05-05","stock":"KPIT","action":"BUY","qty":"4,00,000","price":"₹1,450","value":"₹580 Cr","potential":"Auto-tech EV software — Target ₹2,200","pattern":"Smallcap to midcap re-rating"},{"date":"2026-04-18","stock":"KAYNES","action":"BUY","qty":"1,50,000","price":"₹2,800","value":"₹420 Cr","potential":"Electronics PLI beneficiary","pattern":"Early entry before order inflow"},{"date":"2026-03-10","stock":"SYRMA","action":"BUY","qty":"5,00,000","price":"₹540","value":"₹270 Cr","potential":"EMS sector boom — Target ₹800","pattern":"Bought at IPO listing dip"},{"date":"2026-02-05","stock":"WAAREE","action":"BUY","qty":"80,000","price":"₹2,100","value":"₹168 Cr","potential":"Solar module exports surge","pattern":"Pre-earnings accumulation"}],
  "w4":[{"date":"2026-05-02","stock":"RAIN","action":"BUY","qty":"10,00,000","price":"₹165","value":"₹165 Cr","potential":"Carbon black demand revival","pattern":"Contrarian buy at 3yr low"},{"date":"2026-04-10","stock":"SPICEJET","action":"BUY","qty":"20,00,000","price":"₹42","value":"₹84 Cr","potential":"Turnaround play — airline recovery","pattern":"Distressed asset buy"},{"date":"2026-03-22","stock":"THANGAMAYL","action":"BUY","qty":"1,00,000","price":"₹1,820","value":"₹182 Cr","potential":"Gold loan NBFC growth in South India","pattern":"Hidden gem — low analyst coverage"}],
  "w5":[{"date":"2026-05-07","stock":"RPGLIFE","action":"BUY","qty":"8,00,000","price":"₹220","value":"₹176 Cr","potential":"Pharma API turnaround","pattern":"Bought during regulatory clearance"},{"date":"2026-04-05","stock":"WOCKPHARMA","action":"BUY","qty":"5,00,000","price":"₹450","value":"₹225 Cr","potential":"US FDA approval pipeline","pattern":"Accumulated before USFDA inspection"}],
  "w6":[{"date":"2026-05-06","stock":"ELECON","action":"BUY","qty":"6,00,000","price":"₹680","value":"₹408 Cr","potential":"Capital goods upcycle — Target ₹1,000","pattern":"SMILE: Small, Mediocre, Improving"},{"date":"2026-04-14","stock":"TITAGARH","action":"BUY","qty":"3,00,000","price":"₹1,100","value":"₹330 Cr","potential":"Railway wagon orders surge","pattern":"Govt capex play"},{"date":"2026-03-18","stock":"CSBBANK","action":"BUY","qty":"15,00,000","price":"₹280","value":"₹420 Cr","potential":"Kerala MSME bank expansion","pattern":"Undervalued PSU bank"}],
  "w7":[{"date":"2026-05-04","stock":"COALINDIA","action":"BUY","qty":"20,00,000","price":"₹418","value":"₹836 Cr","potential":"Dividend yield 8% + energy security","pattern":"Dhandho: heads I win, tails I don't lose much"},{"date":"2026-04-22","stock":"SBIN","action":"BUY","qty":"10,00,000","price":"₹758","value":"₹758 Cr","potential":"PSB consolidation — Target ₹1,000","pattern":"Concentrated bet on banking reform"}],
  "w8":[{"date":"2026-05-08","stock":"HDFCAMC","action":"BUY","qty":"1,50,000","price":"₹3,600","value":"₹540 Cr","potential":"MF industry AUM doubling story","pattern":"Quality compounder at fair value"},{"date":"2026-04-28","stock":"BSE","action":"BUY","qty":"2,00,000","price":"₹2,800","value":"₹560 Cr","potential":"Exchange monetization — derivatives surge","pattern":"Bought after regulatory clarity"}],
  "w9":[{"date":"2026-05-09","stock":"RELIANCE","action":"BUY","qty":"50,00,000","price":"₹1,435","value":"₹7,175 Cr","potential":"Jio Financial + Retail re-rating","pattern":"Index weight increase — passive inflow"},{"date":"2026-05-01","stock":"HDFCBANK","action":"BUY","qty":"30,00,000","price":"₹1,620","value":"₹4,860 Cr","potential":"MSCI weight increase","pattern":"Rebalancing + fresh allocation"},{"date":"2026-04-15","stock":"INFY","action":"SELL","qty":"15,00,000","price":"₹1,540","value":"₹2,310 Cr","potential":"IT sector rotation out","pattern":"Reduced weight on guidance cut risk"}],
  "w10":[{"date":"2026-05-08","stock":"BAJFINANCE","action":"BUY","qty":"25,00,000","price":"₹6,900","value":"₹1,725 Cr","potential":"Long-term NBFC hold — 20yr story","pattern":"LIC systematic accumulation"},{"date":"2026-04-20","stock":"HAL","action":"BUY","qty":"10,00,000","price":"₹3,800","value":"₹3,800 Cr","potential":"Defence PLI — ₹1L Cr order book","pattern":"Strategic holding in PSU defence"},{"date":"2026-03-10","stock":"ITC","action":"BUY","qty":"1,00,00,000","price":"₹415","value":"₹4,150 Cr","potential":"FMCG demerger value unlock","pattern":"Largest LIC holding — income + growth"}],
  "w11":[{"date":"2026-05-07","stock":"TCS","action":"BUY","qty":"20,00,000","price":"₹3,890","value":"₹7,780 Cr","potential":"AI services + large deal wins","pattern":"SIP inflow — systematic buy"},{"date":"2026-05-03","stock":"MARUTI","action":"BUY","qty":"5,00,000","price":"₹12,400","value":"₹6,200 Cr","potential":"SUV cycle + CNG dominance","pattern":"Largecap rebalance buy"}],
  "w12":[{"date":"2026-05-06","stock":"ZOMATO","action":"BUY","qty":"1,00,00,000","price":"₹215","value":"₹2,150 Cr","potential":"Quick commerce Blinkit dominance","pattern":"Growth at reasonable price"},{"date":"2026-04-30","stock":"NYKAA","action":"BUY","qty":"2,00,00,000","price":"₹172","value":"₹3,440 Cr","potential":"Beauty market $28B opportunity","pattern":"Bought at 52-week low"}],
  "w13":[{"date":"2026-05-05","stock":"STARHEALTH","action":"BUY","qty":"30,00,000","price":"₹480","value":"₹1,440 Cr","potential":"Health insurance penetration story","pattern":"Family legacy holding"},{"date":"2026-04-12","stock":"METROPOLIS","action":"BUY","qty":"5,00,000","price":"₹1,820","value":"₹910 Cr","potential":"Diagnostics sector re-rating","pattern":"Healthcare portfolio expansion"}],
  "w14":[{"date":"2026-05-04","stock":"DIXON","action":"BUY","qty":"3,00,000","price":"₹13,500","value":"₹405 Cr","potential":"PLI electronics — Samsung/Apple supply chain","pattern":"GARP: 30% growth at 40x PE"},{"date":"2026-04-15","stock":"KAYNES","action":"BUY","qty":"2,00,000","price":"₹2,750","value":"₹550 Cr","potential":"EMS sector — 5x revenue potential","pattern":"Early stage compounder"}],
  "w15":[{"date":"2026-05-03","stock":"PERSISTENT","action":"BUY","qty":"2,50,000","price":"₹4,800","value":"₹1,200 Cr","potential":"GenAI deals + US banking vertical","pattern":"Asset light IT compounder"},{"date":"2026-04-10","stock":"COFORGE","action":"BUY","qty":"3,00,000","price":"₹6,200","value":"₹1,860 Cr","potential":"BFSI + BPS transformation","pattern":"Niche IT at reasonable PE"}],
  "w16":[{"date":"2026-05-02","stock":"ONGC","action":"BUY","qty":"50,00,000","price":"₹263","value":"₹1,315 Cr","potential":"Oil PSU — dividend + capex recovery","pattern":"Value cyclical at trough"},{"date":"2026-04-05","stock":"BPCL","action":"BUY","qty":"30,00,000","price":"₹312","value":"₹936 Cr","potential":"Refinery upgrade + marketing margin","pattern":"Bought at GRM trough"}],
  "w17":[{"date":"2026-05-09","stock":"ICICIBANK","action":"BUY","qty":"40,00,000","price":"₹1,245","value":"₹4,980 Cr","potential":"Best-in-class ROE 18%+ bank","pattern":"Global EM fund allocation"},{"date":"2026-05-01","stock":"TATASTEEL","action":"SELL","qty":"20,00,000","price":"₹148","value":"₹2,960 Cr","potential":"China steel glut risk reduction","pattern":"Risk-off metals rotation"}],
  "w18":[{"date":"2026-05-08","stock":"INFOSYS","action":"BUY","qty":"25,00,000","price":"₹1,545","value":"₹3,862 Cr","potential":"ESG tech leader — governance premium","pattern":"Sovereign fund ESG mandate"},{"date":"2026-04-25","stock":"NTPC","action":"BUY","qty":"60,00,000","price":"₹345","value":"₹2,070 Cr","potential":"Green energy transition play","pattern":"ESG utility allocation"}],
  "w19":[{"date":"2026-05-07","stock":"TATAPOWER","action":"BUY","qty":"20,00,000","price":"₹392","value":"₹784 Cr","potential":"Solar + EV charging — 3x growth","pattern":"Quality growth at inflection"},{"date":"2026-04-18","stock":"POLYCAB","action":"BUY","qty":"5,00,000","price":"₹5,400","value":"₹2,700 Cr","potential":"Infra + real estate wiring boom","pattern":"Monopoly in cables"}],
  "w20":[{"date":"2026-05-06","stock":"BSE","action":"BUY","qty":"4,00,000","price":"₹2,750","value":"₹1,100 Cr","potential":"India market depth — 10x in 10 years","pattern":"Multibagger: exchange is the toll booth"},{"date":"2026-04-20","stock":"CDSL","action":"BUY","qty":"8,00,000","price":"₹1,650","value":"₹1,320 Cr","potential":"Demat account growth — 16 Cr accounts by 2027","pattern":"Duopoly with NSDL"}],
  "w21":[{"date":"2026-05-05","stock":"SUZLON","action":"BUY","qty":"1,00,00,000","price":"₹52","value":"₹520 Cr","potential":"Wind energy revival — 10 GW pipeline","pattern":"Special situation: debt-free turnaround"},{"date":"2026-04-10","stock":"RPOWER","action":"BUY","qty":"5,00,00,000","price":"₹18","value":"₹900 Cr","potential":"Anil Ambani group restructuring","pattern":"Deep distressed play"}],
  "w22":[{"date":"2026-05-09","stock":"NIFTY-BET","action":"BUY","qty":"Futures","price":"22,800","value":"₹500 Cr","potential":"Breakout above 23,000 — Target 24,500","pattern":"Momentum: 200DMA cross + volume surge"},{"date":"2026-05-07","stock":"HDFCBANK","action":"BUY","qty":"Options Call","price":"₹1,620 Strike","value":"₹80 Cr","potential":"FII buying + MSCI weight increase","pattern":"Options momentum play"}],
  "w23":[{"date":"2026-05-08","stock":"RELIANCE","action":"BUY","qty":"35,00,000","price":"₹1,440","value":"₹5,040 Cr","potential":"Nifty50 rebalancing + JFS listing","pattern":"Passive inflow on index weight"},{"date":"2026-05-02","stock":"HCLTECH","action":"BUY","qty":"15,00,000","price":"₹1,680","value":"₹2,520 Cr","potential":"AI + cloud deals momentum","pattern":"Large-cap IT systematic buy"}],
  "w24":[{"date":"2026-05-07","stock":"ADANIPORTS","action":"BUY","qty":"20,00,000","price":"₹1,280","value":"₹2,560 Cr","potential":"Port capacity + logistics expansion","pattern":"Infrastructure theme allocation"},{"date":"2026-04-28","stock":"GODREJPROP","action":"BUY","qty":"5,00,000","price":"₹2,800","value":"₹1,400 Cr","potential":"Premium real estate launch pipeline","pattern":"Real estate upcycle play"}],
  "w25":[{"date":"2026-05-09","stock":"INFY","action":"SELL","qty":"30,00,000","price":"₹1,542","value":"₹4,626 Cr","potential":"Reduce IT weight on global slowdown","pattern":"Risk-off global macro"},{"date":"2026-05-05","stock":"ICICIBANK","action":"BUY","qty":"50,00,000","price":"₹1,240","value":"₹6,200 Cr","potential":"India private bank — best risk-reward in EM","pattern":"Blackrock India overweight call"}],
}

# ── 50+ ANNOUNCEMENTS ─────────────────────────────────────────────────────────
ANNOUNCEMENTS = [
  {"id":1,"company":"RELIANCE","type":"Earnings","title":"Q4 FY26 PAT up 18% YoY at ₹18,951 Cr, beats estimates","sentiment":"Positive","impact":9,"time":"2h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Retail + Jio drove growth; net debt reduced by ₹12,000 Cr — strong balance sheet signal","hype":92,"pattern":"Post-earnings gap up historically 4-7%"},
  {"id":2,"company":"TCS","type":"Deal","title":"Wins ₹12,000 Cr 5-year AI transformation deal with UK bank","sentiment":"Positive","impact":9,"time":"3h ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Largest deal in TCS history; adds 2% to FY27 revenue — re-rating catalyst","hype":88,"pattern":"Large deal wins precede 8-12% rally within 30 days"},
  {"id":3,"company":"HDFCBANK","type":"Dividend","title":"Declares ₹22/share dividend — highest ever; record date June 5","sentiment":"Positive","impact":8,"time":"1h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Yield at CMP = 1.4%; signals strong capital position and RBI approval","hype":79,"pattern":"Dividend announcement triggers 3-5% short-term upside"},
  {"id":4,"company":"TATAMOTORS","type":"M&A","title":"Acquires 26% stake in EV battery startup for ₹2,400 Cr","sentiment":"Positive","impact":8,"time":"4h ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Secures battery supply chain for Nexon EV 2.0; reduces cost by 15%","hype":84,"pattern":"Strategic acquisition — stock rallies 5-8% in 2 weeks"},
  {"id":5,"company":"INFY","type":"Earnings","title":"Q4 PAT ₹7,033 Cr; FY27 revenue guidance 8-10% — above Street est","sentiment":"Positive","impact":8,"time":"5h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"GenAI deal TCV $2.1B in Q4; margin expansion of 80bps — analyst upgrades incoming","hype":81,"pattern":"Guidance beat = 6-10% gap up at open"},
  {"id":6,"company":"ADANIENT","type":"Regulatory","title":"SEBI clears Adani Group; all allegations by Hindenburg dismissed","sentiment":"Positive","impact":10,"time":"6h ago","source":"SEBI Order","link":"https://www.sebi.gov.in","insight":"Legal overhang removed; FPI and institutional re-entry expected — massive re-rating","hype":97,"pattern":"Regulatory clearance = 15-25% gap up across group stocks"},
  {"id":7,"company":"ZOMATO","type":"Corporate Action","title":"Blinkit hits 1 crore daily orders; Q4 EBITDA positive for first time","sentiment":"Positive","impact":9,"time":"7h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Quick commerce inflection point; Blinkit alone worth ₹80,000 Cr per analyst models","hype":89,"pattern":"Milestone + profitability = strong re-rating event"},
  {"id":8,"company":"SUNPHARMA","type":"Regulatory","title":"USFDA approves blockbuster dermatology drug Ilumya for new indication","sentiment":"Positive","impact":9,"time":"8h ago","source":"USFDA","link":"https://www.fda.gov","insight":"Ilumya peak sales potential $500M in US market; adds ₹3,000 Cr to revenue by FY28","hype":85,"pattern":"USFDA approval = 8-15% gap up; sustained rally 30 days"},
  {"id":9,"company":"BAJFINANCE","type":"Earnings","title":"Q4 AUM crosses ₹3.8 lakh Cr; NPA stable at 0.25% — clean book","sentiment":"Positive","impact":8,"time":"9h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"GNPA at historic low; consumer lending boom continues — premium valuations justified","hype":77,"pattern":"Clean NPA quarter = stock outperforms sector by 5%"},
  {"id":10,"company":"HAL","type":"Deal","title":"Gets ₹62,000 Cr order for 156 LCA Tejas Mk1A from Indian Air Force","sentiment":"Positive","impact":10,"time":"10h ago","source":"Ministry of Defence","link":"https://mod.gov.in","insight":"Largest defence order in Indian history; 10-year revenue visibility — re-rating to ₹6,000+","hype":95,"pattern":"Defence mega-order = 10-20% rally; sustained upcycle"},
  {"id":11,"company":"RVNL","type":"Deal","title":"Wins ₹4,200 Cr railway electrification project in Northeast","sentiment":"Positive","impact":8,"time":"11h ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Order book now ₹92,000 Cr — 4x FY26 revenue; execution key watch","hype":80,"pattern":"Order wins = 5-8% rally for railway PSUs"},
  {"id":12,"company":"WIPRO","type":"Management","title":"New CEO Srinivas Pallia announces AI-first transformation roadmap","sentiment":"Positive","impact":7,"time":"12h ago","source":"Press Release","link":"https://www.wipro.com","insight":"$1B GenAI investment over 3 years; targets 5% margin improvement — credibility test","hype":68,"pattern":"Strategic roadmap + new CEO = sentiment improvement"},
  {"id":13,"company":"IRCTC","type":"Corporate Action","title":"Stock split 1:5 approved; record date announced for June 20","sentiment":"Positive","impact":7,"time":"13h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Retail participation to surge post-split; liquidity improvement expected","hype":72,"pattern":"Stock split = 5-10% pre-split rally; retail demand surge"},
  {"id":14,"company":"PAYTM","type":"Regulatory","title":"RBI lifts all restrictions; Paytm Payments Bank fully operational","sentiment":"Positive","impact":10,"time":"14h ago","source":"RBI Circular","link":"https://www.rbi.org.in","insight":"Business back to full capacity; loss of ₹800 Cr/quarter reversed — strong rebound","hype":93,"pattern":"Regulatory reversal = 20-30% gap up; short squeeze likely"},
  {"id":15,"company":"DLF","type":"Earnings","title":"Q4 pre-sales ₹7,200 Cr — highest ever; launches 3 luxury projects","sentiment":"Positive","impact":8,"time":"15h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Luxury real estate demand insatiable; net debt zero; JDA pipeline ₹25,000 Cr","hype":82,"pattern":"Real estate pre-sales beat = 6-9% rally"},
  {"id":16,"company":"COALINDIA","type":"Dividend","title":"Interim dividend ₹7.50/share; total FY26 dividend ₹27/share — yield 6.5%","sentiment":"Positive","impact":7,"time":"16h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Government cash flow requirement met; PSU dividend yield play intact","hype":65,"pattern":"High-yield PSU dividend = institutional accumulation"},
  {"id":17,"company":"DIXON","type":"Partnership","title":"Signs 5-year Samsung display manufacturing JV — ₹8,000 Cr capex","sentiment":"Positive","impact":9,"time":"17h ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"India's first large display fab; PLI benefits + Samsung supply lock-in","hype":87,"pattern":"Global OEM JV = 12-18% re-rating for EMS stocks"},
  {"id":18,"company":"ICICIBANK","type":"Earnings","title":"Q4 ROE hits 18.4% — best in 15 years; NIM expansion to 4.6%","sentiment":"Positive","impact":8,"time":"18h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Best-in-class metrics; credit cost at 5yr low — premium multiple expansion imminent","hype":79,"pattern":"ROE > 18% quarter = 4-6% post-result rally"},
  {"id":19,"company":"MARUTI","type":"Earnings","title":"Q4 PAT ₹3,878 Cr up 47% YoY; launches Fronx EV at ₹9.99 lakh","sentiment":"Positive","impact":8,"time":"19h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"CNG + EV dual launch strategy; market share 43% in Q4 — dominance continues","hype":76,"pattern":"Earnings beat + new launch = 5-8% sustained rally"},
  {"id":20,"company":"NTPC","type":"Corporate Action","title":"NTPC Green Energy IPO at ₹108-114; GMP ₹25 — 22% premium","sentiment":"Positive","impact":8,"time":"20h ago","source":"SEBI DRHP","link":"https://www.sebi.gov.in","insight":"India's largest green energy IPO; parent backing + RE target 60 GW by 2032","hype":83,"pattern":"Green IPO from NTPC = strong listing premium 15-25%"},
  {"id":21,"company":"BHARTIARTL","type":"Corporate Action","title":"Airtel acquires Vi spectrum in 5 circles — telecom consolidation accelerates","sentiment":"Positive","impact":8,"time":"21h ago","source":"DoT Filing","link":"https://dot.gov.in","insight":"Market share to 40%+; ARPU expansion story strengthens — ₹300 ARPU by FY28","hype":78,"pattern":"Spectrum acquisition = near-term capex drag but long-term gain"},
  {"id":22,"company":"TATAPOWER","type":"Deal","title":"Wins 4 GW solar EPC contract from SECI — largest ever renewable order","sentiment":"Positive","impact":9,"time":"22h ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Revenue visibility 3 years; renewable capacity 10 GW by FY27","hype":84,"pattern":"Large renewable order = 8-12% rally for power stocks"},
  {"id":23,"company":"PERSISTENT","type":"Deal","title":"Wins $180M 3-year GenAI deal with Fortune 100 US insurer","sentiment":"Positive","impact":9,"time":"23h ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"GenAI TCV growing 60% QoQ; targets $2B revenue by FY27 — premium IT play","hype":86,"pattern":"Mid-cap IT deal win = 10-15% re-rating"},
  {"id":24,"company":"TITAN","type":"Earnings","title":"Q4 jewellery revenue ₹8,900 Cr up 22%; wedding season demand strong","sentiment":"Positive","impact":7,"time":"1d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Gold price tailwind + premiumization; Tanishq gaining vs unorganised","hype":71,"pattern":"Titan Q4 beats = 4-6% post-result rally"},
  {"id":25,"company":"APOLLO HOSP","type":"Expansion","title":"Opens 3 new hospitals in Tier-2 cities; targets 10,000 beds by FY28","sentiment":"Positive","impact":7,"time":"1d ago","source":"Press Release","link":"https://www.apollohospitals.com","insight":"Healthcare infra gap in Tier-2; Apollo Digital revenue ₹1,200 Cr and growing","hype":69,"pattern":"Hospital expansion = 5-7% rally for healthcare stocks"},
  {"id":26,"company":"SBIN","type":"Earnings","title":"SBI Q4 PAT ₹19,500 Cr — first time crossing ₹19K Cr; NPA at 10yr low","sentiment":"Positive","impact":8,"time":"1d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Book value ₹610; P/B 1.2x — cheap for quality; ₹1,000 target reiterated","hype":77,"pattern":"SBI PAT record = institutional buying + re-rating"},
  {"id":27,"company":"BAJAJ-AUTO","type":"Earnings","title":"Q4 EV motorcycle sales 1.2 lakh units; export revenue ₹3,200 Cr","sentiment":"Positive","impact":7,"time":"1d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Chetak EV gaining share; ASEAN export ramp-up — international diversification","hype":68,"pattern":"EV + export beat = 5% rally"},
  {"id":28,"company":"NYKAA","type":"Partnership","title":"Exclusive partnership with Sephora — 200 stores pan-India by 2027","sentiment":"Positive","impact":8,"time":"1d ago","source":"Press Release","link":"https://www.nykaa.com","insight":"Premium beauty market $5B opportunity; Sephora brand pull drives footfall","hype":75,"pattern":"Brand exclusive partnership = 10-12% gap up"},
  {"id":29,"company":"TECHM","type":"M&A","title":"Acquires US cybersecurity firm for $320M — strengthens BFSI vertical","sentiment":"Positive","impact":7,"time":"1d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Cybersecurity $50B TAM; bolt-on acquisition fills key gap in portfolio","hype":66,"pattern":"Strategic US acquisition = 5-8% post-announcement rally"},
  {"id":30,"company":"LT","type":"Deal","title":"Wins ₹45,000 Cr infrastructure mega-project in Saudi Arabia","sentiment":"Positive","impact":9,"time":"1d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Middle East capex boom; L&T order book crosses ₹5 lakh Cr — revenue visibility 4 years","hype":88,"pattern":"Mega overseas order = 8-12% rally for L&T"},
  {"id":31,"company":"VEDL","type":"Dividend","title":"Vedanta declares ₹40/share special dividend ahead of demerger","sentiment":"Positive","impact":8,"time":"2d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Yield 12% at CMP; demerger to unlock value in Zinc, Oil, Aluminum separately","hype":80,"pattern":"High special dividend = 5-10% short-term pop"},
  {"id":32,"company":"IRFC","type":"Earnings","title":"Q4 PAT ₹1,720 Cr up 15%; sanctions ₹1.2 lakh Cr in FY26","sentiment":"Positive","impact":7,"time":"2d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Railway capex guarantee; near-zero credit risk — defensive compounder","hype":62,"pattern":"IRFC steady beats = 3-5% post-result move"},
  {"id":33,"company":"POLYCAB","type":"Earnings","title":"Q4 revenue ₹5,200 Cr up 28%; FMEG segment doubles","sentiment":"Positive","impact":7,"time":"2d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Real estate + infra wiring boom; B2C FMEG growing 50% — Havells challenger","hype":70,"pattern":"Revenue beat + FMEG traction = 6-8% rally"},
  {"id":34,"company":"INDUSINDBK","type":"Management","title":"New MD Suresh Ganapathy announces ₹2,000 Cr provisions clean-up plan","sentiment":"Negative","impact":7,"time":"2d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"One-time clean-up positive long-term; stock may dip 5-8% short-term on provisions","hype":55,"pattern":"Kitchen sinking = short-term pain, 6-month buy opportunity"},
  {"id":35,"company":"KOTAKBANK","type":"Regulatory","title":"RBI removes IT restrictions on Kotak — app can onboard new customers","sentiment":"Positive","impact":9,"time":"2d ago","source":"RBI Circular","link":"https://www.rbi.org.in","insight":"Digital acquisition channel restored; 2 million customer addition/month expected","hype":87,"pattern":"Regulatory clearance = 8-12% gap up; institutional re-entry"},
  {"id":36,"company":"HINDALCO","type":"M&A","title":"Novelis (Hindalco sub) acquires US aluminum recycler for $900M","sentiment":"Positive","impact":7,"time":"2d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Circular economy play; recycled aluminum premium margin 25% above primary","hype":67,"pattern":"Novelis deal = 5-7% rally for Hindalco"},
  {"id":37,"company":"TRENT","type":"Earnings","title":"Zudio opens 150 stores in Q4; revenue ₹3,800 Cr up 54% YoY","sentiment":"Positive","impact":9,"time":"2d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Fastest retail expansion in India; Zudio targeting 1,000 stores by FY28 — Tata success story","hype":91,"pattern":"Trent Zudio milestone = 10-15% rally"},
  {"id":38,"company":"SUZLON","type":"Deal","title":"Bags 1,000 MW wind order from Adani Green — largest ever for company","sentiment":"Positive","impact":9,"time":"3d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Debt-free turnaround complete; order book ₹18,000 Cr covers 3 years revenue","hype":89,"pattern":"Turnaround + mega order = 12-18% rally"},
  {"id":39,"company":"PAGEIND","type":"Earnings","title":"Q4 EPS ₹380 — beats est by 12%; volume growth 8% despite price hike","sentiment":"Positive","impact":7,"time":"3d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Premium innerwear brand pricing power; rural distribution expansion key driver","hype":63,"pattern":"Jockey brand loyalty = consistent 4-6% beat reaction"},
  {"id":40,"company":"BEL","type":"Deal","title":"Secures ₹26,000 Cr defence electronics order from Navy and Army","sentiment":"Positive","impact":9,"time":"3d ago","source":"Ministry of Defence","link":"https://mod.gov.in","insight":"Radar + BMS systems; order book 4x revenue — 5-year growth visibility","hype":86,"pattern":"Defence order announcements = 8-12% rally for BEL"},
  {"id":41,"company":"JUBLFOOD","type":"Expansion","title":"Domino's crosses 2,000 stores; same-store sales growth 12% YoY","sentiment":"Positive","impact":7,"time":"3d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"QSR recovery complete; delivery platform dependency reducing — margins improving","hype":65,"pattern":"SSG > 10% = 5-7% re-rating for QSR stocks"},
  {"id":42,"company":"GODREJPROP","type":"Earnings","title":"Q4 bookings ₹6,500 Cr — record; launches 8 new projects in FY27","sentiment":"Positive","impact":8,"time":"3d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"NCR luxury + Pune projects oversubscribed; brand premium in real estate intact","hype":74,"pattern":"Bookings record = 6-10% rally for realty stocks"},
  {"id":43,"company":"BIOCON","type":"Regulatory","title":"Biosimilar Tremfya gets EMA approval — EU market entry Q3 FY27","sentiment":"Positive","impact":8,"time":"3d ago","source":"EMA Press Release","link":"https://www.ema.europa.eu","insight":"$8B immunology market; 15% market share target; adds ₹1,200 Cr revenue by FY28","hype":78,"pattern":"EMA approval = 10-12% gap up for pharma"},
  {"id":44,"company":"MUTHOOTFIN","type":"Earnings","title":"Q4 AUM ₹96,000 Cr; gold loan disbursals up 35% — rural credit boom","sentiment":"Positive","impact":7,"time":"4d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Gold price rally = AUM growth without credit risk; NIM 11% — best in NBFC","hype":67,"pattern":"Gold loan AUM beat = 4-6% rally"},
  {"id":45,"company":"HAVELLS","type":"Earnings","title":"Q4 cables revenue ₹2,400 Cr up 31%; Lloyd AC market share hits 20%","sentiment":"Positive","impact":7,"time":"4d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Summer demand + real estate boom dual tailwind; Lloyd AC turnaround complete","hype":66,"pattern":"Havells cable + Lloyd beat = 5-7% post-result move"},
  {"id":46,"company":"LUPIN","type":"Regulatory","title":"USFDA issues 3 approvals for US generics — Spiriva, Advair, Symbicort","sentiment":"Positive","impact":8,"time":"4d ago","source":"USFDA","link":"https://www.fda.gov","insight":"Complex inhaler generics — limited competition; combined peak sales $2B","hype":80,"pattern":"Multiple USFDA approvals = 8-12% sustained rally"},
  {"id":47,"company":"DMART","type":"Expansion","title":"DMart opens 50 stores in Q4; targets 100 stores in FY27","sentiment":"Positive","impact":8,"time":"4d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"SSSG 10.5%; gross margin expansion 20bps — Damani's retail machine unstoppable","hype":76,"pattern":"DMart store expansion = consistent re-rating"},
  {"id":48,"company":"AXISBANK","type":"M&A","title":"Acquires Max Life 7% additional stake — becomes 20% co-promoter","sentiment":"Positive","impact":7,"time":"4d ago","source":"IRDAI Filing","link":"https://irdai.gov.in","insight":"Insurance bancassurance synergy; Max Life embedded value ₹28,000 Cr","hype":64,"pattern":"Insurance stake increase = 4-6% rally for private banks"},
  {"id":49,"company":"KPIT","type":"Deal","title":"Signs 5-year $220M EV software deal with European OEM","sentiment":"Positive","impact":9,"time":"5d ago","source":"NSE Filing","link":"https://www.nseindia.com","insight":"Software-defined vehicle trend; KPIT positioned as picks-and-shovels EV play","hype":85,"pattern":"Automotive software deal = 12-15% re-rating for KPIT"},
  {"id":50,"company":"IRCTC","type":"Earnings","title":"Q4 revenue ₹1,180 Cr up 22%; convenience fee hike approved by MoR","sentiment":"Positive","impact":8,"time":"5d ago","source":"BSE Filing","link":"https://www.bseindia.com","insight":"Monopoly + pricing power; internet ticketing volume 2 Cr/day — steady compounder","hype":73,"pattern":"Fee hike approval = 8-10% re-rating"},
]

GOVT_NEWS = [
  {"id":1,"title":"RBI cuts repo rate by 25bps to 6.0% — cheapest credit in 4 years","category":"Monetary Policy","impact":9,"sentiment":"Positive","time":"1h ago","source":"RBI","link":"https://www.rbi.org.in","insight":"EMI reduction + credit growth boost; HDFC Bank, SBI, housing finance rally expected","sectors":["Banking","NBFC","Realty"]},
  {"id":2,"title":"SEBI mandates T+0 settlement for top 500 stocks from June 2026","category":"Regulation","impact":8,"sentiment":"Positive","time":"3h ago","source":"SEBI","link":"https://www.sebi.gov.in","insight":"Liquidity boost; brokers like Angel, Zerodha benefit; FII inflows accelerate","sectors":["Brokerage","Fintech"]},
  {"id":3,"title":"PLI scheme extended to 14 new sectors including toys, furniture, EV components","category":"Policy","impact":9,"sentiment":"Positive","time":"6h ago","source":"DPIIT","link":"https://dpiit.gov.in","insight":"Rs 2.5 lakh Cr capex trigger; Dixon, Amber, Havells among key beneficiaries","sectors":["Manufacturing","EV","Electronics"]},
  {"id":4,"title":"Budget 2026: Capital gains tax harmonized — LTCG 10% across all assets","category":"Budget","impact":8,"sentiment":"Neutral","time":"1d ago","source":"Finance Ministry","link":"https://finmin.nic.in","insight":"MF equity and debt on par; short-term volatility, long-term simplification positive","sectors":["Mutual Funds","Equity Market"]},
  {"id":5,"title":"NITI Aayog releases India 2047 semiconductor roadmap — Rs 3 lakh Cr investment","category":"Policy","impact":10,"sentiment":"Positive","time":"1d ago","source":"NITI Aayog","link":"https://niti.gov.in","insight":"TATA Semicon, Micron, Kaynes Technology direct beneficiaries; decade-long theme","sectors":["Semiconductors","Electronics"]},
  {"id":6,"title":"FDI cap in insurance raised to 100% — foreign players can enter India","category":"Regulation","impact":8,"sentiment":"Positive","time":"1d ago","source":"IRDAI","link":"https://irdai.gov.in","insight":"Competition increases but market expansion accelerates; LIC, New India may consolidate","sectors":["Insurance"]},
  {"id":7,"title":"National Monetization Pipeline 2.0: Rs 10 lakh Cr assets to be monetized by 2030","category":"Infrastructure","impact":9,"sentiment":"Positive","time":"2d ago","source":"Finance Ministry","link":"https://finmin.nic.in","insight":"Highways, railways, airports, ports — NHAI, IRFC, Adani Ports top beneficiaries","sectors":["Infrastructure","Logistics"]},
  {"id":8,"title":"Green Hydrogen Mission: Rs 19,744 Cr incentive for 5 MT green H2 by 2030","category":"Energy","impact":9,"sentiment":"Positive","time":"2d ago","source":"MNRE","link":"https://mnre.gov.in","insight":"Reliance, NTPC Green, Adani Green positioning; export market $100B opportunity","sectors":["Green Energy","Chemicals"]},
  {"id":9,"title":"UDAN 5.0 launches 100 new routes — tier-2 city air connectivity focus","category":"Aviation","impact":7,"sentiment":"Positive","time":"2d ago","source":"MoCA","link":"https://civilaviation.gov.in","insight":"IndiGo, SpiceJet, Air India gain routes; airport infra stocks GMR, AAHL benefit","sectors":["Aviation","Infrastructure"]},
  {"id":10,"title":"GST Council reduces EV rate from 5% to 0% — all categories included","category":"Tax","impact":10,"sentiment":"Positive","time":"2d ago","source":"GST Council","link":"https://gstcouncil.gov.in","insight":"Tata Motors EV, Ola Electric, Ather demand surge expected; 40% cost reduction","sectors":["EV","Auto"]},
  {"id":11,"title":"Defence export target raised to Rs 50,000 Cr by 2029 — new corridor zones","category":"Defence","impact":8,"sentiment":"Positive","time":"3d ago","source":"Ministry of Defence","link":"https://mod.gov.in","insight":"HAL, BEL, MTAR, Data Patterns, Paras Defence — all in export queue","sectors":["Defence","PSU"]},
  {"id":12,"title":"PMAY Urban 2.0: 1 crore affordable homes — Rs 2.5 lakh Cr spending plan","category":"Housing","impact":9,"sentiment":"Positive","time":"3d ago","source":"MoHUA","link":"https://mohua.gov.in","insight":"Cement (UltraTech, Shree), steel (JSW, SAIL), tile (Kajaria) stocks to rally","sectors":["Realty","Cement","Steel"]},
  {"id":13,"title":"National Logistics Policy: multimodal hubs in 35 cities; rail freight priority","category":"Logistics","impact":8,"sentiment":"Positive","time":"3d ago","source":"Commerce Ministry","link":"https://commerce.gov.in","insight":"Container Corp, VRL, Mahindra Logistics, Allcargo benefit from freight efficiency","sectors":["Logistics","Railways"]},
  {"id":14,"title":"SEBI cracks down on P-note opacity — mandatory disclosure for all FPI holdings","category":"Regulation","impact":7,"sentiment":"Negative","time":"3d ago","source":"SEBI","link":"https://www.sebi.gov.in","insight":"Short-term outflow risk from opaque FPIs; long-term market integrity positive","sectors":["Equity Market","FPI"]},
  {"id":15,"title":"Critical Minerals Mission: lithium, cobalt, nickel reserves to be auctioned","category":"Mining","impact":9,"sentiment":"Positive","time":"4d ago","source":"Mines Ministry","link":"https://mines.gov.in","insight":"NMDC, HZL, MOIL, NALCO positioned for critical mineral extraction push","sectors":["Mining","EV Battery"]},
  {"id":16,"title":"India-UK FTA finalized — zero duty on 85% Indian goods including textiles, pharma","category":"Trade","impact":9,"sentiment":"Positive","time":"4d ago","source":"Commerce Ministry","link":"https://commerce.gov.in","insight":"Arvind, Welspun, Sun Pharma, Dr Reddy's gain UK market access advantage","sectors":["Textiles","Pharma","Exports"]},
  {"id":17,"title":"National Education Policy 2.0: EdTech regulation, 50% public university digitization","category":"Education","impact":7,"sentiment":"Positive","time":"4d ago","source":"Education Ministry","link":"https://education.gov.in","insight":"School infra stocks benefit; EdTech regulation brings order to sector","sectors":["EdTech","Infrastructure"]},
  {"id":18,"title":"Solar panel import duty reduced to 5% — domestic manufacturing to get PLI boost","category":"Energy","impact":8,"sentiment":"Positive","time":"4d ago","source":"MNRE","link":"https://mnre.gov.in","insight":"Short-term: Waaree, Adani Solar face price pressure; long-term: deployment acceleration","sectors":["Solar","Renewables"]},
  {"id":19,"title":"RBI introduces CBDC retail pilot in 50 cities — UPI integration by Q2 FY27","category":"Fintech","impact":8,"sentiment":"Positive","time":"5d ago","source":"RBI","link":"https://www.rbi.org.in","insight":"Payment rails evolve; NPCI, SBI Card, HDFC Bank CBDC infrastructure plays","sectors":["Fintech","Banking"]},
  {"id":20,"title":"Atmanirbhar Bharat 4.0: Rs 1.5 lakh Cr for deep-tech startups and unicorn creation","category":"Startup","impact":8,"sentiment":"Positive","time":"5d ago","source":"DPIIT","link":"https://dpiit.gov.in","insight":"AI, robotics, biotech startups; BSE SME IPO pipeline to surge in FY27","sectors":["Technology","Startup"]},
  {"id":21,"title":"RERA amendment: faster grievance redressal, penalty doubled for builders","category":"Regulation","impact":7,"sentiment":"Negative","time":"5d ago","source":"MoHUA","link":"https://mohua.gov.in","insight":"Short-term builder NIM pressure; buyer confidence boost positive for mid-term sales","sectors":["Realty"]},
  {"id":22,"title":"National Water Mission: Rs 87,000 Cr for Jal Jeevan piped water in 1.3L villages","category":"Infrastructure","impact":8,"sentiment":"Positive","time":"5d ago","source":"Jal Shakti Ministry","link":"https://jalshakti.gov.in","insight":"Finolex Pipes, Astral, Supreme, Prince Pipes — rural water infra play","sectors":["Infrastructure","Building Materials"]},
  {"id":23,"title":"Pharma Vision 2035: India to be $100B pharma export hub — new clusters planned","category":"Pharma","impact":9,"sentiment":"Positive","time":"6d ago","source":"Pharma Ministry","link":"https://pharmaceuticals.gov.in","insight":"Sun, Cipla, Dr Reddy, Divi's benefit; API sector gets dedicated industrial parks","sectors":["Pharma","API"]},
  {"id":24,"title":"Digital India 3.0: 5G coverage 100% by 2027; govt to spend Rs 1.5 lakh Cr on digital infra","category":"Technology","impact":9,"sentiment":"Positive","time":"6d ago","source":"MeitY","link":"https://meity.gov.in","insight":"Jio, Airtel, Nokia, Ericsson India, Tejas Networks, HFCL — telecom infra wave","sectors":["Telecom","Technology"]},
  {"id":25,"title":"MSP hike: Paddy Rs 2,425/qtl (+7%), Wheat Rs 2,360/qtl (+6%) for Kharif 2026","category":"Agriculture","impact":7,"sentiment":"Positive","time":"6d ago","source":"CCEA","link":"https://pib.gov.in","insight":"Rural income boost — FMCG (HUL, ITC, Dabur), two-wheelers (Hero, TVS) demand rise","sectors":["Agriculture","FMCG","Auto"]},
  {"id":26,"title":"SEBI approves REITs for smaller assets — Rs 50 Cr minimum (was Rs 500 Cr)","category":"Regulation","impact":8,"sentiment":"Positive","time":"7d ago","source":"SEBI","link":"https://www.sebi.gov.in","insight":"Democratizes real estate investing; Brookfield REIT, Embassy, Mindspace expand asset base","sectors":["REITs","Realty"]},
  {"id":27,"title":"India-Middle East-Europe Corridor (IMEC) agreement signed — India as trade hub","category":"Trade","impact":10,"sentiment":"Positive","time":"7d ago","source":"Commerce Ministry","link":"https://commerce.gov.in","insight":"Shipping, ports, logistics decade-long tailwind; Adani Ports, JNPA, Gujarat Pipavav","sectors":["Ports","Logistics","Shipping"]},
  {"id":28,"title":"Coal India production target raised to 1 billion tonnes by FY27","category":"Energy","impact":7,"sentiment":"Positive","time":"7d ago","source":"Coal Ministry","link":"https://coal.gov.in","insight":"Energy security focus; Coal India dividend play; power sector fuel cost stability","sectors":["Energy","Coal","Power"]},
  {"id":29,"title":"IBC amendment: faster resolution, 180-day hard cap; creditor haircuts capped at 40%","category":"Regulation","impact":8,"sentiment":"Positive","time":"8d ago","source":"MCA","link":"https://mca.gov.in","insight":"NPA resolution acceleration; banking sector asset quality improves; ARCs benefit","sectors":["Banking","NBFC","ARC"]},
  {"id":30,"title":"National Quantum Computing Mission: Rs 6,000 Cr over 8 years — IIT led","category":"Technology","impact":8,"sentiment":"Positive","time":"8d ago","source":"DST","link":"https://dst.gov.in","insight":"Long-term deep-tech play; TCS, Infosys, ISRO spin-offs likely to bid for projects","sectors":["Technology","Deep Tech"]},
]

price_cache = {}
cache_time = {}

def get_live_price(symbol):
    import time as time_mod
    now = time_mod.time()
    if symbol in price_cache and now - cache_time.get(symbol, 0) < 60:
        return price_cache[symbol]
    try:
        import yfinance as yf
        tick = yf.Ticker(symbol + ".NS")
        hist = tick.history(period="1d", interval="1m")
        if not hist.empty:
            price = round(float(hist['Close'].iloc[-1]), 2)
            price_cache[symbol] = price
            cache_time[symbol] = now
            return price
    except:
        pass
    return None

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def index():
    return render_template('index.html')

@app.route('/api/announcements')
def get_announcements():
    q = request.args.get('q','').lower()
    data = ANNOUNCEMENTS if not q else [a for a in ANNOUNCEMENTS if q in a['company'].lower() or q in a['title'].lower()]
    return jsonify(data)

@app.route('/api/govt-news')
def get_govt_news():
    q = request.args.get('q','').lower()
    data = GOVT_NEWS if not q else [n for n in GOVT_NEWS if q in n['title'].lower() or q in n['category'].lower()]
    return jsonify(data)

@app.route('/api/stock-price/<symbol>')
def stock_price(symbol):
    price = get_live_price(symbol.upper())
    if price:
        return jsonify({"symbol": symbol.upper(), "price": price})
    return jsonify({"error": "not found"}), 404

@app.route('/api/stock-prices')
def stock_prices():
    result = []
    for s in TRACKED_STOCKS[:20]:
        p = get_live_price(s['symbol'])
        row = dict(s)
        if p:
            row['ltp'] = p
        result.append(row)
    return jsonify(result)

@app.route('/api/whales')
def get_whales():
    return jsonify(WHALES)

@app.route('/api/whale/<int:whale_id>')
def get_whale(whale_id):
    whale = next((w for w in WHALES if w['id'] == whale_id), None)
    if not whale:
        return jsonify({"error": "not found"}), 404
    investments = WHALE_INVESTMENTS.get(whale_id, [])
    return jsonify({"whale": whale, "investments": investments})

@app.route('/api/search/<query>')
def search(query):
    q = query.lower()
    stocks = [s for s in TRACKED_STOCKS if q in s['symbol'].lower() or q in s['name'].lower()]
    ann = [a for a in ANNOUNCEMENTS if q in a['company'].lower() or q in a['title'].lower()]
    news = [n for n in GOVT_NEWS if q in n['title'].lower()]
    return jsonify({"stocks": stocks[:10], "announcements": ann[:5], "news": news[:5]})

@app.route('/api/screener')
def screener():
    sector = request.args.get('sector','')
    min_impact = int(request.args.get('min_impact', 0))
    sentiment = request.args.get('sentiment','')
    data = ANNOUNCEMENTS
    if sector:
        data = [a for a in data if sector.lower() in a.get('company','').lower()]
    if min_impact:
        data = [a for a in data if a['impact'] >= min_impact]
    if sentiment:
        data = [a for a in data if a['sentiment'].lower() == sentiment.lower()]
    return jsonify(data)

@app.route('/api/fii-dii')
def fii_dii():
    data = [
        {"date":"2026-05-09","fii_buy":12450,"fii_sell":9870,"fii_net":2580,"dii_buy":8230,"dii_sell":6140,"dii_net":2090},
        {"date":"2026-05-08","fii_buy":9100,"fii_sell":11200,"fii_net":-2100,"dii_buy":9800,"dii_sell":7200,"dii_net":2600},
        {"date":"2026-05-07","fii_buy":14200,"fii_sell":10100,"fii_net":4100,"dii_buy":7600,"dii_sell":8900,"dii_net":-1300},
        {"date":"2026-05-06","fii_buy":8900,"fii_sell":8400,"fii_net":500,"dii_buy":9200,"dii_sell":8100,"dii_net":1100},
        {"date":"2026-05-05","fii_buy":11300,"fii_sell":9600,"fii_net":1700,"dii_buy":8500,"dii_sell":7800,"dii_net":700},
        {"date":"2026-05-02","fii_buy":7800,"fii_sell":10200,"fii_net":-2400,"dii_buy":10100,"dii_sell":7400,"dii_net":2700},
        {"date":"2026-05-01","fii_buy":13600,"fii_sell":9800,"fii_net":3800,"dii_buy":7900,"dii_sell":9200,"dii_net":-1300},
        {"date":"2026-04-30","fii_buy":10200,"fii_sell":8700,"fii_net":1500,"dii_buy":8800,"dii_sell":7600,"dii_net":1200},
        {"date":"2026-04-29","fii_buy":9400,"fii_sell":12100,"fii_net":-2700,"dii_buy":11200,"dii_sell":8300,"dii_net":2900},
        {"date":"2026-04-28","fii_buy":15300,"fii_sell":10800,"fii_net":4500,"dii_buy":8100,"dii_sell":9600,"dii_net":-1500},
    ]
    return jsonify(data)

@app.route('/api/options/<symbol>')
def options_chain(symbol):
    import random
    sym = symbol.upper()
    base = 500
    strikes = list(range(base-100, base+150, 50))
    chain = []
    for k in strikes:
        itm = k < base
        chain.append({
            "strike": k,
            "ce_ltp": round(max(base-k,0) + random.uniform(5,80), 1),
            "ce_oi": random.randint(10000,500000),
            "ce_volume": random.randint(1000,50000),
            "ce_iv": round(random.uniform(18,45), 1),
            "pe_ltp": round(max(k-base,0) + random.uniform(5,80), 1),
            "pe_oi": random.randint(10000,500000),
            "pe_volume": random.randint(1000,50000),
            "pe_iv": round(random.uniform(18,45), 1),
            "itm": itm
        })
    return jsonify({"symbol": sym, "expiry": "2026-05-29", "spot": base, "chain": chain})

@app.route('/api/ai-recommendation/<symbol>')
def ai_recommendation(symbol):
    import random
    actions = ["Strong Buy","Buy","Hold","Sell","Strong Sell"]
    weights = [0.25,0.35,0.25,0.1,0.05]
    action = random.choices(actions, weights)[0]
    reasons = {
        "Strong Buy": ["Breakout above key resistance with volume surge","Institutional accumulation detected — FII buying 3 sessions","RSI bullish divergence + MACD crossover","52-week high breakout with delivery volumes 3x average"],
        "Buy": ["Pullback to support zone — good entry","Moving average golden cross forming","Strong quarterly results with guidance upgrade","Sector tailwind + company-specific catalyst"],
        "Hold": ["Consolidating in range — wait for breakout","Mixed signals: fundamentals strong but technicals neutral","Awaiting next catalyst — results or regulatory outcome","Fair valued at current levels"],
        "Sell": ["RSI overbought at 78 — caution zone","Insider selling detected in recent disclosures","Sector headwinds: regulation/competition pressure","Negative divergence on MACD and price"],
        "Strong Sell": ["Death cross formed — 50 DMA below 200 DMA","Promoter pledge increase — red flag","USFDA warning letter / regulatory action pending","Consecutive earnings misses with guidance cut"]
    }
    return jsonify({
        "symbol": symbol.upper(),
        "action": action,
        "confidence": random.randint(65, 95),
        "target_1w": round(random.uniform(-8, 12), 1),
        "target_1m": round(random.uniform(-15, 25), 1),
        "reasons": random.sample(reasons[action], min(2, len(reasons[action]))),
        "risk": random.choice(["Low","Medium","High"]),
        "stop_loss": round(random.uniform(-5, -2), 1)
    })

@app.route('/api/earnings-calendar')
def earnings_calendar():
    data = [
        {"company":"TCS","date":"2026-05-12","time":"After Market","est_eps":32.4,"prev_eps":30.1,"sector":"IT"},
        {"company":"INFY","date":"2026-05-13","time":"Before Market","est_eps":18.2,"prev_eps":16.8,"sector":"IT"},
        {"company":"HDFC Bank","date":"2026-05-14","time":"After Market","est_eps":21.5,"prev_eps":19.2,"sector":"Banking"},
        {"company":"Reliance","date":"2026-05-15","time":"After Market","est_eps":68.4,"prev_eps":62.1,"sector":"Conglomerate"},
        {"company":"WIPRO","date":"2026-05-16","time":"Before Market","est_eps":8.9,"prev_eps":8.2,"sector":"IT"},
        {"company":"Asian Paints","date":"2026-05-19","time":"After Market","est_eps":9.1,"prev_eps":8.4,"sector":"FMCG"},
        {"company":"Bajaj Finance","date":"2026-05-20","time":"After Market","est_eps":37.8,"prev_eps":34.2,"sector":"NBFC"},
        {"company":"Maruti Suzuki","date":"2026-05-21","time":"After Market","est_eps":142.3,"prev_eps":128.6,"sector":"Auto"},
        {"company":"ICICI Bank","date":"2026-05-23","time":"After Market","est_eps":17.8,"prev_eps":15.4,"sector":"Banking"},
        {"company":"L&T","date":"2026-05-26","time":"After Market","est_eps":54.2,"prev_eps":49.8,"sector":"Infrastructure"},
        {"company":"Sun Pharma","date":"2026-05-27","time":"Before Market","est_eps":14.6,"prev_eps":13.2,"sector":"Pharma"},
        {"company":"HUL","date":"2026-06-02","time":"After Market","est_eps":14.1,"prev_eps":13.4,"sector":"FMCG"},
    ]
    return jsonify(data)

@app.route('/api/ipo-tracker')
def ipo_tracker():
    data = [
        {"company":"Ola Electric Q2","open":"2026-05-12","close":"2026-05-14","price":88,"lot":170,"gmp":18,"sector":"EV","rating":"Subscribe","size":2500},
        {"company":"FirstCry Expansion","open":"2026-05-15","close":"2026-05-19","price":452,"lot":33,"gmp":85,"sector":"E-Commerce","rating":"Subscribe for Listing","size":4200},
        {"company":"NSDL IPO","open":"2026-05-26","close":"2026-05-28","price":920,"lot":16,"gmp":210,"sector":"Financial Infra","rating":"Strong Subscribe","size":3000},
        {"company":"Boat Lifestyle","open":"2026-06-02","close":"2026-06-04","price":310,"lot":48,"gmp":55,"sector":"Consumer Electronics","rating":"Subscribe","size":2800},
        {"company":"PhysicsWallah","open":"2026-06-09","close":"2026-06-11","price":480,"lot":31,"gmp":90,"sector":"EdTech","rating":"Subscribe","size":3500},
        {"company":"Mobikwik","open":"2026-05-05","close":"2026-05-07","price":279,"lot":53,"gmp":-12,"sector":"Fintech","rating":"Avoid","size":572,"listed":True,"listing_price":248},
        {"company":"Waaree Renewables 2","open":"2026-04-28","close":"2026-04-30","price":1250,"lot":12,"gmp":340,"sector":"Solar","rating":"Subscribe","size":5000,"listed":True,"listing_price":1680},
    ]
    return jsonify(data)

@app.route('/api/indices')
def indices():
    data = [
        {"name":"NIFTY 50","value":24186.50,"change":142.30,"pct":0.59,"color":"green"},
        {"name":"SENSEX","value":79648.20,"change":487.60,"pct":0.62,"color":"green"},
        {"name":"BANK NIFTY","value":52340.80,"change":-124.50,"pct":-0.24,"color":"red"},
        {"name":"NIFTY IT","value":38420.60,"change":680.20,"pct":1.80,"color":"green"},
        {"name":"NIFTY MIDCAP100","value":54820.30,"change":312.40,"pct":0.57,"color":"green"},
        {"name":"NIFTY SMALLCAP","value":18640.70,"change":-89.20,"pct":-0.48,"color":"red"},
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
