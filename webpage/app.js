"use strict"

const DATA_URL = "http://localhost:8001/stream";

$(document).ready( function() {
  let graphConfig = null;

  const graph = new TimeChart({
    container: "#graph-container",
    legendContainer: '#legend-container',

    // FIXME: que clase cree estos
    xZoomBtn: ["#btn-zoomXdec", "#btn-zoomXinc"],
    yZoomBtn: ["#btn-zoomYin", "#btn-zoomYout"],
    yMoveBtn: ["#btn-moveYdown", "#btn-moveYup"],
    yHomeBtn: "#btn-homeY",
    yAutoUpdate: "#auto-update-y-axis",
    secondsIndicator: "#segX",

    width: 700,
    height: 400,
    yMin: -100,
    yMax: 100,
    xTicks: 5,
    yTicks: 5,
    secondsInScreen: 10,
    dxZoom: 1,
  });

  const recvMsg = function(e){
    if(!graph.isReady) return;
    graph.update(JSON.parse(e.data));
  }

  const recvConfig = function (e){
    graph.setGraphType(JSON.parse(e.data));
    graph.initEmptyData();
  }

  const stream = new Connection({
    url: DATA_URL,
    statusText: "#status-text",
    statusIcon: "#status-icon",
    recvMsg,
    recvConfig,
  });

  const streamAcc = new Connection({
    url: "http://localhost:8001/acc",
    recvMsg: (e) => {
      let data = JSON.parse(e.data);
      $("#acc-data-x").text(data.x.toFixed(3));
      $("#acc-data-y").text(data.y.toFixed(3));
      $("#acc-data-z").text(data.z.toFixed(3));
    },
    recvConfig: (e) => {}, // console.log("CONFIG RECEIVED: ", e.data),
  });

  $("#btn-start-conn").click(function(){
    stream.start();
    // streamAcc.start();
  });

  $("#btn-close-conn").click(function(){
    // streamAcc.close();

    if(!graph.isReady) return;
    stream.close();
    graph.initEmptyData();
  });

  stream.start();
  // streamAcc.start();

  console.log("All set");
});
