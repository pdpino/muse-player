/**
 * Receive a stream of data from a muse server and plots it
 */


class Graph {
  /**
   * Intialize
   */
  constructor(container, w, h, title, y_min, y_max, x_ticks, y_ticks, n_secs) {
    // Save variables
    this._update_x_axis(n_secs);
    this.y_min = Number(y_min);
    this.y_max = Number(y_max);
    this.y_min_home = Number(y_min);
    this.y_max_home = Number(y_max);

    this.create_empty_graph(container, w, h, title, x_ticks, y_ticks);
  }


  /**
   * Create an empty graph
   * @param {String} container HTML ID to locate the graph
   * @param {Number} w width
   * @param {Number} h height
   * @param {String} title
   * @param {Number} y_min initial minimum for y axis
   * @param {Number} y_max initial maximum for y axis
   * @param {Number} x_ticks
   * @param {Number} y_ticks
   * @param {Number} n_secs Amount of seconds to plot in the x axis
   */
  create_empty_graph(container, w, h, title, x_ticks, y_ticks){
    // Margin
    this.margin = {top: 40, right: 10, bottom: 30, left: 60};
    this.width = w - this.margin.left - this.margin.right;
    this.height = h - this.margin.top - this.margin.bottom;

    // Svg
    this.svg = d3.select(container).append("svg")
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

    // Clip para tomar lo que sale por la izquierda
    this.svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", this.width)
        .attr("height", this.height);

    // Rangos de ejes
    this.x_range = d3.scale.linear().domain([0, this.n_secs]).range([0, this.width]);
    this.y_range = d3.scale.linear().domain([this.y_min, this.y_max]).range([this.height, 0]);

    // Eje del tiempo
    this.x_axis = d3.svg.axis().scale(this.x_range).orient("bottom").ticks(x_ticks);
    this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.height + ")")
        .call(this.x_axis);

    // Y axis
    this.y_axis = d3.svg.axis().scale(this.y_range).orient("left").ticks(y_ticks);
    this.svg.append("g")
        .attr("class", "y axis")
        .call(this.y_axis);

