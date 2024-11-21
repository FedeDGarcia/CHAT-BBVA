from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import yaml
import pandas as pd
import numpy as np
import re
import unidecode
from datetime import datetime
from pydantic import BaseModel
from openai import OpenAI
from pandas.tseries.offsets import MonthEnd

app = FastAPI()

client = OpenAI(api_key='')

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.BaseLoader)

mensajes = config['mensajes']
feriados = config['feriados']
prompts = config['prompts']
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
    dnis.to_csv(config['planilla_salida'], index=False)

def leer_csv(campo, dni):
    dnis = pd.read_csv(config['planilla_salida'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
    return dnis[dnis['DNI'] == dni][campo].values[0]

def leer_xlsx(campo, dni):
    dnis = pd.read_excel(config['planilla_entrada'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
    return dnis[dnis['DNI'] == dni][campo].values[0]

def fin(parametro, *args):
    return 'fin'

def verificar_dni(dni: str, *args):
    if dni_mal_escrito(dni):
        return 'mal escrito'
    else:
        dnis = pd.read_excel(config['planilla_entrada'], dtype={'DNI': str, 'CANT  CUOTAS 1': int, 'CANT  CUOTAS 2': int, 'CANT  CUOTAS 3': int, 'telefono': str})
        return dni in dnis['DNI'].values

def ya_tiene_promesa(dni: str):
    estado = leer_csv('ESTADO', dni)
    resolucion = leer_csv('resolucion', dni)
    return estado.lower() in ['compromete fecha', 'promesa en curso'] or resolucion.lower in ['compromete fecha', 'promesa en curso']

def verificar_correo(correo: str, dni: str):
    respuesta = None
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, correo) is None:
        respuesta = False
    else:
        modificar_csv('mail_nuevo', correo, dni)
        respuesta = True
    if ya_tiene_promesa(dni):
        respuesta = 'promesa en curso'

    return respuesta

def verificar_estado(opcion :str, dni:str):
    estado = None
    opcion = unidecode.unidecode(opcion.lower())
    if opcion == '3' or opcion == 'libre deuda':
        estado = 'LIBRE DEUDA'
    elif opcion == '4' or opcion == 'defensa del consumidor':
        estado = 'DEFENSA DEL CONSUMIDOR'
    elif opcion == '5' or opcion == 'desconozco deuda' or opcion == 'no tengo deuda con bbva':
        estado = 'DESCONOCE DEUDA'
    modificar_csv('resolucion', estado, dni)
    return unidecode.unidecode(opcion.lower())

def verificar_mes_actual(fecha: str, dni: str):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')
    mes_actual = datetime.today().strftime('%m/%Y')
    if fecha <= datetime.today() and fecha.strftime('%m/%Y') == mes_actual:
        modificar_csv('resolucion', 'Ya pagó', dni)
        return True
    else:
        raise Exception('mes incorrecto')

def verificar_fecha(fecha: str, dni: str):
    if fecha == '1' or unidecode.unidecode(fecha.lower()) == 'si':
        fecha = dame_fecha_limite(dni)
    if fecha == '2' or unidecode.unidecode(fecha.lower()) == 'no':
        modificar_csv('fecha_de_pago', None, dni)
        modificar_csv('resolucion', 'No puede pagar', dni)
        modificar_csv('monto_elegido', None, dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        return False
    fecha_formateada = datetime.strptime(fecha, '%d/%m/%Y').date()
    fecha_limite_2 = datetime.strptime(dame_fecha_limite_2(dni), '%d/%m/%Y').date()
    if fecha_formateada >= datetime.today().date() and fecha_formateada <= fecha_limite_2:
        modificar_csv('fecha_de_pago', fecha, dni)
        modificar_csv('resolucion', 'Compromete fecha', dni)

        return True
    else:
        modificar_csv('fecha_de_pago', None, dni)
        modificar_csv('resolucion', 'No puede pagar', dni)
        modificar_csv('monto_elegido', None, dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        return False

def verificar_fecha_un_pago(fecha: str, dni: str):
    if fecha == '1' or unidecode.unidecode(fecha.lower()) == 'si':
        fecha = dame_fecha_limite(dni)
    elif fecha == '2' or unidecode.unidecode(fecha.lower()) == 'no':
        modificar_csv('fecha_de_pago', None, dni)
        modificar_csv('resolucion', 'No puede pagar', dni)
        modificar_csv('monto_elegido', None, dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        return False
    # Convertir la fecha ingresada y la fecha límite a objetos datetime.date()
    fecha_formateada = datetime.strptime(fecha, '%d/%m/%Y').date()
    fecha_limite_2 = datetime.strptime(dame_fecha_limite_2(dni), '%d/%m/%Y').date()
    # Verificar que la fecha_formateada sea mayor o igual que la fecha actual y menor o igual a fecha_limite_2
    if fecha_formateada >= datetime.today().date() and fecha_formateada <= fecha_limite_2:
        modificar_csv('fecha_de_pago', fecha, dni)
        modificar_csv('resolucion', 'Compromete fecha', dni)
        oferta = leer_xlsx('OFERTA CANCELATORIA ', dni)
        modificar_csv('monto_elegido', oferta, dni)
        modificar_csv('cant_cuotas_elegido', 1, dni)
        return True
    else:
        modificar_csv('fecha_de_pago', None, dni)
        modificar_csv('resolucion', 'No puede pagar', dni)
        modificar_csv('monto_elegido', None, dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        return False


def dame_deuda(dni: str, *args):
    return leer_xlsx('DEUDA_TOTAL', dni)

def dame_nombre(dni: str, *args):
    return leer_xlsx('NOMBRE', dni)

def dame_oferta(dni: str, *args):
    oferta = leer_xlsx('OFERTA CANCELATORIA ', dni)
    return '{0:.2f}'.format(oferta)

def dame_fecha_limite(dni: str, *args):
    cantidad_dias = int(config['cantidad_dias_primer_oferta'])
    fecha_actual = pd.Timestamp(datetime.today())
    fecha_limite = fecha_actual + calendario_con_feriados * cantidad_dias
        # Comprobar si la fecha límite cae en un mes diferente al mes actual
    if fecha_limite.month != fecha_actual.month:
        # Encontrar el último día hábil del mes actual
        ultimo_dia_mes = (fecha_actual + MonthEnd(0)).normalize()
        # Buscar el último día hábil antes o en el último día del mes
        while ultimo_dia_mes.weekday() >= 5 or ultimo_dia_mes in pd.to_datetime(feriados):
            ultimo_dia_mes -= pd.Timedelta(days=1)
        # Actualizar la fecha límite al último día hábil del mes actual
        fecha_limite = ultimo_dia_mes
    return fecha_limite.date().strftime('%d/%m/%Y')

def dame_fecha_limite_2(dni: str, *args):
    cantidad_dias = int(config['cantidad_dias_segunda_oferta'])
    fecha_actual = pd.Timestamp(datetime.today())
    # Calcular la fecha límite sumando 7 días corrientes
    fecha_limite = fecha_actual + pd.Timedelta(days= cantidad_dias)
    # Comprobar si la fecha límite cae en un mes diferente al mes actual
    if fecha_limite.month != fecha_actual.month:
        # Encontrar el último día del mes actual
        ultimo_dia_mes = (fecha_actual + MonthEnd(0)).normalize()
        # Buscar el último día hábil antes o en el último día del mes
        while ultimo_dia_mes.weekday() >= 5 or ultimo_dia_mes in pd.to_datetime(feriados):
            ultimo_dia_mes -= pd.Timedelta(days=1)
        # Actualizar la fecha límite al último día hábil del mes actual
        fecha_limite = ultimo_dia_mes
    # Formatear la fecha al formato 'dd/mm/yyyy'
    return fecha_limite.date().strftime('%d/%m/%Y')

def dame_planes(dni: str, *args):
    lista = list(leer_xlsx(['CANT  CUOTAS 1', 'MONTO CUOTA 1', 'CANT  CUOTAS 2', 'MONTO CUOTA 2', 'CANT  CUOTAS 3', 'MONTO CUOTA 3'], dni))
    lista = list(map(lambda x: int(x[1]) if x[0] % 2 == 0 else '{0:.2f}'.format(x[1]), enumerate(lista)))
    return lista

def dame_oferta_fecha(dni: str, *args):
    oferta = leer_xlsx('OFERTA CANCELATORIA ', dni)
    oferta = '{0:.2f}'.format(oferta)
    fecha_limite = dame_fecha_limite(dni)
    return [oferta, fecha_limite]

def dame_primera_cuota(dni: str, *args):
    cuota = leer_csv('monto_elegido', dni)
    if np.isnan(cuota):
        cuota = leer_csv('OFERTA CANCELATORIA ', dni)
    return '{0:.2f}'.format(cuota)

def confirma_pago(mensaje: str, dni: str):
    mensaje = unidecode.unidecode(mensaje.lower())
    if mensaje == "1" or mensaje == 'si':
        fecha_limite = dame_fecha_limite(dni)
        modificar_csv('fecha_de_pago', fecha_limite, dni)
        modificar_csv('resolucion', 'Compromete fecha', dni)
    if mensaje == "2" or mensaje == 'no':
        modificar_csv('resolucion', 'No puede pagar', dni)
        modificar_csv('cant_cuotas_elegido', None, dni)
        modificar_csv('monto_elegido', None, dni)
    return mensaje

def elegir_plan(mensaje: str, dni: str):
    if mensaje in ['1', '2', '3']:
        modificar_csv('cant_cuotas_elegido', leer_xlsx('CANT  CUOTAS '+mensaje, dni), dni)
        modificar_csv('monto_elegido', leer_xlsx('MONTO CUOTA '+mensaje, dni), dni)
        return "17"

def modificar_telefono(numero_telefono, dni, campo='telefono2'):
    regex = r"\+54 9 (\d{4} \d{2}|\d{3} \d{3}|\d{2} \d{4})[- ]\d{4}"
    if re.fullmatch(regex, numero_telefono) is not None and verificar_dni(dni) and (campo != 'telefono2' or leer_csv('telefono', dni) != numero_telefono):
        modificar_csv(campo, numero_telefono, dni)
        return True
    else:
        raise Exception('Telefono invalido')

def dni_mal_escrito(dni):
    dni = dni.rstrip()  # Elimina los espacios al final del DNI
    if "." in dni or " " in dni:
        return True
    else:
        return False

class Nodo(BaseModel):
    numero_nodo: int

def llamar_GPT(mensaje, prompt):
    completion = client.beta.chat.completions.parse(
                        model=config['modelo_GPT'],
                        messages=[
                            {"role": "system", "content": prompts[prompt]},
                            {"role": "user", "content": f"A que se nodo iria este mensaje {mensaje}?"}
                        ],
            	        response_format=Nodo,
                        temperature=0.7
                    )
    nodo = completion.choices[0].message.parsed.numero_nodo
    if nodo == -1:
        return None
    return str(nodo)

def preguntar_salto(mensaje, dni, mail_pedido, cuotas_dadas, fecha_dada_un_pago, fecha_dada_cuotas):

    if mail_pedido:
        salto = llamar_GPT(mensaje, "0")
        if salto is not None and not ya_tiene_promesa(dni):
            return salto

    if not cuotas_dadas:
        salto = llamar_GPT(mensaje, "1")
        if salto is not None:
            return salto

    if cuotas_dadas:
        salto2 = llamar_GPT(mensaje, "2")
        if salto2 is not None:
            return salto2

    if fecha_dada_un_pago:
        salto3 = llamar_GPT(mensaje, "3")
        if salto3 is not None:
            return salto3

    if fecha_dada_cuotas:
        salto4 = llamar_GPT(mensaje, "4")
        if salto4 is not None:
            return salto4

    # Si todos son None, devolverá None automáticamente
    return None

@app.post('/respuesta')
async def respuesta(state: ActualState):
    try:
        nodo = str(state.nodo)

        if nodo in ['3']:
            mail_pedido = True
        else:
            mail_pedido = False

        if nodo in ['15', '17']:
            cuotas_dadas = True
        else:
            cuotas_dadas = False

        if nodo in ['6', '11']:
            fecha_dada_un_pago = True
        else:
            fecha_dada_un_pago = False

        if nodo in ['15', '17']:
            fecha_dada_cuotas = True
        else:
            fecha_dada_cuotas = False

        salto = preguntar_salto(state.mensaje, state.dni, mail_pedido, cuotas_dadas, fecha_dada_un_pago, fecha_dada_cuotas)

        if salto:
            proximo_nodo = salto

        else:
            funcion = mensajes[nodo]['siguientes']['funcion']
            decision = str(eval(funcion)(state.mensaje, state.dni))
            proximo_nodo = mensajes[nodo]['siguientes']['resultados'][decision]
        if nodo not in ("0","1","2","22","23") and not verificar_dni(state.dni):
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
        proximo_nodo = -1
    return {"respuesta": texto, "nodo": proximo_nodo}

@app.post('/telefono')
async def telefono(telefono: Telefono):
    try:
        numero_telefono = telefono.numero_telefono.strip()
        modificar_telefono(numero_telefono, telefono.dni, 'telefono')
        texto = 'OK'
    except:
        texto = 'payload invalido'
    return {'respuesta': texto}

@app.post('/subir_xlsx')
async def subir_planilla(file: UploadFile = File(...)):
    try:
        if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            raise Exception('Bad content type, must be application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        contents = file.file.read()
        with open(config['planilla_entrada'], 'wb') as f:
            f.write(contents)

        df = pd.read_excel(config['planilla_entrada'])
        columnas_necesarias = ['DNI', 'ESTADO', 'DEUDA_TOTAL', 'NOMBRE', 'CANT  CUOTAS 1', 
                               'MONTO CUOTA 1', 'CANT  CUOTAS 2', 'MONTO CUOTA 2', 
                               'CANT  CUOTAS 3', 'MONTO CUOTA 3', 'OFERTA CANCELATORIA ']
        df = df.dropna(subset=columnas_necesarias)
        df.to_excel(config['planilla_entrada'], index=False)

        nuevas_columnas = ['mail_nuevo', 'telefono', 'telefono2', 'resolucion', 
                           'fecha_de_pago', 'cant_cuotas_elegido', 'monto_elegido']
        for col in nuevas_columnas:
            if col not in df.columns:
                df[col] = None

        # Leer el archivo de salida existente
        df_original = pd.read_csv(config['planilla_salida'])

        # Identificar registros con DNI repetidos
        comunes = df_original[df_original['DNI'].isin(df['DNI'])].copy()
        nuevos = df[~df['DNI'].isin(df_original['DNI'])]

        # Mantener valores originales para DNIs repetidos
        comunes_actualizados = comunes.set_index('DNI').combine_first(df.set_index('DNI')).reset_index()

        # Concatenar los nuevos registros y los actualizados
        df_final = pd.concat([comunes_actualizados, nuevos], ignore_index=True)

        df_final.to_csv(config['planilla_salida'], index=False)

        texto = 'OK'
    except Exception as e:
        texto = f"payload invalido, {e}"
    return {'respuesta': texto}


@app.get('/bajar_csv')
async def bajar_planilla():
    df = pd.read_csv(config['planilla_salida'])
    
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
    
    temp_file = 'planilla.csv'
    df.to_csv(temp_file, index=False)
    
    return FileResponse(temp_file)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3000)
