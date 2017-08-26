"use strict"

class Graph {
  /**
   * Constructor
   */
  constructor(config) {
    // Assure that the config object is correct
    if(!this._validateDefaultValues(config)) return;

    this.n_channels = Number(config.n_channels); // HACK: copy by value
    this.secs_indicator = String(config.sec_x);
    this._updateXAxis(config.n_secs);
    this.y_min = Number(config.y_min);
    this.y_max = Number(config.y_max);
    this.y_min_home = Number(config.y_min);
    this.y_max_home = Number(config.y_max);

    this._initEmptyGraph(config.container, config.width, config.height, config.title, config.xTicks, config.yTicks);

    this._initLines();
    this._initChannels(config.data, config.colors);
    this._initAxisParams(config.dx_zoom, config.dy_zoom, config.dy_move);
    this._initLegend(config.legend_container, config.ch_names);
    this._addEventsXAxis(config.x_zoom_btn[0], config.x_zoom_btn[1]);
    this._addEventsYAxis(config.y_zoom_btn, config.y_move_btn, config.y_home_btn);
  }

  /**
   * Receive a configuration object, if a value is missing fill it with default
   */
  _validateDefaultValues(config){
    if(config.container === undefined){
      console.log("ERROR: Missing graph container");
      return false;
    }

    if(config.n_channels === undefined){
      console.log("ERROR: Declaring a graph without the number of channels");
      return false;
    }

    if(config.ch_names === undefined){
      config.ch_names = new Array(config.n_channels);

      for(let i = 0; i < config.n_channels; i++){
        config.ch_names[i] = "ch".concat(i);
      }
    }

    config.title = config.title || "Graph";

    if(config.colors === undefined){
      config.colors = new Array(config.n_channels);

      for(let i = 0; i < config.n_channels; i++){
        config.colors[i] = generateRandomColor();
      }
    }

    return true;
  }

  /**
   * Create an empty graph
   * @param {String} container HTML ID to locate the graph
   * @param {Number} width width of the graph in (pixels???)
   * @param {Number} height height of the graph in (pixels???)
   * @param {String} title
   * @param {Number} xTicks
   * @param {Number} yTicks
   */
  _initEmptyGraph(containerID, width, height, title, xTicks, yTicks){
    this.margin = {top: 40, right: 10, bottom: 30, left: 60};
    this.width = width - this.margin.left - this.margin.right;
    this.height = height - this.margin.top - this.margin.bottom;

    this.svg = d3.select(containerID).append("svg")
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

    // Clip to grab the data that comes off the left side
    this.svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", this.width)
        .attr("height", this.height);

    this.x_range = d3.scale.linear().domain([0, this.n_secs]).range([0, this.width]);
    this.y_range = d3.scale.linear().domain([this.y_min, this.y_max]).range([this.height, 0]);

    this.x_axis = d3.svg.axis().scale(this.x_range).orient("bottom").ticks(xTicks);
    this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.height + ")")
        .call(this.x_axis);

    this.y_axis = d3.svg.axis().scale(this.y_range).orient("left").ticks(yTicks);
    this.svg.append("g")
        .attr("class", "y axis")
        .call(this.y_axis);

    this.svg.append("text")
        .attr("id", "graph_title")
        .attr("x", (this.width / 2))
        .attr("y", 0 - (this.margin.top / 2))
        .attr("text-anchor", "middle")
        .text(title);
  }

  /**
   * Initialize the d3 functions that return the channels in the data
   */
  _initLines(){
    this.lines = new Array(this.n_channels);

    for(let i=0;i<this.n_channels;i++){
      this.lines[i] = null; //HACK: start as null so actual assign below wont throw error
    }

    let graph = this; // NOTE: using arrow functions to call graphs won't work, because of nested functions
    this.lines.forEach((l, i) => {
      this.lines[i] = d3.svg.line()
        .x(function(d){ return graph.x_range(d[0]); })
        .y(function(d){ return graph.y_range(d[i + 1]); });
    });


  }

  /**
   * Init the paths in the graph and an array of bools to show the lines
   * @param {Array} data
   * @param {Array} colors
   */
  _initChannels(data, colorNames){
    this.colorNames = colorNames; // REVIEW: copy?

    this.paths = new Array(this.n_channels); // Lines in svg
    this.plot_bools = new Array(this.n_channels); // Bools to show each line

    for(let i = 0; i < this.n_channels; i++){
      this.plot_bools[i] = true; // DEFAULT: By default show line
      this.paths[i] = null;
    }

    this.paths.forEach((p, i) => {
      this.paths[i] = this.svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .attr("class", "line")
        .style("stroke", colorNames[i])
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
              .css("fill", graph.colorNames[i]) // Pintar del color
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
    //   d3.select(ids_rect[i]).style("fill", graph.colorNames[i]);
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
   * Constructor, receives an object with the following attributes
   * @param {String} url url to connect to
   * @param {String} status_text HTML id of the text of the connection message
   * @param {String} status_icon HTML id of the icon of the connection message
   * @param {function} recv_msg Function to connect to the 'onmessage' event
   */
  constructor(config){
    this.name = config.name;
    this.url = config.url;
    this.stream = null;

    this.status_text = config.status_text;
    this.status_icon = config.status_icon;
    this._setStatus(StatusEnum.OFF);

    this.recv_msg = config.recv_msg;
  }

  _isConnecting(){
    return this.status === StatusEnum.CONNECTING;
  }

  _isDisconnected(){
    return this.status === StatusEnum.OFF || this.status === StatusEnum.DISCONNECTED;
  }

  /**
   * Set the status of the connection. Updates the screen with an icon and a text
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
        icon = "hourglass"; // Sand clock
        color = "orange";
        break;
      case StatusEnum.CONNECTED:
        text = "Connected";
        icon = "ok"; // OK ticket
        color = "green";
        break;
      case StatusEnum.DISCONNECTED:
        text = "Disconnected";
        icon = "remove"; // X
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
 * Receive a stream of data from a muse server and plots it
 */
$(document).ready( function() {
  // Parameters
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

  // Start
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
    xTicks: 5,
    yTicks: 5,
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
 * @param {Number} n_channels Amount of channels
 * @return {Array} shape (n_points, n_channels + 1); starts with 1 0-filled item
 */
function initEmptyData(n_channels){
  let emptyData = new Array(1);
  emptyData[0] = new Array(n_channels + 1);

  for(let i = 0; i <= n_channels; i++){
    emptyData[0][i] = 0;
  }

  return emptyData;
}


/**
 * Return a random color
 * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
 */
function generateRandomColor(){
  let letters = '0123456789ABCDEF';
  let color = '#';

  for (let i = 0; i < 6; i++){
      color += letters[Math.floor(Math.random() * 16)];
  }

  return color;
}
