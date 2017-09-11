"use strict"

class Graph {
  /**
   * Create an empty graph
   */
  constructor(config) {
    // Assure that the config object is correct
    if(!this._validateConstructorParams(config)) return;

    this.data = null;
    this.isSet = false;

    this.legend_container = config.legend_container;
    this.secs_indicator = config.sec_x;
    this._updateXAxis(config.n_secs);
    this.y_min = config.y_min;
    this.y_max = config.y_max;
    this.y_min_home = config.y_min;
    this.y_max_home = config.y_max;

    this._initEmptyGraph(config.container, config.width, config.height, config.xTicks, config.yTicks);
    this._initAxisParams(config.dx_zoom, config.dy_zoom, config.dy_move);
    this._addEventsXAxis(config.x_zoom_btn[0], config.x_zoom_btn[1]);
    this._addEventsYAxis(config.y_zoom_btn, config.y_move_btn, config.y_home_btn);
    this._initLegend();
    this._initTitle();
  }

  /**
   * Receive a configuration object, if a value is missing fill it with default
   */
  _validateConstructorParams(config){
    if(config.container === undefined){
      console.log("ERROR: Missing graph container");
      return false;
    }
    if(config.legend_container === undefined){
      console.log("ERROR: Missing legend container")
      return false;
    }
    return true;
  }

  /**
   * Validate a config object given to the selectType method
   */
  _validateSelectParams(config){
    if(config.nChannels === undefined){
      console.log("ERROR: Declaring a graph without the number of channels");
      return false;
    }

    if(config.channelNames === undefined){
      config.channelNames = new Array(config.nChannels);

      for(let i = 0; i < config.nChannels; i++){
        config.channelNames[i] = "ch".concat(i);
      }
    }

    config.title = config.title || "Graph";
    config.colors = config.colors || generateRandomColors(config.nChannels);

    config.xAxisLabel = config.xAxisLabel || "Time (s)";
    config.yAxisLabel = config.yAxisLabel || "Value";

    return true;
  }

  /**
   * Create an empty graph
   * @param {String} container HTML ID to locate the graph
   * @param {Number} width width of the graph in (pixels???)
   * @param {Number} height height of the graph in (pixels???)
   * @param {Number} xTicks
   * @param {Number} yTicks
   */
  _initEmptyGraph(containerID, width, height, xTicks, yTicks){
    this.margin = {top: 40, right: 10, bottom: 50, left: 60};
    this.labelPadding = {bottom: 40, left: 40};
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
  }

  /**
   * Set amounts to update the axis
   */
  _initAxisParams(dx_zoom, dy_zoom, dy_move){
    this.dx_zoom = dx_zoom;
    this.dy_zoom = dy_zoom;
    this.dy_move = dy_move;
  }

  /**
   * Init an empty legend container
   */
  _initLegend(){
    // Create panel for the legend
    $(this.legend_container).append(
      $('<div>', {
        'id':'legend-panel',
        'class':'panel panel-primary',
        // 'html':'<span>For HTML</span>',
      })
    );

    // Add body and legend
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

  }

