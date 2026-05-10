import socket
socket.setdefaulttimeout(4)
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf
import json, random, threading, time
from datetime import datetime

app = Flask(__name__)
CORS(app)

TRACKED_STOCKS = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "HDFCBANK": "HDFCBANK.NS",
    "WIPRO": "WIPRO.NS", "INFOSYS": "INFY.NS", "TATAMOTORS": "TATAMOTORS.NS",
    "ICICIBANK": "ICICIBANK.NS", "BAJFINANCE": "BAJFINANCE.NS",
    "HCLTECH": "HCLTECH.NS", "ADANIPORTS": "ADANIPORTS.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "MARUTI": "MARUTI.NS",
    "ONGC": "ONGC.NS", "COALINDIA": "COALINDIA.NS", "SBIN": "SBIN.NS"
}

WHALES = [
    {"id":"w1","name":"Rakesh Jhunjhunwala Estate","type":"Legendary Investor","aum":"₹35,000 Cr","avatar":"🐋"},
    {"id":"w2","name":"Mukesh Ambani","type":"Promoter/Industrialist","aum":"₹8,50,000 Cr","avatar":"🦈"},
    {"id":"w3","name":"LIC (Life Insurance Corp)","type":"Institutional","aum":"₹40,00,000 Cr","avatar":"🏛️"},
    {"id":"w4","name":"SBI Mutual Fund","type":"Mutual Fund","aum":"₹7,50,000 Cr","avatar":"🏦"},
    {"id":"w5","name":"Foreign Portfolio Investors","type":"FPI Aggregate","aum":"₹60,00,000 Cr","avatar":"🌐"},
    {"id":"w6","name":"Vijay Kedia","type":"Ace Investor","aum":"₹1,200 Cr","avatar":"🐋"},
    {"id":"w7","name":"Radhakishan Damani","type":"Ace Investor","aum":"₹2,00,000 Cr","avatar":"🦈"},
    {"id":"w8","name":"Dolly Khanna","type":"Ace Investor","aum":"₹600 Cr","avatar":"🐋"},
]

WHALE_INVESTMENTS = {
    "w1": [
        {"date":"2025-05-01","stock":"TATAMOTORS","action":"BUY","qty":"5,00,000","price":"₹612","value":"₹306 Cr","potential":"EV expansion play - Target ₹800+","pattern":"Bought during market dip, historically returns 35%+"},
        {"date":"2025-04-15","stock":"TITAN","action":"BUY","qty":"2,00,000","price":"₹3,250","value":"₹650 Cr","potential":"Consumer brand with 20% YoY growth","pattern":"Pre-quarterly earnings accumulation"},
        {"date":"2025-03-20","stock":"CRISIL","action":"HOLD","qty":"10,00,000","price":"₹5,100","value":"₹510 Cr","potential":"Rating agency monopoly - stable 15% returns","pattern":"Long term hold - 5+ years"},
    ],
    "w2": [
        {"date":"2025-05-05","stock":"RELIANCE","action":"BUY","qty":"50,00,000","price":"₹2,950","value":"₹14,750 Cr","potential":"Jio Financial + Retail expansion - Target ₹3,500","pattern":"Promoter buying = strong bullish signal"},
        {"date":"2025-04-28","stock":"JIOFINANCIAL","action":"BUY","qty":"20,00,000","price":"₹320","value":"₹640 Cr","potential":"NBFC + Fintech play, target ₹500 in 18M","pattern":"New listing accumulation phase"},
    ],
    "w3": [
        {"date":"2025-05-07","stock":"SBIN","action":"BUY","qty":"1,00,00,000","price":"₹820","value":"₹8,200 Cr","potential":"PSU bank re-rating - Target ₹1,000","pattern":"LIC buying = institutional confidence boost"},
        {"date":"2025-05-02","stock":"ITC","action":"INCREASE","qty":"5,00,00,000","price":"₹435","value":"₹21,750 Cr","potential":"FMCG demerger value unlock - Target ₹600","pattern":"Increased stake to 15.5% - major conviction"},
        {"date":"2025-04-10","stock":"ADANIPORTS","action":"BUY","qty":"80,00,000","price":"₹1,180","value":"₹9,440 Cr","potential":"Port capacity expansion - 30% growth potential","pattern":"Infrastructure sector allocation increase"},
    ],
    "w4": [
        {"date":"2025-05-06","stock":"INFOSYS","action":"BUY","qty":"30,00,000","price":"₹1,480","value":"₹4,440 Cr","potential":"AI services revenue - Target ₹2,000","pattern":"IT sector rotation incoming"},
        {"date":"2025-04-20","stock":"BAJFINANCE","action":"BUY","qty":"15,00,000","price":"₹7,200","value":"₹10,800 Cr","potential":"NBFC expansion + credit growth - Target ₹9,500","pattern":"Strong retail lending momentum"},
    ],
    "w5": [
        {"date":"2025-05-08","stock":"HDFCBANK","action":"BUY","qty":"2,00,00,000","price":"₹1,620","value":"₹32,400 Cr","potential":"Post-merger rerating - Target ₹2,200","pattern":"FPI inflows surge - banking sector preferred"},
        {"date":"2025-05-03","stock":"TCS","action":"BUY","qty":"1,00,00,000","price":"₹3,750","value":"₹37,500 Cr","potential":"AI/Cloud deals pipeline strong - Target ₹4,500","pattern":"IT export outlook improving"},
    ],
    "w6": [
        {"date":"2025-04-25","stock":"CERA","action":"BUY","qty":"1,00,000","price":"₹5,800","value":"₹58 Cr","potential":"Sanitaryware monopoly - 25% CAGR","pattern":"Small cap multi-bagger pattern - similar to past picks"},
        {"date":"2025-04-01","stock":"TALBROS","action":"BUY","qty":"2,00,000","price":"₹280","value":"₹56 Cr","potential":"Auto ancillary EV transition play","pattern":"Pre-results accumulation"},
    ],
    "w7": [
        {"date":"2025-05-04","stock":"DMART","action":"HOLD","qty":"3,50,00,000","price":"₹4,200","value":"₹14,700 Cr","potential":"Retail dominance - 18% revenue growth","pattern":"Promoter holds 74% - no selling pressure"},
    ],
    "w8": [
        {"date":"2025-04-30","stock":"MAYURUNIQ","action":"BUY","qty":"5,00,000","price":"₹680","value":"₹34 Cr","potential":"Textile export theme - 40% upside","pattern":"Hidden gem pattern - pre-discovery phase"},
        {"date":"2025-04-15","stock":"PALRED","action":"BUY","qty":"8,00,000","price":"₹145","value":"₹11.6 Cr","potential":"Tech turnaround story","pattern":"Low float + accumulation = explosive move potential"},
    ]
}

