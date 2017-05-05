// Version 6: adapted from http://jsfiddle.net/XZSuK/

$(document).ready( function() {
  // var n = 40, random = d3.random.normal(0, .2), data = d3.range(n).map(random);

  // Data inicial
  var data = [];
  var n = 100;
  var segs = 5; //segundos de ventana // HACK
  for(var i=0;i<n;i++){
    data.push({X: i*segs/n - segs, Y: 0, Z: 0});
  }

  // console.log(data);

  // Margenes
  var margin = {top: 10, right: 10, bottom: 20, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

  // Rango de x
  var x = d3.scale.linear().domain([-segs, 0]).range([0, width]);

  // Rango de y
  var y = d3.scale.linear().domain([-1000, 1000]).range([height, 0]);

  // Funcion para obtener linea
  var lineA = d3.svg.line()
      .x(function(d) { return x(d.X); })
      .y(function(d) { return y(d.Y); });

  var lineB = d3.svg.line()
      .x(function(d) { return x(d.X); })
      .y(function(d) { return y(d.Z); });



  // Svg
  var svg = d3.select("#chart_container").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Clip para tomar lo que sale por la izquierda
  svg.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);

  // X axis
  var xAxis = d3.svg.axis().scale(x).orient("bottom");
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  // Y axis
  var yAxis = d3.svg.axis().scale(y).orient("left").ticks(5);
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  // Line A
  var pathA = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      // .data(data)
      .attr("class", "line")
      .attr("d", lineA(data));

  // Line B
  var pathB = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      // .data(data)
      .attr("class", "line")
      .style("stroke", "red")
      .attr("d", lineB(data));

  function update(px, py, pz) {

    // push a new data point onto the back
    data.push({X: px, Y: py, Z: pz});

    // redraw line A
    pathA.attr("d", lineA(data))
        .attr("transform", null)
      .transition()
        .duration(1000)
        .ease("linear");

    // redraw line B
    pathB.attr("d", lineB(data))
        .attr("transform", null)
      .transition()
        .duration(1000)
        .ease("linear");
        // .attr("transform", "translate(" + x(-1) + ")");
  //      .each("end", tick);

    // Scale the range of the data again
    x.domain(d3.extent(data, function(d) { return d.X; }));
    // y.domain(d3.extent(data, function(d) { return d.Y; }));
    // y.domain([d3.min(data, function(d) { return Math.max(d.Y, -5);}),
    //           d3.max(data, function(d) { return Math.min(d.Y, 5); })]);

    svg.select(".x.axis") // change the x axis
        // .duration(750)
        .call(xAxis);
    // svg.select(".y.axis") // change the y axis
    //     // .duration(750)
    //     .call(yAxis);

    // pop the old data point off the front
    data.shift();
  };

  // Conectarse con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/prueba';
  var stream = new EventSource(dir);
  stream.onopen = function (e) {
     console.log("CONNECTED");
  };

  stream.onmessage = function (e) {
    var arr = e.data.split(",");
    var t = parseFloat(arr[0]); // tiempo
    var s1 = parseFloat(arr[1]); // señal 1
    var s2 = parseFloat(arr[2]); // señal 2
    update(t, s1, s2);
  };

  stream.onerror = function (e) {
    console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
    stream.close();
  };



  // Botones
  var counter = 0;
  $("#data-btn").click(function(){
    update(counter, Math.random(100));
    counter += 1;
  });
  $("#close-con-btn").click(function(){
    stream.close();
    counter = data[data.length-1].X;
    console.log("Connection closed");
  });



});
