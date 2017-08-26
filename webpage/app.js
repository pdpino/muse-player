"use strict"

/**
 * Receive a stream of data from a muse server and plots it
 */

class Graph {
  /**
   * Intialize
   */
  constructor(config) {
    // Assure that the config object is correct
    if(this._fillDefaultValues(config) !== 0){
      // missing arguments
      return;
    }

    // Save variables // HACK
    this.n_channels = Number(config.n_channels);
    this.secs_indicator = String(config.sec_x);
    this._updateXAxis(config.n_secs);
    this.y_min = Number(config.y_min);
    this.y_max = Number(config.y_max);
    this.y_min_home = Number(config.y_min);
    this.y_max_home = Number(config.y_max);

    // Create graph
    this._createEmptyGraph(config.container, config.width, config.height, config.title, config.x_ticks, config.y_ticks);

    // Set the line functions
    this._initLines();

    // Init paths, bools and color for each channel
    this._initChannels(config.data, config.colors);

    // Set parameters to update the axis
    this._initAxisParams(config.dx_zoom, config.dy_zoom, config.dy_move);

    // Set the legend, and the proper events
    this._initLegend(config.legend_container, config.ch_names);

    // Buttons to update axis
    this._addEventsXAxis(config.x_zoom_btn[0], config.x_zoom_btn[1]);
    this._addEventsYAxis(config.y_zoom_btn, config.y_move_btn, config.y_home_btn);
  }

  /**
   * Receive a configuration object, if a value is missing fill it with default
   */
  _fillDefaultValues(config){
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
      for(let i=0;i<config.n_channels;i++){
        config.ch_names[i] = "ch".concat(i);
      }
    }

    config.title = config.title || "Graph";
    // if(config.title === undefined){
    //   config.title = "Graph";
    // }

    /**
     * Get a random color
     * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
     */
    function getRandomColor() {
      let letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++ ) {
          color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    }

