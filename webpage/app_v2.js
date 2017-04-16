// Version 2: usa CanvasJS para plotear

$(document).ready( function() {
  //Crear grafico
  data = [];
  var chart = new CanvasJS.Chart("tester", {
    title: {
      text: "Live Muse Data"
    },
    data: [
    {
      type: "spline",
      dataPoints: data
    }
    ]
  });
  chart.render();

  //Conectarse con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/prueba';
  var stream = new EventSource(dir);
  stream.onopen = function (e) {
     console.log("CONNECTED");
  };

  stream.onmessage = function (e) {
    var arr = e.data.split(",");
    var x = parseFloat(arr[0]);
    var y = parseFloat(arr[1]);

    var length = chart.options.data[0].dataPoints.length;
    if(length > 20){
      //REVIEW: shift is not efficient?
      // chart.options.data[0].dataPoints.shift();
      data[0].x = null;
      data[0].y = null;
      data.shift();
    }
    // chart.options.data[0].dataPoints.push({ x: x, y: y });
    data.push({ x: x, y: y });
    chart.render();
  };



  stream.onerror = function (e) {
    console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
    stream.close();
  };



  // Boton close connection
  $("#close-con-btn").click(function(){
    console.log("Closing connection.\nReload the page to reconnect to the server")
    stream.close();
  });

});
