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
feriados = config['feriados']
calendario_con_feriados = pd.offsets.CustomBusinessDay(holidays=feriados)

class ActualState(BaseModel):
    nodo: int
    mensaje: str
    dni: Optional[str] = None

class Telefono(BaseModel):
    numero_telefono: str
    dni: str

def modificar_csv(campo, valor, dni):
    dnis = pd.read_csv(config['planilla_salida'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
    dnis.loc[dnis['DNI'] == dni, [campo]] = valor
    dnis.to_csv(config['planilla'], index=False)

def leer_xlsx(campo, dni):
    dnis = pd.read_excel(config['planilla_entrada'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
    return dnis[dnis['DNI'] == dni][campo].values[0]

def fin(parametro, *args):
    return 'fin'

def verificar_dni(dni: str, *args):
    dnis = pd.read_excel(config['planilla_entrada'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
    return dni in dnis['DNI'].values

def verificar_correo(correo: str, dni: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, correo) is None:
        raise Exception('mail invalido')
    else:
        modificar_csv('MAIL2', correo, dni)
        return True

def verificar_estado(opcion :str, dni:str):
    estado = None
    if opcion == '3':
        estado = 'LIBRE DEUDA'
    elif opcion == '4':
        estado = 'DEFENSA DEL CONSUMIDOR'
    elif opcion == '5':
        estado = 'DESCONOCE DEUDA'
    modificar_csv('ESTADO', estado, dni)
    return opcion

def verificar_mes_actual(fecha: str, dni: str):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    mes_actual = datetime.today().strftime('%m/%Y')
    if fecha <= datetime.today() and fecha.strftime('%m/%Y') == mes_actual:
        modificar_csv('ESTADO', 'Ya pagó', dni)
        return True
    else:
        raise Exception('mes incorrecto')

def verificar_fecha(fecha: str, dni: str):
    fecha_formateada = datetime.strptime(fecha, '%d/%m/%Y')
    if fecha_formateada > datetime.today():
        modificar_csv('fecha_de_pago', fecha, dni)
        return True
    else:
        raise Exception('fecha incorrecta')

def dame_deuda(dni: str, *args):
    return leer_xlsx('DEUDA_TOTAL', dni)

def dame_nombre(dni: str, *args):
    return leer_xlsx('NOMBRE', dni)

def dame_oferta(dni: str, *args):
    oferta = leer_xlsx('OFERTA', dni)
    return '{0:.2f}'.format(oferta)

def dame_fecha_limite(dni: str, *args):
    cantidad_dias = config['cantidad_dias']
    fecha_limite = pd.Timestamp(datetime.today()) + calendario_con_feriados * cantidad_dias
    return fecha_limite.date().strftime('%d/%m/%Y')

def dame_planes(dni: str, *args):
    lista = list(leer_xlsx(['CANT  CUOTAS 1', 'MONTON CUOTA 1', 'CANT  CUOTAS 2', 'MONTON CUOTA 2', 'CANT  CUOTAS 3', 'MONTON CUOTA 3'], dni))
    lista = list(map(lambda x: int(x[1]) if x[0] % 2 == 0 else '{0:.2f}'.format(x[1]), enumerate(lista)))
    return lista

def dame_oferta_fecha(dni: str, *args):
    oferta = leer_xslx('OFERTA CANCELATORIA ', dni)
    fecha_limite = dame_fecha_limite(dni)
    return [oferta, fecha_limite]

def confirma_pago(mensaje: str, dni: str):
    if mensaje == "2":
        modificar_csv('ESTADO', 'No puede pagar', dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        modificar_csv('monto_elegido', None, dni)
    return mensaje

def elegir_plan(mensaje: str, dni: str):
    modificar_csv('cant_cuotas_elegido', 'CANT  CUOTAS'+mensaje, dni)
    modificar_csv('monto_elegido', 'MONTON CUOTA '+mensaje, dni)
    return "17"

@app.post('/respuesta')
async def respuesta(state: ActualState):
    try:
        nodo = str(state.nodo)
        funcion = mensajes[nodo]['siguientes']['funcion']
        decision = str(eval(funcion)(state.mensaje, state.dni))
        proximo_nodo = mensajes[nodo]['siguientes']['resultados'][decision]
        if nodo not in ("0","1") and not verificar_dni(state.dni):
            raise Exception('DNI invalido')
        if 'funcion' in mensajes[proximo_nodo].keys():
            valor_placeholder = eval(mensajes[proximo_nodo]['funcion'])(state.dni)
            if isinstance(valor_placeholder, list):
                texto = mensajes[proximo_nodo]['texto'].format(*valor_placeholder)
            else:
                texto = mensajes[proximo_nodo]['texto'].format(valor_placeholder)
        else:
            texto = mensajes[proximo_nodo]['texto']
    except Exception as e:
        print(e)
        texto = 'payload invalido'
    return {"respuesta": texto}

@app.post('/telefono')
async def telefono(telefono: Telefono):
    numero_telefono = telefono.numero_telefono.strip()
    regex = r"\+54 9 (\d{4} \d{2}|\d{3} \d{3}|\d{2} \d{4})[- ]\d{4}"
    if re.fullmatch(regex, numero_telefono) is not None:
        modificar_csv('telefono', numero_telefono, dni)
        texto = 'OK'
    else:
        texto = 'payload invalido'
    return {'respuesta': texto}

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
