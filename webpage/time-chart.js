"use strict"

class TimeChart {
  /**
   * Create an empty graph
   */
  constructor(config) {
    // Constants
    this.MIN_Y_AXIS_RANGE = 1;
    this.ZOOM_Y_PERCENTAGE = 0.1; // Zoom 10% of Y axis
    this.MOVE_Y_PERCENTAGE = 0.2; // Move 20% of Y axis
    this.UPDATE_Y_USE_ALL_DATA = true; // update y axis using all the data or just the incoming
    this.Y_PADDING = 0.05; // 5% of air up and down when updating the axis

    // Assure that the config object is correct
    if(!this._validateConstructorParams(config)) return;

    this.data = null;
    this.isReady = false;

    this.legendContainer = config.legendContainer;
    this.secondsIndicator = config.secondsIndicator;
    this.yMin = config.yMin;
    this.yMax = config.yMax;
    this.yMinHome = config.yMin;
    this.yMaxHome = config.yMax;

    this._initEmptyTimeChart(config.container, config.width, config.height, config.xTicks, config.yTicks);
    this._initAxisDeltas(config.dxZoom);
    this._initEmptyLegend();
    this._initEmptyTitle();
    this._addEventsXAxis(config.xZoomBtn[0], config.xZoomBtn[1]);
    this._addEventsYAxis(config.yZoomBtn, config.yMoveBtn, config.yHomeBtn);
    this._initAutoUpdateYCheckbox(config.yAutoUpdate);
    this._updateXAxis(config.secondsInScreen);

    // Select recalculateYAxisFunction
    this.recalculateYAxisFunction = (this.UPDATE_Y_USE_ALL_DATA) ?
      this._recalculateYAxisFull : this._recalculateYAxisIncoming;
    // NOTE: assigning functions like this is dangerous without bind,
    // although in this case should work
  }

  /** Validate params methods **/

  /**
   * Receive a configuration object, if a value is missing fill it with default
   */
  _validateConstructorParams(config){
    config.container = config.container || "#graph-container";
    config.legendContainer = config.legendContainer || "#legend-container";
    config.yAutoUpdate = config.yAutoUpdate || "#auto-update-y-axis";

    return true;
  }

  /**
   * Validate a config object given to the setGraphType method
   */
  _validateSelectParams(config){
    if(config.categories === undefined || config.categories.length === 0){
      console.log("ERROR: No categories found in configuration for time-chart");
      return false;
    }

    config.title = config.title || "TimeChart";

    for(let i=0; i < config.categories.length; i++){
      if (config.categories[i].color === undefined){
        config.categories[i].color = generateRandomColor();
      }
    }

    config.xAxisLabel = config.xAxisLabel || "Time (s)";
    config.yAxisLabel = config.yAxisLabel || "Value";

    return true;
  }




  /** Init empty stuff methods **/

