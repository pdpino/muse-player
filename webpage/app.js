$(document).ready( function() {

    // LEER CSV
    // Papa.parse("./data/dump.csv", {
    //   download: true,
    //   // worker: true,
    //   header: true,
    //   dynamicTyping: true,
    //   skipEmptyLines: true,
    //   complete: function(results){
    //     crear_grafico(results.data);
    //   }
    // });




    // CREAR GRAFICO
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
          showline: true,
          showgrid: true,
          showticklabels: true,
          linewidth: 2,
          autotick: false,
          ticks: 'outside',
          tickcolor: 'rgb(204,204,204)',
          tickwidth: 2,
          ticklen: 5,
          tickfont: {
            family: 'Arial',
            size: 12,
            color: 'rgb(82, 82, 82)'
          }
        },
        yaxis: {
          title: 'Y',
          autorange: true,
          showgrid: true,
          zeroline: false,
          showline: true,
          showticklabels: true
        }
      };

      Plotly.plot('tester', lines, layout);

    };

    function update_graph(x, y){
      // TODO: make animation smoother
      var xmin = x - 2;
      var xmax = x + 2;

      x_data.push(x);
      y_data.push(y);

      // if(x_data.length >= 10){ //maximo 10 puntos
      //   x_data.shift();
      //   y_data.shift();
      // }

      x_data = x_data.slice(-10);
      y_data = y_data.slice(-10);

      Plotly.animate('tester', { data: [{x: x_data, y: y_data}] }, {
        transition: {
          duration: 0
        },
        frame: {
          duration: 0,
          easing: 'cubic-in-out'
        },
        layout: {
          // xaxis: {range: [xmin, xmax]}
          // yaxis: {range: [min, max]}
        }
      });
    }

    crear_grafico_simple();


    //CONECTARSE CON SERVER
    //Event Source, necesita server python
    var dir = 'http://localhost:8889/data/prueba';
    var stream = new EventSource(dir);
    stream.onopen = function (e) {
       console.log("CONNECTED");
    };

    stream.onmessage = function (e) {
      // console.log(e.data);
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
      // FIXME: al cerrar conexion sigue graficando // solo a veces pasa
    });

    console.log("chao");

  }
);

// FUNCIONES PARA LEER CSV
// var crear_grafico = function(data){
//   var trace1 = {
//     x: slice_col(data, "timestamps"),
//     y: slice_col(data, "AF7"),
//     // type: 'scatter',
//     mode: 'lines',
//     name: 'af7'
//   };
//
//   var trace2 = {
//     x: slice_col(data, "timestamps"),
//     y: slice_col(data, "AF8"),
//     // type: 'scatter',
//     mode: 'lines',
//     name: 'af8'
//   };
//
//   var lines = [trace1, trace2]
//
//   var layout = {
//     title:'Muse data',
//     width: 800,
//     height: 500,
//     xaxis: {
//       title: 'Tiempo (s)',
//       showline: true,
//       showgrid: true,
//       showticklabels: true,
//       linewidth: 2,
//       autotick: false,
//       ticks: 'outside',
//       tickcolor: 'rgb(204,204,204)',
//       tickwidth: 2,
//       ticklen: 5,
//       tickfont: {
//         family: 'Arial',
//         size: 12,
//         color: 'rgb(82, 82, 82)'
//       }
//     },
//     yaxis: {
//       title: 'Y',
//       autorange: true,
//       showgrid: true,
//       zeroline: false,
//       showline: true,
//       showticklabels: false
//     }
//   };
//
//
//
//   Plotly.newPlot('tester', lines, layout);
//
// };
// var slice_col = function(arr, label){
//   var x = new Array(arr.length);
//   for(var i=0;i<arr.length;i++){
//     x[i] = arr[i][label];
//   }
//   return x;
// };





//
// var crear_grafico = function(data, label){
//   var t = slice_col(data, "timestamps");
//
//   var af7 = slice_col(data, label);
//
//
//   var trace1 = {
//     x: t,
//     y: af7,
//     // type: 'scatter',
//     mode: 'lines',
//     name: label
//   };
//
//   var trace2 = {
//     x: t,
//     y: af8,
//     // type: 'scatter',
//     mode: 'lines+markers',
//     name: 'AF8',
//     marker: {
//       color: 'rgb(128, 0, 128)',
//       size: 8
//     },
//     line: {
//       color: 'rgb(128, 0, 128)',
//       width: 1
//     }
//   };
//
//   var lineas = [trace1, trace2];
//   var layout = {
//     title:'Muse data',
//     width: 800,
//     height: 500,
//     xaxis: {
//       title: 'Tiempo (s)',
//       autorange: true,
//       showline: true,
//       showgrid: true,
//       showticklabels: true,
//       linecolor: 'rgb(204,204,204)',
//       linewidth: 2,
//       autotick: false,
//       ticks: 'outside',
//       tickcolor: 'rgb(204,204,204)',
//       tickwidth: 2,
//       ticklen: 5,
//       tickfont: {
//         family: 'Arial',
//         size: 12,
//         color: 'rgb(82, 82, 82)'
//       }
//     },
//     yaxis: {
//       title: 'Y',
//       autorange: true,
//       showgrid: true,
//       zeroline: false,
//       showline: true,
//       showticklabels: false
//     }
//   };
//
//
//   Plotly.newPlot('tester', [trace1], layout);
//
// };
