// Plot using d3, adapted from http://jsfiddle.net/XZSuK/

// TODO: ordenar codigo


function create_graph(segs, yMin, yMax){
  // Margenes
  var margin = {top: 10, right: 10, bottom: 20, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

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

  // Rangos de ejes
  var xRange = d3.scale.linear().domain([-segs, 0]).range([0, width]); // x
  var yRange = d3.scale.linear().domain([yMin, yMax]).range([height, 0]); // y // HACK: adaptar eje

  // Eje del tiempo
  var xAxis = d3.svg.axis().scale(xRange).orient("bottom");
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  // Y axis
  var yAxis = d3.svg.axis().scale(yRange).orient("left").ticks(5);
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  return {svg: svg, xRange: xRange, yRange: yRange, xAxis: xAxis, yAxis: yAxis};
}

function create_line_functions(x, y){
  var lines = Array(5);

  // Funciones para obtener lineas
  lines[0] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH1); });
  lines[1] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH2); });
  lines[2] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH3); });
  lines[3] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH4); });
  lines[4] = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH5); });

  return lines;
};

$(document).ready( function() {
  // Data
  var n = 100;
  var n_channels = 5;
  var data = new Array(n);
  var segs = 5; //segundos de ventana // HACK
  for(var i=0;i<n;i++){
    data[i] = {T: i*segs/n - segs, CH1: 0, CH2: 0, CH3: 0, CH4: 0, CH5: 0};
  }


  var yMin = -1000;
  var yMax = 1000;


  var colors = ["black", "red", "blue", "green", "cyan"];

  var graph = create_graph(segs, yMin, yMax);

  var lines = create_line_functions(graph.xRange, graph.yRange);

  // Crear paths
  function create_path(line, color){
    return graph.svg.append("g")
            .attr("clip-path", "url(#clip)")
          .append("path")
            .attr("class", "line")
            .style("stroke", color)
            .attr("d", line(data));

  };

  var paths = Array(n_channels);
  for(var i=0;i<n_channels;i++){
    paths[i] = create_path(lines[i], colors[i]);
  }

  var plot_bools = Array(n_channels);
  for(var i=0;i<n_channels;i++){
    plot_bools[i] = true;
  }

  function update_line(plot_ch, path, line){
    if(plot_ch){
      path.attr("d", line(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }
  }

  // Funcion para updatear el grafico
  function update_graph() {
    for(var i=0;i<n_channels;i++){
      update_line(plot_bools[i], paths[i], lines[i]);
    }

    // Setear rango de tiempo de nuevo
    graph.xRange.domain(d3.extent(data, function(d) { return d.T; }));
    // y.domain(d3.extent(data, function(d) { return d.Y; }));
    // y.domain([d3.min(data, function(d) { return Math.max(d.Y, -5);}),
    //           d3.max(data, function(d) { return Math.min(d.Y, 5); })]);
    // TODO: scale Y

    graph.svg.select(".x.axis") // change the x axis
        .call(graph.xAxis);
  };

  // Pintar leyenda
  d3.select("#ch1-rect").style("fill", colors[0]);
  d3.select("#ch2-rect").style("fill", colors[1]);
  d3.select("#ch3-rect").style("fill", colors[2]);
  d3.select("#ch4-rect").style("fill", colors[3]);
  d3.select("#ch5-rect").style("fill", colors[4]);





  // Conectarse con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/muse';
  var stream = new EventSource(dir); // TODO: usar try catch
  stream.onopen = function (e) {
    console.log("CONNECTED");
  };

  stream.onmessage = function (e) {
    var arr = e.data.split(",");
    var t = parseFloat(arr[0]); // tiempo
    var ch1 = parseFloat(arr[1]);
    var ch2 = parseFloat(arr[2]);
    var ch3 = parseFloat(arr[3]);
    var ch4 = parseFloat(arr[4]);
    var ch5 = parseFloat(arr[5]);

    // Push datos
    data.push({T: t, CH1: ch1, CH2: ch2, CH3: ch3, CH4: ch4, CH5: ch5});

    // Update grafico
    update_graph();

    // Pop primer dato
    data.shift();
  };

  stream.onerror = function (e) {
    console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
    stream.close();
  };


  function toggle_show_path(path, checked){
    path.style("opacity", checked ? 1 : 0);
  }

  // Form de mostrar o no canales
  $("#ch1").click(function(){
    plot_bools[0] = this.checked;
    toggle_show_path(paths[0], this.checked);
  });
  $("#ch2").click(function(){
    plot_bools[1] = this.checked;
    toggle_show_path(paths[1], this.checked);
  });
  $("#ch3").click(function(){
    plot_bools[2] = this.checked;
    toggle_show_path(paths[2], this.checked);
  });
  $("#ch4").click(function(){
    plot_bools[3] = this.checked;
    toggle_show_path(paths[3], this.checked);
  });
  $("#ch5").click(function(){
    plot_bools[4] = this.checked;
    toggle_show_path(paths[4], this.checked);
  });

  // Boton cerrar conexion
  $("#close-con-btn").click(function(){
    stream.close();
    console.log("Connection closed");
  });

  // Boton debug
  $("#debug-btn").click(function(){

  });



  console.log("All set.");
});
