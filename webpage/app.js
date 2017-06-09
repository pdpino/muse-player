// Plot using d3, adapted from http://jsfiddle.net/XZSuK/

// TODO: estandarizar nombres de funciones y variables: minusMayus, _

function create_graph(yMin, yMax, xTicks, yTicks, n_secs){
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
  var xRange = d3.scale.linear().domain([0, n_secs]).range([0, width]);
  var yRange = d3.scale.linear().domain([yMin, yMax]).range([height, 0]);

  // Eje del tiempo
  var xAxis = d3.svg.axis().scale(xRange).orient("bottom").ticks(5);
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
  //// Parametros iniciales
  // Rango de eje y
  var yMin = -1000;
  var yMax = 1000;
  var xTicks = 5;
  var yTicks = 5;
  var n_secs = 20; // Cantidad de segundos maximo que guarda el plot

  // Data
  var n_channels = 5;
  var data = new Array(1);
  data[0] = {T: 0, CH1: 0, CH2: 0, CH3: 0, CH4: 0, CH5: 0};


  var colors = ["black", "red", "blue", "green", "cyan"];
  var graph = create_graph(yMin, yMax, xTicks, yTicks, n_secs);
  var lines = create_line_functions(graph.xRange, graph.yRange);

  // Funcion para crear paths
  function create_path(line, color){
    return graph.svg.append("g")
            .attr("clip-path", "url(#clip)")
          .append("path")
            .attr("class", "line")
            .style("stroke", color)
            .attr("d", line(data));

  };

  // Funcion para update linea en grafico
  function update_line(plot_ch, path, line){
    if(plot_ch){
      path.attr("d", line(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }
  }

  // Paths y bools para cada canal
  var paths = Array(n_channels); // Lineas en svg
  var plot_bools = Array(n_channels); // Bools para esconder path
  for(var i=0;i<n_channels;i++){
    paths[i] = create_path(lines[i], colors[i]);
    plot_bools[i] = true;
  }

  // Funcion para updatear el grafico
  function update_graph() {
    for(var i=0;i<n_channels;i++){
      update_line(plot_bools[i], paths[i], lines[i]);
    }

    // Setear rango de tiempo de nuevo
    graph.xRange.domain(d3.extent(data, function(d) { return d.T; }));
    graph.svg.select(".x.axis").call(graph.xAxis); // change the x axis
  };

  // Pintar leyenda
  d3.select("#ch1-rect").style("fill", colors[0]);
  d3.select("#ch2-rect").style("fill", colors[1]);
  d3.select("#ch3-rect").style("fill", colors[2]);
  d3.select("#ch4-rect").style("fill", colors[3]);
  d3.select("#ch5-rect").style("fill", colors[4]);



  // Update axis
  var dxRange = 1;
  var dyRange = 100;
  function update_y_axis(y1, y2){
    if(y1 < y2){ // update solo si tiene sentido
      graph.yRange.domain([y1, y2]);
      graph.svg.select(".y.axis").call(graph.yAxis); // update svg
    }
  }

  // Botones para updatear
  $("#btn-zoomYin").click(function(){
    if(yMin + dyRange < yMax - dyRange){ // Solo si tiene sentido
      yMin += dyRange;
      yMax -= dyRange;
      update_y_axis(yMin, yMax);
    }
    else{
      dyRange = dyRange/2;
    }
  });
  $("#btn-zoomYout").click(function(){
    yMin -= dyRange;
    yMax += dyRange;
    update_y_axis(yMin, yMax);
  });
  $("#btn-zoomXin").click(function(){
    if(n_secs > 1){ // Minimo 5 segundos de ventana
      n_secs -= dxRange;
    }
  });
  $("#btn-zoomXout").click(function(){
    n_secs += dxRange;
  });


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

    // Pop datos hasta tener solo n_secs
    while(data[data.length-1].T - data[0].T > n_secs){
      data.shift();
    }
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
  $("#btn-close-con").click(function(){
    stream.close();
    console.log("Connection closed");
  });

  // Boton debug
  $("#btn-debug").click(function(){
    console.log("Debug button disconnected");
  });


  console.log("All set.");
});