ANNOUNCEMENTS = [
    {"company":"TCS","title":"TCS wins $2.5B deal with European telecom giant for 5-year digital transformation","summary":"Massive deal win adds revenue visibility. Deal size equals ~10% of annual revenue. Target: ₹4,200","source":"NSE Filing","link":"https://www.nseindia.com/companies-listing/corporate-filings-announcements","time":"2025-05-09 09:15","impact":9,"sentiment":"Positive","direction":"up","type":"Deal","hype_score":94},
    {"company":"HDFCBANK","title":"HDFC Bank Q4 profit surges 32% to ₹18,500 Cr, NIM expands to 4.2%, asset quality improves","summary":"Beat street estimates by 8%. NIM expansion is key positive. Asset quality improvement removes overhang. Target ₹2,000","source":"BSE Filing","link":"https://www.bseindia.com/corporates/ann.html","time":"2025-05-09 08:45","impact":9,"sentiment":"Positive","direction":"up","type":"Earnings","hype_score":97},
    {"company":"RELIANCE","title":"Reliance Jio launches 6G pilot in Mumbai, Delhi, Bangalore — commercial rollout Q3 FY26","summary":"First-mover 6G advantage. Telecom ARPU boost expected. Jio Financial synergy play. Target ₹3,200","source":"Economic Times","link":"https://economictimes.indiatimes.com/markets/stocks","time":"2025-05-09 10:00","impact":8,"sentiment":"Positive","direction":"up","type":"General","hype_score":89},
    {"company":"TATAMOTORS","title":"Tata Motors EV sales cross 1 lakh units in FY26, Nexon EV leads market with 40% share","summary":"EV dominance in domestic market. JLR profitability improving. Debt reduction on track. Target ₹850","source":"Company Press Release","link":"https://www.tatamotors.com/press-release/","time":"2025-05-09 11:30","impact":8,"sentiment":"Positive","direction":"up","type":"General","hype_score":86},
    {"company":"WIPRO","title":"Wipro acquires Finnish AI startup for €380M to strengthen GenAI capabilities","summary":"AI capability boost = premium valuation. Deal funded from cash reserves, no dilution. Target ₹620","source":"Moneycontrol","link":"https://www.moneycontrol.com/news/business/companies/","time":"2025-05-09 07:30","impact":7,"sentiment":"Positive","direction":"up","type":"M&A","hype_score":78},
    {"company":"SUNPHARMA","title":"Sun Pharma gets USFDA approval for blockbuster dermatology drug, launches in US market","summary":"US market launch adds $200M+ revenue potential. Specialty pharma strategy paying off. Target ₹1,800","source":"NSE Filing","link":"https://www.nseindia.com/companies-listing/corporate-filings-announcements","time":"2025-05-09 09:00","impact":8,"sentiment":"Positive","direction":"up","type":"Regulatory","hype_score":85},
    {"company":"BAJFINANCE","title":"Bajaj Finance board approves ₹10,000 Cr NCD issue, maintains AAA credit rating","summary":"Strong credit rating + fundraise = expansion capital. AUM growth trajectory intact. Target ₹9,500","source":"BSE Filing","link":"https://www.bseindia.com/corporates/ann.html","time":"2025-05-09 12:00","impact":7,"sentiment":"Positive","direction":"up","type":"Corporate Action","hype_score":75},
    {"company":"ICICIBANK","title":"ICICI Bank launches AI-powered banking platform, targets 50M new digital customers by FY27","summary":"Fintech play within banking — premium valuation justified. Digital MAU growth = CASA improvement. Target ₹1,400","source":"BusinessLine","link":"https://www.thehindubusinessline.com/markets/","time":"2025-05-08 15:00","impact":8,"sentiment":"Positive","direction":"up","type":"General","hype_score":82},
    {"company":"HCLTECH","title":"HCL Tech secures 10-year $1.8B IT outsourcing deal with US financial services firm","summary":"Long-term revenue lock-in. US financial sector deal = margin accretive. Target ₹2,100","source":"NSE Filing","link":"https://www.nseindia.com/companies-listing/corporate-filings-announcements","time":"2025-05-08 14:30","impact":9,"sentiment":"Positive","direction":"up","type":"Deal","hype_score":91},
    {"company":"MARUTI","title":"Maruti Suzuki launches India's first CNG SUV; pre-bookings cross 50,000 in 48 hours","summary":"CNG = lower fuel cost = mass market hit. Pre-booking surge = strong Q1 volumes. Target ₹14,500","source":"Economic Times","link":"https://economictimes.indiatimes.com/markets/stocks","time":"2025-05-08 11:00","impact":8,"sentiment":"Positive","direction":"up","type":"General","hype_score":88},
    {"company":"ADANIPORTS","title":"Adani Ports wins ₹8,500 Cr Vizhinjam Phase 2 port contract from Govt of India","summary":"Govt contract = guaranteed revenue. Vizhinjam is strategic deep-sea port. Target ₹1,500","source":"PIB","link":"https://pib.gov.in/","time":"2025-05-08 09:00","impact":9,"sentiment":"Positive","direction":"up","type":"Deal","hype_score":93},
    {"company":"ONGC","title":"ONGC discovers new deep-sea oil reserve off Andhra coast, estimated 500 MMbbl reserve","summary":"New reserve discovery = long-term production boost. At $80/bbl = $40B value unlock. Target ₹320","source":"Moneycontrol","link":"https://www.moneycontrol.com/news/business/companies/","time":"2025-05-07 16:00","impact":9,"sentiment":"Positive","direction":"up","type":"General","hype_score":96},
    {"company":"INFOSYS","title":"Infosys Q4 revenue beats estimates; raises FY26 guidance to 8-10% growth","summary":"Guidance raise = analyst upgrades incoming. AI services deal wins accelerating. Target ₹2,000","source":"BSE Filing","link":"https://www.bseindia.com/corporates/ann.html","time":"2025-05-07 08:30","impact":9,"sentiment":"Positive","direction":"up","type":"Earnings","hype_score":95},
    {"company":"COALINDIA","title":"Coal India declares special dividend of ₹5/share; board approves buyback at ₹580","summary":"Special dividend + buyback = massive value return to shareholders. PSU re-rating play. Target ₹620","source":"NSE Filing","link":"https://www.nseindia.com/companies-listing/corporate-filings-announcements","time":"2025-05-07 10:00","impact":8,"sentiment":"Positive","direction":"up","type":"Corporate Action","hype_score":80},
    {"company":"SBIN","title":"SBI reports record quarterly profit of ₹22,000 Cr; NPA ratio drops to 1.8%, lowest in 10 years","summary":"Record profit + clean book = re-rating candidate. PSU bank premium valuation justified. Target ₹1,000","source":"BSE Filing","link":"https://www.bseindia.com/corporates/ann.html","time":"2025-05-06 17:00","impact":9,"sentiment":"Positive","direction":"up","type":"Earnings","hype_score":98},
]

