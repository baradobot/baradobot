"""Señales deterministas experimentales. No acreditan rentabilidad."""
from statistics import mean

def señal(velas, tipo):
    if len(velas)<60: return None
    cierres=[v['close'] for v in velas]
    precio=cierres[-1]
    atr=mean([max(v['high']-v['low'],abs(v['high']-cierres[i-1]),abs(v['low']-cierres[i-1])) for i,v in enumerate(velas) if i>=len(velas)-14])
    if atr<=0 or precio<=0: return None
    if tipo=='ruptura':
        entrada=precio>max(v['high'] for v in velas[-56:-1]) and atr/precio>=.001
    elif tipo=='retroceso':
        bajos=min(v['low'] for v in velas[-14:]); altos=max(v['high'] for v in velas[-14:])
        k=100*(precio-bajos)/(altos-bajos) if altos>bajos else 50
        entrada=mean(cierres[-20:])>mean(cierres[-50:]) and k<30
    else: raise ValueError('Estrategia desconocida')
    if not entrada: return None
    return {'lado':'COMPRA','entrada':precio,'stop':precio-2*atr,'objetivo':precio+4*atr,'estrategia':tipo}

def tamaño(patrimonio, entrada, stop, efectivo):
    distancia=entrada-stop
    if min(patrimonio,entrada,distancia,efectivo)<=0: return 0
    return min(patrimonio*.0005/distancia,efectivo/entrada,patrimonio*.05/entrada)
