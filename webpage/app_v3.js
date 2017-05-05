// Version 3: usa d3.v3 para plotear
//TODO

$(document).ready( function() {

  // Set the dimensions of the canvas / graph
  var margin = {top: 30, right: 20, bottom: 30, left: 50},
      width = 600 - margin.left - margin.right,
      height = 270 - margin.top - margin.bottom;

  // Parse the time to seconds
  // var parseTime = d3.time.format("%S").parse;

  // Set the ranges of the axis
  // var x = d3.time.scale().range([0, width]);
  var x = d3.scale.linear().range([0, width]);
  var y = d3.scale.linear().range([height, 0]);

  // Define the axes
  var xAxis = d3.svg.axis().scale(x)
      .orient("bottom").ticks(10);

  var yAxis = d3.svg.axis().scale(y)
      .orient("left").ticks(5);

  // Define the line
  var valueAF7 = d3.svg.line()
      .interpolate("none") //smooth the line //see d3 tips and tricks p55 for more options
      .x(function(d) { return x(d.timestamps); })
      .y(function(d) { return y(d.AF7); });

  // // Define the line 2
  // var valueAF8 = d3.svg.line()
  //     .x(function(d) { return x(d.timestamps); })
  //     .y(function(d) { return y(d.AF8); });


  // Adds the svg canvas
  var svg = d3.select("#chart_container")
      .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
      .append("g")
          .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

  svg.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);


  function make_x_axis() {
    return d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .ticks(5)
  }
  function make_y_axis() {
    return d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(5)
  }

  // Data inicial
  var data = [];
  for(var i=0;i<20;i++){
    xx = 1*i/20 - 1;
    data.push({timestamps: xx, AF7: 0});
  }

  // Setear grafico inicial
  // Scale the range of the data
  x.domain(d3.extent(data, function(d) { return d.timestamps; }));
  y.domain(d3.extent(data, function(d) { return d.AF7; }));

  //Dos formas de setear rango: valores min y max, o extent():
  // y.domain([0, d3.max(data, function(d) { return Math.max(d.AF7, d.AF8); })]);

  // Add the line
  // var path = svg.append("path")
  //     .attr("class", "line")
  //     .attr("d", valueAF7(data));
  var path = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .data([data])
      .attr("class", "line")
      .attr("d", valueAF7(data));

  // Add the X Axis
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  // Label for the x axis
  svg.append("text")
      .attr("x", width / 2 )
      .attr("y", height + margin.bottom)
      .attr("dy", "0em") // FIXME: subir grafico para que haya mas espacio para label
      .style("text-anchor", "middle")
      .text("Time (s)");

  // Add the Y Axis
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  // Label y axis
  svg.append("text")
      .attr("dx", "-2em")
      .attr("dy", "-1em")
      .style("text-anchor", "middle")
      .text("Value");

  //Titulo
  svg.append("text")
      .attr("x", (width / 2))
      .attr("y", 0 - (margin.top / 2))
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      // .style("text-decoration", "underline")
      .text("Live muse data");

  //Grid lines
  svg.append("g")
      .attr("class", "grid")
      .attr("transform", "translate(0," + height + ")")
      .call(make_x_axis()
        .tickSize(-height, 0, 0)
        .tickFormat("")
      )
  svg.append("g")
      .attr("class", "grid")
      .call(make_y_axis()
        .tickSize(-width, 0, 0)
        .tickFormat("")
      )

  // ** Update data section (Called from the onclick)
  function update_graph(p_x, p_y) {

    // Agregar nuevo dato
    data.push({timestamps: p_x, AF7: p_y});

    console.log("updating", p_x, p_y);

    // path.attr("d", valueAF7(data))
    //   .attr("transform", null)
    // .transition()
    //   .duration(100)
    //   .ease("linear")
    //   .attr("transform", "translate(" + x(-1) + ")");


    data.shift();

    // Scale the range of the data again
    x.domain(d3.extent(data, function(d) { return d.timestamps; }));
    y.domain(d3.extent(data, function(d) { return d.AF7; }));

    // Select the section we want to apply our changes to
    var svg = d3.select("#chart_container").transition();

    // Make the changes
    svg.select(".line")   // change the line
        .duration(750)
        .attr("d", valueAF7(data))
        .ease("back");

    svg.select(".x.axis") // change the x axis
        .duration(750)
        .call(xAxis);
    svg.select(".y.axis") // change the y axis
        .duration(750)
        .call(yAxis);
  }

// g.append("defs").append("clipPath")
//     .attr("id", "clip")
//   .append("rect")
//     .attr("width", width)
//     .attr("height", height);
// g.append("g")
//     .attr("clip-path", "url(#clip)")
//   .append("path")
//     .datum(data)
//     .attr("class", "line")
//   .transition()
//     .duration(500)
//     .ease(d3.easeLinear)
//     .on("start", tick);


  // Conectarse con server (python) usando Event Source
  // var dir = 'http://localhost:8889/data/prueba';
  // var stream = new EventSource(dir);
  // stream.onopen = function (e) {
  //    console.log("CONNECTED");
  // };
  //
  // stream.onmessage = function (e) {
  //   var arr = e.data.split(",");
  //   var x = parseFloat(arr[0]);
  //   var y = parseFloat(arr[1]);
  // };
  //
  // stream.onerror = function (e) {
  //   console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
  //   stream.close();
  // };


  var counter = 0;
  // Boton
  $("#close-con-btn").click(function(){
    update_graph(counter, Math.random());
    counter += 1;
  });



});


// Get the data
// d3.csv("data/dump4.csv", function(error, data) {
//     data.forEach(function(d) {
//         d.timestamps = +d.timestamps;
//         d.AF7 = +d.AF7; // + ensures a number
//         // console.log(d.timestamps, d.AF7);
//     });
//
// });