GOVT_NEWS = [
    {"title":"Govt allocates ₹2.5 lakh Cr for infrastructure push in FY26 supplementary budget","link":"https://pib.gov.in/","source":"PIB (Press Info Bureau)","sector":"Infrastructure","impact":8,"sentiment":"Positive","time":"2025-05-09 10:00","affected_stocks":["ADANIPORTS","L&T","NTPC"]},
    {"title":"RBI keeps repo rate unchanged at 6.5%, signals rate cut in June if inflation cools","link":"https://www.rbi.org.in/","source":"RBI Press Release","sector":"Banking & Finance","impact":7,"sentiment":"Positive","time":"2025-05-09 10:30","affected_stocks":["HDFCBANK","ICICIBANK","SBIN"]},
    {"title":"PLI scheme for semiconductor manufacturing extended by 3 years with ₹76,000 Cr outlay","link":"https://pib.gov.in/","source":"PIB","sector":"Technology","impact":8,"sentiment":"Positive","time":"2025-05-08 14:00","affected_stocks":["TATAELXSI","DIXON","KAYNES"]},
    {"title":"EV policy: 100% road tax exemption extended to 2027, GST reduced to 5% on commercial EVs","link":"https://morth.nic.in/","source":"Ministry of Road Transport","sector":"Auto","impact":9,"sentiment":"Positive","time":"2025-05-08 11:00","affected_stocks":["TATAMOTORS","OLECTRA","GREENPANEL"]},
    {"title":"SEBI tightens F&O lot size rules; circuit breakers widened for small/mid caps","link":"https://www.sebi.gov.in/","source":"SEBI","sector":"General Market","impact":5,"sentiment":"Neutral","time":"2025-05-08 09:00","affected_stocks":["NIFTY50","BANKNIFTY"]},
    {"title":"India signs $12B defence deal with France for 26 Rafale Marine jets — boost to defence sector","link":"https://pib.gov.in/","source":"PIB","sector":"Defence","impact":9,"sentiment":"Positive","time":"2025-05-07 16:30","affected_stocks":["HAL","BEL","BHEL"]},
    {"title":"Govt launches National Logistics Policy 2.0; targets cutting logistics cost from 14% to 8% of GDP","link":"https://pib.gov.in/","source":"PIB","sector":"Infrastructure","impact":7,"sentiment":"Positive","time":"2025-05-07 12:00","affected_stocks":["CONCOR","ADANIPORTS","GATEWAY"]},
    {"title":"MSME credit guarantee scheme expanded; ₹5 lakh Cr corpus for small businesses","link":"https://pib.gov.in/","source":"Ministry of Finance","sector":"Banking & Finance","impact":6,"sentiment":"Positive","time":"2025-05-06 10:00","affected_stocks":["SBIN","BANDHANBNK","MICROFINANCE"]},
    {"title":"India-UAE trade corridor operationalised; zero duty on 97% goods from May 15","link":"https://commerce.gov.in/","source":"Ministry of Commerce","sector":"FMCG","impact":7,"sentiment":"Positive","time":"2025-05-06 09:30","affected_stocks":["ITC","HUL","NESTLEIND"]},
    {"title":"DPIIT approves 100% FDI in space sector; Isro spinoff privatisation accelerates","link":"https://dpiit.gov.in/","source":"DPIIT","sector":"Technology","impact":8,"sentiment":"Positive","time":"2025-05-05 15:00","affected_stocks":["ISRO-SPINOFF","NELCO","CENTUM"]},
]

