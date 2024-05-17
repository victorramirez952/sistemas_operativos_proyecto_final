import time
import jsonpickle
import json
import asyncio
import threading
import sys
from collections import deque

def mlfq_check_arrival_highest_process(time_service, processes, queue_index, flag_equal=True):
    arrived_highest_processes = deque()
    if(flag_equal):
        for i in range(len(processes)):
            it_process = processes[i]
            if(it_process.completed):
                continue
            if(it_process.arrival_time == time_service and it_process.queue_index < queue_index):
                arrived_highest_processes.append(it_process)
    else:
        for i in range(len(processes)):
            it_process = processes[i]
            if(it_process.completed):
                continue
            if(it_process.arrival_time <= time_service and it_process.queue_index < queue_index):
                arrived_highest_processes.append(it_process)
    return arrived_highest_processes

def mlfq_rr_check_arrival(time_service, processes, _deque, is_mlfq=False, removed_processes=None, queue_index=-1):
    if(not is_mlfq):
        for p in processes:
            if(p.arrival_time <= time_service and p not in _deque and not p.completed):
                _deque.append(p)
    else:
        for i in range(len(processes)):
            it_process = processes[i]
            if(it_process.arrival_time > time_service):
                break
            if(it_process not in _deque and it_process not in removed_processes and it_process.queue_index == queue_index):
                if(not it_process.completed):
                    _deque.append(it_process)

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

class Proceso_MLFQ(Proceso):
    def __init__(self, id, arrival_time, burst_time):
        Proceso.__init__(self, id, arrival_time, burst_time)
        self.queue_index = 0
        self.mlfq_ed = False

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
    
    async def send_json(self, websocket):
        json_list = jsonpickle.encode(self.processes)
        json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
        await websocket.send(json_string)
    

    def turnaround_time_waiting_time(self):
        for i in self.processes:
            i.turnaround_time = i.completion_time - i.arrival_time
            i.waiting_time = i.turnaround_time - i.burst_time
    
