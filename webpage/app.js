// Plot using d3, adapted from http://jsfiddle.net/XZSuK/

// TODO: ordenar codigo

$(document).ready( function() {
  // Data inicial
  var n = 100;
  var data = new Array(n);
  var segs = 5; //segundos de ventana // HACK
  for(var i=0;i<n;i++){
    data[i] = {T: i*segs/n - segs, CH1: 0, CH2: 0, CH3: 0, CH4: 0, CH5: 0};
  }

  // Margenes
  var margin = {top: 10, right: 10, bottom: 20, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

  // Rangos de ejes
  var x = d3.scale.linear().domain([-segs, 0]).range([0, width]); // x
  var y = d3.scale.linear().domain([-100, 4000]).range([height, 0]); // y // HACK: adaptar eje

  // Funciones para obtener lineas
  var lineCH1 = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH1); });
  var lineCH2 = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH2); });
  var lineCH3 = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH3); });
  var lineCH4 = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH4); });
  var lineCH5 = d3.svg.line()
      .x(function(d) { return x(d.T); })
      .y(function(d) { return y(d.CH5); });



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

  // Eje del tiempo
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


  // Crear paths
  function create_path(line, color){
    return svg.append("g")
            .attr("clip-path", "url(#clip)")
          .append("path")
            .attr("class", "line")
            .style("stroke", color)
            .attr("d", line(data));

  }

  var colors = ["black", "red", "blue", "green", "cyan"];

  var pathCH1 = create_path(lineCH1, colors[0]);
  var pathCH2 = create_path(lineCH2, colors[1]);
  var pathCH3 = create_path(lineCH3, colors[2]);
  var pathCH4 = create_path(lineCH4, colors[3]);
  var pathCH5 = create_path(lineCH5, colors[4]);

  var plot_ch1 = true; //$("#ch1").checked;
  var plot_ch2 = true; //$("#ch2").checked;
  var plot_ch3 = true; //$("#ch3").checked;
  var plot_ch4 = true; //$("#ch4").checked;
  var plot_ch5 = true; //$("#ch5").checked;


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
    update_line(plot_ch1, pathCH1, lineCH1);
    update_line(plot_ch2, pathCH2, lineCH2);
    update_line(plot_ch3, pathCH3, lineCH3);
    update_line(plot_ch4, pathCH4, lineCH4);
    update_line(plot_ch5, pathCH5, lineCH5);

    // Setear rango de tiempo de nuevo
    x.domain(d3.extent(data, function(d) { return d.T; }));
    // y.domain(d3.extent(data, function(d) { return d.Y; }));
    // y.domain([d3.min(data, function(d) { return Math.max(d.Y, -5);}),
    //           d3.max(data, function(d) { return Math.min(d.Y, 5); })]);
    // TODO: scale Y

    svg.select(".x.axis") // change the x axis
        .call(xAxis);
  };

  d3.select("#ch1-rect").style("fill", colors[0]);
  d3.select("#ch2-rect").style("fill", colors[1]);
  d3.select("#ch3-rect").style("fill", colors[2]);
  d3.select("#ch4-rect").style("fill", colors[3]);
  d3.select("#ch5-rect").style("fill", colors[4]);

  //$("#ch1").textContent = "textContent";
  // $("#ch1").text("d3");
  // $("#ch1").value = "value";
  // $("#ch1").innerText = "innerText";
  // $("#ch1").innerHTML = "innerHTML";



  // var legend = svg.append("g")
  //     .attr("class","legend")
  //     .attr("transform","translate(50,30)")
  //     .style("font-size","12px")
  //     .call(d3.legend);
  // Legend: ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX']



  // Conectarse con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/prueba';
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
    plot_ch1 = this.checked;
    toggle_show_path(pathCH1, this.checked);
  });
  $("#ch2").click(function(){
    plot_ch2 = this.checked;
    toggle_show_path(pathCH2, this.checked);
  });
  $("#ch3").click(function(){
    plot_ch3 = this.checked;
    toggle_show_path(pathCH3, this.checked);
  });
  $("#ch4").click(function(){
    plot_ch4 = this.checked;
    toggle_show_path(pathCH4, this.checked);
  });
  $("#ch5").click(function(){
    plot_ch5 = this.checked;
    toggle_show_path(pathCH5, this.checked);
  });

  // Boton cerrar conexion
  $("#close-con-btn").click(function(){
    stream.close();
    console.log("Connection closed");
  });


  console.log("All set.");
});
