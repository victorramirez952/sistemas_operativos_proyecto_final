let id_client = 0;

function send_message(message){
  return JSON.stringify({
    "type": "message",
    "value": message,
    "id_client": id_client
  });
}

function suscribe(websocket, event_name){
  websocket.send(JSON.stringify({ 
    type: "suscribe_event", 
    value: event_name, 
    id_client: id_client
  }));
}

function unsuscribe(websocket, event_name){
  websocket.send(JSON.stringify({ 
    type: "unsuscribe_event", 
    value: event_name, 
    id_client: id_client
  }));
}

function ask_events(websocket){
  websocket.send(JSON.stringify({ 
    type: "ask_events",
    id_client: id_client
  }));
}

function list_suscribed_events(websocket){
  websocket.send(JSON.stringify({ 
    type: "list_suscribed_events",
    id_client: id_client
  }));
}

function list_algorithms(websocket){
  websocket.send(JSON.stringify({ 
    type: "list_algorithms_client",
    id_client: id_client
  }));
}



window.addEventListener("DOMContentLoaded", () => {
  id_client = Math.random().toString(36).slice(2, 13);
  console.log("ID de cliente: ", id_client);
  
  const items = document.createElement("ul");
  document.body.appendChild(items);
  
  let greeting = `Hola soy un nuevo cliente html con ID ${id_client}`
  
  const websocket = new WebSocket("ws://localhost:8765/");

  document.querySelector("#btn_suscribe").addEventListener("click", () => {
    suscribe(websocket, "omega");
  });

  document.querySelector("#btn_unsuscribe").addEventListener("click", () => {
    unsuscribe(websocket, "omega");
  });

  document.querySelector("#btn_ask").addEventListener("click", () => {
    ask_events(websocket);
  });

  document.querySelector("#btn_list_events").addEventListener("click", () => {
    list_suscribed_events(websocket);
  });

  document.querySelector("#btn_list_algorithms").addEventListener("click", () => {
    list_algorithms(websocket);
  });

  websocket.onopen = () => {
      websocket.send(send_message(greeting))
    }
    websocket.onmessage = ({ data }) => {
      console.log(data);
      const suceso = JSON.parse(data);
      if(suceso.type == "list_data"){
        available_events = suceso.data
        const item = document.createElement("li");
        const content = document.createTextNode(suceso.message);
        item.appendChild(content);
        items.appendChild(item)
        for(let i = 0; i < available_events.length; i++){
          const item = document.createElement("li");
          const content = document.createTextNode(available_events[i]);
          item.appendChild(content);
          items.appendChild(item)
        }
      } else {
        const item = document.createElement("li");
        const content = document.createTextNode(suceso.value);
        item.appendChild(content);
        items.appendChild(item);
        if(suceso.value == "El servidor va a finalizar"){
          console.log("El servidor esta finalizando ahora mismo");
          websocket.close()
        }
      }
    };
  });