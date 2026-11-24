"""Simulación de señales idénticas con y sin filtro. Sin conexión a bróker."""
from dataclasses import dataclass, field
from estrategias import tamaño

@dataclass
class Cartera:
    efectivo: float = 10000.
    posiciones: dict = field(default_factory=dict)
    operaciones: list = field(default_factory=list)
    comision: float = .003
    deslizamiento: float = .001
    def patrimonio(self, precios):
        return self.efectivo+sum(p['cantidad']*precios.get(a,p['entrada']) for a,p in self.posiciones.items())
    def abrir(self, activo, señal, precio, precios):
        if activo in self.posiciones: return False
        entrada=precio*(1+self.deslizamiento)
        stop=señal['stop']; objetivo=señal['objetivo']
        if not 0<stop<entrada<objetivo: return False
        cantidad=min(tamaño(self.patrimonio(precios),entrada,stop,self.efectivo),self.efectivo/(entrada*(1+self.comision)))
        if cantidad<=0: return False
        coste=cantidad*entrada*(1+self.comision)
        self.efectivo-=coste
        self.posiciones[activo]=dict(cantidad=cantidad,entrada=entrada,stop=stop,objetivo=objetivo,coste=coste)
        return True
    def actualizar(self, activo, vela):
        p=self.posiciones.get(activo)
        if not p: return
        if vela['low']<=p['stop']: salida=min(vela['open'],p['stop'])
        elif vela['high']>=p['objetivo']: salida=p['objetivo']
        else: return
        neto=p['cantidad']*salida*(1-self.deslizamiento)*(1-self.comision)
        self.efectivo+=neto
        self.operaciones.append(dict(activo=activo,resultado=neto-p['coste']))
        del self.posiciones[activo]

@dataclass
class Comparador:
    control: Cartera = field(default_factory=Cartera)
    filtrada: Cartera = field(default_factory=Cartera)
    decisiones: dict = field(default_factory=dict)
    def procesar(self, activo, vela_id, señal, precio, precios, permitir, motivo):
        clave=(activo,vela_id,señal['estrategia'])
        if clave in self.decisiones: return False
        if not isinstance(permitir,bool): raise ValueError('Decisión inválida')
        c=self.control.abrir(activo,señal,precio,precios)
        f=self.filtrada.abrir(activo,señal,precio,precios) if permitir else False
        self.decisiones[clave]=dict(permitir=permitir,motivo=motivo,control=c,filtrada=f)
        return True
