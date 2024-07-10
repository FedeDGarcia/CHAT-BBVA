## Ejecucion del server
Desde el root del repositorio:
```bash
$ uvicorn app:app --host 172.31.7.51 --port 3000 --reload
```

## endpoints
- POST /respuesta: Dado un id de nodo y un mensaje devuelve el texto correspondiente al siguiente nodo

## Ejemplos de uso
* Responder mensaje
```bash
$ curl -X POST http://localhost:3000/respuesta/ -H 'Content-Type: application/json' -d '{"nodo": 0, "mensaje": "12345678"}'
```
