/**
 * Receive a stream of data from a muse server and plots it
 */


class Graph {
  /**
   * Intialize
   */
  constructor(config) {
    // Assure that the config object is correct
    if(this._fill_default_values(config) !== 0){
      // missing arguments
      return;
    }

    // Save variables // HACK
    this.n_channels = Number(config.n_channels);
    this.secs_indicator = String(config.sec_x);
    this._update_x_axis(config.n_secs);
    this.y_min = Number(config.y_min);
    this.y_max = Number(config.y_max);
    this.y_min_home = Number(config.y_min);
    this.y_max_home = Number(config.y_max);

    // Create graph
    this._create_empty_graph(config.container, config.width, config.height, config.title, config.x_ticks, config.y_ticks);

    // Set the line functions
    this._set_lines();

    // Init paths, bools and color for each channel
    this._init_channels(config.data, config.colors);

    // Set parameters to update the axis
    this._set_axis_params(config.dx_zoom, config.dy_zoom, config.dy_move);

    // Set the legend, and the proper events
    this._set_legend(config.legend_container, config.ch_names);

    // Buttons to update axis
    this._add_events_x_axis(config.x_zoom_btn[0], config.x_zoom_btn[1]);
    this._add_events_y_axis(config.y_zoom_btn, config.y_move_btn, config.y_home_btn);
  }

