let id_client = 0;
let websocket
let existing_processes = new Map()

function show_processes(processes){
    for(let i = 0; i < processes.length; i++){
        it_process = processes[i]
        if(existing_processes.get(it_process.id)){
            document.getElementById(`status-${it_process.id}`).innerText = it_process.status
            document.getElementById(`completion_time-${it_process.id}`).innerText = it_process.completion_time
        } else {
            const row = document.createElement("tr");
            const td_1 = document.createElement("td");
            const td_2 = document.createElement("td");
            const td_3 = document.createElement("td");
            td_1.setAttribute("id", `id-${it_process.id}`);
            td_2.setAttribute("id", `status-${it_process.id}`);
            td_3.setAttribute("id", `completion_time-${it_process.id}`);
            const content_1 = document.createTextNode(it_process.id);
            const content_2 = document.createTextNode(it_process.status);
            const content_3 = document.createTextNode(it_process.completion_time);
            td_1.appendChild(content_1);
            td_2.appendChild(content_2);
            td_3.appendChild(content_3);
            row.appendChild(td_1)
            row.appendChild(td_2)
            row.appendChild(td_3)
            existing_processes.set(it_process.id, true)
            document.getElementById("processes-table").appendChild(row)
        }
    }
}

function send_message(message){
    return JSON.stringify({
      "type": "message",
      "value": message,
      "id_client": id_client
    });
  }

function send_data_algorithm(data_algorithm) {
    // let response = await fetch(
    //   "http://127.0.0.1:5500/proyecto/casos_prueba_algoritmos/MLFQ/mlfq_hrrn.json"
    // );
    // let algorithm = response.json();
    websocket.send(
      JSON.stringify({
        type: "send_data_algorithm",
        id_client: id_client,
        data: data_algorithm,
      })
    );
}


window.addEventListener("DOMContentLoaded", () => {
    id_client = Math.random().toString(36).slice(2, 13);
    console.log("ID de cliente: ", id_client);

    let greeting = `Hola soy un nuevo cliente html con ID ${id_client}`

    websocket = new WebSocket("ws://localhost:8765/");

    websocket.onopen = () => {
        websocket.send(send_message(greeting))
    }

    let output_server = document.getElementById("output_server");
    websocket.onmessage = ({ data }) => {
        // console.log(data);
        const suceso = JSON.parse(data);
        if(suceso.type == "list_data"){
            available_events = suceso.data
            const item = document.createElement("li");
            const content = document.createTextNode(suceso.message);
            item.appendChild(content);
            outputer_server.appendChild(item)
            for(let i = 0; i < available_events.length; i++){
            const item = document.createElement("li");
            const content = document.createTextNode(available_events[i]);
            item.appendChild(content);
            output_server.appendChild(item)
            }
        } else if(suceso.type == "algorithm_result"){
            let processes = suceso.data
            console.log(processes);
            for(let i = 0; i < processes.length; i++){
                let process = processes[i]
                console.log(`Proceso ${process.id}; Status: ${process.status}; Completion time: ${process.completion_time}; Waiting time: ${process.waiting_time}`);
            }
            console.log("\n");
            processes.sort(
                (p1, p2) => p1.id[1] - p2.id[1]
            )
            show_processes(processes)
        } else {
            const item = document.createElement("li");
            const content = document.createTextNode(suceso.value);
            item.appendChild(content);
            output_server.appendChild(item);
            if(suceso.value == "El servidor va a finalizar"){
                console.log("El servidor esta finalizando ahora mismo");
                websocket.close()
            }
        }
    };

});