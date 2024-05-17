// Constantes para definir los comandos disponibles a utilizar
const COMMAND_ASK = "ask";
const COMMAND_SUBSCRIBE = "sub";
const COMMAND_UNSUBSCRIBE = "unsub";
const COMMAND_LIST = "list";
const COMMAND_ASK_ALGORITHM = "ask algorithm";
const CONFIRMATION_SUBSCRIBE = "Estás seguro de que quieres suscribirte a este evento?";
const CONFIRMATION_UNSUBSCRIBE = "Estás seguro de que quieres desuscribirte a este evento?";
//Constantes para asignar los botones de los algoritmos y que cada uno realice alguna acción
const algorithmButtons = document.getElementById('algorithm-buttons');
const buttons = Array.from(algorithmButtons.children);

//Dependiendo del botón al que se haga click, se ejecutarán ciertas funciones y se almacenará el nombre del algoritmo elegido
buttons.forEach((button) => {
    button.addEventListener('click', (e) => {
        const algorithm = e.target.textContent;
        document.getElementById("processes-table").replaceChildren()
        existing_processes = new Map() // Modifica la variable global
        
        // Si ese botón elegido contiene los algoritmos "FCFS", "SJF", "SRT", "HRNN"
        // Se declaran las variables de número de procesos, el tiempo de llegada y de salida de cada algoritmo 
        if (['FCFS', 'SJF', 'SRT', 'HRRN'].includes(algorithm)) {
            let numberOfProcesses = null;
            let arrivalTimes = [];
            let burstTimes = [];

            // Función para obtener el número de procesos de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco
            function numeroProcesos() {
                numberOfProcesses = prompt(`Ingrese el número de procesos para el algoritmo ${algorithm}`);
                if (numberOfProcesses == null) {
                    return null
                } else {
                    numberOfProcesses = parseInt(numberOfProcesses);
                    if (isNaN(numberOfProcesses)) {
                        alert(`El número de procesos debe ser un número entero.`);
                        numeroProcesos();
                    } else {
                        for (let i = 0; i < numberOfProcesses; i++) {
                            if(tiempoLlegada(i + 1) == null){
                                return null
                            }
                        }
                    }
                    return numberOfProcesses
                }
            }
            // Función para obtener el tiempo de llegada o Arrival Time de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco

            function tiempoLlegada(index) {
                let arrivalTime = null;
                do {
                    arrivalTime = prompt(`Ingrese el tiempo de llegada o Arrival Time para el proceso ${index} de ${algorithm}`);
                    if (arrivalTime == null) {
                        return null
                    }
                    arrivalTime = validateNumber(arrivalTime, 'arrival time');
                } while (arrivalTime == -1);
                arrivalTimes.push(arrivalTime);
                if(tiempoSalida(index) == null){
                    return null
                }
                return arrivalTime
            }

          // Función para obtener el tiempo de salida o Burst Time de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco

            function tiempoSalida(index) {
                let burstTime = null;
                do {
                    burstTime = prompt(`Ingrese el tiempo de salida o Burst Time para el proceso ${index} de ${algorithm}`);
                    if (burstTime == null) {
                        return null
                    }
                    burstTime = validateNumber(burstTime, 'burst time');
                } while (burstTime == -1);
                burstTimes.push(burstTime);
                return burstTime
            }
          // Función para validar que el número ingresado sea un número entero
            function validateNumber(value, field) {
                let validNumber = parseInt(value);
                if (isNaN(validNumber)) {
                    alert(`El ${field} debe ser un número entero.`);
                    return -1;
                } else {
                    return validNumber;
                }
            }

            if(numeroProcesos() == null){
                return
            }

            const data_algorithm = {
                "algorithm_name": `${algorithm}`,
                "quantum": -1,
                "processes": []
            }

            for(let i = 0; i < arrivalTimes.length; i++){
                let new_process = {
                    "id_process": `P${i+1}`,
                    "arrival_time": arrivalTimes[i],
                    "burst_time": burstTimes[i]
                }
                data_algorithm.processes.push(new_process)
            }

            data_algorithm.processes.sort(
                (p1, p2) => p1.arrival_time - p2.arrival_time
            )

            send_data_algorithm(data_algorithm)

          // Si el algoritmo elegido es RR, se manda llamar a la función handleRRAlgorithm
        } else if (algorithm == 'RR') {
            handleRRAlgorithm();
          // Si el algoritmo elegido es MLFQ, se declaran el número de colas y las colas en un arreglo.
        } else if (algorithm == 'MLFQ') {
            let numberOfQueues = null;
            let queues_names = [];
            let queues_quantums = [];
            let numberOfProcesses = null;
            let arrivalTimes = [];
            let burstTimes = [];

            // Función para obtener el número de colas para cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco
            function askNumberOfQueues() {
                numberOfQueues = prompt(`Ingrese el número de colas para el algoritmo ${algorithm}`);
                if (numberOfQueues == null) {
                    return null
                } else {
                    numberOfQueues = parseInt(numberOfQueues);
                    if (isNaN(numberOfQueues)) {
                        alert(`El número de colas debe ser un número entero.`);
                        askNumberOfQueues();
                    } else {
                        for (let i = 0; i < numberOfQueues; i++) {
                            if(askAlgorithmForQueue(i + 1) == null){
                                return null
                            }
                        }
                    }
                    return numberOfQueues
                }
            }
            // Función para solicitar el tipo de algoritmo que será usado para cada una de las colas, solo se puede ingresar "FCFS","RR" "SJF", "SRT", y "HRNN"

            function askAlgorithmForQueue(queueNumber) {
                let algorithmChoice = null;
                do {
                    algorithmChoice = prompt(`Escriba / Seleccione el algoritmo para la cola ${queueNumber}: FCFS, RR, SJF, SRT, HRRN`);
                    if(algorithmChoice == null){
                        return null
                    }
                } while (!['FCFS', 'RR', 'SJF', 'SRT', 'HRRN'].includes(algorithmChoice));

                 // Si el Algoritmo que se escribió es RR, entonces adicionalmente se pedirá el tamaño del quantum
                if (algorithmChoice == 'RR') {
                    queues_names.push("RR")
                    let quantumSize = null
                    do {
                        quantumSize = prompt(`Ingrese el tamaño del quantum para el algoritmo RR en la cola ${queueNumber}`);
                        if (quantumSize == null){
                            return null
                        }
                        quantumSize = validateNumber(quantumSize, 'quantum')
                    } while(quantumSize == -1)
                    queues_quantums.push(parseInt(quantumSize))
                } else {
                    queues_names.push(algorithmChoice)
                    queues_quantums.push(-1)
                }
                return true
            }
            
            // Función para obtener el número de procesos de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco
            function numeroProcesos() {
                numberOfProcesses = prompt(`Ingrese el número de procesos para el algoritmo ${algorithm}`);
                if (numberOfProcesses == null) {
                    return null
                } else {
                    numberOfProcesses = parseInt(numberOfProcesses);
                    if (isNaN(numberOfProcesses)) {
                        alert(`El número de procesos debe ser un número entero.`);
                        numeroProcesos();
                    } else {
                        for (let i = 0; i < numberOfProcesses; i++) {
                            if(tiempoLlegada(i + 1) == null){
                                return null
                            }
                        }
                    }
                    return numberOfProcesses
                }
            }
            // Función para obtener el tiempo de llegada o Arrival Time de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco

            function tiempoLlegada(index) {
                let arrivalTime = null;
                do {
                    arrivalTime = prompt(`Ingrese el tiempo de llegada o Arrival Time para el proceso ${index} de ${algorithm}`);
                    if (arrivalTime == null) {
                        return null
                    }
                    arrivalTime = validateNumber(arrivalTime, 'arrival time');
                } while (arrivalTime == -1);
                arrivalTimes.push(arrivalTime);
                if(tiempoSalida(index) == null){
                    return null
                }
                return arrivalTime
            }

          // Función para obtener el tiempo de salida o Burst Time de cada algoritmo, se debe de ingresar un número entero y no se puede dejar en blanco

            function tiempoSalida(index) {
                let burstTime = null;
                do {
                    burstTime = prompt(`Ingrese el tiempo de salida o Burst Time para el proceso ${index} de ${algorithm}`);
                    if (burstTime == null) {
                        return null
                    }
                    burstTime = validateNumber(burstTime, 'burst time');
                } while (burstTime == -1);
                burstTimes.push(burstTime);
                return burstTime
            }
          
          // Función para validar que el número ingresado sea un número entero
            function validateNumber(value, field) {
                let validNumber = parseInt(value);
                if (isNaN(validNumber)) {
                    alert(`El ${field} debe ser un número entero.`);
                    return -1;
                } else {
                    return validNumber;
                }
            }

            if(askNumberOfQueues() == null){
                return
            }

            if(numeroProcesos() == null){
                return
            }

            const data_algorithm = {
                "algorithm_name": "MLFQ",
                "quantums": queues_quantums,
                "queues": queues_names,
                "processes": []
            }

            for(let i = 0; i < arrivalTimes.length; i++){
                let new_process = {
                    "id_process": `P${i+1}`,
                    "arrival_time": arrivalTimes[i],
                    "burst_time": burstTimes[i]
                }
                data_algorithm.processes.push(new_process)
            }

            data_algorithm.processes.sort(
                (p1, p2) => p1.arrival_time - p2.arrival_time
            )

            send_data_algorithm(data_algorithm)
        }
    });
});

