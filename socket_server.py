#!/usr/bin/env python

import asyncio
import signal
import websockets
import threading
import os
import time
import json
import jsonpickle

# jsonpickle para convertir objetos complejos a json

from Eventos import *
from Algoritmos import *
from MLFQ import MLFQ

USERS = set() # Almacena los websockets clientes
global parent_PID

EVENTOS = set() # Almacena los eventos registrados en el servidor
ALGORITHMS = ["FCFS", "RR", "SJF", "SRT", "HRNN", "MLFQ"]

def send_message(message):
    return json.dumps({"type": "message", "value": message})

# Envia una lista de datos con un mensaje especifico
def send_list(lista, message):
    return json.dumps({"type": "list_data", "data": lista, "message": message})

def stop():
    global parent_PID
    print(f"Terminando servidor en 2 segundos...")
    time.sleep(2)
    os.kill(parent_PID, signal.SIGTERM) # Se envía una señal SIGTERM para llamar al manejador de señales y terminar el servidor


# Cliente websocket, datos del algoritmo, id del cliente
async def fcfs(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_FCFS = FCFS(algorithm['algorithm_name'])
    for p in algorithm['processes']:
        new_process = Proceso(p['id_process'], p['arrival_time'], p['burst_time'])
        new_FCFS.add_process(new_process)
    await new_FCFS.run_algorithm(websocket, id_client)

# Cliente websocket, datos del algoritmo, id del cliente
async def rr(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_RR = RR(algorithm['algorithm_name'], algorithm['quantum'])
    for p in algorithm['processes']:
        new_process = Proceso(p['id_process'], p['arrival_time'], p['burst_time'])
        new_RR.add_process(new_process)
    await new_RR.run_algorithm(websocket, id_client)

# Cliente websocket, datos del algoritmo, id del clientesd
async def sjf(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_SJF = SJF(algorithm['algorithm_name'])
    for p in algorithm['processes']:
        new_process = Proceso(p['id_process'], p['arrival_time'], p['burst_time'])
        new_SJF.add_process(new_process)
    await new_SJF.run_algorithm(websocket, id_client)

# Cliente websocket, datos del algoritmo, id del cliente
async def srt(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_SRT = SRT(algorithm['algorithm_name'])
    for p in algorithm['processes']:
        new_process = Proceso(p['id_process'], p['arrival_time'], p['burst_time'])
        new_SRT.add_process(new_process)
    await new_SRT.run_algorithm(websocket, id_client)

# Cliente websocket, datos del algoritmo, id del cliente
async def hrrn(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_HRRN = HRRN(algorithm['algorithm_name'])
    for p in algorithm['processes']:
        new_process = Proceso(p['id_process'], p['arrival_time'], p['burst_time'])
        new_HRRN.add_process(new_process)
    await new_HRRN.run_algorithm(websocket, id_client)

# Cliente websocket, datos del algoritmo, id del cliente
async def mlfq(websocket, algorithm, id_client):
    print(f"Ejecutando el algorithmo {algorithm['algorithm_name']} para el client {id_client}")
    new_MLFQ = MLFQ(algorithm['algorithm_name'], algorithm['queues'], algorithm['quantums'])
    for p in algorithm['processes']:
        new_process = Proceso_MLFQ(p['id_process'], p['arrival_time'], p['burst_time'])
        new_MLFQ.add_process(new_process)
    await new_MLFQ.run_algorithm(websocket, id_client)

# Proceso principal del servidor, que atiende a cada nuevo cliente (websocket)
async def servidor(websocket):
    global EVENTOS # Para manejar la variable global EVENTOS
    try:
        USERS.add(websocket)
        greeting = f"Hola nuevo cliente, soy el servidor con PID: {parent_PID}"
        await websocket.send(send_message(greeting))
        async for message in websocket: # Función asíncrona que espera por nuevas peticiones de los clientes
            suceso = json.loads(message) # Transforma el message a un formato JSON
            if(suceso['type'] == "message"):
                id_client = suceso['id_client']
                message = suceso['value']
                print(f"{id_client}: {message}")
            elif(suceso['type'] == "stop_server"):
                print(f"USERS: {USERS}")
                websockets.broadcast(USERS, send_message("El servidor va a finalizar"))
                stop()
            elif(suceso['type'] == "create_event"):
                new_name_evento = suceso['value']
                new_event = Evento(new_name_evento)
                EVENTOS.add(new_event)
                websockets.broadcast(USERS, send_message(f"Se ha creado el evento {new_event.nombre}"))
            elif(suceso['type'] == "delete_event"):
                event_name = suceso['value']
                event_founded = False
                for e in EVENTOS:
                    if(e.nombre == event_name):
                        EVENTOS.remove(e)
                        await websocket.send(send_message(f"Evento {event_name} eliminado"))
                        event_founded = True
                        break
                if not event_founded:
                    await websocket.send(send_message(f"El evento {event_name} no existe"))
            elif(suceso['type'] == "trigger_event"):
                event_name = suceso['value']
                event_founded = False
                for e in EVENTOS:
                    if(e.nombre == event_name):
                        websockets.broadcast(USERS, send_message(f"Se ha publicado el evento {event_name}"))
                        event_founded = True
                        break
                if not event_founded:
                    await websocket.send(send_message(f"El evento {event_name} no existe"))
            elif(suceso['type'] == "list_event"):
                event_name = suceso['value']
                event_founded = False
                for e in EVENTOS:
                    if(e.nombre == event_name):
                        event_founded = True
                        if len(e.id_clientes) != 0:
                            await websocket.send(send_list(e.get_id_clientes(), "Clientes suscritos:"))
                        break
                if not event_founded:
                    await websocket.send(send_message(f"El evento {event_name} no existe"))
            elif(suceso['type'] == "list_algorithms"):
                algorithms = suceso['value']
                print(algorithms)
                string = "Los algoritmos disponibles son: "
                for i in algorithms:
                    string += i + ", "
                websockets.broadcast(USERS, send_message(string))
            elif(suceso['type'] == "ask_events"): ## Comandos del cliente
                id_client = suceso['id_client']
                print(f"{id_client}: Ha solicitado la lista de los eventos disponibles")
                available_events = []
                if(len(EVENTOS) == 0):
                    await websocket.send(send_message("No hay eventos disponibles"))
                else:
                    for e in EVENTOS:
                        available_events.append(e.nombre)
                    await websocket.send(send_list(available_events, "Eventos disponibles:"))
            elif(suceso['type'] == "suscribe_event"):
                event_name = suceso['value']
                id_client = suceso['id_client']
                event_founded = False
                print(f"{id_client}: Ha solicitado suscribirse al evento {event_name}")
                for e in EVENTOS:
                    if(e.nombre == event_name):
                        e.clientes.add(websocket)
                        e.id_clientes.append(id_client)
                        await websocket.send(send_message(f"Se ha suscrito al evento {event_name}"))
                        event_founded = True
                        break
                if not event_founded:
                    await websocket.send(send_message(f"El evento {event_name} no existe"))
            elif(suceso['type'] == "unsuscribe_event"):
                event_name = suceso['value']
                id_client = suceso['id_client']
                event_founded = False
                print(f"{id_client}: Ha solicitado darse de baja del evento {event_name}")
                for e in EVENTOS:
                    if(e.nombre == event_name):
                        event_founded = True
                        if(e.eliminar_cliente(id_client)):
                            e.clientes.remove(websocket)
                            await websocket.send(send_message(f"Se ha dado de baja del evento {event_name}"))
                            break
                        else:
                            await websocket.send(send_message(f"Usted no esta suscrito al evento {event_name}"))        
                if not event_founded:
                    await websocket.send(send_message(f"El evento {event_name} no existe"))
            elif(suceso['type'] == "list_suscribed_events"):
                id_client = suceso['id_client']
                print(f"{id_client}: Ha solicitado la lista de eventos en los que esta suscrito")
                events = []
                for e in EVENTOS:
                    if(id_client in e.id_clientes):
                        events.append(e.nombre)
                if len(events) == 0:
                    await websocket.send(send_message(f"No se ha registrado a ningun evento"))
                else:
                    await websocket.send(send_list(events, "Eventos a los que se ha suscrito:"))
            elif(suceso['type'] == "list_algorithms_client"):
                id_client = suceso['id_client']
                print(f"{id_client}: Ha solicitado la lista de algoritmos disponibles")
                await websocket.send(send_list(ALGORITHMS, "Los algoritmos disponibles son:"))
            elif(suceso['type'] == "send_data_algorithm"): ## Cuando un cliente envía datos para procesarlos por un algoritmo
                id_client = suceso['id_client']
                algorithm = suceso['data']
                print(f"{id_client}: Ha enviado datos para efectuar el algoritmo {algorithm['algorithm_name']}")
                if(algorithm['algorithm_name'] == "FCFS"):
                    new_thread = threading.Thread(target=asyncio.run, args=(fcfs(websocket,algorithm, id_client),))
                    new_thread.start()
                elif(algorithm['algorithm_name'] == "RR"):
                    new_thread = threading.Thread(target=asyncio.run, args=(rr(websocket,algorithm, id_client),))
                    new_thread.start()
                elif(algorithm['algorithm_name'] == "SJF"):
                    new_thread = threading.Thread(target=asyncio.run, args=(sjf(websocket,algorithm, id_client),))
                    new_thread.start()
                elif(algorithm['algorithm_name'] == "SRT"):
                    new_thread = threading.Thread(target=asyncio.run, args=(srt(websocket,algorithm, id_client),))
                    new_thread.start()
                elif(algorithm['algorithm_name'] == "HRRN"):
                    new_thread = threading.Thread(target=asyncio.run, args=(hrrn(websocket,algorithm, id_client),))
                    new_thread.start()
                elif(algorithm['algorithm_name'] == "MLFQ"):
                    new_thread = threading.Thread(target=asyncio.run, args=(mlfq(websocket,algorithm, id_client),))
                    new_thread.start()
    except RuntimeError as error: # Si surge alguna excepción
      print('Something went wrong')
      print(error)
    finally:
        print("Removiendo cliente websocket") # Cuando un cliente se desconecta
        USERS.remove(websocket)
    
async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None) # Para el servidor con la señal SIGTERM
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None) # Para el servidor con la señal SIGINT
    
    async with websockets.serve(servidor, "localhost", 8765, ping_interval=None):
        await stop

if __name__ == "__main__":
    parent_PID = threading.get_native_id()
    print(f"Parent PID: {parent_PID}")
    asyncio.run(main())