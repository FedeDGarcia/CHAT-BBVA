from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import yaml
import pandas as pd
import re
import datetime

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']
dnis = pd.read_excel(config['planilla'])
feriados = ['2024-07-09', '2024-10-11']
calendario_con_feriados = pd.offsets.CustomBusinessDay(holidays=feriados)

class ActualState(BaseModel):
    nodo: int
    mensaje: str

def fin(parametro):
    return 'fin'

def verificar_dni(dni: str):
    dni = int(dni)
    return dni in dnis['DNI'].values

def verificar_correo(correo: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, correo) is not None

def verificar_mes_actual(fecha: str):
    fecha = datetime.datetime(fecha, '%d/%m/%Y')
    mes_actual = datetime.today().strftime('%m/%Y')
    return fecha.strftime('%m/%Y') == mes_actual

def verificar_fecha(fecha: str):
    fecha = datetime.datetime(fecha, '%d/%m/%Y')
    return fecha > datetime.today()

def dame_nombre(dni: str):
    dni = int(dni)
    return dnis[dnis['DNI'] == dni]['NOMBRE'].values[0]

def dame_deuda(dni: str):
    dni = int(dni)
    return dnis[dnis['DNI'] == dni]['DEUDA_TOTAL'].values[0]

def dame_fecha_limite():
    cantidad_dias = 5
    fecha_limite = pd.Timestamp(datetime.today()) + calendario_con_feriados * cantidad_dias
    return fecha_limite

def dame_planes(dni: str):
    dni = int(dni)
    fila = dnis[dnis['DNI'] == dni]
    return fila[['CANT CUOTAS 1', 'MONTON CUOTA 1', 'CANT CUOTAS 2', 'MONTON CUOTA 2', 'CANT CUOTAS 3', 'MONTON CUOTAS 3']]

def dame_oferta_fecha(dni: str):
    dni = str(dni)
    fila = dnis[dnis['DNI'] == dni]
    oferta = fila['OFERTA CANCELATORIA'].values[0]
    fecha_limite = dame_fecha_limite()
    return (oferta, fecha_limite)

@app.post('/respuesta')
async def respuesta(state: ActualState):
    funcion = mensajes[state.nodo]['siguientes']['funcion']
    decision = eval(funcion)(state.mensaje)
    proximo_nodo = mensajes[state.nodo]['siguientes']['resultados'][decision]
    valor_placeholder = eval(mensajes[proximo_nodo]['funcion'])(state.mensaje)
    texto = mensajes[proximo_nodo]['texto'].format(valor_placeholder)
    return texto

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
