import time
import jsonpickle
import json
import asyncio
import threading

async def send_algorithm_result(message):
    await asyncio.sleep(2)
    return json.dumps({"type": "message", "value": message})

class Proceso:
    def __init__(self, id, arrival_time, burst_time):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.status = "En espera"
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.completed = False
        self.remaining_time = self.burst_time
    def set_status(self, new_status):
        self.status = new_status


class Algoritmo:
    def __init__(self, name):
        self.name = name
        self.processes = []
    def add_process(self, process):
        self.processes.append(process)
    def delete_process(process):
        self.processes.remove(process)
    def get_processes():
        return self.processes
    def show_processes(self):
        print("Processes: ")
        for p in self.processes:
            print(f"{p.id}, ")

class FCFS(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    async def run_algorithm(self, websocket):
        print(f"Longitud del arreglo: {len(self.processes)}")
        time_service = 0
        for i in self.processes:
            i.set_status("En ejecucion")
            _burst_time = i.burst_time
            print(f"Ejecutando proceso {i.id} durante {_burst_time} segundos: ")
            time.sleep(_burst_time)
            time_service += _burst_time
            i.completion_time += time_service
            i.set_status("Finalizado")
            json_list = jsonpickle.encode(self.processes)
            json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
            await websocket.send(json_string)
            #print(await send_algorithm_result("Testing"))
            # new_thread = threading.Thread(target=asyncio.run, args=(send_algorithm_result(websocket, json_string),))
            # new_thread.start()
        for i in self.processes:
            i.turnaround_time = i.completion_time - i.arrival_time
            i.waiting_time = i.turnaround_time - i.burst_time
        json_list = jsonpickle.encode(self.processes)
        json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
        await websocket.send(json_string)
        print("Proceso FCFS completado")

class RR(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    async def run_algorithm(self, websocket):
        print(f"Longitud del arreglo: {len(self.processes)}")
        time_service = 0
        for i in self.processes:
            i.set_status("En ejecucion")
            _burst_time = i.burst_time
            print(f"Ejecutando proceso {i.id} durante {_burst_time} segundos: ")
            time.sleep(_burst_time)
            time_service += _burst_time
            i.completion_time += time_service
            i.set_status("Finalizado")
            json_list = jsonpickle.encode(self.processes)
            json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
            await websocket.send(json_string)
            #print(await send_algorithm_result("Testing"))
            # new_thread = threading.Thread(target=asyncio.run, args=(send_algorithm_result(websocket, json_string),))
            # new_thread.start()
        for i in self.processes:
            i.turnaround_time = i.completion_time - i.arrival_time
            i.waiting_time = i.turnaround_time - i.burst_time
        json_list = jsonpickle.encode(self.processes)
        json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
        await websocket.send(json_string)
        print("Proceso FCFS completado")