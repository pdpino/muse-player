$(document).ready( function() {
    // Crear grafico
    var x_data = [];
    var y_data = [];

    var crear_grafico_simple = function(){
      var trace1 = {
        x: x_data,
        y: y_data,
        mode: 'lines+markers',
        name: 'af7'
      };

      var lines = [trace1]

      var layout = {
        title:'Muse data',
        width: 800,
        height: 500,
        xaxis: {
          title: 'Tiempo (s)',
        },
        yaxis: {
          title: 'Y',
        }
      };

      Plotly.newPlot('tester', lines, layout);

    };

    function update_graph(x, y){
      // TODO: make animation smoother // pq es tan lento?
      // FIXME: se atrasa al plotear? lleva segundos corriendo y graficos va en 0.2 //revisar si esta bien la escala
      // FIXME: datos se desordenan

      var xmin = x - 2;
      var xmax = x + 2;

      x_data.push(x);
      y_data.push(y);

      // Tomar los ultimos 10 puntos
      var n_points = 10;
      x_data = x_data.slice(-n_points);
      y_data = y_data.slice(-n_points);

      Plotly.animate('tester', { data: [{x: x_data, y: y_data}] }, {
        transition: {
          duration: 1,
          easing: 'cubic-in-out'
        },
        frame: {
          duration: 1
        },
        layout: {
          // xaxis: {range: [xmin, xmax]}
          // yaxis: {range: [ymin, ymax]}
        }
      });
    }

    crear_grafico_simple();


    //Conectarse con server (python) usando Event Source
    var dir = 'http://localhost:8889/data/prueba';
    var stream = new EventSource(dir);
    stream.onopen = function (e) {
       console.log("CONNECTED");
    };

    stream.onmessage = function (e) {
      var arr = e.data.split(",");
      var ch = parseInt(arr[0]); //Canal
      var x = parseFloat(arr[1]);
      var y = parseFloat(arr[2]);

      if(ch == 0){
        update_graph(x, y);
      }
    };

    stream.onerror = function (e) {
      console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
      stream.close();
    };

    // BOTON CLOSE CONNECTION
    $("#close-con-btn").click(function(){
      console.log("Closing connection.\nReload the page to reconnect to the server")
      stream.close();
      // FIXME: al cerrar conexion sigue actualizando grafico
    });

  }
);
