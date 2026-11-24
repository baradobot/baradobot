import os, json, time, sqlite3, urllib.request, math, argparse
from datetime import datetime, timezone

ASSETS = {'BTC':'XBTUSD','ETH':'ETHUSD','SOL':'SOLUSD'}

def fetch(url, payload=None, headers=None):
    req=urllib.request.Request(url, data=None if payload is None else json.dumps(payload).encode(), headers={'Content-Type':'application/json', **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def market(pair):
    d=fetch('https://api.kraken.com/0/public/OHLC?pair='+pair+'&interval=5')
    if d['error']: raise ValueError(d['error'])
    rows=next(v for k,v in d['result'].items() if k!='last')[:-1]
    if len(rows)<30: raise ValueError('Insufficient candles')
    if time.time()-float(rows[-1][0])>900: raise ValueError('Stale candles')
    return [{'time':int(r[0]),'open':float(r[1]),'high':float(r[2]),'low':float(r[3]),'close':float(r[4]),'volume':float(r[6])} for r in rows[-60:]]

def decide(asset, candles, position, history):
    key=os.environ.get('OPENAI_API_KEY')
    if not key: raise RuntimeError('OPENAI_API_KEY missing; no orders generated')
    prompt={'asset':asset,'closed_5m_candles':candles,'position':position,'recent_decisions':history}
    response=fetch('https://api.openai.com/v1/chat/completions', {'model':os.getenv('ORION_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':'You are a paper trading research agent. Use only supplied data. Return JSON with action BUY, SELL or HOLD and reason (max 300 chars). BUY opens a long, SELL closes it. Prefer HOLD when uncertain. No leverage. Do not claim guaranteed returns.'},{'role':'user','content':json.dumps(prompt)}],'response_format':{'type':'json_object'}}, {'Authorization':'Bearer '+key})
    decision=json.loads(response['choices'][0]['message']['content'])
    if decision.get('action') not in ('BUY','SELL','HOLD'): raise ValueError('Invalid action')
    return decision['action'],str(decision.get('reason',''))[:300]

class Paper:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript('CREATE TABLE IF NOT EXISTS wallet(id INTEGER PRIMARY KEY CHECK(id=1), cash REAL NOT NULL); INSERT OR IGNORE INTO wallet VALUES(1,10000); CREATE TABLE IF NOT EXISTS positions(asset TEXT PRIMARY KEY, qty REAL, entry REAL); CREATE TABLE IF NOT EXISTS journal(id INTEGER PRIMARY KEY, ts TEXT, asset TEXT, candle INTEGER, action TEXT, price REAL, qty REAL, reason TEXT, UNIQUE(asset,candle));')
    def cash(self): return self.db.execute('SELECT cash FROM wallet').fetchone()[0]
    def position(self,a): return self.db.execute('SELECT qty,entry FROM positions WHERE asset=?',(a,)).fetchone()
    def seen(self,a,c): return self.db.execute('SELECT 1 FROM journal WHERE asset=? AND candle=?',(a,c)).fetchone() is not None
    def execute(self,a,c,action,price,reason):
        if not math.isfinite(price) or price<=0: raise ValueError('Invalid price')
        with self.db:
            self.db.execute('UPDATE wallet SET cash=cash WHERE id=1')
            if self.seen(a,c): return 'DUPLICATE'
            cash=self.cash(); p=self.position(a); qty=0.; fee=.003; slip=.001
            if p and price<=p[1]*.98: action,reason='SELL','Risk stop (sampled price)'
            if action=='BUY' and not p:
                budget=min(cash*.05,500); fill=price*(1+slip); qty=budget/(fill*(1+fee))
                if budget>=10:
                    self.db.execute('UPDATE wallet SET cash=cash-? WHERE id=1',(budget,)); self.db.execute('INSERT INTO positions VALUES(?,?,?)',(a,qty,fill))
                else: action,qty='HOLD',0.
            elif action=='SELL' and p:
                qty=p[0]; self.db.execute('UPDATE wallet SET cash=cash+? WHERE id=1',(qty*price*(1-slip)*(1-fee),)); self.db.execute('DELETE FROM positions WHERE asset=?',(a,))
            else: action='HOLD'
            self.db.execute('INSERT INTO journal(ts,asset,candle,action,price,qty,reason) VALUES(?,?,?,?,?,?,?)',(datetime.now(timezone.utc).isoformat(),a,c,action,price,qty,reason))
        return action

def cycle(p):
    for a,pair in ASSETS.items():
        try:
            candles=market(pair); c=candles[-1]['time']; price=candles[-1]['close']; pos=p.position(a)
            if p.seen(a,c): continue
            if pos and price<=pos[1]*.98: action,reason='SELL','Risk stop (sampled price)'
            else:
                history=p.db.execute('SELECT action,price,reason FROM journal WHERE asset=? ORDER BY id DESC LIMIT 8',(a,)).fetchall()
                action,reason=decide(a,candles,pos,history)
            print(a,p.execute(a,c,action,price,reason),reason,flush=True)
        except Exception as e: print(a,'ERROR',str(e),flush=True)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--once',action='store_true'); parser.add_argument('--db',default=os.getenv('ORION_DB','orion.db')); args=parser.parse_args(); p=Paper(args.db)
    while True:
        cycle(p)
        if args.once: break
        time.sleep(300)
if __name__=='__main__': main()
