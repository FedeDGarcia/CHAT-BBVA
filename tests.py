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
df = pd.read_excel(config['planilla'], dtype={'DNI': str})

def requestAPI(payload):
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.text.strip('"')

dni_invalido = '12345678'
dni_valido = '43527224'

class Nodo0(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 0, 'mensaje': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'URO ROCIO MARCELA Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 0, 'mensaje': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Hoy no tenemos asignada una deuda con tu número de DNI. Indicanos por favor el número de DNI DEL TITULAR DE LA CUENTA')

class Nodo1(unittest.TestCase):
    def test_dni_valido(self):
        payload = {'nodo': 1, 'mensaje': dni_valido}
        response = requestAPI(payload)
        self.assertEqual(response, 'URO ROCIO MARCELA Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

    def test_dni_invalido(self):
        payload = {'nodo': 1, 'mensaje': dni_invalido}
        response = requestAPI(payload)
        self.assertEqual(response, 'Al momento en CDN no tenemos asignada tu deuda, por favor contactate con BBVA al 0800-999-2282 DE LUNES A VIERNES DE 10 A 15 HS')

class Nodo2(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 2, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo3(unittest.TestCase):
    def test_mail_valido(self):
        payload = {'nodo': 3, 'dni': dni_valido, 'mensaje': 'prueba@gmail.com'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Muchas gracias')

    def test_mail_invalido(self):
        payload = {'nodo': 3, 'dni': dni_valido, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'ACOSTA ARRIETA FEDERICO AGUSTI Un gusto saludarte! Te pedimos que nos facilites un correo electrónico para continuar la gestión')

class Nodo4(unittest.TestCase):
    def test_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, te pedimos que nos indiques la fecha de pago EJ: 01/03/2024 y nos envíes el archivo adjunto del comprobante para poder registrarlo')

    def test_opciones_pago(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, hoy tenemos una oferta única para vos, con una quita extraordinaria, cancelás por $ 10 ¿Ves factible abonar esto al 01/01/2020?\n1) SI\n2)NO')

    def test_libre_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '3'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Para solicitar el libre deuda podés acercarte a la sucursal más cercana o comunicarse al 0800-999-2282 de lunes a viernes de 10 a 15 hs. Muchas gracias')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'LIBRE DEUDA')

    def test_defensa_consumidor(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '4'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Estimado/a te va a estar llamando a la brevedad el asesor designado a tu legajo en el horario de 9 a 17 hs. Saludos!')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'DEFENSA DEL CONSUMIDOR')

    def test_desconozco_deuda(self):
        payload = {'nodo': 4, 'dni': dni_valido, 'mensaje': '5'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Como desconoces tu deuda, en breve un asesor se comunicará y te dará más detalles. Recordá que nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059. Muchas gracias')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'DESCONOCE DEUDA')

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
        self.assertEqual(response, 'Muchas gracias por enviarnos el comprobante de pago en las proximas 48 hs impactara en su cuenta')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'Ya pagó')

    def test_otro_mes(self):
        fecha_hoy = datetime.today()
        fecha_mes_siguiente = fecha_hoy + timedelta(days=30)
        fecha_mes_siguiente = fecha_mes_siguiente.strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_mes_siguiente}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

    def test_dni_invalido(self):
        fecha_hoy = datetime.today().strftime("%d/%m/%Y")
        payload = {'nodo': 5, 'dni': dni_valido, 'mensaje': fecha_hoy}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo6(unittest.TestCase):
    def test_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 01/01/2020 ¿Confirma?\n1) SI\n2) NO')

    def test_no_acepta(self):
        payload = {'nodo': 6, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Desconocemos la sitación particular de cada uno, pero queremos ayudarte a no tener este problema. Tu cuenta está a punto de ser derivada a la etapa siguiente, la de un fideicomiso, lo que implica costes y honorarios por la operación. Podemos ofrecerte un plan de pagos con hasta 50 % off. Abonando hoy cancelás tu deuda por $ 10. Ves factible abonar este saldo?\n1) SI\n2) NO')

    def test_dni_invalido(self):
        payload = {'nodo': 6, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo7(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 7, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo8(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 8, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo9(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 9, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo10(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 10, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo11(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 11, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio. El importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTSYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663')
        self.assertEqual(df[df['dni'] == dni]['fecha_de_pago'].values[0] == '01/01/2024')

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
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 01/01/2020 ¿Confirma?\n1) SI\n2) NO')

    def test_no_abona(self):
        payload = {'nodo': 12, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entendemos que este no es un monto viable para vos para cancelar tu deuda. Desde CDN te podemos ofrecer las siguientes opciones de pago ¡Elegí la que más te convenga!\nA) Cancelas por 1 DE $ 10\nB) Cancelas por 2 DE $ 20\nC) Cancelas por 3 de $ 30')

    def test_dni_invalido(self):
        payload = {'nodo': 12, 'dni': dni_invalido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo13(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 13, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo14(unittest.TestCase):
    def test_fecha_pasada(self):
        fecha_hoy = datetime.today()
        fecha_pasada = fecha_hoy - timedelta(days=1000)
        fecha_pasada = fecha_pasada.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_pasada}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entiendo. Te voy a pedir un correo electrónico para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059 o por mail cdncobranzas@companiadelnorte.com')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'No puede pagar')

    def test_fecha_futura(self):
        fecha_hoy = datetime.today()
        fecha_futura = fecha_hoy + timedelta(days=1000)
        fecha_futura = fecha_futura.strftime("%d/%m/%Y")
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': fecha_futura}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio. El importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTSYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663')
        self.assertEqual(df[df['dni'] == dni]['fecha_de_pago'].values[0] == fecha_futura)

    def test_fecha_mal_formateada(self):
        payload = {'nodo': 14, 'dni': dni_valido, 'mensaje': '2100-02-02'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entiendo. Te voy a pedir un correo electrónico para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059 o por mail cdncobranzas@companiadelnorte.com')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'No puede pagar')

    def test_dni_invalido(self):
        payload = {'nodo': 14, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo15(unittest.TestCase):
    def elige_opcion_pago(self):
        payload = {'nodo': 15, 'dni': dni_valido, 'mensaje': 'A'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Perfecto, entonces el pago deberá realizarse antes de 01/01/2020')
        self.assertEqual(df[df['dni'] == dni]['cant_cuotas_elegido'].values[0] == 1)
        self.assertEqual(df[df['dni'] == dni]['monto_elegido'].values[0] == 1)

    def test_dni_invalido(self):
        payload = {'nodo': 15, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

class Nodo16(unittest.TestCase):
    def test_terminar(self):
        payload = {'nodo': 16, 'mensaje': 'blabla'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Conversacion terminada')

class Nodo17(unittest.TestCase):
    def test_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '1'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Gracias entonces registro tu compromiso de pago para esa fecha. Te solicitamos por favor un correo electrónico para poder realizarte el envío del convenio. El importe deberá ser abonado, mediante depósito bancario en cualquier sucursal del BBVA, cajero automático del BBVA o transferencia bancaria:\nTe brindamos el paso a paso de como debés realizarlo en un cajero automático:\n1º PAGOS\n2º RECAUDACIONES\n3º EFECTIVO EN PESOS\n4º CODIGO DE SERVICIO: 4482\n5º NUMERO DE DEPOSITANTE. Por favor verificá de ingresar el DNI/CUIL/CUIT de la persona/empresa que adeuda.\n6º TOTAL A PAGAR: (Valor primera cuota)\n7º PARA TRANSFERENCIA A ICHTSYS S.R.L. (Razón social)\nNUMERO: 331-422456/6 CUIT: 30715141627 CBU: 0170331120000042245663')
        self.assertEqual(df[df['dni'] == dni]['fecha_de_pago'].values[0] == '01/01/2020')

    def test_no_confirma(self):
        payload = {'nodo': 17, 'dni': dni_valido, 'mensaje': '2'}
        response = requestAPI(payload)
        self.assertEqual(response, 'Entiendo. Te voy a pedir un correo electrónico para que en un futuro podamos enviarte mejoras en tu oferta cancelatoria.\nTe brindamos además nuestro horario de atención es de lunes a viernes de 09 a 20 hs y te podés contactar con nosotros al 0800 220 0059 o por mail cdncobranzas@companiadelnorte.com')
        self.assertEqual(df[df['dni'] == dni]['ESTADO'].values[0] == 'No puede pagar')

    def test_dni_invalido(self):
        payload = {'nodo': 17, 'dni': dni_invalido, 'mensaje': '03/03/2100'}
        response = requestAPI(payload)
        self.assertEqual(response, 'payload invalido')

if __name__ == '__main__':
    unittest.main()
