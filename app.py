from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import yaml
import pandas as pd
import re
from datetime import datetime

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.BaseLoader)

mensajes = config['mensajes']
dnis = pd.read_csv(config['planilla'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int})
feriados = ['2024-07-09', '2024-10-11']
calendario_con_feriados = pd.offsets.CustomBusinessDay(holidays=feriados)

class ActualState(BaseModel):
    nodo: int
    mensaje: str
    dni: Optional[str] = None

def fin(parametro, *args):
    return 'fin'

def verificar_dni(dni: str, *args):
    return dni in dnis['DNI'].values

def verificar_correo(correo: str, dni: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, correo) is None:
        raise Exception('mail invalido')
    else:
        dnis.loc[dnis['DNI'] == dni, ['MAIL2']] = correo
        dnis.to_csv(config['planilla'], index=False)
        return True

def verificar_estado(opcion :str, dni:str):
    if opcion == '3':
        dnis.loc[dnis['DNI'] == dni, ['ESTADO']] = 'LIBRE DEUDA'
    elif opcion == '4':
        dnis.loc[dnis['DNI'] == dni, ['ESTADO']] = 'DEFENSA DEL CONSUMIDOR'
    elif opcion == '5':
        dnis.loc[dnis['DNI'] == dni, ['ESTADO']] = 'DESCONOCE DEUDA'
    dnis.to_csv(config['planilla'], index=False)
    return opcion

def verificar_mes_actual(fecha: str, dni: str):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    mes_actual = datetime.today().strftime('%m/%Y')
    if fecha <= datetime.today() and fecha.strftime('%m/%Y') == mes_actual:
        dnis.loc[dnis['DNI'] == dni, ['ESTADO']] = 'Ya pagó'
        dnis.to_csv(config['planilla'], index=False)
        return True
    else:
        raise Exception('mes incorrecto')

def verificar_fecha(fecha: str, dni: str):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    if fecha > datetime.today():
        dnis.loc[dnis['DNI'] == dni, ['fecha_de_pago']] = fecha
        dnis.to_csv(config['planilla'], index=False)
        return True
    else:
        raise Exception('fecha incorrecta')

def dame_deuda(dni: str, *args):
    return dnis[dnis['DNI'] == dni]['DEUDA_TOTAL'].values[0]

def dame_nombre(dni: str, *args):
    return dnis[dnis['DNI'] == dni]['NOMBRE'].values[0]

def dame_oferta(dni: str, *args):
    return dnis[dnis['DNI'] == dni]['OFERTA'].values[0]

def dame_fecha_limite(dni: str, *args):
    cantidad_dias = 5
    fecha_limite = pd.Timestamp(datetime.today()) + calendario_con_feriados * cantidad_dias
    return fecha_limite.date().strftime('%d/%m/%Y')

def dame_planes(dni: str, *args):
    fila = dnis[dnis['DNI'] == dni]
    return list(fila[['CANT  CUOTAS 1', 'MONTON CUOTA 1', 'CANT  CUOTAS 2', 'MONTON CUOTA 2', 'CANT  CUOTAS 3', 'MONTON CUOTA 3']].values[0])

def dame_oferta_fecha(dni: str, *args):
    fila = dnis[dnis['DNI'] == dni]
    oferta = fila['OFERTA CANCELATORIA '].values[0]
    fecha_limite = dame_fecha_limite(dni)
    return [oferta, fecha_limite]

@app.post('/respuesta')
async def respuesta(state: ActualState):
    try:
        nodo = str(state.nodo)
        funcion = mensajes[nodo]['siguientes']['funcion']
        decision = str(eval(funcion)(state.mensaje, state.dni))
        proximo_nodo = mensajes[nodo]['siguientes']['resultados'][decision]
        if not verificar_dni(state.dni):
            raise Exception('DNI invalido')
        if 'funcion' in mensajes[proximo_nodo].keys():
            valor_placeholder = eval(mensajes[proximo_nodo]['funcion'])(state.dni)
            if isinstance(valor_placeholder, list):
                texto = mensajes[proximo_nodo]['texto'].format(*valor_placeholder)
            else:
                print(mensajes[proximo_nodo]['texto'])
                texto = mensajes[proximo_nodo]['texto'].format(valor_placeholder)
        else:
            texto = mensajes[proximo_nodo]['texto']
    except Exception as e:
        print(e)
        texto = 'payload invalido'
    return texto

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
