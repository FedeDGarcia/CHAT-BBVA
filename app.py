from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import yaml
import pandas as pd
import re

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']
dnis = pd.read_excel(config['planilla'])

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

def dame_nombre(dni: str):
    dni = int(dni)
    return dnis[dnis['DNI'] == dni]['NOMBRE'].values[0]

def dame_deuda(dni: str):
    dni = int(dni)
    return dnis[dnis['DNI'] == dni]['DEUDA_TOTAL'].values[0]

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
