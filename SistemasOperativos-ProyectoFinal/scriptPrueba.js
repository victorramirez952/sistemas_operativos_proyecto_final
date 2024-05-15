var commandInput = document.getElementById("command");
var eventosDisponibles = ["Evento 1", "Evento 2", "Evento 3"];

commandInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    if (commandInput.value.trim() === "ask") {
      var resultado = "Eventos disponibles: \n" + eventosDisponibles.join("\n");
      commandInput.value = resultado;
    } else if(commandInput.value.trim() === "sub event_name"){
      
    } else if(commandInput.value.trim() === "unsub event_name"){
      
    } else if(commandInput.value.add() === "list"){
      
    }
  }
});


