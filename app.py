from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import yaml
import pandas as pd

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']
dnis = pd.read_excel(config['planilla'])

class ActualState(BaseModel):
    nodo: int
    mensaje: str

def pasar(parametro):
    return 'pasar'

def fin(parametro):
    return 'fin'

def verificar_dni(dni: str):
    dni = int(dni)
    return dni in dnis['DNI'].values

def dame_nombre(dni: str):
    dni = int(dni)
    return dnis[dnis['DNI'] == dni]['NOMBRE'].values[0]

@app.post('/respuesta')
async def respuesta(state: ActualState):
    funcion = mensajes[state.nodo]['siguientes']['funcion']
    decision = eval(funcion)(state.mensaje)
    proximo_nodo = mensajes[state.nodo]['siguientes']['resultados'][decision]
    nombre = eval(mensajes[proximo_nodo]['funcion'])(state.mensaje)
    print(nombre)
    texto = mensajes[proximo_nodo]['texto'].format(nombre)
    return texto

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
