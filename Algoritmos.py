import time
import jsonpickle
import json
import asyncio
import threading
import sys
from collections import deque

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
        self.time_service = 0
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
    
    def send_json(self):
        json_list = jsonpickle.encode(self.processes)
        json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
        return json_string
    
    def turnaround_time_waiting_time(self):
        for i in self.processes:
            i.turnaround_time = i.completion_time - i.arrival_time
            i.waiting_time = i.turnaround_time - i.burst_time
    
class FCFS(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    async def run_algorithm(self, websocket):
        time_service = 0
        for i in self.processes:
            i.set_status("En ejecucion")
            _burst_time = i.burst_time
            print(f"Ejecutando proceso {i.id} durante {_burst_time} segundos: ")
            time.sleep(_burst_time)
            time_service += _burst_time
            i.completion_time += time_service
            i.set_status("Finalizado")
            json_string = self.send_json()
            await websocket.send(json_string)
            #print(await send_algorithm_result("Testing"))
            # new_thread = threading.Thread(target=asyncio.run, args=(send_algorithm_result(websocket, json_string),))
            # new_thread.start()
        self.turnaround_time_waiting_time()
        json_string = json_string = self.send_json()
        await websocket.send(json_string)
        print("Proceso FCFS completado")

class SJF(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    
    def __index_sjf(self, queue_index = -1):
        index_sjf = -1
        min_burst_time = sys.maxsize
        for i in range(len(self.processes)):
            it_process = self.processes[i]
            if(queue_index != -1 and it_process.queue_index != queue_index):
                continue
            if(not it_process.completed and it_process.arrival_time <= self.time_service and it_process.burst_time < min_burst_time):
                index_sjf = i
                min_burst_time = it_process.burst_time
        return index_sjf
    
    async def run_algorithm(self, websocket):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        current_index = self.__index_sjf()

        while True:
            if(current_index == -1):
                break
            
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].remaining_time -= 1
                self.processes[current_index].set_status("Finalizado")
                json_string = self.send_json()
                await websocket.send(json_string)
                await asyncio.sleep(1)
                self.time_service += 1

            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                json_string = self.send_json()
                await websocket.send(json_string)
            
            current_index = self.__index_sjf()
        self.turnaround_time_waiting_time()
        json_string = json_string = self.send_json()
        await websocket.send(json_string)

class RR(Algoritmo):
    def __init__(self, name, _quantum):
        Algoritmo.__init__(self, name)
        self.quantum = _quantum
        self._deque = deque()
    
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    def set_deque(self, deque):
        self._deque = deque
    
    def __checkArrival(self, _deque):
        for p in self.processes:
            if(p.arrival_time <= self.time_service and p not in _deque and not p.completed):
                _deque.append(p)

    async def run_algorithm(self, websocket):
        self.time_service = 0
        _deque = deque()
        
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        if(len(_deque) == 0):
            _deque.append(self.processes[0])
        
        while True:
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            current_process = _deque[0]
            current_index = 0
            for p in self.processes:
                if(p.id == current_process.id):
                    break
                else:
                    current_index += 1
            counter = 0
            while((self.processes[current_index].remaining_time > 0) and (counter < self.quantum)):
                self.processes[current_index].set_status("En ejecucion")
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
                counter += 1
                self.__checkArrival(_deque)
            
            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                _deque.popleft()
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
            else:
                temp_process = _deque.popleft()
                _deque.append(temp_process)
        self.turnaround_time_waiting_time()
        json_string = json_string = self.send_json()
        await websocket.send(json_string)

class SRT(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    
    def __checkMinBurstTime(self, current_index, queue_index=-1):
        for i in range(len(self.processes)):
            it_process = self.processes[i]
            if(queue_index != -1 and it_process.queue_index != queue_index):
                continue
            if(it_process.id == self.processes[current_index].id):
                continue
            elif (it_process.arrival_time <= self.time_service and it_process.burst_time <= self.processes[current_index].remaining_time and not it_process.completed):
                return i
        return -1
    
    def __getMinBurstTime(self, queue_index = -1):
        min_index = -1
        min_burst_time = sys.maxsize
        previous_index = -1
        for i in range(len(self.processes)):
            it_process = self.processes[i]
            if(queue_index != -1 and it_process.queue_index != queue_index):
                continue
            if(not it_process.completed and it_process.arrival_time <= self.time_service and it_process.burst_time < min_burst_time):
                min_index = i
                min_burst_time = it_process.burst_time
        return min_index
    
    async def run_algorithm(self, websocket):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1

        current_index = 0
        while True:
            if(current_index == -1):
                break
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                self.processes[current_index].remaining_time -= 1
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
                await asyncio.sleep(1)
                self.time_service += 1
                new_index = self.__checkMinBurstTime(current_index)
                if(new_index != -1):
                    current_index = new_index
                    break

            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
                current_index = self.__getMinBurstTime()
        self.turnaround_time_waiting_time()
        json_string = json_string = self.send_json()
        await websocket.send(json_string)
            
class HRRN(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    
    def __calculate_hrrn(self, process):
        waiting_time = self.time_service - process.arrival_time
        return ((waiting_time + process.burst_time) / process.burst_time)
    
    def __get_index_hrrn(self, queue_index = -1):
        max_hrrn = -sys.maxsize - 1
        max_hrrn_index = -1
        for i in range(len(self.processes)):
            it_process = self.processes[i]
            if(queue_index != -1 and it_process.queue_index != queue_index):
                continue
            if(not it_process.completed and it_process.arrival_time <= self.time_service):
                temp_hrrn = self.__calculate_hrrn(it_process)
                if(temp_hrrn > max_hrrn):
                    max_hrrn_index = i
                    max_hrrn = temp_hrrn
        return max_hrrn_index
    
    async def run_algorithm(self, websocket):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        current_index = 0

        while True:
            if(current_index == -1):
                break
            
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
            
            if(self.processes[current_index].remaining_time == 0):
                print(f"Completion time of {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                json_string = json_string = self.send_json()
                await websocket.send(json_string)
            current_index = self.__get_index_hrrn()
        self.turnaround_time_waiting_time()
        json_string = json_string = self.send_json()
        await websocket.send(json_string)