    if(config.colors === undefined){
      config.colors = new Array(config.n_channels);
      for(let i=0;i<config.n_channels;i++){
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
  _createEmptyGraph(container, w, h, title, x_ticks, y_ticks){
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
  _initLines(){
    this.lines = new Array(this.n_channels);
    for(let i=0;i<this.n_channels;i++){ this.lines[i] = null; } //HACK: start as null so actual assign wont throw error
    let graph = this;
    this.lines.forEach((l, i) => {
      this.lines[i] = d3.svg.line()
        .x(function(d){ return graph.x_range(d[0]); })
        .y(function(d){ return graph.y_range(d[i + 1]); });
    });


  }

  /**
   * Init the paths in the graph and an array of bools to show the lines
   */
  _initChannels(data, colors){
    this.colors = colors; // REVIEW: copy?

    // Create path and bools for each channel
    this.paths = new Array(this.n_channels); // Lines in svg
    this.plot_bools = new Array(this.n_channels); // Bools to show each line
    for(let i=0;i<this.n_channels;i++){
      this.plot_bools[i] = true; // By default show line
      this.paths[i] = null;
    }
    this.paths.forEach((p, i) => {
      this.paths[i] = this.svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .attr("class", "line")
        .style("stroke", colors[i])
        .attr("d", this.lines[i](data));
    });

  }

  /**
   * Paint the squares in the legend
   */
  _initLegend(legend_container, ch_names){
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



    // Add checkbox for each channel
    let ids_tick = new Array(this.n_channels);
    let graph = this;
    for(let i=0;i<this.n_channels;i++){
      ids_tick[i] = "ch".concat(String(i)).concat("-tick");
      let input_i = "<input id='".concat(String(ids_tick[i]))
        .concat("' type='checkbox' checked/>");
      let channel_name = String(ch_names[i]).concat('<br>');

      // Add square with color
      $("#legend-form").append(
        $('<svg>')
          .attr('class', 'legend-rect-container')
          .append(
            $('<rect>')
              .attr('class','legend-rect')
              .css("fill", graph.colors[i]) // Pintar del color
            )
      );

      // Add input
      $("#legend-form").append(
        ' ', // space
        input_i, // input
        ' ', // space
        channel_name,
      );

      ids_tick[i] = "#".concat(ids_tick[i]); // Generate id-like tag
    }

    // HACK: Refresh svg
    $("#legend-form").html($("#legend-form").html());


    // Paint colors
    // for(let i=0;i<this.n_channels;i++){
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
  _initAxisParams(dx_zoom, dy_zoom, dy_move){
    this.dx_zoom = Number(dx_zoom); // HACK: copy by value
    this.dy_zoom = Number(dy_zoom);
    this.dy_move = Number(dy_move);
  }

  /**
   * Update the y axis
   */
  _updateYAxis(y1, y2){
    if(y1 < y2){
      this.y_min = Number(y1); // copy by value // HACK
      this.y_max = Number(y2);
      this.y_range.domain([y1, y2]);
      this.svg.select(".y.axis").call(this.y_axis); // update svg
    }
  }

  /**
   *
   */
  _updateXAxis(segundos){
    if(segundos > 1){
      this.n_secs = Number(segundos); // HACK
      $(this.secs_indicator).text(this.n_secs.toFixed(0))
    }
  }

  /**
   * Connect the x axis buttons with the corresponding events
   */
  _addEventsXAxis(btn_dec, btn_inc){
    $(btn_dec).click(() => { this.zoomXAxis(false); });
    $(btn_inc).click(() => { this.zoomXAxis(true); });
  }

  /**
   * Connect the y axis buttons with the corresponding events
   */
  _addEventsYAxis(btns_zoom, btns_move, btn_home){
    $(btns_zoom[0]).click(() => { this.zoomYAxis(false); });
    $(btns_zoom[1]).click(() => { this.zoomYAxis(true); });
    $(btns_move[0]).click(() => { this.moveYAxis(false); });
    $(btns_move[1]).click(() => { this.moveYAxis(true); });
    $(btn_home).click(() => { this.homeYAxis(); });
  }



  /**
   * Zoom the y axis
   * @param {bool} out Direction of the zoom
   */
  zoomYAxis(out){
    let sign_min;
    let sign_max;

    if(out){
      sign_min = -1; // decrease y_min
      sign_max = 1; // increase y_max
    }
    else{
      sign_min = 1; // increase y_min
      sign_max = -1; // decrease y_max
    }

    let y_min_new = this.y_min + sign_min*this.dy_zoom;
    let y_max_new = this.y_max + sign_max*this.dy_zoom;

    // Safe to zoom in
    if(!out){
      if(y_max_new - y_min_new < 10){
        return;
      }
    }

    this._updateYAxis(y_min_new, y_max_new);
  };

  /**
   * Set the y axis to the original values
   */
  homeYAxis(){
    this._updateYAxis(this.y_min_home, this.y_max_home);
  }

  /**
   * Move the y axis range
   * @param {bool} up Direction of the move
   */
  moveYAxis(up){
    let sign;

    if(up){
      sign = 1;
    }
    else{
      sign = -1;
    }

    let y_min_new = this.y_min + sign*this.dy_move;
    let y_max_new = this.y_max + sign*this.dy_move;

    this._updateYAxis(y_min_new, y_max_new);
  }

  /**
   *
   * @param {bool} increase increase or decrease the amount of seconds shown
   */
  zoomXAxis(increase){
    let sign;
    if(increase){
      sign = 1;
    }
    else{
      sign = -1;
    }
    this._updateXAxis(this.n_secs + sign*this.dx_zoom);
  }

  /**
   * Update all the lines in the graph
   */
  update(data, shift=true) {
    for(let i=0;i<this.n_channels;i++){
      // this._update_line(data, this.paths[i], this.lines[i], this.plot_bools[i]);
      if(this.plot_bools[i]){
        this.paths[i].attr("d", this.lines[i](data))
            .attr("transform", null)
          .transition()
            .duration(1000)
            .ease("linear");
      }
    }

    // actualizar rango de tiempo
    let rango = d3.extent(data, function(d) { return d[0]; });
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

const StatusEnum = {OFF: 0, CONNECTING: 1, CONNECTED: 2, DISCONNECTED: 3};
class Connection{
  /**
   * Constructor
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
    this._setStatus(StatusEnum.OFF);

    // Stream
    this.stream = null;

    // Receive message function
    this.recv_msg = config.recv_msg;
  }

  /**
   * Return a bool
   */
  _isConnecting(){
    return this.status === StatusEnum.CONNECTING;
  }

  /**
   * Return a bool
   */
  _isDisconnected(){
    return this.status === StatusEnum.OFF || this.status === StatusEnum.DISCONNECTED;
  }


  /**
   * Set the status of the connection.
   * Set a number in the conn object, an icon and a text in the page
   */
  _setStatus(status){
    let text = "";
    let icon = "";
    let color = "";

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
  close(){
    if(this._isDisconnected()){ // Ya esta desconectado
      return;
    }

    // Update stream
    if(this.stream !== null){
      if(this.stream.readyState < 2){ // Is not closed
        //States. 0: connecting, 1: ready, 2: closed
        this.stream.close();
      }
    }

    // Change in screen
    this._setStatus(StatusEnum.DISCONNECTED);

    console.log("Connection closed with", this.name);
  }

  /**
   * Start a connection
   */
  start(){
    if(!this._isDisconnected()){ // Is connecting or connected
      return;
    }

    if(this.stream !== null){
      if(this.stream.readyState === 1){ // Is already connected (but enum not updated)
        //States. 0: connecting, 1: ready, 2: closed
        this._setStatus(StatusEnum.CONNECTED);
        return;
      }
    }

    this._setStatus(StatusEnum.CONNECTING);
    this.stream = new EventSource(this.url);

    // Events
    this.stream.onopen = (e) => {
      this._setStatus(StatusEnum.CONNECTED);
      console.log("Connected:", this.name);
      // console.log("Opened");
    };
    // REVIEW: use a different event for start? redundant?
    // this.stream.addEventListener('start', (e) => {
    //   this._setStatus(StatusEnum.CONNECTED);
    //   console.log("Connected:", this.name);
    // }, false);
    this.stream.onmessage = this.recv_msg;
    this.stream.onerror = (e) => {
      if(this._isConnecting()){
        console.log("Can't connect to:", this.name);
        // TODO: send alert to the client
      }
      else{
        console.log("Error in the connection", this.name);
      }
      this.close();
    };

  }

}

/**
 * Main process
 */
$(document).ready( function() {
  let n_channels = 5;
  let waves = true; // HACK: select type hardcoded
  let channel_names, titulo, conn_name;
  if(waves){
    channel_names = ["delta", "theta", "alpha", "beta", "gamma"];
    titulo = "Waves";
    conn_name = "waves data";
  }
  else{
    channel_names = ["TP9", "AF7", "AF8", "TP10", "Right Aux"];
    titulo = "Electrodes";
    conn_name = "eeg data";
  }

  let nchs = n_channels;
  let data = initEmptyData(nchs);
  let graph = new Graph({
    container: "#graph_container",
    legend_container: '#legend_container',
    data: data,
    n_channels: nchs,
    title: titulo,
    ch_names: channel_names,
    colors: ["black", "red", "blue", "green", "cyan"],

    // FIXME: que clase cree estos
    x_zoom_btn: ["#btn-zoomXdec", "#btn-zoomXinc"],
    y_zoom_btn: ["#btn-zoomYin", "#btn-zoomYout"],
    y_move_btn: ["#btn-moveYdown", "#btn-moveYup"],
    y_home_btn: "#btn-homeY",
    sec_x: "#segX",

    width: 700,
    height: 400,
    y_min: -100,
    y_max: 100,
    x_ticks: 5,
    y_ticks: 5,
    n_secs: 5,
    dx_zoom: 1, // FIXME: que clase calcule esto y vaya cambiando
    dy_zoom: 10,
    dy_move: 50
    });

  /**
   * Recibe un mensaje entrante de eeg
   */
  function receive_data(e) {
    let arr = e.data.split(",").map(parseFloat);

    if(arr[0] < 0){ // Ignore negative time (wrong streaming from python?)
      return;
    }

    // REVIEW: check arr.length == n channels
    while(arr.length < nchs + 1){ // Fill with 0s if received less channels
      arr.push(0.0);
    }

    data.push(arr); // Push new data
    graph.update(data); // Update graph
  };

  // EEG connection
  let eeg_conn = new Connection({
    name: conn_name,
    url: "http://localhost:8889/data/muse",
    status_text: "#status-text", //FIXME: que la clase cree estos
    status_icon: "#status-icon",
    recv_msg: receive_data
    });

  // Botones iniciar/cerrar conexion
  $("#btn-start-conn").click(function(){ data = initEmptyData(nchs); eeg_conn.start() });
  $("#btn-close-conn").click(function(){ eeg_conn.close(); data = initEmptyData(nchs); });


  eeg_conn.start();

  console.log("All set");
});

/**
 * Initialize an empty array that will hold data
 * The data is an array of shape (n_points, n_channels), where each point is a sample in time
 */
function initEmptyData(n_channels){
  let data = new Array(1); // Starts with one item
  data[0] = new Array(n_channels + 1); // +1 for the time, the rest are channels

  for(let i = 0; i <= n_channels; i++){
    data[0][i] = 0; // init in 0
  }

  return data;
}