// Función para manejar el algoritmo Round Robin
function handleRRAlgorithm() {
    let numberOfProcesses = null;
    let arrivalTimes = [];
    let burstTimes = [];
    let quantumSize = null;

  // Función para obtener el número de procesos del RR, se debe de ingresar un número entero y no se puede dejar en blanco
    function askNumberOfProcesses() {
        numberOfProcesses = prompt(`Ingrese el número de procesos para el algoritmo RR`);
        if (numberOfProcesses == null) {
            return null
        } else {
            numberOfProcesses = parseInt(numberOfProcesses);
            if (isNaN(numberOfProcesses)) {
                alert(`El número de procesos debe ser un número entero.`);
                askNumberOfProcesses();
            } else {
                for (let i = 0; i < numberOfProcesses; i++) {
                    if(askArrivalTime(i + 1) == null){
                        return null
                    }
                }
                return numberOfProcesses
            }
        }
    }
    // Función para obtener el tiempo de llegada o Arrival Time del RR, se debe de ingresar un número entero y no se puede dejar en blanco
    function askArrivalTime(index) {
        let arrivalTime = null;
        do {
            arrivalTime = prompt(`Ingrese el tiempo de llegada o Arrival Time para el proceso ${index} de RR`);
            if (arrivalTime == null) {
                return null
            }
            arrivalTime = validateNumber(arrivalTime, 'arrival time');
        } while (arrivalTime == -1);
        arrivalTimes.push(arrivalTime);
        if(askBurstTime(index) == null){
            return null
        }
        return arrivalTime
    }

    // Función para obtener el tiempo de salida o Burst Time del RR, se debe de ingresar un número entero y no se puede dejar en blanco

    function askBurstTime(index) {
        let burstTime = null;
        do {
            burstTime = prompt(`Ingrese el tiempo de salida o Burst Time para el proceso ${index} de RR`);
            if (burstTime == null) {
                return null
            }
            burstTime = validateNumber(burstTime, 'burst time');
        } while (burstTime == -1);
        burstTimes.push(burstTime);
        return burstTime
    }

  // Función para obtener el tamaño del quantum del RR, se debe de ingresar un número entero y no se puede dejar en blanco

    function askQuantumSize() {
        quantumSize = prompt(`Ingrese el tamaño del quantum para el algoritmo RR`);
        if (quantumSize == null) {
            return null
        } else {
            quantumSize = parseInt(quantumSize);
            if (isNaN(quantumSize)) {
                alert(`El tamaño del quantum debe ser un número entero.`);
                askQuantumSize();
            }
            return quantumSize
        }
    }
  
  // Función para validar que el número ingresado sea un número entero
    function validateNumber(value, field) {
        let validNumber = parseInt(value);
        if (isNaN(validNumber)) {
            alert(`El ${field} debe ser un número entero.`);
            return -1;
        } else {
            return validNumber;
        }
    }

    if(askNumberOfProcesses() == null){
        console.log("Omega_2")
        return
    };
    if(askQuantumSize() == null){
        console.log("Omega")
        return
    };

    const data_algorithm = {
        "algorithm_name": "RR",
        "quantum": parseInt(`${quantumSize}`),
        "processes": []
    }

    for(let i = 0; i < arrivalTimes.length; i++){
        let new_process = {
            "id_process": `P${i+1}`,
            "arrival_time": arrivalTimes[i],
            "burst_time": burstTimes[i]
        }
        data_algorithm.processes.push(new_process)
    }

    data_algorithm.processes.sort(
        (p1, p2) => p1.arrival_time - p2.arrival_time
    )

    send_data_algorithm(data_algorithm)

}

