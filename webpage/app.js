"use strict"

const DATA_URL = "http://localhost:8001/stream";

// DEPRECATED: TODO: pass them to server available configurations
// const eegGraphConfig = {
//   channelNames: ["TP9", "AF7", "AF8", "TP10", "Right Aux"],
//   colors: ["black", "red", "blue", "green", "cyan"],
//   title: 'EEG electrodes',
//   yAxisLabel: 'Raw signal (mV)',
// }
//
// const wavesGraphConfig = {
//   channelNames: ["delta", "theta", "alpha", "beta", "gamma"],
//   colors: ["blue", "orange", "red", "green", "magenta"],
//   title: 'Waves',
//   yAxisLabel: 'Power (dB)',
// }
//
// const feelRelaxConcGraphConfig = {
//   channelNames: ["relaxation", "concentration"],
//   colors: ["blue", "red"],
//   title: 'State of mind',
//   yAxisLabel: 'Measure of state',
// }
//
// const feelValAroGraphConfig = {
//   channelNames: ["arousal", "valence"],
//   colors: ["blue", "red"],
//   title: 'Emotion',
//   yAxisLabel: 'Measure of emotion',
// }

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

  $("#btn-start-conn").click(function(){
    stream.start();
  });

  $("#btn-close-conn").click(function(){
    if(!graph.isReady) return;
    stream.close();
    graph.initEmptyData();
  });

  stream.start();

  console.log("All set");
});
