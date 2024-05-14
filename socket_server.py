#!/usr/bin/env python

import asyncio
import signal
import websockets
import threading
import os
import time
import json

from Eventos import *

USERS = set()
global parent_PID

EVENTOS = set()
ALGORITHMS = ["FCFS", "RR", "SJF", "SRT", "HRNN", "MLFQ"]

def send_message(message):
    return json.dumps({"type": "message", "value": message})

def send_list(lista, message):
    return json.dumps({"type": "list_data", "data": lista, "message": message})

def stop():
    global parent_PID
    print(f"Terminando servidor en 2 segundos...")
    time.sleep(2)
    os.kill(parent_PID, signal.SIGTERM)

async def servidor(websocket):
    global EVENTOS
    try:
        USERS.add(websocket)
        greeting = f"Hola nuevo cliente, soy el servidor con PID: {parent_PID}"
        await websocket.send(send_message(greeting))
        async for message in websocket:
            #print(f"Message received: {message}")
            suceso = json.loads(message)
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
                #print(f"new_event.name: {new_event.nombre}")
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
                            #send_list(e.get_id_clientes())
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
                        e.clientes.remove(websocket)
                        e.id_clientes.remove(id_client)
                        await websocket.send(send_message(f"Se ha dado de baja del evento {event_name}"))
                        event_founded = True
                        break
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
    except RuntimeError as error:
      print('Something went wrong')
      print(error)
    finally:
        print("Removiendo cliente websocket")
        USERS.remove(websocket)
    

def sigusr1_handler(signum, frame):
    print(f"Terminando servidor")
    websockets.broadcast(USERS, "Finalizar")

async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    
    async with websockets.serve(servidor, "localhost", 8765, ping_interval=None):
        await stop

# signal.signal(signal.SIGINT, signal_handler)
if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    parent_PID = threading.get_native_id()
    print(f"Parent PID: {parent_PID}")
    asyncio.run(main())