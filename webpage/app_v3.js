// Version 3: usa d3 para plotear
//TODO

$(document).ready( function() {

  // Set the dimensions of the canvas / graph
  var margin = {top: 30, right: 20, bottom: 30, left: 50},
      width = 600 - margin.left - margin.right,
      height = 270 - margin.top - margin.bottom;

  // Parse the date / time
  var parseDate = d3.time.format("%d-%b-%y").parse;

  // Set the ranges
  var x = d3.time.scale().range([0, width]);
  var y = d3.scale.linear().range([height, 0]);

  // Define the axes
  var xAxis = d3.svg.axis().scale(x)
      .orient("bottom").ticks(5);

  var yAxis = d3.svg.axis().scale(y)
      .orient("left").ticks(5);

  // Define the line
  var valueline = d3.svg.line()
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.close); });

  // Adds the svg canvas
  var svg = d3.select("body")
      .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
      .append("g")
          .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

  // Get the data
  d3.csv("data/dump.csv", function(error, data) {
      data.forEach(function(d) {
          d.TP9 = parseDate(d.date);
          d.AF7 = +d.close;
      });

      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain([0, d3.max(data, function(d) { return d.close; })]);

      // Add the valueline path.
      svg.append("path")
          .attr("class", "line")
          .attr("d", valueline(data));

      // Add the X Axis
      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      // Add the Y Axis
      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis);

  });

  // // ** Update data section (Called from the onclick)
  // function updateData() {
  //
  //     // Get the data again
  //     d3.csv("data-alt.csv", function(error, data) {
  //        	data.forEach(function(d) {
  // 	    	d.date = parseDate(d.date);
  // 	    	d.close = +d.close;
  // 	    });
  //
  //     	// Scale the range of the data again
  //     	x.domain(d3.extent(data, function(d) { return d.date; }));
  // 	    y.domain([0, d3.max(data, function(d) { return d.close; })]);
  //
  //     // Select the section we want to apply our changes to
  //     var svg = d3.select("body").transition();
  //
  //     // Make the changes
  //         svg.select(".line")   // change the line
  //             .duration(750)
  //             .attr("d", valueline(data));
  //         svg.select(".x.axis") // change the x axis
  //             .duration(750)
  //             .call(xAxis);
  //         svg.select(".y.axis") // change the y axis
  //             .duration(750)
  //             .call(yAxis);
  //
  //     });
  // }





  //Conectarse con server (python) usando Event Source
  // var dir = 'http://localhost:8889/data/prueba';
  // var stream = new EventSource(dir);
  // stream.onopen = function (e) {
  //    console.log("CONNECTED");
  // };

  // stream.onmessage = function (e) {
  //   var arr = e.data.split(",");
  //   var x = parseFloat(arr[0]);
  //   var y = parseFloat(arr[1]);
  //
  //   var length = chart.options.data[0].dataPoints.length;
  //   if(length > 20){
  //     //REVIEW: shift is not efficient?
  //     // chart.options.data[0].dataPoints.shift();
  //     data[0].x = null;
  //     data[0].y = null;
  //     data.shift();
  //   }
  //   // chart.options.data[0].dataPoints.push({ x: x, y: y });
  //   data.push({ x: x, y: y });
  //   chart.render();
  // };

  // stream.onerror = function (e) {
  //   console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
  //   stream.close();
  // };

  // // Boton close connection
  // $("#close-con-btn").click(function(){
  //   console.log("Closing connection.\nReload the page to reconnect to the server")
  //   stream.close();
  // });

});
