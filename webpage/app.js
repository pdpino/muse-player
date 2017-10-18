"use strict"

class Graph {
  /**
   * Create an empty graph
   */
  constructor(config) {
    // Some constants
    this.MIN_Y_AXIS_RANGE = 1;

    // Assure that the config object is correct
    if(!this._validateConstructorParams(config)) return;

    this.data = null;
    this.isReady = false;

    this.legendContainer = config.legendContainer;
    this.secondsIndicator = config.secondsIndicator;
    this._updateXAxis(config.secondsInScreen);
    this.yMin = config.yMin;
    this.yMax = config.yMax;
    this.yMinHome = config.yMin;
    this.yMaxHome = config.yMax;

    this._initEmptyGraph(config.container, config.width, config.height, config.xTicks, config.yTicks);
    this._initAxisParams(config.dxZoom, config.dyZoom, config.dyMove);
    this._addEventsXAxis(config.xZoomBtn[0], config.xZoomBtn[1]);
    this._addEventsYAxis(config.yZoomBtn, config.yMoveBtn, config.yHomeBtn);
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
    if(config.legendContainer === undefined){
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

    this.xRange = d3.scale.linear().domain([0, this.secondsInScreen]).range([0, this.width]);
    this.yRange = d3.scale.linear().domain([this.yMin, this.yMax]).range([this.height, 0]);

    this.xAxis = d3.svg.axis().scale(this.xRange).orient("bottom").ticks(xTicks);
    this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.height + ")")
        .call(this.xAxis);

    this.yAxis = d3.svg.axis().scale(this.yRange).orient("left").ticks(yTicks);
    this.svg.append("g")
        .attr("class", "y axis")
        .call(this.yAxis);
  }

  /**
   * Set amounts to update the axis
   */
  _initAxisParams(dxZoom, dyZoom, dyMove){
    this.dxZoom = dxZoom;
    this.dyZoom = dyZoom;
    this.dyMove = dyMove;
  }

