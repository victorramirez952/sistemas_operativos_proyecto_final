import websocket
import time
import os
import threading
import json
from timedinput import timedinput

ID_CLIENT = "1934Ty9Bwp"
STATUS = True

PROCS = []

def send_message(message):
    return json.dumps({"type": "message", "value": message, "id_client": ID_CLIENT})

def create_event(event_name):
    return json.dumps({"type": "create_event", "value": event_name})

def delete_event(event_name):
    return json.dumps({"type": "delete_event", "value": event_name})

def trigger_event(event_name):
    return json.dumps({"type": "trigger_event", "value": event_name})

def list_event(event_name):
    return json.dumps({"type": "list_event", "value": event_name})

def list_algorithms():
    algorithms = ["FCFS", "RR", "SJF", "SRT", "HRNN", "MLFQ"]
    return json.dumps({"type": "list_algorithms", "value": algorithms})

def stop_server():
    return json.dumps({"type": "stop_server"})

def user_input(wsapp):
    print(f"Current process PID: {os.getpid()}")
    global STATUS
    #print(f"Ingresa un comando: ")
    while STATUS:
        try:
            # command = f"Mensaje del proceso cliente {os.getpid()}"
            #print(f"El STATUS es {STATUS}")
            command = timedinput("Ingresa un comando: \n", timeout=5, default="Null")
            if not STATUS:
                break
            elif command == "Null":
                continue
            elif command == "exit":
                wsapp.send(stop_server())
            elif command[:4] == "add ":
                if(command.count(' ') > 1):
                    print("El nombre del evento debe ser una sola palabra")
                else:
                    event_name = command[4:len(command)]
                    wsapp.send(create_event(event_name))
            elif command[:7] == "remove ":
                if(command.count(' ') > 1):
                    print("El nombre del evento debe ser una sola palabra")
                else:
                    event_name = command[7:len(command)]
                    wsapp.send(delete_event(event_name))
            elif command[:8] == "trigger ":
                if(command.count(' ') > 1):
                    print("El nombre del evento debe ser una sola palabra")
                else:
                    event_name = command[8:len(command)]
                    wsapp.send(trigger_event(event_name))
            elif command[:5] == "list ":
                #list algorithm
                if(command[5:14] == "algorithm"):
                    wsapp.send(list_algorithms())
                elif(command.count(' ') > 1):
                    print("El nombre del evento debe ser una sola palabra")
                else:
                    event_name = command[5:len(command)]
                    wsapp.send(list_event(event_name))
            else:
                continue
            #time.sleep(2)
        except RuntimeError as error:
            #print('An exception occurred in line 20')
            #print(error)
            STATUS = False

def on_message(wsapp, message):
    global STATUS
    suceso = json.loads(message)
    if suceso['type'] == "message":
        print(suceso["value"])
    elif suceso['type'] == "list_data":
        for c in suceso['data']:
            print(f"{c}")

def on_ping(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")

def on_pong(wsapp, message):
    print("Got a pong! No need to respond")

def on_close(wsapp, close_status_code, close_msg):
    global STATUS
    print("Finalizando programa")
    STATUS = False
    wsapp.close()

def on_open(wsapp):
    wsapp.send(send_message(f"Soy el administrador con ID {ID_CLIENT}"))
    x = threading.Thread(target=user_input, args=(wsapp,))
    x.start()
    

if __name__ == "__main__":
    wsapp = websocket.WebSocketApp("ws://localhost:8765", on_open=on_open, on_message=on_message, on_close=on_close, on_ping=on_ping, on_pong=on_pong)
    wsapp.run_forever()