  /**
   * Create an empty graph
   * @param {String} container HTML ID to locate the graph
   * @param {Number} width width of the graph in (pixels???)
   * @param {Number} height height of the graph in (pixels???)
   * @param {Number} xTicks
   * @param {Number} yTicks
   */
  _initEmptyTimeChart(containerID, width, height, xTicks, yTicks){
    this.margin = {top: 60, right: 10, bottom: 50, left: 60};
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
   * Init an empty legend container
   */
  _initEmptyLegend(){
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
  _initEmptyTitle(){
    const oldTitle = this.svg.select("graph-title");
    if (oldTitle) {
      oldTitle.remove();
    }

    this.titleSVG = this.svg.append("text")
      .attr("id", "graph-title")
      .attr("x", (this.width / 2))
      .attr("y", 0 - (this.margin.top / 2))
      .attr("text-anchor", "middle");
  }

  /**
   * Set amounts to update the axiss (dx and dy)
   */
  _initAxisDeltas(dxZoom){
    this.dxZoom = dxZoom;
    this._recalculateDyValues();
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
   * Connect event to toggle auto update y axis
   */
  _initAutoUpdateYCheckbox(checkboxSelector){
    const graph = this;
    $(checkboxSelector).click(function(){
      graph.autoUpdateYAxis = this.checked;
    });
    graph.autoUpdateYAxis = true; // DEFAULT: start enabled
  }



  /** Set graph type methods **/

  /**
   * Set the tickboxes and names for the legend, given the channel names
   */
  _setLegend(){
    $('#legend-form').empty(); // drop old controllers

    // Add checkbox for each channel
    let ticksID = {};
    this.channels.forEach((channel, index) => {
      ticksID[channel.name] = 'ch'.concat(index).concat('-tick');
      const inputTag = "<input id='".concat(ticksID[channel.name]).concat("' type='checkbox' checked/>");

      // Add square with color
      $('#legend-form').append(
        $('<svg>')
          .attr('class', 'legend-rect-container')
          .append(
            $('<rect>')
              .attr('class','legend-rect')
              .css('fill', channel.color)
            )
      );

      // Add input
      $('#legend-form').append(' ', inputTag, ' ', channel.name, '<br>');

      // Generate id-like tag
      ticksID[channel.name] = '#'.concat(ticksID[channel.name]);
    });

    // HACK: Refresh svg
    $("#legend-form").html($("#legend-form").html());


    // Show/hide events
    let graph = this; // this is needed to call nested functions
    this.channelNames.forEach((channelName) => {
      let tickID = ticksID[channelName];
      $(tickID).click(function() {
        graph.enablePath[channelName] = this.checked;
        graph.paths[channelName].style("opacity", this.checked ? 1 : 0);
      });
    });
  }

  /**
   * Set the title for the graph
   */
  _setTitle(title){
    this.titleSVG.text(title);
  }

  /**
   * Initialize the d3 functions that return the channels in the data
   */
  _setLineFunctions(){
    this.lines = {};
    const graph = this; // needed for nested functions

    this.channelNames.forEach((channelName) => {
      this.lines[channelName] = d3.svg.line()
        .x(function(d){ return graph.xRange(d.timestamp); })
        .y(function(d){ return graph.yRange(d[channelName]); });
    });

  }

  /**
   * Set the paths in the graph and an array of bools to show the lines
   * @param {Array} data
   * @param {Array} colorNames
   */
  _setChannels(){
    this.paths = {}; // Lines in svg
    this.enablePath = {}; // Bools to show each line

    this.channelNames.forEach((channelName) => {
      this.enablePath[channelName] = true; // DEFAULT: By default show line
      this.paths[channelName] = null;
    });

    d3.selectAll("path.line").remove(); // previous lines, if any

    this.channels.forEach((channel) => {
      this.paths[channel.name] = this.svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .attr("class", "line")
        .style("stroke", channel.color);
    });
  }

  /**
   * @source: http://bl.ocks.org/phoebebright/3061203
   */
  _setAxisLabels(xAxisLabel, yAxisLabel){
    // Delete previous labels
    d3.selectAll("text.label").remove();

    this.svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "middle")
      .attr("x", this.width/2)
      .attr("y", this.height + this.labelPadding.bottom)
      .text(xAxisLabel);

    this.svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "middle")
      .attr("x", -this.height/2)
      .attr("y", -this.labelPadding.left)
      .attr("transform", "rotate(-90)")
      .text(yAxisLabel);
  }



  /** Update methods **/

  /** Recalculate dyZoom value based on the current window size **/
  _recalculateDyValues(){
    const windowSize = this.yMax - this.yMin;
    this.dyZoom = windowSize * this.ZOOM_Y_PERCENTAGE;
    this.dyMove = windowSize * this.MOVE_Y_PERCENTAGE;
  }

  /** AutoUpdateYAxis using only new data **/
  _recalculateYAxisIncoming(newData){
    // NOTE: Something like this could be done (just with the newData), but instead is better to
    // let yMin = d3.min(this.data, function(d) { return Math.min(...d.slice(1)); });
    // let yMax = d3.max(this.data, function(d) { return Math.max(...d.slice(1)); });

    let yMin = newData[this.channels[0].name]; // HACKy way
    let yMax = yMin;
    this.channelNames.forEach((channelName) => {
      if (!this.enablePath[channelName]) {
        return;
      }

      let value = newData[channelName];

      // Update min and max
      if(value > yMax){
        yMax = value;
      } else if(value < yMin){
        yMin = value;
      }
    });

    return { yMin, yMax };
  }

  /** AutoUpdateYAxis using all the data **/
  _recalculateYAxisFull(){
    let yMin = this.data[0][this.channels[0].name]; // HACKy way
    let yMax = yMin;
    for(let i_time = 0; i_time < this.data.length; i_time++) {
      this.channelNames.forEach((channelName) => {
        if (!this.enablePath[channelName]) {
          return;
        }

        let value = this.data[i_time][channelName];

        // Update min and max
        if(value > yMax){
          yMax = value;
        } else if(value < yMin){
          yMin = value;
        }
      });
    }

    return { yMin, yMax };
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

    this._recalculateDyValues();
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
   * Parse incoming data
   * Input example: [{'name': 'concentration', 'value': 3}, ...]
   * Output example: { 'concentration': 3, ... }
   * One of the channels should be 'timestamp'
   */
  _parseData(newData){
    const parsedData = newData.reduce((accumulated, channel) => {
      accumulated[channel.name] = parseFloat(channel.value);
      return accumulated;
    }, {});

    if (parsedData.timestamp < 0) {
      console.log("ERROR: received negative time: ", parsedData.timestamp);
      return null;
    }

    // REVIEW: Fill with 0s is needed?
    // IDEA: parsedData starts as 0s in each [channel.name] available (according to configuration)
    // while(arr.length < this.nChannels + 1){ // Fill with 0s if received less channels
    //   arr.push(0.0);
    // }

    return parsedData;
  }



  /** Public methods **/

  /**
   * Initialize the data as an empty array of objects
   */
  initEmptyData(){
    this.data = new Array();

    // Start with a point at 0, 0 // REVIEW: is this needed?
    // if (!this.isReady) return;
    // const zeroPoint = this.channelNames.reduce((accumulated, channelName) => {
    //   accumulated[channelName] = 0;
    //   return accumulated;
    // }, {});
    // zeroPoint.timestamp = 0;
    //
    // this.data.push(zeroPoint);
  }

  /**
   * Select the type of the graph
   * Config example:
   * {
   *    "categories": [
   *      {"name": "concentration", "color": "red"},
   *      {"name": "relaxation", "color": "blue"}
   *    ],
   *    "yAxisLabel": "Measure of state", "title": "State of mind"
   * }
   */
  setGraphType(config){
    if(!this._validateSelectParams(config)){
      console.log("ERROR: Validation of config params failed");
      return;
    }

    this.channels = config.categories.slice();
    this.channelNames = this.channels.map((channel) => channel.name); // convenient sometimes

    this._setChannels();
    this._setLineFunctions();
    this._setLegend();
    this._setTitle(config.title);
    this._setAxisLabels(config.xAxisLabel, config.yAxisLabel);

    this.isReady = true;
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

    let yMinNew = this.yMin + signMin * this.dyZoom;
    let yMaxNew = this.yMax + signMax * this.dyZoom;

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
    this._updateXAxis(this.secondsInScreen + sign * this.dxZoom);
  }

  /**
   * Update all the lines in the graph
   * @param {Boolean} shift
   */
  update(newData, shift=true) {
    let parsedData = this._parseData(newData);

    if(!parsedData){
      console.log("ERROR: can't parse data");
      return;
    }

    this.data.push(parsedData);

    this.channelNames.forEach((channelName) => {
      if(!this.enablePath[channelName]) return;

      this.paths[channelName].attr("d", this.lines[channelName](this.data))
        .attr("transform", null)
        .transition()
        .duration(1000)
        .ease("linear");
    });

    // Update Y Axis
    // this.autoUpdateYAxis = false;
    if(this.autoUpdateYAxis){
      let { yMin, yMax } = this.recalculateYAxisFunction(newData);

      // Give some air (this is a bit ugly)
      let windowSize = this.yMax - this.yMin;
      yMin -= windowSize * this.Y_PADDING;
      yMax += windowSize * this.Y_PADDING;

      this._updateYAxis(yMin, yMax);
    }

    // Update X Axis
    let xRange = d3.extent(this.data, function(d) { return d.timestamp; });
    // if(xRange[1] - xRange[0] < this.secondsInScreen){ xRange[1] = xRange[0] + this.secondsInScreen; } // Que el xRange minimo sea secondsInScreen
    this.xRange.domain(xRange);

    this.svg.select(".x.axis").call(this.xAxis);

    if(shift){
      while(this.data[this.data.length - 1].timestamp - this.data[0].timestamp > this.secondsInScreen){
        this.data.shift();
      }
    }
  }

}
