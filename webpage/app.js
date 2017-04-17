// version 1: usa plotly

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
      // FIXME: data delay
        // probar solo añadir un dato a grafico y mover eje, en vez de añadir todos los datos de nuevo

      // FIXME: datos se desordenan (pocas veces)

      x_data.push(x);
      y_data.push(y);

      // Tomar los ultimos 10 puntos
      var n_points = 10;
      x_data = x_data.slice(-n_points); //splice?
      y_data = y_data.slice(-n_points);
      // if(x_data.length > 10){
      //   x_data.pop();
      //   y_data.pop();
      // }


      Plotly.animate('tester', { data: [{x: x_data, y: y_data}] }
      , {
        transition: {
          duration: 0,
          easing: 'cubic-in-out'
        },
        frame: {
          duration: 0,
        }
      }
      );
      // Plotly.update('tester', { data: [{x: x_data, y: y_data}] }
      // , {
      //   transition: {
      //     duration: 0,
      //     easing: 'cubic-in-out'
      //   },
      //   frame: {
      //     duration: 0,
      //   }
      // }
      // );
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
      var x = parseFloat(arr[0]);
      var y = parseFloat(arr[1]);

      update_graph(x, y);
    };

    stream.onerror = function (e) {
      console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
      stream.close();
    };

    // BOTON CLOSE CONNECTION
    $("#close-con-btn").click(function(){
      console.log("Closing connection.\nReload the page to reconnect to the server")
      stream.close();
      // Plotly.purge('tester'); //Eliminar el grafico //A la mala
      // FIXME: al cerrar conexion sigue actualizando grafico //es pq grafico va (muy) atrasado
      Plotly.deleteTraces('tester', 0); //HACK: Eliminar trace 0 del grafico
    });

  }
);
