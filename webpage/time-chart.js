"use strict"

class TimeChart {
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
    this.yMin = config.yMin;
    this.yMax = config.yMax;
    this.yMinHome = config.yMin;
    this.yMaxHome = config.yMax;
    this._setCheckboxAutoUpdateY(config.yAutoUpdate);
    this._updateXAxis(config.secondsInScreen);

    this._initEmptyTimeChart(config.container, config.width, config.height, config.xTicks, config.yTicks);
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
    config.container = config.container || "#graph-container";
    config.legendContainer = config.legendContainer || "#legend-container";
    config.yAutoUpdate = config.yAutoUpdate || "#auto-update-y-axis";

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

    config.title = config.title || "TimeChart";
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
  _initEmptyTimeChart(containerID, width, height, xTicks, yTicks){
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
    const oldTitle = this.svg.select("graph-title");
    if (oldTitle) {
      oldTitle.remove();
    }

    this.title = this.svg.append("text")
        .attr("id", "graph-title")
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
    this.enablePath = new Array(this.nChannels); // Bools to show each line

    for(let i = 0; i < this.nChannels; i++){
      this.enablePath[i] = true; // DEFAULT: By default show line
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
        graph.enablePath[i] = this.checked;
        graph.paths[i].style("opacity", this.checked ? 1 : 0);
      });
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
   * Connect event to toggle auto update y axis
   */
  _setCheckboxAutoUpdateY(checkboxSelector){
    const graph = this;
    $(checkboxSelector).click( function(){
      graph.autoUpdateYAxis = this.checked;
    });
    graph.autoUpdateYAxis = true; // DEFAULT: start enabled
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
    this._updateXAxis(this.secondsInScreen + sign * this.dxZoom);
  }

  /**
   * Update all the lines in the graph
   * @param {Boolean} shift
   */
  update(newData, shift=true) {
    this.data.push(newData);

    for(let channel = 0; channel < this.nChannels; channel++){
      if(!this.enablePath[channel]) continue;

      this.paths[channel].attr("d", this.lines[channel](this.data))
        .attr("transform", null)
        .transition()
        .duration(1000)
        .ease("linear");
    }

    // Update Y Axis
    // this.autoUpdateYAxis = false;
    if(this.autoUpdateYAxis){
      // NOTE: Something like this could be done (just with the newData), but instead is better to
      // let yMin = d3.min(this.data, function(d) { return Math.min(...d.slice(1)); });
      // let yMax = d3.max(this.data, function(d) { return Math.max(...d.slice(1)); });

      let yMin = this.yMin;
      let yMax = this.yMax;
      for(let channel = 1; channel < this.nChannels + 1; channel++){
        let value = newData[channel];

        // Update min and max
        if(value > yMax){
          yMax = value;
        } else if(value < yMin){
          yMin = value;
        }
      }
      // NOTE: instead of iterating only over the newData, it could be searched on all the data
      // for(let i_time = 0; i_time < this.data.length; i_time ++) { let value = this.data[i_time][channel]; }

      // TODO: decide when to update and when not to (in base on the values)
      this._updateYAxis(yMin, yMax);
    }

    // Update X Axis
    let xRange = d3.extent(this.data, function(d) { return d[0]; });
    // if(xRange[1] - xRange[0] < this.secondsInScreen){ xRange[1] = xRange[0] + this.secondsInScreen; } // Que el xRange minimo sea secondsInScreen
    this.xRange.domain(xRange);

    this.svg.select(".x.axis").call(this.xAxis);

    if(shift){
      while(this.data[this.data.length - 1][0] - this.data[0][0] > this.secondsInScreen){
        this.data.shift();
      }
    }
  }

}
