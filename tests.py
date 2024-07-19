import unittest
import requests

url = 'http://localhost:3000/respuesta'
headers = {'Content-type': 'application/json'}

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