def get_stock_price(ticker_ns):
    try:
        t = yf.Ticker(ticker_ns)
        hist = t.history(period="2d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else price
            change = price - prev
            pct = (change / prev) * 100
            return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}
    except:
        pass
    return {"price": 0, "change": 0, "pct": 0}

# Cache for stock prices
price_cache = {}
price_cache_time = {}

def get_cached_price(sym):
    now = time.time()
    if sym in price_cache and now - price_cache_time.get(sym, 0) < 120:
        return price_cache[sym]
    ticker = TRACKED_STOCKS.get(sym.upper(), f"{sym}.NS")
    data = get_stock_price(ticker)
    price_cache[sym] = data
    price_cache_time[sym] = now
    return data

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def index():
    return render_template('index.html')

@app.route('/api/announcements')
def get_announcements():
    return jsonify(ANNOUNCEMENTS)

@app.route('/api/govt-news')
def get_govt_news():
    return jsonify(GOVT_NEWS)

@app.route('/api/stock-price/<symbol>')
def get_price(symbol):
    return jsonify(get_cached_price(symbol.upper()))

@app.route('/api/stock-prices')
def get_all_prices():
    prices = {}
    for sym in list(TRACKED_STOCKS.keys())[:12]:
        prices[sym] = get_cached_price(sym)
    return jsonify(prices)

@app.route('/api/whales')
def get_whales():
    return jsonify(WHALES)

@app.route('/api/whale/<whale_id>')
def get_whale_details(whale_id):
    whale = next((w for w in WHALES if w['id'] == whale_id), None)
    if not whale:
        return jsonify({"error": "Whale not found"}), 404
    return jsonify({"whale": whale, "investments": WHALE_INVESTMENTS.get(whale_id, [])})

@app.route('/api/search/<query>')
def search_stocks(query):
    q = query.upper()
    results = [{"symbol": sym, "ticker": TRACKED_STOCKS[sym]} for sym in TRACKED_STOCKS if q in sym]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