// Algoritmos disponibles a usar
var algoritmosDisponibles = ["FCFS", "FIFO", "RR", "SJF", "SRT", "HRNN", "MLFQ"];

// Eventos disponibles a usar
var eventosDisponibles = ["Evento1", "Evento2", "Evento3"];
// Eventos suscritos
var eventosSuscritos = [];

// Permitir la escritura de comandos en el search-input y mostrar los resultados en la terminal
var commandInput = document.getElementById("search-input");
var commandOutput = document.getElementById("command");

// Enviar los comandos que escriba un cliente a la función handleCommand
commandInput.addEventListener("keydown", handleCommand);

// Ejecutar las funciones de comandos cada vez que se presione Enter
function handleCommand(event) {
    if (event.key == "Enter") {
        const command = commandInput.value.trim();
        switch (command.split(" ")[0]) {
            case COMMAND_ASK:
                handleAskCommand();
                break;
            case COMMAND_SUBSCRIBE:
                handleSubscribeCommand(command.split(" ")[1]);
                break;
            case COMMAND_UNSUBSCRIBE:
                handleUnsubscribeCommand(command.split(" ")[1]);
                break;
            case COMMAND_LIST:
                handleListCommand();
                break;
            case COMMAND_ASK_ALGORITHM:
                handleAskAlgorithmCommand();
                break;
            default:
                handleInvalidCommand();
        }
    }
}

