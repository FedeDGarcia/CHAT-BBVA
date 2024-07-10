from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import yaml
import pandas as pd

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']

class ActualState(BaseModel):
    nodo: int
    mensaje: str

def fin(parametro):
    return 'fin'

def verificar_dni(dni: str):
    dni = int(dni)
    dnis = pd.read_excel(config['planilla'])
    return dni in dnis['DNI'].values

@app.post('/respuesta')
async def respuesta(state: ActualState):
    funcion = mensajes[state.nodo]['siguientes']['funcion']
    decision = eval(funcion)(state.mensaje)
    proximo_nodo = mensajes[state.nodo]['siguientes']['resultados'][decision]
    texto = mensajes[proximo_nodo]['texto']
    return texto

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