    // Titulo
    this.svg.append("text")
        .attr("id", "chart_title")
        .attr("x", (this.width / 2))
        .attr("y", 0 - (this.margin.top / 2))
        .attr("text-anchor", "middle")
        .text(title);
  }

  /**
   * Set
   * @param {function} line_function function that return an array of line functions
   */
  set_lines(line_function){
    this.lines = line_function(this.x_range, this.y_range);
  }

  /**
   * Init the paths in the graph and an array of bools to show the lines
   */
  init_channels(data, n_channels, colors){
    this.n_channels = Number(n_channels);

    // Create path and bools for each channel
    this.paths = Array(n_channels); // Lines in svg
    this.plot_bools = Array(n_channels); // Bools to show each line
    for(var i=0;i<n_channels;i++){
      this.plot_bools[i] = true; // Default: show line

      // Append to svg
      this.paths[i] = this.svg.append("g")
              .attr("clip-path", "url(#clip)")
            .append("path")
              .attr("class", "line")
              .style("stroke", colors[i])
              .attr("d", this.lines[i](data));
    }

  }

  /**
   * Set amounts to update the axiss
   */
  set_axis_params(dx_zoom, dy_zoom, dy_move){
    this.dx_zoom = Number(dx_zoom); // HACK: copy by value
    this.dy_zoom = Number(dy_zoom);
    this.dy_move = Number(dy_move);
  }

  /**
   * Show/Hide channels
   */
  toggle_show_path(i, checked){
    this.plot_bools[i] = checked;
    this.paths[i].style("opacity", checked ? 1 : 0);
  }


  /**
   * Update the y axis
   */
  _update_y_axis(y1, y2){
    if(y1 < y2){
      this.y_min = Number(y1); // ccpy by value // HACK
      this.y_max = Number(y2);
      this.y_range.domain([y1, y2]);
      this.svg.select(".y.axis").call(this.y_axis); // update svg
    }
  }

  /**
   * Zoom the y axis
   * @param {bool} out Direction of the zoom
   */
  zoom_y_axis(out){
    var sign_min;
    var sign_max;

    if(out){
      sign_min = -1; // decrease y_min
      sign_max = 1; // increase y_max
    }
    else{
      sign_min = 1; // increase y_min
      sign_max = -1; // decrease y_max
    }

    var y_min_new = this.y_min + sign_min*this.dy_zoom;
    var y_max_new = this.y_max + sign_max*this.dy_zoom;

    // Safe to zoom in
    if(!out){
      if(y_max_new - y_min_new < 100){ // At least a 100 window
        return;
      }
    }

    this._update_y_axis(y_min_new, y_max_new);
  };

  /**
   * Set the y axis to the original values
   */
  home_y_axis(){
    this._update_y_axis(this.y_min_home, this.y_max_home);
  }

  /**
   * Move the y axis range
   * @param {bool} up Direction of the move
   */
  move_y_axis(up){
    var sign;

    if(up){
      sign = 1;
    }
    else{
      sign = -1;
    }

    var y_min_new = this.y_min + sign*this.dy_move;
    var y_max_new = this.y_max + sign*this.dy_move;

    this._update_y_axis(y_min_new, y_max_new);
  }


  /**
   *
   */
  _update_x_axis(segundos){
    if(segundos > 1){
      this.n_secs = Number(segundos); // HACK
      $("#segX").text(this.n_secs.toFixed(0))
    }
  }

  /**
   *
   * @param {bool} increase increase or decrease the amount of seconds shown
   */
  zoom_x_axis(increase){
    var sign;
    if(increase){
      sign = 1;
    }
    else{
      sign = -1;
    }
    this._update_x_axis(this.n_secs + sign*this.dx_zoom);
  }


  /**
   * Update the line in the graph, use when updated the data
   */
  _update_graph_line(data, path, line, plot_ch){
    if(plot_ch){
      path.attr("d", line(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }
  }


  /**
   * Update all the lines in the graph
   */
  update_graph(data, shift=true) {
    for(var i=0;i<this.n_channels;i++){
      this._update_graph_line(data, this.paths[i], this.lines[i], this.plot_bools[i]);
    }

    // actualizar rango de tiempo
    var rango = d3.extent(data, function(d) { return d.T; });
    // if(rango[0] + this.n_secs > rango[1]){ rango[1] = rango[0] + this.n_secs; } // Que el rango minimo sea n_secs
    this.x_range.domain(rango);

    this.svg.select(".x.axis").call(this.x_axis); // change the x axis

    if(shift){ // shift the data to fit in n_secs
      while(data[data.length-1].T - data[0].T > this.n_secs){
        data.shift();
      }
    }
  }

}



/**
 * Create an array of functions that returns the channels in the electrode data
 * @param {d3.scale.linear} x range for x axis
 * @param {d3.scale.linear} y range for y axis
 */
function electrode_lines(x, y){
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
function is_connecting(conn){
  return conn.status === StatusEnum.CONNECTING;
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
    if(is_connecting(conn)){
      console.log("Can't connect to the server");
      // TODO: send alert to the client
    }
    else{
      console.log("Error in the server connection");
    }
    close_conn(conn, arr_data);
  };

  return;
}




/**
 * Main process
 */
$(document).ready( function() {
  // TODO: buscar header y footer bootstrap

  // Not important:
  // TODO: estandarizar nombres de funciones y variables: minusMayus vs _; graph vs chart

  // Data
  var n_channels = 5;
  var data = initialize_data();


  var colors = ["black", "red", "blue", "green", "cyan"];
  var graph = new Graph("#chart_container", 700, 400, "Electrodes", -1000, 1000, 5, 5, 5);
  graph.set_lines(electrode_lines);
  graph.init_channels(data, n_channels, colors);
  graph.set_axis_params(1, 100, 50); // dx_zoom, dy_zoom, dy_move


  // Pintar leyenda
  for(var i=0;i<n_channels;i++){
    var id_element = "#ch".concat(String(i+1), "-rect");
    d3.select(id_element).style("fill", colors[i]);
  }

  // Show/hide events
  for(var i=0;i<n_channels;i++){
    var id_element = "#ch".concat(String(i+1));
    $(id_element).click(function(){ graph.toggle_show_path(i, this.checked); });
  }

  // Botones para updatear ejes
  $("#btn-zoomYin").click(function(){ graph.zoom_y_axis(false); });
  $("#btn-zoomYout").click(function(){ graph.zoom_y_axis(true); });
  $("#btn-moveYdown").click(function(){ graph.move_y_axis(false); });
  $("#btn-moveYup").click(function(){ graph.move_y_axis(true); });
  $("#btn-homeY").click(function(){ graph.home_y_axis(); });
  $("#btn-zoomXdec").click(function(){ graph.zoom_x_axis(false); });
  $("#btn-zoomXinc").click(function(){ graph.zoom_x_axis(true); });



  // Conexion: con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/muse';
  var conn = {stream: null, status: StatusEnum.OFF};


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

    graph.update_graph(data); // Update grafico
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