// Manejar comando "ask"
function handleAskCommand() {
    const resultado = "Eventos disponibles: " + eventosDisponibles.join("\n");
    commandOutput.value = resultado;
}

// Manejar comando "sub"
function handleSubscribeCommand(eventName) {
    if (eventName) {
        if (eventosDisponibles.includes(eventName)) {
            if (confirm(CONFIRMATION_SUBSCRIBE)) {
                eventosSuscritos.push(eventName);
                commandOutput.value = `Suscrito a ${eventName}`;
            }
        } else {
            commandOutput.value = `El ${eventName} no existe`;
        }
    } else {
        commandOutput.value = "Nombre del Evento Inválido";
    }
}

// Manejar comando "unsub"
function handleUnsubscribeCommand(eventName) {
    if (eventName) {
        if (eventosSuscritos.includes(eventName)) {
            if (confirm(CONFIRMATION_UNSUBSCRIBE)) {
                const index = eventosSuscritos.indexOf(eventName);
                eventosSuscritos.splice(index, 1);
                commandOutput.value = `Desuscrito de ${eventName}`;
            }
        } else {
            commandOutput.value = `El ${eventName} no existe`;
        }
    } else {
        commandOutput.value = "Nombre del Evento Inválido";
    }
}

// Manejar comando "list"
function handleListCommand() {
    const subscribedResultado = "Eventos suscritos: \n" + eventosSuscritos.join("\n");
    commandOutput.value = subscribedResultado;
}

// Manejar comando "askalgorithm"
function handleAskAlgorithmCommand() {
    const resultado = "Algoritmos Disponibles: \n" + algoritmosDisponibles.join("\n");
    commandOutput.value = resultado;
}

// Manejar comando inválido
function handleInvalidCommand() {
    commandOutput.value = "Comando Inválido. Solo se pueden usar ask, subevent_name client_name, unsub event_name, list o ask algorithm";
}