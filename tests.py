import unittest
import requests
from datetime import datetime, timedelta
import pandas as pd
import yaml
import json

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
    return json.loads(response.text)['respuesta'].strip('"')

class Nodo0(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 0, 'mensaje': dni_valido, 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'URO ROCIO MARCELA Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 0, 'mensaje': dni_invalido, 'dni': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Hoy no tenemos asignada una deuda con tu número de DNI. Indicanos por favor el número de DNI DEL TITULAR DE LA CUENTA')

class Nodo1(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 1, 'mensaje': dni_valido, 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'URO ROCIO MARCELA Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 1, 'mensaje': dni_invalido, 'dni': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Al momento en CDN no tenemos asignada tu deuda, por favor contactate con BBVA al 0800-999-2282 DE LUNES A VIERNES DE 10 A 15 HS')

class Nodo2(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 2, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo3(unittest.TestCase):
    def test_mail_valido(self):
        payload = {'nodo': 3, 'mensaje': 'prueba@gmail.com', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Muchas gracias! Te contamos que a la fecha estás en mora por un importe de $16543.75. Para poder ayudarte, decime el motivo de tu contacto\n1) Ya pague\n2) Quiero conocer mis opciones de pago\n3) Libre deuda\n4) Defensa del consumidor\n5) Desconozco deuda/No tengo deuda con BBVA')
        self.assertTrue(verificar_valor(dni_valido, 'MAIL2', 'prueba@gmail.com'))

    def test_mail_invalido(self):
        payload = {'nodo': 3, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo4(unittest.TestCase):
    def test_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, te pedimos que nos indiques la fecha de pago EJ: 01/03/2024 y nos envíes el archivo adjunto del comprobante para poder registrarlo')

    def test_opciones_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, hoy tenemos una oferta única para vos, con una quita extraordinaria, cancelás por $15026.59613. ¿Ves factible abonar esto al 29/07/2024?\n1) SI\n2) NO')

    def test_libre_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '3'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Para solicitar el libre deuda podés acercarte a la sucursal más cercana o comunicarse al 0800-999-2282 de lunes a viernes de 10 a 15 hs. Muchas gracias')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'LIBRE DEUDA'))

    def test_defensa_consumidor(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '4'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Estimado/a te va a estar llamando a la brevedad el asesor designado a tu legajo en el horario de 9 a 17 hs. Saludos!')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'DEFENSA DEL CONSUMIDOR'))

    def test_desconozco_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '5'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Como desconoces la deuda, en breves un asesor se comunicará y te dará más detalles. Recordá que nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059. Muchas gracias')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'DESCONOCE DEUDA'))

    def test_opcion_invalida(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '6'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        payload = {'nodo': 4, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo5(unittest.TestCase):
    def test_mes_actual(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response, 'Muchas gracias por enviarnos el comprobante de pago, en las proximas 48 hs impactará en su cuenta')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'Ya pagó'))

    def test_otro_mes(self):
        fecha_hoy = datetime.today()
        fecha_mes_siguiente = fecha_hoy + timedelta(days=30)
        fecha_mes_siguiente = fecha_mes_siguiente.strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_mes_siguiente}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_invalido, 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo6(unittest.TestCase):
    def test_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 29/07/2024. ¿Confirma?\n  1) SI\n  2) NO')

    def test_no_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Desconocemos la situación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes y honorarios por la operación. Podemos ofrecerte un plan de pagos CON HASTA 50 % OFF. Abonando hoy cancelás tu deuda por $5080.84.\nVes factible abonar este saldo?\n1) SI\n2) NO')

    def test_dni_invalido(self):
        payload = {'nodo': 6, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo7(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 7, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo8(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 8, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo9(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 9, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo10(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 10, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo11(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 11, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTHYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663\nUna vez que realices el pago por favor enviá el comprobante por:\nwhatsapp: wa.link/bbva_estudiocdn\nemail: cdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 9 a 17:30 hs o bien te podes contactar con nosotros al 0800 220 0059.\nSaludos.')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', '18/04/2027'))

    def test_no_confirma(self):
        payload = {'nodo': 11, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Indicanos en que fecha ves factible abonar tu deuda con BBVA en el siguiente formato EJ: 02/03/2024')

    def test_dni_invalido(self):
        payload = {'nodo': 11, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo12(unittest.TestCase):
    def test_abona(self):
        payload = {'nodo': 12, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 29/07/2024. ¿Confirma?\n  1) SI\n  2) NO')

    def test_no_abona(self):
        payload = {'nodo': 12, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entendemos que este no es un monto viable para vos para cancelar tu deuda. Desde CDN te podemos ofrecer las siguientes opciones de pago ¡Elegí la que más te convenga!\n1) Cancelas por 2 DE $6010.64\n2) Cancelas por 3 DE $3506.21\n3) Cancelas por 3 DE $4507.98')

    def test_dni_invalido(self):
        payload = {'nodo': 12, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo13(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 13, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo14(unittest.TestCase):
    def test_fecha_pasada(self):
        fecha_hoy = datetime.today()
        fecha_pasada = fecha_hoy - timedelta(days=1000)
        fecha_pasada = fecha_pasada.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_pasada}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')
        #self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'No puede pagar'))

    def test_fecha_futura(self):
        fecha_hoy = datetime.today()
        fecha_futura = fecha_hoy + timedelta(days=1000)
        fecha_futura = fecha_futura.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_futura}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTHYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663\nUna vez que realices el pago por favor enviá el comprobante por:\nwhatsapp: wa.link/bbva_estudiocdn\nemail: cdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 9 a 17:30 hs o bien te podes contactar con nosotros al 0800 220 0059.\nSaludos.')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', fecha_futura))

    def test_fecha_mal_formateada(self):
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': '2100-02-02'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        payload = {'nodo': 14, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo15(unittest.TestCase):
    def elige_opcion_pago(self):
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 01/01/2020')
        self.assertTrue(verificar_valor(dni_valido, 'cant_cuotas_elegido', 2))
        self.assertTrue(verificar_valor(dni_valido, 'monto_elegido', 6010.64))

    def test_dni_invalido(self):
        payload = {'nodo': 15, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo16(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 16, 'mensaje': 'blabla', 'dni': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversación terminada')

class Nodo17(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias, entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio.\nEl importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTHYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663\nUna vez que realices el pago por favor enviá el comprobante por:\nwhatsapp: wa.link/bbva_estudiocdn\nemail: cdncobranzas@companiadelnorte.com\nNuestro horario de recepción es de lunes a viernes de 9 a 17:30 hs o bien te podes contactar con nosotros al 0800 220 0059.\nSaludos.')
        self.assertTrue(verificar_valor(dni_valido, 'fecha_de_pago', '18/04/2027'))

    def test_no_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entiendo. Te voy a pedir un correo electrónico para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059 o por mail cdncobranzas@companiadelnorte.com')
        self.assertTrue(verificar_valor(dni_valido, 'ESTADO', 'No puede pagar'))
        self.assertTrue(verificar_valor(dni_valido, 'cant_cuotas_elegido', None))
        self.assertTrue(verificar_valor(dni_valido, 'monto_elegido', None))

    def test_dni_invalido(self):
        payload = {'nodo': 17, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Telefono(unittest.TestCase):
    url = 'http://localhost:3000/telefono'
    def test_telefono_valido(self):
        payload = {'numero_telefono': '+54 9 11 1234-5678', 'dni': dni_valido}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        self.assertEqual(response.text, 'OK')
        self.assertTrue(verificar_valor(dni_valido, 'telefono', '+54 9 11 1234-5678'))

    def test_telefono_invalido(self):
        payload = {'numero_telefono': '+54 9 11 1234sdf-5678', 'dni': dni_valido}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        self.assertEqual(response.text, 'payload invalido')

    def test_dni_invalido(self):
        payload = {'numero_telefono': '+54 9 11 1234-5678', 'dni': dni_valido}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        self.assertEqual(response.text, 'payload invalido')

if __name__ == '__main__':
    unittest.main()