  /**
   * Receive a configuration object, if a value is missing fill it with default
   */
  _fill_default_values(config){
    if(config.container === undefined){
      console.log("ERROR: Missing graph container");
      return 1;
    }
    // TODO: handle when there is no legend container

    if(config.n_channels === undefined){
      console.log("ERROR: Declaring a graph without the number of channels");
      return 1;
    }



    if(config.ch_names === undefined){
      config.ch_names = new Array(config.n_channels);
      for(var i=0;i<config.n_channels;i++){
        config.ch_names[i] = "ch".concat(i);
      }
    }

    if(config.title === undefined){
      config.title = "Graph";
    }

    /**
     * Get a random color
     * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
     */
    function getRandomColor() {
      var letters = '0123456789ABCDEF';
      var color = '#';
      for (var i = 0; i < 6; i++ ) {
          color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    }

    if(config.colors === undefined){
      config.colors = new Array(config.n_channels);
      for(var i=0;i<config.n_channels;i++){
        config.colors[i] = getRandomColor();
      }
    }

    return 0;
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
  _create_empty_graph(container, w, h, title, x_ticks, y_ticks){
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
        .attr("id", "graph_title")
        .attr("x", (this.width / 2))
        .attr("y", 0 - (this.margin.top / 2))
        .attr("text-anchor", "middle")
        .text(title);
  }

  /**
   * Create an array of functions that returns the channels in the data
   * The data always come in the following format:
   * Array of Arrays, each of the inner arrays is a moment in time, which is formed by:
   * [t, ch1, ch2, ch3, ..., chN], where 't' is the time, and the rest are the n channels
   */
  _set_lines(){
    this.lines = new Array(this.n_channels);
    for(var i=0;i<this.n_channels;i++){ this.lines[i] = null; } //HACK: iniciar todo como null
    var graph = this;
    this.lines.forEach(function(l, i){
      graph.lines[i] = d3.svg.line()
        .x(function(d) { return graph.x_range(d[0]); })
        .y(function(d) { return graph.y_range(d[i + 1]); });
    });


  }

  /**
   * Init the paths in the graph and an array of bools to show the lines
   */
  _init_channels(data, colors){
    this.colors = colors; // REVIEW: copy?

    // Create path and bools for each channel
    this.paths = new Array(this.n_channels); // Lines in svg
    this.plot_bools = new Array(this.n_channels); // Bools to show each line
    var graph = this;
    for(var i=0;i<this.n_channels;i++){
      this.plot_bools[i] = true; // Default: show line
      this.paths[i] = null; // HACK
    }
    this.paths.forEach(function(p, i){
      graph.paths[i] = graph.svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .attr("class", "line")
        .style("stroke", colors[i])
        .attr("d", graph.lines[i](data));
    });

  }

  /**
   * Paint the squares in the legend
   */
  _set_legend(legend_container, ch_names){
    // Crear panel para leyenda
    $(legend_container).append(
      $('<div>', {
        'id':'legend-panel',
        'class':'panel panel-primary',
        // 'html':'<span>For HTML</span>',
      })
    );

    // Agregar header y body a panel
    $("#legend-panel").append(
      $('<div>', {
        'class': 'panel-heading text-center',
        'html': 'Legend'
      }),
      $('<form>', {
        'id': 'legend-form',
        'class': 'panel-body'
      })
    );



    // Agregar inputs para cada channel
    var ids_tick = new Array(this.n_channels);
    var graph = this;
    for(var i=0;i<this.n_channels;i++){
      ids_tick[i] = "ch".concat(String(i)).concat("-tick");
      var input_i = "<input id='".concat(String(ids_tick[i]))
        .concat("' type='checkbox' checked/>");
      var channel_name = String(ch_names[i]).concat('<br>');

      $("#legend-form").append(
        $('<svg>')
          .attr('class', 'legend-rect-container')
          .append(
            $('<rect>')
              .attr('class','legend-rect')
              .css("fill", graph.colors[i]) // Pintar del color
            )
      );

      $("#legend-form").append(
        ' ', // space
        input_i,
        ' ', // space
        channel_name,
      );
    }

    $("#legend-form").html($("#legend-form").html()); // HACK: Refresh svg





    // Paint colors
    // for(var i=0;i<this.n_channels;i++){
    //   d3.select(ids_rect[i]).style("fill", graph.colors[i]);
    // }

    // Show/hide events
    ids_tick.forEach(function(t, i){
      $(t).click( function(){
        graph.plot_bools[i] = this.checked;
        graph.paths[i].style("opacity", this.checked ? 1 : 0);
      });
    });

  }

  /**
   * Set amounts to update the axiss
   */
  _set_axis_params(dx_zoom, dy_zoom, dy_move){
    this.dx_zoom = Number(dx_zoom); // HACK: copy by value
    this.dy_zoom = Number(dy_zoom);
    this.dy_move = Number(dy_move);
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
   *
   */
  _update_x_axis(segundos){
    if(segundos > 1){
      this.n_secs = Number(segundos); // HACK
      $(this.secs_indicator).text(this.n_secs.toFixed(0))
    }
  }

  /**
   * Connect the x axis buttons with the corresponding events
   */
  _add_events_x_axis(btn_dec, btn_inc){
    var graph = this;
    $(btn_dec).click(function(){ graph.zoom_x_axis(false); });
    $(btn_inc).click(function(){ graph.zoom_x_axis(true); });
  }

  /**
   * Connect the y axis buttons with the corresponding events
   */
  _add_events_y_axis(btns_zoom, btns_move, btn_home){
    var graph = this;
    $(btns_zoom[0]).click(function(){ graph.zoom_y_axis(false); });
    $(btns_zoom[1]).click(function(){ graph.zoom_y_axis(true); });
    $(btns_move[0]).click(function(){ graph.move_y_axis(false); });
    $(btns_move[1]).click(function(){ graph.move_y_axis(true); });
    $(btn_home).click(function(){ graph.home_y_axis(); });
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
   * Update all the lines in the graph
   */
  update_graph(data, shift=true) {
    for(var i=0;i<this.n_channels;i++){
      // this._update_graph_line(data, this.paths[i], this.lines[i], this.plot_bools[i]);
      if(this.plot_bools[i]){
        this.paths[i].attr("d", this.lines[i](data))
            .attr("transform", null)
          .transition()
            .duration(1000)
            .ease("linear");
      }
    }

    // actualizar rango de tiempo
    var rango = d3.extent(data, function(d) { return d[0]; });
    // if(rango[0] + this.n_secs > rango[1]){ rango[1] = rango[0] + this.n_secs; } // Que el rango minimo sea n_secs
    this.x_range.domain(rango);

    this.svg.select(".x.axis").call(this.x_axis); // change the x axis

    if(shift){ // shift the data to fit in n_secs
      while(data[data.length-1][0] - data[0][0] > this.n_secs){
        data.shift();
      }
    }
  }

}


var StatusEnum = {OFF: 0, CONNECTING: 1, CONNECTED: 2, DISCONNECTED: 3};
class Connection{
  /**
   *
   * @param {String} url url to connect to
   * @param {String} status_text HTML id of the text of the connection message
   * @param {String} status_icon HTML id of the icon of the connection message
   * @param {function} recv_msg Function to connect to the onmessage event
   */
  constructor(config){
    // Name
    this.name = config.name;

    // URL
    this.url = config.url;

    // Status
    this.status_text = config.status_text;
    this.status_icon = config.status_icon;
    this._set_status(StatusEnum.OFF);

    // Stream
    this.stream = null;

    // Receive message function
    this.recv_msg = config.recv_msg;
  }

  /**
   * Return a bool
   */
  _is_connecting(){
    return this.status === StatusEnum.CONNECTING;
  }

  /**
   * Return a bool
   */
  _is_disconnected(){
    return this.status === StatusEnum.OFF || this.status === StatusEnum.DISCONNECTED;
  }


  /**
   * Set the status of the connection.
   * Set a number in the conn object, an icon and a text in the page
   */
  _set_status(status){
    var text = "";
    var icon = "";
    var color = "";

    this.status = status;

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

    $(this.status_text).text(text);
    $(this.status_text).css("color", color);
    $(this.status_icon).attr("class", "glyphicon glyphicon-".concat(icon));
  }


  /**
  * Close the connection
  */
  close_conn(){
    if(this._is_disconnected()){ // Ya esta desconectado
      return;
    }

    if(this.stream !== null){
      if(this.stream.readyState === 2){ // Esta closed
        //States. 0: connecting, 1: ready, 2: closed
        this._set_status(StatusEnum.DISCONNECTED);
        return;
      }
      this.stream.close();
    }

    this._set_status(StatusEnum.DISCONNECTED);
    console.log("Connection closed with", this.name);
  }

  /**
   * Start a connection
   */
  start_conn(){
    if(!this._is_disconnected()){ // Esta conectado o conectando
      return;
    }

    if(this.stream !== null){
      if(this.stream.readyState === 1){ //States. 0: connecting, 1: ready, 2: closed
        this._set_status(StatusEnum.CONNECTED);
        return;
      }
    }

    var conn = this;
    this._set_status(StatusEnum.CONNECTING);
    this.stream = new EventSource(this.url); // Conectar por url

    // Conectar eventos
    this.stream.onopen = function (e) {
      conn._set_status(StatusEnum.CONNECTED);
      console.log("Connected:", conn.name);
    };
    this.stream.onmessage = this.recv_msg;
    this.stream.onerror = function (e) {
      if(conn._is_connecting()){
        console.log("Can't connect to:", conn.name);
        // TODO: send alert to the client
      }
      else{
        console.log("Error in the connection", conn.name);
      }
      conn.close_conn();
    };

  }

}





/**
 * Initialize an empty array that holds data
 * @param {Number} n number of channels
 */
function init_data(n){
  var data = new Array(1);
  data[0] = new Array(n+1); // one for the time, the rest are channels
  for(var i=0;i<=n;i++){ data[0][i] = 0; } // init 0
  return data;
}


/**
 * Main process
 */
$(document).ready( function() {
  // TODO: buscar header y footer bootstrap


  // DEBUG.
  var use_eeg = false; // CHANGE THIS
  if(use_eeg){
    var n_channels = 5;
    var channel_names = ["TP9", "AF7", "AF8", "TP10", "Right Aux"];
    var color_names = ["black", "red", "blue", "green", "cyan"];
  }
  else{
    var n_channels = 5;  // CHANGE THIS, if use_eeg is false
    var channel_names = undefined;
    var color_names = undefined;
  }
  /////////////////


  

  // EEG Data
  var nchs = n_channels;
  var data = init_data(nchs);
  var graph = new Graph({
    container: "#graph_container",
    legend_container: '#legend_container',
    data: data,
    n_channels: nchs,
    title: "Electrodes",
    ch_names: channel_names,
    colors: color_names,

    // FIXME: que clase cree estos
    x_zoom_btn: ["#btn-zoomXdec", "#btn-zoomXinc"],
    y_zoom_btn: ["#btn-zoomYin", "#btn-zoomYout"],
    y_move_btn: ["#btn-moveYdown", "#btn-moveYup"],
    y_home_btn: "#btn-homeY",
    sec_x: "#segX",

    width: 700,
    height: 400,
    y_min: -1000,
    y_max: 1000,
    x_ticks: 5,
    y_ticks: 5,
    n_secs: 5,
    dx_zoom: 1, // FIXME: que clase calcule esto
    dy_zoom: 100,
    dy_move: 50
    });

  /**
   * Recibe un mensaje entrante de eeg
   */
  function receive_data(e) {
    var arr = e.data.split(",").map(parseFloat);

    // REVIEW: check arr.length == n channels
    while(arr.length < nchs){
      arr.push(0.0);
    }

    data.push(arr); // Push new data
    graph.update_graph(data); // Update graph
  };

  // EEG connection
  var eeg_conn = new Connection({
    name: "data",
    url: "http://localhost:8889/data/muse",
    status_text: "#status-text", //FIXME: que la clase cree estos
    status_icon: "#status-icon",
    recv_msg: receive_data
    });

  // Botones iniciar/cerrar conexion
  $("#btn-start-conn").click(function(){ data = init_data(nchs); eeg_conn.start_conn() });
  $("#btn-close-conn").click(function(){ eeg_conn.close_conn(); data = init_data(nchs); });


  eeg_conn.start_conn();

  console.log("All set");
});
