import unittest
import requests
from datetime import datetime, timedelta
import pandas as pd
import yaml
import json
import numpy as np

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

mensajes = config['mensajes']
url = 'http://localhost:3000/respuesta'
headers = {'Content-type': 'application/json'}

dni_invalido = '12345678'
dni_valido = '43527224'

def verificar_valor(dni, campo, valor_esperado):
    df = pd.read_csv(config['planilla_salida'], dtype={'DNI': str})
    return df[df['DNI'] == dni][campo].values[0] == valor_esperado

def requestAPI(payload):
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    respuesta_json = json.loads(response.text)
    return respuesta_json['respuesta'].strip('"'), respuesta_json['nodo']

class Nodo0(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 0, 'mensaje': dni_valido, 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'URO ROCIO MARCELA Un gusto saludarte!\nTe pedimos que nos facilites un correo electrónico para continuar con la gestión')
        self.assertEqual(response[1], '3')

    def test_dni_invalido(self):
        payload = {'nodo': 0, 'mensaje': dni_invalido, 'dni': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Hoy no tenemos asignada una deuda con tu número de DNI...\nIndicanos por favor el número de DNI DEL TITULAR DE LA CUENTA')
        self.assertEqual(response[1], '1')

class Nodo1(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 1, 'mensaje': dni_valido, 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'URO ROCIO MARCELA Un gusto saludarte!\nTe pedimos que nos facilites un correo electrónico para continuar con la gestión')
        self.assertEqual(response[1], '3')

    def test_dni_invalido(self):
        payload = {'nodo': 1, 'mensaje': dni_invalido, 'dni': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Al momento en CDN no tenemos asignada tu deuda, por favor contactate con BBVA al 0800-999-2282 DE LUNES A VIERNES DE 10 A 15 HS')
        self.assertEqual(response[1], '2')

class Nodo2(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 2, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo3(unittest.TestCase):
    def test_mail_valido(self):
        payload = {'nodo': 3, 'mensaje': 'prueba@gmail.com', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')
        self.assertTrue(verificar_valor(dni_valido, 'MAIL2', 'prueba@gmail.com'))

    def test_mail_invalido(self):
        payload = {'nodo': 3, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

    def test_no_tiene_mail(self):
        payload = {'nodo': 3, 'mensaje': 'No tengo mail', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')
        payload = {'nodo': 3, 'mensaje': 'No tengo correo electronico', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')

    def test_no_usa_mail(self):
        payload = {'nodo': 3, 'mensaje': 'No uso mail', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')
        payload = {'nodo': 3, 'mensaje': 'No uso correo electronico', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')

    def test_no_recuerda_correo(self):
        payload = {'nodo': 3, 'mensaje': 'No lo recuerdo', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')
        payload = {'nodo': 3, 'mensaje': 'No me acuerdo', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], '¡Muchas gracias!\n Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n 1) YA PAGUE\n 2) QUIERO CONOCER MIS OPCIONES DE PAGO\n 3) LIBRE DEUDA\n 4) DEFENSA DEL CONSUMIDOR\n 5) DESCONOZCO DEUDA / NO TENGO DEUDA CON BBVA')
        self.assertEqual(response[1], '4')

class Nodo4(unittest.TestCase):
    maxDiff = None
    def test_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Perfecto, te pedimos  que nos indiques la fecha de pago EJ: 01/03/2024\nY nos envies el archivo adjunto del comprobante para poder registrarlo')
        self.assertEqual(response[1], '5')

    def test_opciones_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Perfecto, hoy tenemos una oferta única para vos, con una quita extraordinaria , cancelás por $15026.60 ¿Ves factible abonar esto al 16/08/2024?\n1) SI\n2) NO')
        self.assertEqual(response[1], '6')

    def test_libre_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '3'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Para solicitar el LIBRE DEUDA  podés acercarte a la sucursal más cercana o comunicarse al 0800-999-2282 de Lunes a Viernes de 10 a 15 hs\nMuchas gracias')
        self.assertEqual(response[1], '7')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'LIBRE DEUDA'))

    def test_defensa_consumidor(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '4'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Estimado/a te va estar llamando a la brevedad el asesor designado a tu legajo en el horario de 9 a 17 hs.\n¡Saludos!')
        self.assertEqual(response[1], '8')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'DEFENSA DEL CONSUMIDOR'))

    def test_desconozco_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '5'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Como desconoces la deuda, en breves un asesor se comunicará y  te dará más detalles.\nRecordá que nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podes contactar con nosotros al 0800 220 0059.\nMuchas gracias')
        self.assertEqual(response[1], '9')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'DESCONOCE DEUDA'))

    def test_opcion_invalida(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '6'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

    def test_dni_invalido(self):
        payload = {'nodo': 4, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo5(unittest.TestCase):
    def test_mes_actual(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Muchas gracias por enviarnos el comprobante de pago, en las proximas 48 hs impactará en su cuenta')
        self.assertEqual(response[1], '10')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'Ya pagó'))

    def test_otro_mes(self):
        fecha_hoy = datetime.today()
        fecha_mes_siguiente = fecha_hoy + timedelta(days=30)
        fecha_mes_siguiente = fecha_mes_siguiente.strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_mes_siguiente}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

    def test_dni_invalido(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_invalido, 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo6(unittest.TestCase):
    def test_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Perfecto, entonces el pago deberá realizarse antes de 16/08/2024. ¿Confirma?\n1) SI\n2) NO')
        self.assertEqual(response[1], '11')

    def test_no_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')

    def test_pide_cuotas(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Necesito cuotas'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Necesito un plan de pagos'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Plan en cuotas'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Cuotas'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')

    def test_pide_refinanciacion(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Necesito refinanciar'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Quiero refinanciar'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Refinanciacion'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')

    def test_pide_otras(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'Acuerdo'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': 'A cuenta'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes  y honorarios por la operación.\nPodemos ofrecerte un plan de pagos abonando hasta el día de hoy CON HASTA 50% OFF\n¿Te interesaría conocer nuestras propuestas?\n1) SI\n2) NO')
        self.assertEqual(response[1], '12')

    def test_dni_invalido(self):
        payload = {'nodo': 6, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo7(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 7, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo8(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 8, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo9(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 9, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo10(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 10, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo11(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 11, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envio del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debes realizarlo en un cajero automático:\n1° PAGOS\n2° RECAUDACIONES\n3° EFECTIVO EN PESOS\n4° CODIGO DE SERVICIO: 4482\n5° NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6° TOTAL A PAGAR: (Valor primera cuota)\n7° PARA TRANSFERENCIA A ICHTHYS S.R.L (Razón social)\nNUMERO: :331-422456/6 CUIT: 30715141627 CBU:0170331120000042245663\nUna vez que realices el pago por favor envia el comprobante por:\nWhatsapp: wa.link/bbva_estudiocdn\nEmail:\ncdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 09 a 17.30 hs\no bien te podes contactar con nosotros al 0800 220 0059\nSaludos.')
        self.assertEqual(response[1], '13')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', '16/08/2024'))

    def test_no_confirma(self):
        payload = {'nodo': 11, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Indicanos en que fecha ves factible abonar tu deuda con BBVA en el siguiente formato\nEJ: 02/03/2024.')
        self.assertEqual(response[1], '14')

    def test_dni_invalido(self):
        payload = {'nodo': 11, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo12(unittest.TestCase):
    maxDiff = None
    def test_quiere_conocer_cuotas(self):
        payload = {'nodo': 12, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entendemos que este no es un monto viable para vos para cancelar tu deuda.\nDesde CDN te podemos ofrecer las siguientes opciones de pago.\n¡Elegi la opción que más te convenga!\n1) Cancelas por 2  DE $ 6010.64.\n2) Cancelas por 3  DE $ 3506.21.\n3) Cancelas por 3  DE $ 4507.98.')
        self.assertEqual(response[1], '15')

    def test_no_quiere_cuotas(self):
        payload = {'nodo': 12, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')

    def test_dni_invalido(self):
        payload = {'nodo': 12, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo13(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 13, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

class Nodo14(unittest.TestCase):
    def test_fecha_pasada(self):
        fecha_hoy = datetime.today()
        fecha_pasada = fecha_hoy - timedelta(days=1000)
        fecha_pasada = fecha_pasada.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_pasada}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)
        #self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'No puede pagar'))

    def test_fecha_futura(self):
        fecha_hoy = datetime.today()
        fecha_futura = fecha_hoy + timedelta(days=1000)
        fecha_futura = fecha_futura.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_futura}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envio del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debes realizarlo en un cajero automático:\n1° PAGOS\n2° RECAUDACIONES\n3° EFECTIVO EN PESOS\n4° CODIGO DE SERVICIO: 4482\n5° NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6° TOTAL A PAGAR: (Valor primera cuota)\n7° PARA TRANSFERENCIA A ICHTHYS S.R.L (Razón social)\nNUMERO: :331-422456/6 CUIT: 30715141627 CBU:0170331120000042245663\nUna vez que realices el pago por favor envia el comprobante por:\nWhatsapp: wa.link/bbva_estudiocdn\nEmail:\ncdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 09 a 17.30 hs\no bien te podes contactar con nosotros al 0800 220 0059\nSaludos.')
        self.assertEqual(response[1], '13')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', fecha_futura))

    def test_fecha_mal_formateada(self):
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': '2100-02-02'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

    def test_dni_invalido(self):
        payload = {'nodo': 14, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo15(unittest.TestCase):
    def elige_opcion_pago(self):
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Perfecto, entonces el pago deberá realizarse antes de 01/01/2020\n¿Confirma?\n1) SI \n2) NO')
        self.assertEqual(response[1], 17)
        self.assertTrue(verificar_valor(dni_valido, 'cant_cuotas_elegido', 2))
        self.assertTrue(verificar_valor(dni_valido, 'monto_elegido', 6010.64))

    def test_dni_invalido(self):
        payload = {'nodo': 15, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

    def test_rechaza_cuotas(self):
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': 'No me sirven esas cuotas'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': 'Necesito mas cuotas'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': 'No puedo pagar en esa fecha'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': 'No puedo pagar esos montos'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')

class Nodo16(unittest.TestCase):
    def test_telefono_valido(self):
        payload = {'nodo': 16, 'mensaje': '+54 9 11 1234-5678', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')
        self.assertTrue(verificar_valor(dni_valido, 'telefono2', '+54 9 11 1234-5678'))

    def test_telefono_invalido(self):
        payload = {'nodo': 16, 'mensaje': '+54 9 11 1234-sdfsfg5678', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Conversación terminada')
        self.assertEqual(response[1], '18')

    def test_dni_invalido(self):
        payload = {'nodo': 16, 'mensaje': '+54 9 11 1234-5678', 'dni': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Nodo17(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envio del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debes realizarlo en un cajero automático:\n1° PAGOS\n2° RECAUDACIONES\n3° EFECTIVO EN PESOS\n4° CODIGO DE SERVICIO: 4482\n5° NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6° TOTAL A PAGAR: (Valor primera cuota)\n7° PARA TRANSFERENCIA A ICHTHYS S.R.L (Razón social)\nNUMERO: :331-422456/6 CUIT: 30715141627 CBU:0170331120000042245663\nUna vez que realices el pago por favor envia el comprobante por:\nWhatsapp: wa.link/bbva_estudiocdn\nEmail:\ncdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 09 a 17.30 hs\no bien te podes contactar con nosotros al 0800 220 0059\nSaludos.')
        self.assertEqual(response[1], '13')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', '20/04/2027'))

    def test_no_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'Entiendo. Te voy a pedir un teléfono de contacto alternativo para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs\ny te podes contactar con nosotros al 0800 220 0059 o  por mail\ncdncobranzas@companiadelnorte.com')
        self.assertEqual(response[1], '16')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'No puede pagar'))
        self.assertTrue(verificar_valor(dni_valido, 'cant_cuotas_elegido', np.nan))
        self.assertTrue(verificar_valor(dni_valido, 'monto_elegido', np.nan))

    def test_dni_invalido(self):
        payload = {'nodo': 17, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response[0], 'payload invalido')
        self.assertEqual(response[1], -1)

class Telefono(unittest.TestCase):
    url = 'http://localhost:3000/telefono'
    def test_telefono_valido(self):
        payload = {'numero_telefono': '+54 9 11 1234-5678', 'dni': dni_valido}
        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(json.loads(response.text)['respuesta'], 'OK')
        self.assertTrue(verificar_valor(dni_valido, 'telefono', '+54 9 11 1234-5678'))

    def test_telefono_invalido(self):
        payload = {'numero_telefono': '+54 9 11 1234sdf-5678', 'dni': dni_valido}
        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(json.loads(response.text)['respuesta'], 'payload invalido')

    def test_dni_invalido(self):
        payload = {'numero_telefono': '+54 9 11 1234-5678', 'dni': dni_invalido}
        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(json.loads(response.text)['respuesta'], 'payload invalido')

if __name__ == '__main__':
    unittest.main()
