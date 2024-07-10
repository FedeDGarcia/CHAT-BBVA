from fastapi import fastAPI
from pydantic import BaseModel
import uvicorn
import yaml
import pandas

app = fastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']

class ActualState:
    nodo: int
    mensaje: str

def fin(parametro):
    pass

def verificar_dni(dni: str):
    dni = int(str)
    dnis = pd.read_excel(config['planilla'])
    return dni in dnis['DNI']

@app.post('/respuesta')
async def respuesta(state: ActualState):
    funcion = mensajes[state.nodo]['siguientes']['funcion']
    decision = funcion(state.mensaje)
    proximo_nodo = mensajes[state.nodo]['siguientes'][decision]
    texto = mensajes[proximo_nodo]['texto']
    return texto

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