  /**
   * Init an empty title
   */
  _initTitle(){
    this.title = this.svg.append("text")
        .attr("id", "graph_title")
        .attr("x", (this.width / 2))
        .attr("y", 0 - (this.margin.top / 2))
        .attr("text-anchor", "middle");
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
   * Initialize the d3 functions that return the channels in the data
   */
  _setLineFunctions(){
    this.lines = new Array(this.nChannels);

    for(let i = 0; i < this.nChannels; i++){
      this.lines[i] = null; // HACK: start as null so actual assign below wont throw error
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
   * @param {Array} colorNames
   */
  _initChannels(colorNames){
    this.colorNames = colorNames.slice(); // copy by value

    this.paths = new Array(this.nChannels); // Lines in svg
    this.plot_bools = new Array(this.nChannels); // Bools to show each line

    for(let i = 0; i < this.nChannels; i++){
      this.plot_bools[i] = true; // DEFAULT: By default show line
      this.paths[i] = null;
    }

    d3.selectAll("path.line").remove();

    this.paths.forEach((p, i) => {
      this.paths[i] = this.svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .attr("class", "line")
        .style("stroke", colorNames[i]);
    });
  }

  /**
   * Set the tickboxes and names for the legend, given the channel names
   */
  _setLegend(channelNames){
    let graph = this; // NOTE: this is needed because there are calls to nested functions

    $("#legend-form").empty(); // NOTE: drop old controllers

    // Add checkbox for each channel
    let ticksID = new Array(this.nChannels);
    for(let i = 0; i < this.nChannels; i++){
      ticksID[i] = "ch".concat(String(i)).concat("-tick");
      const inputTag = "<input id='".concat(ticksID[i]).concat("' type='checkbox' checked/>");

      // Add square with color
      $("#legend-form").append(
        $('<svg>')
          .attr('class', 'legend-rect-container')
          .append(
            $('<rect>')
              .attr('class','legend-rect')
              .css("fill", graph.colorNames[i])
            )
      );

      // Add input
      $("#legend-form").append(' ', inputTag, ' ', channelNames[i], '<br>');

      ticksID[i] = "#".concat(ticksID[i]); // Generate id-like tag
    }

    // HACK: Refresh svg
    $("#legend-form").html($("#legend-form").html());

    // Show/hide events
    ticksID.forEach(function(t, i){
      $(t).click( function(){
        graph.plot_bools[i] = this.checked;
        graph.paths[i].style("opacity", this.checked ? 1 : 0);
      });
    });
  }

  /**
   * @source: http://bl.ocks.org/phoebebright/3061203
   */
  _setAxisLabels(xAxisLabel, yAxisLabel){
    this.svg.append("text")
      // .attr("class", "y label")
      .attr("text-anchor", "middle")
      .attr("x", this.width/2)
      .attr("y", this.height + this.labelPadding.bottom)
      .text(xAxisLabel);

    this.svg.append("text")
      // .attr("class", "y label")
      .attr("text-anchor", "middle")
      .attr("x", -this.height/2)
      .attr("y", -this.labelPadding.left)
      .attr("transform", "rotate(-90)")
      .text(yAxisLabel);
  }

  /**
   * Set the title for the graph
   */
  _setTitle(title){
    this.title.text(title);
  }

  /**
   * Update the y axis
   */
  _updateYAxis(y1, y2){
    if(y1 >= y2) return;

    this.y_min = y1;
    this.y_max = y2;
    this.y_range.domain([y1, y2]);
    this.svg.select(".y.axis").call(this.y_axis); // update svg
  }

  /**
   *
   */
  _updateXAxis(seconds){
    if(seconds <= 1) return;

    this.n_secs = seconds;
    $(this.secs_indicator).text(this.n_secs.toFixed(0));
  }

  /**
   * Select the type of the graph
   */
  selectType(config){
    this._validateSelectParams(config);
    this.nChannels = config.nChannels;
    this._initChannels(config.colors);
    this._setLegend(config.channelNames);
    this._setLineFunctions();
    this._setTitle(config.title);
    this._setAxisLabels(config.xAxisLabel, config.yAxisLabel);

    this.isSet = true;
  }

  /**
   * Initialize the data as an empty array. shape: (n_points, nChannels + 1)
   */
  initEmptyData(nChannels){
    this.data = new Array(1);
    this.data[0] = new Array(this.nChannels + 1);

    for(let i = 0; i <= this.nChannels; i++){
      this.data[0][i] = 0;
    }
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
    const sign = up ? 1 : -1;

    let y_min_new = this.y_min + sign*this.dy_move;
    let y_max_new = this.y_max + sign*this.dy_move;

    this._updateYAxis(y_min_new, y_max_new);
  }

  /**
   *
   * @param {bool} increase increase or decrease the amount of seconds shown
   */
  zoomXAxis(increase){
    const sign = increase ? 1 : -1;
    this._updateXAxis(this.n_secs + sign*this.dx_zoom);
  }

  /**
   * Update all the lines in the graph
   * @param {Boolean} shift
   */
  update(new_data, shift=true) {
    this.data.push(new_data);
    for(let i = 0; i < this.nChannels; i++){
      if(!this.plot_bools[i]) continue;

      this.paths[i].attr("d", this.lines[i](this.data))
        .attr("transform", null)
        .transition()
        .duration(1000)
        .ease("linear");
    }

    let range = d3.extent(this.data, function(d) { return d[0]; });
    // if(range[0] + this.n_secs > range[1]){ range[1] = range[0] + this.n_secs; } // Que el range minimo sea n_secs
    this.x_range.domain(range);

    this.svg.select(".x.axis").call(this.x_axis);

    if(shift){
      while(this.data[this.data.length-1][0] - this.data[0][0] > this.n_secs){
        this.data.shift();
      }
    }
  }

}

const StatusEnum = {OFF: 0, CONNECTING: 1, CONNECTED: 2, DISCONNECTED: 3};
class Connection{
  /**
   * Constructor, receives an object with the following attributes
   * @param {String} url url to connect to
   * @param {String} statusText HTML id of the text of the connection message
   * @param {String} statusIcon HTML id of the icon of the connection message
   * @param {function} recvMsg Function to connect to the 'message' event
   * @param {function} recvConfig Function to connect to the 'config' event
   */
  constructor(config){
    this.url = config.url;
    this.stream = null;

    this.statusText = config.statusText;
    this.statusIcon = config.statusIcon;
    this._setStatus(StatusEnum.OFF);

    this.recvMsg = config.recvMsg;
    this.recvConfig = config.recvConfig;
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

    $(this.statusText).text(text);
    $(this.statusText).css("color", color);
    $(this.statusIcon).attr("class", "glyphicon glyphicon-".concat(icon));
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

    console.log("Connection closed with the server");
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

    this.stream.addEventListener('open', (e) => {
      this._setStatus(StatusEnum.CONNECTED);
      console.log("Connected to the server");
    }, false);

    this.stream.addEventListener('config', (e) => {
      this.recvConfig(e);
    }, false);

    this.stream.addEventListener('message', (e) => {
      this.recvMsg(e);
    }, false);

    this.stream.addEventListener('error', (e) => {
      // TODO: send alert to the user
      if(this._isConnecting()) console.log("Can't connect to the server");
      else console.log("Error in the connection with the server");

      this.close();
    }, false);

  }

}

/**
 * Receive a stream of data from a muse server and plots it
 */
$(document).ready( function() {
  let graphConfig = null;

  const eegGraphConfig = {
    nChannels: 5,
    channelNames: ["TP9", "AF7", "AF8", "TP10", "Right Aux"],
    colors: ["black", "red", "blue", "green", "cyan"],
    title: 'EEG electrodes',
    yAxisLabel: 'Raw signal (mV)',
  }

  const wavesGraphConfig = {
    nChannels: 5,
    channelNames: ["delta", "theta", "alpha", "beta", "gamma"],
    colors: ["blue", "orange", "red", "green", "magenta"],
    title: 'Waves',
    yAxisLabel: 'Power (dB)',
  }

  // const debugGraphConfig = {
  //   nChannels: 5,
  //   channelNames: ["delta", "theta", "alpha", "beta", "gamma"],
  //   colors: ["blue", "orange", "red", "green", "magenta"],
  //   title: 'Waves',
  //   yAxisLabel: 'Power (dB)',
  // }

  const graph = new Graph({
    container: "#graph_container",
    legend_container: '#legend_container',

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

  const stream = new Connection({
      url: "http://localhost:8889/data/muse",
      statusText: "#status-text",
      statusIcon: "#status-icon",
      recvMsg: function(e){
                if(!graph.isSet) return;

                let arr = e.data.split(",").map(parseFloat);

                if(arr[0] < 0) return; // Ignore negative time

                // REVIEW: check arr.length == n channels
                while(arr.length < graphConfig.nChannels + 1){ // Fill with 0s if received less channels
                  arr.push(0.0);
                }

                graph.update(arr);
              },
      recvConfig: function(e){
                    switch(e.data) {
                      case "eeg":
                        graphConfig = eegGraphConfig;
                        break;

                      case "waves":
                        graphConfig = wavesGraphConfig;
                        break;

                      default:
                        console.log("Type of graph received from server not recognized: ", e.data);
                        return;
                    }
                    graph.selectType(graphConfig);
                    graph.initEmptyData();
                  },
    });

  $("#btn-start-conn").click( function(){
    stream.start();
  });

  $("#btn-close-conn").click( function(){
    if(!graph.isSet) return;
    stream.close();
    graph.initEmptyData();
  });

  stream.start();

  console.log("All set");
});

/**
 * Return an array of randomly generated colors
 * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
 */
function generateRandomColors(nColors){
  function genRandColor(){
    let letters = '0123456789ABCDEF';
    let color = '#';

    for (let i = 0; i < 6; i++){
      color += letters[Math.floor(Math.random() * 16)];
    }

    return color;
  }
  let colorArr = new Array(nColors);

  for(let i = 0; i < nColors; i++){
    colorArr[i] = genRandColor();
  }

  return colorArr;
}
