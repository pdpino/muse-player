/**
 * Receive a stream of data from a muse server and plots it
 */


/* Funciones para grafico */
/**
 * Create an empty graph
 * @param {Number} yMin minimum for y axis
 * @param {Number} yMax maximum for y axis
 * @param {Number} xTicks ticks for x axis
 * @param {Number} yTicks ticks for y axis
 * @param {Number} n_secs Amount of seconds to plot in the x axis
 */
function create_graph(yMin, yMax, xTicks, yTicks, n_secs){
  // Margenes
  var margin = {top: 10, right: 10, bottom: 20, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

  // Svg
  var svg = d3.select("#chart_container").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Clip para tomar lo que sale por la izquierda
  svg.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);

  // Rangos de ejes
  var xRange = d3.scale.linear().domain([0, n_secs]).range([0, width]);
  var yRange = d3.scale.linear().domain([yMin, yMax]).range([height, 0]);

  // Eje del tiempo
  var xAxis = d3.svg.axis().scale(xRange).orient("bottom").ticks(5);
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  // Y axis
  var yAxis = d3.svg.axis().scale(yRange).orient("left").ticks(5);
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  return {svg: svg, xRange: xRange, yRange: yRange, xAxis: xAxis, yAxis: yAxis};
}

/**
 * Create an array of functions that return the data for a line in the graph
 * @param {d3.scale.linear} x range for x axis
 * @param {d3.scale.linear} y range for y axis
 */
function create_line_functions(x, y){
  var lines = Array(5);

  lines[0] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH1); });
  lines[1] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH2); });
  lines[2] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH3); });
  lines[3] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH4); });
  lines[4] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH5); });

  return lines;
};

/**
 * Funcion para actualizar linea en grafico
 */
function update_graph_line(data, path, line, plot_ch){
  if(plot_ch){
    path.attr("d", line(data))
        .attr("transform", null)
      .transition()
        .duration(1000)
        .ease("linear");
  }
}

/**
 * Crear paths en un grafico
 */
function create_path(graph, data, line, color){
  return graph.svg.append("g")
          .attr("clip-path", "url(#clip)")
        .append("path")
          .attr("class", "line")
          .style("stroke", color)
          .attr("d", line(data));
};


/**
 * Set the span in html with the amount of seconds displaying in the x axis
 */
function set_segX(segs){
  $("#segX").text(segs.toFixed(1))
}

/* Funciones para datos */
/**
 * Initialize an empty array that behaves as data
 */
function initialize_data(){
  var data = new Array(1);
  data[0] = {T: 0, CH1: 0, CH2: 0, CH3: 0, CH4: 0, CH5: 0};
  return data;
}



/* Funciones para connection */
var StatusEnum = {OFF: 0, CONNECTING: 1, CONNECTED: 2, DISCONNECTED: 3};
function is_connected(conn){
  return conn.status === StatusEnum.CONNECTED;
}

function is_disconnected(conn){
  return conn.status === StatusEnum.OFF || conn.status === StatusEnum.DISCONNECTED;
}

/**
 * Set the status of the connection.
 * Set a number in the conn object, an icon and a text in the page
 */
function set_status(conn, status){
  var text = "";
  var icon = "";
  var color = "";

  conn.status = status;

  switch (status) {
    case StatusEnum.OFF:
      text = "Off";
      icon = "off";
      color = "black";
      break;
    case StatusEnum.CONNECTING:
      text = "Connecting";
      icon = "hourglass"; //Reloj de arena
      color = "orange";
      break;
    case StatusEnum.CONNECTED:
      text = "Connected";
      icon = "ok"; // Ticket
      color = "green";
      break;
    case StatusEnum.DISCONNECTED:
      text = "Disconnected";
      icon = "remove"; // Equis
      color = "red";
      break;
    default:
      console.log("Status not recognized: ", status);
      return;
  }

  $("#status-text").text(text);
  $("#status-text").css("color", color);
  $("#status-icon").attr("class", "glyphicon glyphicon-".concat(icon));
}

/**
* Close a connection
*/
function close_conn(conn, arr_data){
  if(is_disconnected(conn)){ // Ya esta desconectado
    return;
  }

  if(conn.stream !== null){
    if(conn.stream.readyState === 2){ // Esta closed
      //States. 0: connecting, 1: ready, 2: closed
      set_status(conn, StatusEnum.DISCONNECTED);
      return;
    }
    conn.stream.close();
  }

  set_status(conn, StatusEnum.DISCONNECTED);

  arr_data = initialize_data(); // reiniciar la data
  console.log("Connection closed");
  return;
}

/**
 * Start a connection
 */
function start_conn(url, conn, arr_data, recv_msg){
  if(!is_disconnected(conn)){ // Esta conectado o conectando
    return;
  }
  if(conn.stream !== null){
    if(conn.stream.readyState === 1){ // Esta conectado
      //States. 0: connecting, 1: ready, 2: closed
      set_status(conn, StatusEnum.CONNECTED);
      return;
    }
  }

  conn.stream = new EventSource(url); // Conectar por url

  set_status(conn, StatusEnum.CONNECTING);

  // Conectar eventos
  conn.stream.onopen = function (e) {
    set_status(conn, StatusEnum.CONNECTED);
    arr_data = initialize_data(); // reiniciar la data
    console.log("Connected with server");
  };
  conn.stream.onmessage = recv_msg;
  conn.stream.onerror = function (e) {
    console.log("Error in the server connection");
    close_conn(conn, arr_data);
  };

  return;
}




/**
 * Main process
 */
