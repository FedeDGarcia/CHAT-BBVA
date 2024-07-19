import unittest
import requests
from datetime import datetime, timedelta
import pandas as pd

url = 'http://localhost:3000/respuesta'
headers = {'Content-type': 'application/json'}
df = pd.read_excel(config['planilla'], dtype={'DNI': str})

def requestAPI(payload):
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.text

class Nodo0(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 0, 'mensaje': '38602747'}
        response = requestAPI(payload)
        self.assertEqual(response, 'ACOSTA ARRIETA FEDERICO AGUSTI Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 0, 'mensaje': '12345678'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Hoy no tenemos asignada una deuda con tu numero de DNI. Indicanos por favor el numero de DNI del titular de la cuenta')

class Nodo1(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 0, 'mensaje': '38602747'}
        response = requestAPI(payload)
        self.assertEqual(response, 'ACOSTA ARRIETA FEDERICO AGUSTI Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 0, 'mensaje': '12345678'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Al momento en CDN no tenemos asignada tu deuda por favor contactate con BBVA al 0800-999-2282 de lunes a viernes de 10 a 15 hs')

class Nodo2(unnittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 2, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo3(unnittest.TestCase):
    def test_mail_valido(self):
        payload = {'nodo': 3, 'dni': '38602747', 'mensaje': 'prueba@gmail.com'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Muchas gracias')

    def test_mail_invalido(self):
        payload = {'nodo': 3, 'dni': '38602747', 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'ACOSTA ARRIETA FEDERICO AGUSTI Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

class Nodo4(unnittest.TestCase):
    def test_pago(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, te pedimos que nos indiques la fecha de pago EJ: 01/03/2024 y nos envíes el archivo adjunto del comprobante para poder registrarlo')

    def test_opciones_pago(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, hoy tenemos una oferta única para vos, con una quita extraordinaria, cancelás por $ 10 ¿Ves factible abonar esto al 01/01/2020?\n1) SI\n2)NO')

    def test_libre_deuda(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '3'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Para solicitar el libre deuda podés acercarte a la sucursal más cercana o comunicarse al 0800-999-2282 de lunes a viernes de 10 a 15 hs. Muchas gracias')

    def test_defensa_consumidor(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '4'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Estimado/a te va a estar llamando a la brevedad el asesor designado a tu legajo en el horario de 9 a 17 hs. Saludos!')

    def test_desconozco_deuda(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '5'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Como desconoces tu deuda, en breve un asesor se comunicará y te dará más detalles. Recordá que nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059. Muchas gracias')

    def test_opcion_invalida(self):
        payload = {'nodo': 4, 'dni': '38602747', 'mensaje': '6'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        payload = {'nodo': 4, 'dni': '12345678', 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo5(unnittest.TestCase):
    def test_mes_actual(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': '38602747', 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response, 'Muchas gracias por enviarnos el comprobante de pago en las proximas 48 hs impactara en su cuenta')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'Ya pagó')

    def test_otro_mes(self):
        fecha_hoy = datetime.today()
        fecha_mes_siguiente = fecha_hoy + timedelta(days=30)
        fecha_mes_siguiente = fecha_mes_siguiente.strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': '38602747', 'mensaje': fecha_mes_siguiente}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': '38602747', 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')
