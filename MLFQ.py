import time
import jsonpickle
import json
import asyncio
import threading
import sys
from collections import deque
from Algoritmos import *

class MLFQ(Algoritmo):
    def __init__(self, name, _deque, _quantums):
        Algoritmo.__init__(self, name)
        self.queues = _deque
        self.quantums = _quantums
        self._deque = deque()
    def run_algorithm(self):
        process_with_highest_priority = False
        max_index = len(self.queues) - 1
        MLFQ_deques = [deque()]*len(self.queues)
        while True:
            process_with_highest_priority = False
            # Revisamos si hay un proceso que falta por completarse
            if all(p.completed for p in self.processes):
                break

            for index in range(len(self.queues)):
                if(process_with_highest_priority):
                    break
                
                # Revisamos si hay un proceso que falta por completarse
                if all(p.completed for p in self.processes):
                    break
                
                if(self.queues[index] == "RR"):
                    new_RR_MLFQ = RR(self.queues[index], self.quantums[index],True)
                    new_RR_MLFQ.set_processes(self.processes)
                    new_RR_MLFQ.set_time_service(self.time_service)

                    results = new_RR_MLFQ.run_algorithm_mlfq(index, MLFQ_deques[index], max_index)
                    r_time_service = results[0]
                    process_with_highest_priority = results[1]
                    arrived_highest_processes = results[2]
                    current_processes = results[3]
                    removed_processes = results[4]
                    
                    self.time_service = r_time_service
                    # print(f"Time service MLFQ_RR: {self.time_service}")
                    MLFQ_deques[index] = current_processes

                    if(len(arrived_highest_processes) != 0):
                        MLFQ_deques[index - 1] = arrived_highest_processes

                    if(len(removed_processes) != 0):
                        if(index != len(self.queues) - 1):
                            MLFQ_deques[index + 1].extend(removed_processes)
                elif(self.queues[index] == "FCFS"):
                    new_FCFS_MLFQ = FCFS(self.queues[index])
                    new_FCFS_MLFQ.set_processes(self.processes)
                    new_FCFS_MLFQ.set_time_service(self.time_service)

                    results = new_FCFS_MLFQ.run_algorithm_mlfq(index, MLFQ_deques[index], max_index)
                    r_time_service = results[0]
                    process_with_highest_priority = results[1]
                    arrived_highest_processes = results[2]
                    current_processes = results[3]
                    removed_processes = results[4]

                    self.time_service = r_time_service
                    # print(f"Time service MLFQ-FCFS: {self.time_service}")
                    MLFQ_deques[index] = current_processes

                    if(len(arrived_highest_processes) != 0):
                        MLFQ_deques[index - 1] = arrived_highest_processes

                    if(len(removed_processes) != 0):
                        if(index != len(self.queues) - 1):
                            MLFQ_deques[index + 1].extend(removed_processes)
                elif(self.queues[index] == "SRT"):
                    new_SRT_MLFQ = SRT(self.queues[index])
                    new_SRT_MLFQ.set_processes(self.processes)
                    new_SRT_MLFQ.set_time_service(self.time_service)

                    results = new_SRT_MLFQ.run_algorithm_mlfq(index, MLFQ_deques[index], max_index)
                    r_time_service = results[0]
                    process_with_highest_priority = results[1]
                    arrived_highest_processes = results[2]
                    current_processes = results[3]
                    removed_processes = results[4]

                    self.time_service = r_time_service
                    # print(f"Time service MLFQ-SRT: {self.time_service}")
                    MLFQ_deques[index] = current_processes

                    if(len(arrived_highest_processes) != 0):
                        MLFQ_deques[index - 1] = arrived_highest_processes

                    if(len(removed_processes) != 0):
                        if(index != len(self.queues) - 1):
                            MLFQ_deques[index + 1].extend(removed_processes)
                elif(self.queues[index] == "HRRN"):
                    new_HRRN_MLFQ = HRRN(self.queues[index])
                    new_HRRN_MLFQ.set_processes(self.processes)
                    new_HRRN_MLFQ.set_time_service(self.time_service)

                    results = new_HRRN_MLFQ.run_algorithm_mlfq(index, MLFQ_deques[index], max_index)
                    r_time_service = results[0]
                    process_with_highest_priority = results[1]
                    arrived_highest_processes = results[2]
                    current_processes = results[3]
                    removed_processes = results[4]

                    self.time_service = r_time_service
                    # print(f"Time service MLFQ-HRRN: {self.time_service}")
                    MLFQ_deques[index] = current_processes

                    if(len(arrived_highest_processes) != 0):
                        MLFQ_deques[index - 1] = arrived_highest_processes

                    if(len(removed_processes) != 0):
                        if(index != len(self.queues) - 1):
                            MLFQ_deques[index + 1].extend(removed_processes)
                elif(self.queues[index] == "SJF"):
                    new_SJF_MLFQ = SJF(self.queues[index])
                    new_SJF_MLFQ.set_processes(self.processes)
                    new_SJF_MLFQ.set_time_service(self.time_service)

                    results = new_SJF_MLFQ.run_algorithm_mlfq(index, MLFQ_deques[index], max_index)
                    r_time_service = results[0]
                    process_with_highest_priority = results[1]
                    arrived_highest_processes = results[2]
                    current_processes = results[3]
                    removed_processes = results[4]

                    self.time_service = r_time_service
                    # print(f"Time service MLFQ-SJF: {self.time_service}")
                    MLFQ_deques[index] = current_processes

                    if(len(arrived_highest_processes) != 0):
                        MLFQ_deques[index - 1] = arrived_highest_processes

                    if(len(removed_processes) != 0):
                        if(index != len(self.queues) - 1):
                            MLFQ_deques[index + 1].extend(removed_processes)
                #

            # Revisamos si hay una fila con procesos faltantes
            if all(len(f) == 0 for f in MLFQ_deques):
                break
        print("Algoritmo MLFQ completado")
