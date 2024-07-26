## Ejecucion del server
Desde el root del repositorio:
```bash
$ uvicorn app:app --host 172.31.7.51 --port 3000 --reload
```

## endpoints
- POST /respuesta: Dado un id de nodo, un dni y un mensaje devuelve el texto correspondiente al siguiente nodo
- POST /telefono: Dado un dni y un numero de telefono con el formato que los manda wp (+54 9 XX XXXX-XXXX o +54 9 XXX XXX-XXX o +54 9 XXXX XX-XXXX) lo inserta en la db y devuelve un estado del proceso (OK)
- POST /subir_xlsx: Dado un archivo XLSX lo sube al server y arma la planilla de salida 

## Ejemplos de uso
* Responder mensaje
```bash
$ curl -X POST http://localhost:3000/respuesta -H 'Content-Type: application/json' -d '{"nodo": 0, "mensaje": "12345678", "dni": "12345678"}'
```
* Colocar numero de Telefono
```bash
$ curl -X POST http://localhost:3000/telefono -H 'Content-Type: application/json' -d '{"dni": "12345678", "numero_telefono": "+54 9 11 1234-5678"}'
```
* Subir xlsx
curl -X 'POST' http://localhost:3000/subir_xlsx -H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F 'file=@BASE PRUEBA CHAT BBVA 26072024.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
