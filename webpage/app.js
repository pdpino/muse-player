// Plot using d3, adapted from http://jsfiddle.net/XZSuK/

$(document).ready( function() {
  // Data inicial
  var data = [];
  var n = 100;
  var segs = 5; //segundos de ventana // HACK
  for(var i=0;i<n;i++){
    data.push({T: i*segs/n - segs, CH1: 0, CH2: 0, CH3: 0, CH4: 0, CH5: 0});
  }

  // Margenes
  var margin = {top: 10, right: 10, bottom: 20, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

  // Rangos de ejes
  var x = d3.scale.linear().domain([-segs, 0]).range([0, width]); // x
  var y = d3.scale.linear().domain([-1000, 1000]).range([height, 0]); // y // HACK: adaptar eje

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


  // Paths de canales
  // Channel 1
  var pathCH1 = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .attr("class", "line")
      .style("stroke", "black")
      .attr("d", lineCH1(data));
  // Channel 2
  var pathCH2 = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .attr("class", "line")
      .style("stroke", "red")
      .attr("d", lineCH2(data));
  // Channel 3
  var pathCH3 = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .attr("class", "line")
      .style("stroke", "blue")
      .attr("d", lineCH3(data));
  // Channel 4
  var pathCH4 = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .attr("class", "line")
      .style("stroke", "green")
      .attr("d", lineCH4(data));
  // Channel 5
  var pathCH5 = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .attr("class", "line")
      .style("stroke", "cyan")
      .attr("d", lineCH5(data));



  var plot_ch1 = true; //$("#ch1").checked;
  var plot_ch2 = true; //$("#ch2").checked;
  var plot_ch3 = true; //$("#ch3").checked;
  var plot_ch4 = true; //$("#ch4").checked;
  var plot_ch5 = true; //$("#ch5").checked;

  // Funcion para updatear el grafico
  function update_graph() {
    //Redibujar cada linea, segun sea necesario
    if(plot_ch1){
      pathCH1.attr("d", lineCH1(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }

    if(plot_ch2){
      pathCH2.attr("d", lineCH2(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }

    if(plot_ch3){
      pathCH3.attr("d", lineCH3(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }

    if(plot_ch4){
      pathCH4.attr("d", lineCH4(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }

    if(plot_ch5){
      pathCH5.attr("d", lineCH5(data))
          .attr("transform", null)
        .transition()
          .duration(1000)
          .ease("linear");
    }

    // Setear rango de tiempo de nuevo
    x.domain(d3.extent(data, function(d) { return d.T; }));
    // y.domain(d3.extent(data, function(d) { return d.Y; }));
    // y.domain([d3.min(data, function(d) { return Math.max(d.Y, -5);}),
    //           d3.max(data, function(d) { return Math.min(d.Y, 5); })]);
    // TODO: scale Y

    svg.select(".x.axis") // change the x axis
        .call(xAxis);
  };


  // TODO: ordenar codigo de leyenda
  // TODO: centralizar valores (usar arrays o dicts para colores y texto)
  //Leyenda
  // var margin_leg = {top: 10, right: 10, bottom: 20, left: 40},
  //     width_leg = 100 - margin_leg.left - margin_leg.right,
  //     height_leg = 50 - margin_leg.top - margin_leg.bottom;

  // var svg_legend = d3.select("#legend_container").append("svg")
  //     .attr("width", 100)
  //     .attr("height", 100)
  //   .append("g")
  //     // .attr("transform", "translate(1000, 300)");
  //
  // var legend = svg_legend.append("g")
  //   .attr("class", "legend")
  //   .attr("height", 50)
  //   .attr("width", 50)
  //   // .attr('transform', 'translate(0,-80)')
  //
  // var legend_x_color = 0; //width - 65;
  // var legend_y_color = 0;
  // var dy = 20;
  //
  // var legend_x_text = legend_x_color + 15;
  // var legend_y_text = legend_y_color + 10;
  //
  // var color_dict = {
  //         0 : ["TP9", "black"],
  //         1 : ["AF7", "red"],
  //         2 : ["AF8", "blue"],
  //         3 : ["TP10", "green"],
  //         4 : ["Right AUX", "cyan"],
  //       };
  //
  // var n = Object.keys(color_dict).length;
  // for(var i=0;i<n;i++){
  //   legend.append("rect")
  //     .attr("x", legend_x_color)
  //     .attr("y", legend_y_color + i*dy)
  //     .attr("width", 10)
  //     .attr("height", 10)
  //     .style("fill", color_dict[i][1]);
  //
  //   legend.append("text")
  //     .attr("x", legend_x_text)
  //     .attr("y", legend_y_text + i*dy)
  //     .text(color_dict[i][0]);
  // }

  d3.select("#ch1-rect").style("fill", "black");
  d3.select("#ch2-rect").style("fill", "red");
  d3.select("#ch3-rect").style("fill", "blue");
  d3.select("#ch4-rect").style("fill", "green");
  d3.select("#ch5-rect").style("fill", "cyan");






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


  // Form de mostrar o no canales
  $("#ch1").click(function(){
    plot_ch1 = this.checked;
    var opac = this.checked ? 1 : 0;
    pathCH1.style("opacity", opac);
  });
  $("#ch2").click(function(){
    plot_ch2 = this.checked;
    var opac = this.checked ? 1 : 0;
    pathCH2.style("opacity", opac);
  });
  $("#ch3").click(function(){
    plot_ch3 = this.checked;
    var opac = this.checked ? 1 : 0;
    pathCH3.style("opacity", opac);
  });
  $("#ch4").click(function(){
    plot_ch4 = this.checked;
    var opac = this.checked ? 1 : 0;
    pathCH4.style("opacity", opac);
  });
  $("#ch5").click(function(){
    plot_ch5 = this.checked;
    var opac = this.checked ? 1 : 0;
    pathCH5.style("opacity", opac);
  });
  // Checkbox all channels
    // source: https://stackoverflow.com/questions/386281/how-to-implement-select-all-check-box-in-html
  // $('#all-chs').click(function(event) {
  //   if(this.checked) {
  //     // Iterate each checkbox
  //     $(':checkbox').each(function() {
  //         this.checked = true;
  //     });
  //   }
  //   else {
  //     $(':checkbox').each(function() {
  //           this.checked = false;
  //     });
  //   }
  // });


  // Boton cerrar conexion
  $("#close-con-btn").click(function(){
    stream.close();
    console.log("Connection closed");
  });



});
