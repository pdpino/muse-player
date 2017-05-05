// Version 4: usa d3.v4 para plotear
//TODO

$(document).ready( function() {

  // Data inicial
  var data = [];
  var n = 20;
  for(var i=0;i<n;i++){
    xx = 1*i/n - 1;
    data.push({timestamps: xx, AF7: 0});
  }

  var svg = d3.select("#chart_container"),
      margin = {top: 20, right: 20, bottom: 20, left: 40},
      width = +svg.attr("width") - margin.left - margin.right,
      height = +svg.attr("height") - margin.top - margin.bottom,
      g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  var x = d3.scaleLinear()
      .domain([0, n - 1])
      .range([0, width]);
  var y = d3.scaleLinear()
      .domain([-1, 1])
      .range([height, 0]);
  var line = d3.line()
      .x(function(d, i) { return x(i); })
      .y(function(d, i) { return y(d); });
  g.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);
  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + y(0) + ")")
      .call(d3.axisBottom(x));
  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y));
  g.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .datum(data)
      .attr("class", "line")
    .transition()
      .duration(500)
      .ease(d3.easeLinear)
      .on("start", tick);

  function tick() {
    // Push a new data point onto the back.
    data.push(Math.random());
    // Redraw the line.
    d3.select(this)
        .attr("d", line)
        .attr("transform", null);
    // Slide it to the left.
    d3.active(this)
        .attr("transform", "translate(" + x(-1) + ",0)")
      .transition()
        .on("start", tick);
    // Pop the old data point off the front.
    data.shift();
  }


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
    // update_graph(counter, Math.random());
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