  /**
   * Init an empty legend container
   */
  _initLegend(){
    // Create panel for the legend
    $(this.legendContainer).append(
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
  _addEventsXAxis(btnDecrease, btnIncrease){
    $(btnDecrease).click(() => { this.zoomXAxis(false); });
    $(btnIncrease).click(() => { this.zoomXAxis(true); });
  }

  /**
   * Connect the y axis buttons with the corresponding events
   */
  _addEventsYAxis(btnsZoom, btnsMove, btnHome){
    $(btnsZoom[0]).click(() => { this.zoomYAxis(false); });
    $(btnsZoom[1]).click(() => { this.zoomYAxis(true); });
    $(btnsMove[0]).click(() => { this.moveYAxis(false); });
    $(btnsMove[1]).click(() => { this.moveYAxis(true); });
    $(btnHome).click(() => { this.homeYAxis(); });
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
        .x(function(d){ return graph.xRange(d[0]); })
        .y(function(d){ return graph.yRange(d[i + 1]); });
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
    // TODO: delete previous labels

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
  _updateYAxis(yMin, yMax){
    if(yMin >= yMax) return;

    this.yMin = yMin;
    this.yMax = yMax;
    this.yRange.domain([yMin, yMax]);
    this.svg.select(".y.axis").call(this.yAxis); // update svg
  }

  /**
   *
   */
  _updateXAxis(seconds){
    if(seconds <= 1) return;

    this.secondsInScreen = seconds;
    $(this.secondsIndicator).text(this.secondsInScreen.toFixed(0));
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

    this.isReady = true;
  }

  /**
   * Initialize the data as an empty array. shape: (n_points, nChannels + 1)
   */
  initEmptyData(nChannels){
    this.data = new Array(1);
    this.data[0] = new Array(this.nChannels + 1);

    for(let channel = 0; channel <= this.nChannels; channel++){
      this.data[0][channel] = 0;
    }
  }

  /**
   * Zoom the y axis
   * @param {bool} out Direction of the zoom
   */
  zoomYAxis(out){
    let signMin;
    let signMax;

    if(out){
      signMin = -1; // decrease yMin
      signMax = 1; // increase yMax
    }
    else{
      signMin = 1; // increase yMin
      signMax = -1; // decrease yMax
    }

    let yMinNew = this.yMin + signMin*this.dyZoom;
    let yMaxNew = this.yMax + signMax*this.dyZoom;

    // Safe when zooming in
    if(!out){
      if(yMaxNew - yMinNew < this.MIN_Y_AXIS_RANGE){
        return;
      }
    }

    this._updateYAxis(yMinNew, yMaxNew);
  };

  /**
   * Set the y axis to the original values
   */
  homeYAxis(){
    this._updateYAxis(this.yMinHome, this.yMaxHome);
  }

  /**
   * Move the y axis range
   * @param {bool} up Direction of the move
   */
  moveYAxis(up){
    const sign = up ? 1 : -1;

    let y_min_new = this.yMin + sign*this.dyMove;
    let y_max_new = this.yMax + sign*this.dyMove;

    this._updateYAxis(y_min_new, y_max_new);
  }

  /**
   *
   * @param {bool} increase increase or decrease the amount of seconds shown
   */
  zoomXAxis(increase){
    const sign = increase ? 1 : -1;
    this._updateXAxis(this.secondsInScreen + sign*this.dxZoom);
  }

  /**
   * Update all the lines in the graph
   * @param {Boolean} shift
   */
  update(newData, shift=true) {
    this.data.push(newData);

    for(let channel = 0; channel < this.nChannels; channel++){
      if(!this.plot_bools[channel])
        continue;

      this.paths[channel].attr("d", this.lines[channel](this.data))
        .attr("transform", null)
        .transition()
        .duration(1000)
        .ease("linear");
    }

    let range = d3.extent(this.data, function(d) { return d[0]; });
    // if(range[0] + this.secondsInScreen > range[1]){ range[1] = range[0] + this.secondsInScreen; } // Que el range minimo sea secondsInScreen
    this.xRange.domain(range);

    this.svg.select(".x.axis").call(this.xAxis);

    if(shift){
      while(this.data[this.data.length-1][0] - this.data[0][0] > this.secondsInScreen){
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

  const feelRelaxConcGraphConfig = {
    nChannels: 2,
    channelNames: ["relaxation", "concentration"],
    colors: ["blue", "red"],
    title: 'State of mind',
    yAxisLabel: 'Power (dB)',
  }

  const feelValAroGraphConfig = {
    nChannels: 2,
    channelNames: ["arousal", "valence"],
    colors: ["blue", "red"],
    title: 'State of mind',
    yAxisLabel: 'Power (dB)',
  }

  const graph = new Graph({
    container: "#graph_container",
    legendContainer: '#legend_container',

    // FIXME: que clase cree estos
    xZoomBtn: ["#btn-zoomXdec", "#btn-zoomXinc"],
    yZoomBtn: ["#btn-zoomYin", "#btn-zoomYout"],
    yMoveBtn: ["#btn-moveYdown", "#btn-moveYup"],
    yHomeBtn: "#btn-homeY",
    secondsIndicator: "#segX",

    width: 700,
    height: 400,
    yMin: -100,
    yMax: 100,
    xTicks: 5,
    yTicks: 5,
    secondsInScreen: 5,
    dxZoom: 1, // FIXME: que clase calcule esto y vaya cambiando
    dyZoom: 5,
    dyMove: 50
    });

  const recvMsg = function(e){
    if(!graph.isReady) return;

    let arr = e.data.split(",").map(parseFloat);

    if(arr[0] < 0) return; // Ignore negative time

    // REVIEW: check arr.length == n channels
    while(arr.length < graphConfig.nChannels + 1){ // Fill with 0s if received less channels
      arr.push(0.0);
    }

    graph.update(arr);
  }

  const recvConfig = function (e){
      switch(e.data) {
        case "eeg":
          graphConfig = eegGraphConfig;
          break;

        case "waves":
          graphConfig = wavesGraphConfig;
          break;

        case "feel":
          graphConfig = feelRelaxConcGraphConfig;
          break;

        case "feelValAro":
          graphConfig = feelValAroGraphConfig;
          break;

        default:
          console.log("Type of graph received from server not recognized: ", e.data);
          return;
      }
      graph.selectType(graphConfig);
      graph.initEmptyData();
    }

  const stream = new Connection({
      url: "http://localhost:8889/data/muse",
      statusText: "#status-text",
      statusIcon: "#status-icon",
      recvMsg,
      recvConfig,
    });

  $("#btn-start-conn").click( function(){
    stream.start();
  });

  $("#btn-close-conn").click( function(){
    if(!graph.isReady) return;
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

  for(let color = 0; color < nColors; color++){
    colorArr[color] = genRandColor();
  }

  return colorArr;
}