$(document).ready( function() {
  // TODO: buscar header y footer bootstrap
  // FIXME: en eje y no se alcanza a ver numero


  // Not important:
  // TODO: estandarizar nombres de funciones y variables: minusMayus, _


  // Parametros iniciales
  // Rango de eje y
  var yMin = -1000;
  var yMax = 1000;
  var yMinHome = Number(yMin); // copy by value
  var yMaxHome = Number(yMax);
  var xTicks = 5;
  var yTicks = 5;
  var n_secs = 5; // Cantidad de segundos maximo que guarda el plot

  set_segX(n_secs);

  // Data
  var n_channels = 5;
  var data = initialize_data();


  var colors = ["black", "red", "blue", "green", "cyan"];
  var graph = create_graph(yMin, yMax, xTicks, yTicks, n_secs);
  var lines = create_line_functions(graph.xRange, graph.yRange);

  // Paths y bools para cada canal
  var paths = Array(n_channels); // Lineas en svg
  var plot_bools = Array(n_channels); // Bools para esconder path
  for(var i=0;i<n_channels;i++){
    paths[i] = create_path(graph, data, lines[i], colors[i]);
    plot_bools[i] = true;
  }

  // Funcion para updatear el grafico
  function update_graph() {
    for(var i=0;i<n_channels;i++){
      update_graph_line(data, paths[i], lines[i], plot_bools[i]);
    }

    // actualizar rango de tiempo
    var rango = d3.extent(data, function(d) { return d.T; });
    // if(rango[0] + n_secs > rango[1]){ rango[1] = rango[0] + n_secs; } // Que el rango minimo sea n_secs
    graph.xRange.domain(rango);
    graph.svg.select(".x.axis").call(graph.xAxis); // change the x axis
  };

  // Pintar leyenda
  d3.select("#ch1-rect").style("fill", colors[0]);
  d3.select("#ch2-rect").style("fill", colors[1]);
  d3.select("#ch3-rect").style("fill", colors[2]);
  d3.select("#ch4-rect").style("fill", colors[3]);
  d3.select("#ch5-rect").style("fill", colors[4]);


  // Axis input
  var dxRange = 1;
  var dyZoom = 100;
  var dyMove = 50;
  function update_y_axis(y1, y2){
    if(y1 < y2){ // update solo si tiene sentido
      graph.yRange.domain([y1, y2]);
      graph.svg.select(".y.axis").call(graph.yAxis); // update svg
    }
  };


  // Mostrar/ocultar canales
  function toggle_show_path(path, checked){
    path.style("opacity", checked ? 1 : 0);
  }
  // Eventos
  $("#ch1").click(function(){
    plot_bools[0] = this.checked;
    toggle_show_path(paths[0], this.checked);
  });
  $("#ch2").click(function(){
    plot_bools[1] = this.checked;
    toggle_show_path(paths[1], this.checked);
  });
  $("#ch3").click(function(){
    plot_bools[2] = this.checked;
    toggle_show_path(paths[2], this.checked);
  });
  $("#ch4").click(function(){
    plot_bools[3] = this.checked;
    toggle_show_path(paths[3], this.checked);
  });
  $("#ch5").click(function(){
    plot_bools[4] = this.checked;
    toggle_show_path(paths[4], this.checked);
  });


  // Conexion: con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/muse';
  var conn = {stream: null, status: StatusEnum.OFF};


  // Botones para updatear ejes
  $("#btn-zoomYin").click(function(){
    if(yMin + dyZoom < yMax - dyZoom){ // Solo si tiene sentido
      yMin += dyZoom;
      yMax -= dyZoom;
      update_y_axis(yMin, yMax);
    }
  });
  $("#btn-zoomYout").click(function(){
    yMin -= dyZoom;
    yMax += dyZoom;
    update_y_axis(yMin, yMax);
  });
  $("#btn-zoomXdec").click(function(){
    n_secs -= dxRange;
    set_segX(n_secs);
  });
  $("#btn-zoomXinc").click(function(){
    n_secs += dxRange;
    set_segX(n_secs);
  });
  $("#btn-moveYdown").click(function(){
    yMin -= dyMove;
    yMax -= dyMove;
    update_y_axis(yMin, yMax);
  });
  $("#btn-moveYup").click(function(){
    yMin += dyMove;
    yMax += dyMove;
    update_y_axis(yMin, yMax);
  });
  $("#btn-homeY").click(function(){
    yMin = yMinHome;
    yMax = yMaxHome;
    update_y_axis(yMin, yMax);
  });

  /**
   * Recibe un mensaje entrante
   */
  function receive_msg(e) {
    var arr = e.data.split(",");
    var t = parseFloat(arr[0]); // tiempo
    var ch1 = parseFloat(arr[1]);
    var ch2 = parseFloat(arr[2]);
    var ch3 = parseFloat(arr[3]);
    var ch4 = parseFloat(arr[4]);
    var ch5 = parseFloat(arr[5]);

    // Push datos
    data.push({T: t, CH1: ch1, CH2: ch2, CH3: ch3, CH4: ch4, CH5: ch5});

    // Update grafico
    update_graph();

    // Pop datos hasta tener solo n_secs
    while(data[data.length-1].T - data[0].T > n_secs){
      data.shift();
    }
  };

  // Botones iniciar/cerrar conexion
  $("#btn-start-conn").click(function(){
    data = initialize_data(); // Reiniciar data
    start_conn(dir, conn, data, receive_msg)
  });
  $("#btn-close-conn").click(function(){
    close_conn(conn, data);
  });

  // $("#btn-debug").click(function(){
  //   $("#status-text").text("hola");
  //   // document.getElementById("status-text").innerHTML="newtext";
  // });


  // Conectarse al server
  start_conn(dir, conn, data, receive_msg)

  console.log("All set");
});