class FCFS(Algoritmo):
    def __init__(self, name):
        Algoritmo.__init__(self, name)
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    
    async def run_algorithm(self, websocket, id_client):
        self.time_service = 0
        for i in self.processes:
            while(self.time_service < i.arrival_time):
                self.time_service += 1
            i.set_status("En ejecucion")
            await self.send_json(websocket)
            await asyncio.sleep(i.burst_time)

            self.time_service += i.burst_time
            i.completion_time += self.time_service
            i.remaining_time = 0
            i.set_status("Finalizado")
            i.completed = True
            await self.send_json(websocket)
        self.turnaround_time_waiting_time()
        await self.send_json(websocket)
        print(f"Algoritmo First Come First Serve completado para el cliente {id_client}")

    async def run_algorithm_mlfq(self, websocket, queue_index, _deque, max_index):
        if(len(_deque) == 0):
            for p in self.processes:
                _deque.append(p)
                
        # _deque: Procesos que llegan y tienen la misma prioridad que la cola actual

        removed_processes = deque() # Procesos que van saliendo (para validacion)
        arrived_highest_processes = deque() # Procesos de más alta prioridad que van llegando
        process_with_highest_priority = False
        while True:
            if(process_with_highest_priority):
                break
            if(len(_deque) == 0):
                break
            current_process = _deque[0]
            current_index = 0
            # Se busca el índice del proceso localizado en la fila
            for p in self.processes:
                if(p.id == current_process.id):
                    break
                else:
                    current_index += 1
            
            it_process = self.processes[current_index]
            if(it_process.queue_index != queue_index):
                continue
            
            it_process.set_status("En ejecucion")
            await self.send_json(websocket)
            
            await asyncio.sleep(it_process.remaining_time)
            self.time_service += it_process.remaining_time
            it_process.remaining_time = 0
            it_process.completion_time += self.time_service
            it_process.completed = True

            it_process.set_status("Finalizado")
            await self.send_json(websocket)
            
            _deque.popleft()
            temp_deque = mlfq_check_arrival_highest_process(self.time_service, self.processes, queue_index, False)
            if(len(temp_deque) != 0):
                process_with_highest_priority = True
                arrived_highest_processes = temp_deque
            # print(f"FCFS - Completion time of {it_process.id} is {self.time_service}")
            # json_list = jsonpickle.encode(self.processes)
            # json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
            #await websocket.send(json_string)
        # json_list = jsonpickle.encode(self.processes)
        # json_string = json.dumps({"type": "algorithm_result", "data": json.loads(json_list), "message": "Resultados del algoritmo: "})
        #await websocket.send(json_string)
        remaining_processes = _deque
        return [self.time_service, process_with_highest_priority, arrived_highest_processes, _deque, removed_processes]

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
    
    async def run_algorithm(self, websocket, id_client):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        current_index = self.__index_sjf()

        while True:
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            if(current_index == -1):
                self.time_service += 1
                current_index = self.__index_sjf()
                continue
            
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].remaining_time -= 1
                self.processes[current_index].set_status("En ejecucion")
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.time_service += 1

            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                # print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
            
            current_index = self.__index_sjf()
        self.turnaround_time_waiting_time()
        await self.send_json(websocket)
        print(f"Algoritmo Shortest Job First completado para el cliente {id_client}")

    async def run_algorithm_mlfq(self, websocket, queue_index, _deque, max_index):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        # _deque: Procesos que llegan y tienen la misma prioridad que la cola actual

        removed_processes = deque() # Procesos que van saliendo (para validacion)
        arrived_highest_processes = deque() # Procesos de más alta prioridad que van llegando
        process_with_highest_priority = False

        current_index = self.__index_sjf(queue_index)

        while True:
            if(current_index == -1):
                break
                    
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
            
            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                # print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
    
            temp_deque = mlfq_check_arrival_highest_process(self.time_service, self.processes, queue_index, False)
            if(len(temp_deque) != 0):
                process_with_highest_priority = True
                arrived_highest_processes = temp_deque

                self.processes[current_index].set_status("En espera")
                await self.send_json(websocket)
                # print_elements(arrived_highest_processes, "*")
            if(process_with_highest_priority):
                break
            current_index = self.__index_sjf(queue_index)
        remaining_processes = deque()
        return [self.time_service, process_with_highest_priority, arrived_highest_processes, _deque, removed_processes]


