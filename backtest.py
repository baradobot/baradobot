"""Backtest experimental con CSV de velas UTC ordenadas; ejecución en apertura siguiente."""
import csv, argparse, json, math
from comparador import Comparador
from estrategias import señal

def ejecutar(velas, activo, tipo, vetos=None):
    c=Comparador(); vetos=vetos or {}; pendiente=None; maximos=[10000.,10000.]; caidas=[0.,0.]
    for i,v in enumerate(velas):
        precios={activo:v['open']}
        if pendiente:
            identificador,s=pendiente
            permitir=not vetos.get(str(identificador),False)
            c.procesar(activo,identificador,s,v['open'],precios,permitir,'Veto histórico externo' if not permitir else 'Sin veto')
        for j,p in enumerate((c.control,c.filtrada)):
            p.actualizar(activo,v)
            valor=p.patrimonio({activo:v['close']})
            maximos[j]=max(maximos[j],valor)
            caidas[j]=max(caidas[j],1-valor/maximos[j])
        s=señal(velas[max(0,i-59):i+1],tipo)
        pendiente=(v['time'],s) if s else None
    resultado={}
    for j,(nombre,p) in enumerate((('control',c.control),('filtrada',c.filtrada))):
        resultado[nombre]={'patrimonio':p.patrimonio({activo:velas[-1]['close']}),'operaciones_cerradas':len(p.operaciones),'drawdown':caidas[j]}
    return resultado

def cargar(ruta):
    with open(ruta,newline='') as f:
        velas=[dict(time=int(r['time']),**{k:float(r[k]) for k in ('open','high','low','close')}) for r in csv.DictReader(f)]
    if not velas: raise ValueError('Sin datos')
    for i,v in enumerate(velas):
        if i and v['time']<=velas[i-1]['time']: raise ValueError('Orden temporal inválido')
        if not all(math.isfinite(v[k]) and v[k]>0 for k in ('open','high','low','close')) or v['low']>min(v['open'],v['close']) or v['high']<max(v['open'],v['close']): raise ValueError('Vela inválida')
    return velas

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--activo',default='ACTIVO');p.add_argument('--tipo',choices=['ruptura','retroceso'],default='ruptura');p.add_argument('--vetos');a=p.parse_args()
    vetos={}
    if a.vetos:
        with open(a.vetos) as f: vetos=json.load(f)
    print(json.dumps(ejecutar(cargar(a.csv),a.activo,a.tipo,vetos),indent=2))
