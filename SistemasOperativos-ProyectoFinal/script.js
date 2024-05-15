// Constantes para definir los comandos disponibles a utilizar
const COMMAND_ASK = "ask";
const COMMAND_SUBSCRIBE = "sub";
const COMMAND_UNSUBSCRIBE = "unsub";
const COMMAND_LIST = "list";
const COMMAND_ASK_ALGORITHM = "ask algorithm";
const CONFIRMATION_SUBSCRIBE = "Estás seguro de que quieres suscribirte a este evento?";
const CONFIRMATION_UNSUBSCRIBE = "Estás seguro de que quieres desuscribirte a este evento?";

// Algoritmos disponibles a usar
var algoritmosDisponibles = ["FCFS", "FIFO", "RR", "SJF", "SRT", "HRNN", "MLFQ"];

// Eventos disponibles a usar
var eventosDisponibles = ["Evento1", "Evento2", "Evento3"];
var eventosSuscritos = [];

// Permitir la escritura de comandos en el search-input y mostrar los resultados en la terminal
var commandInput = document.getElementById("search-input");
var commandOutput = document.getElementById("command");

// Añadir Evento
commandInput.addEventListener("keydown", handleCommand);

// Manejar comando
function handleCommand(event) {
  if (event.key === "Enter") {
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
  if (eventName){
    if(eventosSuscritos.includes(eventName)){
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
  const subscribedResultado= "Eventos suscritos: \n" + eventosSuscritos.join("\n");
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