class RR(Algoritmo):
    def __init__(self, name, _quantum, is_mlfq=False):
        Algoritmo.__init__(self, name)
        self.quantum = _quantum
        self._deque = deque()
        self.is_mlfq = is_mlfq
    
    def set_processes(self, processes):
        self.processes = processes
    def set_time_service(self, time_service):
        self.time_service = time_service
    
    def __checkArrival(self, _deque):
        for p in self.processes:
            if(p.arrival_time <= self.time_service and p not in _deque and not p.completed):
                _deque.append(p)

    async def run_algorithm(self, websocket, id_client):
        self.time_service = 0
        _deque = deque()
        
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        if(len(_deque) == 0):
            _deque.append(self.processes[0])
        
        while True:
            # Revisamos si hay un proceso con un burst time faltante
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
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
                counter += 1
                self.__checkArrival(_deque)
            
            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                # print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                _deque.popleft()
                await self.send_json(websocket)
            else:
                self.processes[current_index].set_status("En espera")
                temp_process = _deque.popleft()
                _deque.append(temp_process)
                await self.send_json(websocket)
        self.turnaround_time_waiting_time()
        await self.send_json(websocket)
        print(f"Algoritmo Round Robin completado para el cliente {id_client}")
    
    async def run_algorithm_mlfq(self, websocket, queue_index, _deque, max_index):
        if(not self.is_mlfq):
            return
        
        # _deque: Procesos que llegan y tienen la misma prioridad que la cola actual
        
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        if(len(_deque) == 0 and queue_index == 0):
            _deque.append(self.processes[0])

        removed_processes = deque() # Procesos que van saliendo (para validacion)
        arrived_highest_processes = deque() # Procesos de más alta prioridad que van llegando
        process_with_highest_priority = False
        while True:
            if(process_with_highest_priority):
                break
            if(len(_deque) == 0):
                break
                        
            current_process = _deque[0]
            current_index = 0
            # Se busca el índice del proceso localizado en la fila
            for p in self.processes:
                if(p.id == current_process.id):
                    break
                else:
                    current_index += 1
            counter = 0

            while((self.processes[current_index].remaining_time > 0) and (counter < self.quantum)):
                self.processes[current_index].set_status("En ejecucion")
                await self.send_json(websocket)
                await asyncio.sleep(1)

                self.mlfq_ed = True
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
                counter += 1
                mlfq_rr_check_arrival(self.time_service, self.processes, _deque, True, removed_processes, queue_index)
                temp_deque = mlfq_check_arrival_highest_process(self.time_service, self.processes, queue_index, True)
                if(len(temp_deque) != 0):
                    process_with_highest_priority = True
                    arrived_highest_processes = temp_deque
                    # print_elements(arrived_highest_processes, "*")
            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                # print(f"RR - Completion time for{self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
                _deque.popleft()
            else:
                temp_process = _deque.popleft()
                if(temp_process.queue_index == max_index):
                    _deque.append(temp_process)
                else:
                    # print(f"Elevando prioridad a proceso con id {temp_process.id} y remaining time de {temp_process.remaining_time} in t={self.time_service}")
                    self.processes[current_index].queue_index += 1
                    removed_processes.append(temp_process)
                self.processes[current_index].set_status("En espera")
                await self.send_json(websocket)
        remaining_processes = _deque
        return [self.time_service, process_with_highest_priority, arrived_highest_processes, _deque, removed_processes]


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
        for i in range(len(self.processes)):
            it_process = self.processes[i]
            if(queue_index != -1 and it_process.queue_index != queue_index):
                continue
            if(not it_process.completed and it_process.arrival_time <= self.time_service and it_process.burst_time < min_burst_time):
                min_index = i
                min_burst_time = it_process.burst_time
        return min_index
    
    async def run_algorithm(self, websocket, id_client):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1

        current_index = 0
        future_new_index = -1
        while True:
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            if(current_index == -1):
                self.time_service += 1
                current_index = self.__getMinBurstTime()
                continue
            
            for i in range(len(self.processes)):
                it_process = self.processes[i]
                if(i != current_index and not it_process.completed):
                    it_process.set_status("En espera")
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                self.processes[current_index].remaining_time -= 1
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.time_service += 1
                new_index = self.__checkMinBurstTime(current_index)
                if(new_index != -1):
                    if(self.processes[current_index].remaining_time == 0):
                        self.processes[current_index].completed = True
                        self.processes[current_index].completion_time = self.time_service
                        self.processes[current_index].set_status("Finalizado")
                        await self.send_json(websocket)
                    current_index = new_index
                    break

            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                # print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
                current_index = self.__getMinBurstTime()
            
        self.turnaround_time_waiting_time()
        await self.send_json(websocket)
        # Algoritmo Shortest Remaining Time completado para el cliente {id_client}")

    async def run_algorithm_mlfq(self, websocket, queue_index, _deque, max_index):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        # _deque: Procesos que llegan y tienen la misma prioridad que la cola actual
            
        removed_processes = deque() # Procesos que van saliendo (para validacion)
        arrived_highest_processes = deque() # Procesos de más alta prioridad que van llegando
        process_with_highest_priority = False

        while True:
            if(process_with_highest_priority):
                break
                                    
            flag = True
            for p in self.processes:
                if(p.queue_index != queue_index):
                    continue
                if(p not in removed_processes and p.remaining_time != 0):
                    flag = False
                    break
            if flag: # Si todos los procesos de la cola han agotado su burst time
                break
            
            current_index = self.__getMinBurstTime(queue_index)
            if(current_index == -1):
                break
            
            for i in range(len(self.processes)):
                it_process = self.processes[i]
                if(i != current_index and not it_process.completed):
                    it_process.set_status("En espera")
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                self.processes[current_index].remaining_time -= 1
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.time_service += 1
                temp_deque = mlfq_check_arrival_highest_process(self.time_service, self.processes, queue_index, True)
                if(len(temp_deque) != 0):
                    process_with_highest_priority = True
                    arrived_highest_processes = temp_deque
                    self.processes[current_index].set_status("En espera")
                    await self.send_json(websocket)
                    # print_elements(arrived_highest_processes, "*")
                if(process_with_highest_priority):
                    break
                new_index = self.__checkMinBurstTime(current_index, queue_index)
                if(new_index != -1):
                    temp_process = self.processes[current_index]
                    if(temp_process.queue_index != max_index):
                        # print(f"Elevando prioridad a proceso con id {temp_process.id} y remaining time de {temp_process.remaining_time} in t={self.time_service}")
                        self.processes[current_index].queue_index += 1
                        removed_processes.append(temp_process)
                    self.processes[current_index].set_status("En espera")
                    if(self.processes[current_index].remaining_time == 0):
                        self.processes[current_index].completed = True
                        self.processes[current_index].completion_time = self.time_service
                        self.processes[current_index].set_status("Finalizado")
                    await self.send_json(websocket)              
                    current_index = new_index
                    break
            if(self.processes[current_index].remaining_time == 0):
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
                # print(f"Completion time for {self.processes[current_index].id} is {self.time_service}")
            current_index = self.__getMinBurstTime()
        remaining_processes = deque()
        _deque = deque()
        return [self.time_service, process_with_highest_priority, arrived_highest_processes, _deque, removed_processes]
   
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
    
    async def run_algorithm(self, websocket, id_client):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        current_index = 0

        while True:
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            if(current_index == -1):
                self.time_service += 1
                current_index = self.__get_index_hrrn()
                continue
            
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
            
            if(self.processes[current_index].remaining_time == 0):
                # print(f"Completion time of {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
            current_index = self.__get_index_hrrn()
        self.turnaround_time_waiting_time()
        await self.send_json(websocket)
        print(f"Algoritmo Highest Response Ratio Next completado para el cliente {id_client}")

    async def run_algorithm_mlfq(self, websocket, queue_index, _deque, max_index):
        while(self.time_service < self.processes[0].arrival_time):
            self.time_service += 1
        
        # _deque: Procesos que llegan y tienen la misma prioridad que la cola actual

        removed_processes = deque() # Procesos que van saliendo (para validacion)
        arrived_highest_processes = deque() # Procesos de más alta prioridad que van llegando
        process_with_highest_priority = False

        current_index = self.__get_index_hrrn(queue_index)
        while True:
            if(current_index == -1):
                break
            
            # Revisamos si hay un proceso con un burst time faltante
            if all(p.remaining_time == 0 for p in self.processes):
                break
            
            while(self.processes[current_index].remaining_time > 0):
                self.processes[current_index].set_status("En ejecucion")
                await self.send_json(websocket)
                await asyncio.sleep(1)
                self.processes[current_index].remaining_time -= 1
                self.time_service += 1
            
            if(self.processes[current_index].remaining_time == 0):
                # print(f"Completion time of {self.processes[current_index].id} is {self.time_service}")
                self.processes[current_index].completed = True
                self.processes[current_index].completion_time = self.time_service
                self.processes[current_index].set_status("Finalizado")
                await self.send_json(websocket)
            
            temp_deque = mlfq_check_arrival_highest_process(self.time_service, self.processes, queue_index, False)
            if(len(temp_deque) != 0):
                process_with_highest_priority = True
                arrived_highest_processes = temp_deque
                self.processes[current_index].set_status("En espera")
                await self.send_json(websocket)
                # print_elements(arrived_highest_processes, "-")
            
            if(process_with_highest_priority):
                break
            
            current_index = self.__get_index_hrrn(queue_index)
        remaining_processes = deque()
        _deque = deque()
        return [self.time_service, process_with_highest_priority, arrived_highest_processes, _deque, removed_processes]

