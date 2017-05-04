// version 4: usa rickshaw

$(document).ready( function() {
  data_1 = [ ];
  data_2 = [ ];
  data_3 = [ ];
  data_4 = [ ];

  //Crear grafico
  var palette = new Rickshaw.Color.Palette();
  var graph = new Rickshaw.Graph( {
          element: document.getElementById("chart"),
          // width: 700,
          // height: 240,
          renderer: 'line',
          series: [
                  {
                          name: "Northeast",
                          data: data_1,
                          color: palette.color()
                  },
                  {
                          name: "Midwest",
                          data: data_2,
                          color: palette.color()
                  },
                  {
                          name: "South",
                          data: data_3,
                          color: palette.color()
                  },
                  {
                          name: "West",
                          data: data_4,
                          color: palette.color()
                  }
          ]
  } );
  var x_axis = new Rickshaw.Graph.Axis.X({ graph: graph });
  var y_axis = new Rickshaw.Graph.Axis.Y( {
    graph: graph,
    orientation: 'left',
    // tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
    element: document.getElementById('y_axis'),
  } );
  var legend = new Rickshaw.Graph.Legend( {
    element: document.getElementById('legend'),
    graph: graph
  } );

  graph.render();


  //Conectarse con server (python) usando Event Source
  var dir = 'http://localhost:8889/data/prueba';
  var stream = new EventSource(dir);
  stream.onopen = function (e) {
     console.log("CONNECTED");
  };

  var i = 0;

  stream.onmessage = function (e) {
    var arr = e.data.split(",");
    var p_x = parseFloat(arr[0]);
    var p_y = parseFloat(arr[1]);

    //REVIEW: algo mas eficiente que push y shift?
    data_1.push({ x: p_x, y: p_y });
    if(data_1.length > 30){
      data_1.shift();
    }

    if(i % 100 == 0){
      console.log(p_x);
    }

    i += 1;
    graph.render();
  };

  stream.onerror = function (e) {
    console.log("ERROR. Closing connection.\nReload the page to reconnect to the server");
    stream.close();
  };

  $("#close-con-btn").click(function(){
    console.log("Closing connection.\nReload the page to reconnect to the server")
    stream.close();
  });

});


//Random data:
// data_1 = [ { x: -1893456000, y: 25868573 }, { x: -1577923200, y: 29662053 }, { x: -1262304000, y: 34427091 }, { x: -946771200, y: 35976777 }, { x: -631152000, y: 39477986 }, { x: -315619200, y: 44677819 }, { x: 0, y: 49040703 }, { x: 315532800, y: 49135283 }, { x: 631152000, y: 50809229 }, { x: 946684800, y: 53594378 }, { x: 1262304000, y: 55317240 } ];
//
// data_2 = [ { x: -1893456000, y: 29888542 }, { x: -1577923200, y: 34019792 }, { x: -1262304000, y: 38594100 }, { x: -946771200, y: 40143332 }, { x: -631152000, y: 44460762 }, { x: -315619200, y: 51619139 }, { x: 0, y: 56571663 }, { x: 315532800, y: 58865670 }, { x: 631152000, y: 59668632 }, { x: 946684800, y: 64392776 }, { x: 1262304000, y: 66927001 } ];
//
// data_3 = [ { x: -1893456000, y: 29389330 }, { x: -1577923200, y: 33125803 }, { x: -1262304000, y: 37857633 }, { x: -946771200, y: 41665901 }, { x: -631152000, y: 47197088 }, { x: -315619200, y: 54973113 }, { x: 0, y: 62795367 }, { x: 315532800, y: 75372362 }, { x: 631152000, y: 85445930 }, { x: 946684800, y: 100236820 }, { x: 1262304000, y: 114555744 } ];
//
// data_4 = [ { x: -1893456000, y: 7082086 }, { x: -1577923200, y: 9213920 }, { x: -1262304000, y: 12323836 }, { x: -946771200, y: 14379119 }, { x: -631152000, y: 20189962 }, { x: -315619200, y: 28053104 }, { x: 0, y: 34804193 }, { x: 315532800, y: 43172490 }, { x: 631152000, y: 52786082 }, { x: 946684800, y: 63197932 }, { x: 1262304000, y: 71945553 } ];
