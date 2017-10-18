"use strict"

const DATA_URL = "http://localhost:8889/data/muse";

const eegGraphConfig = {
  nChannels: 5,
  channelNames: ["TP9", "AF7", "AF8", "TP10", "Right Aux"],
  colors: ["black", "red", "blue", "green", "cyan"],
  title: 'EEG electrodes',
  yAxisLabel: 'Raw signal (mV)',
}

const wavesGraphConfig = {
  nChannels: 5,
  channelNames: ["delta", "theta", "alpha", "beta", "gamma"],
  colors: ["blue", "orange", "red", "green", "magenta"],
  title: 'Waves',
  yAxisLabel: 'Power (dB)',
}

const feelRelaxConcGraphConfig = {
  nChannels: 2,
  channelNames: ["relaxation", "concentration"],
  colors: ["blue", "red"],
  title: 'State of mind',
  yAxisLabel: 'Power (dB)',
}

const feelValAroGraphConfig = {
  nChannels: 2,
  channelNames: ["arousal", "valence"],
  colors: ["blue", "red"],
  title: 'State of mind',
  yAxisLabel: 'Power (dB)',
}

/**
 * Receive a stream of data from a muse server and plots it
 */
$(document).ready( function() {
  let graphConfig = null;

  const graph = new Graph({
    container: "#graph_container",
    legendContainer: '#legend_container',

    // FIXME: que clase cree estos
    xZoomBtn: ["#btn-zoomXdec", "#btn-zoomXinc"],
    yZoomBtn: ["#btn-zoomYin", "#btn-zoomYout"],
    yMoveBtn: ["#btn-moveYdown", "#btn-moveYup"],
    yHomeBtn: "#btn-homeY",
    secondsIndicator: "#segX",

    width: 700,
    height: 400,
    yMin: -100,
    yMax: 100,
    xTicks: 5,
    yTicks: 5,
    secondsInScreen: 5,
    dxZoom: 1, // FIXME: que clase calcule esto y vaya cambiando
    dyZoom: 5,
    dyMove: 50
    });

  const recvMsg = function(e){
    if(!graph.isReady) return;

    let arr = e.data.split(",").map(parseFloat);

    if (arr[0] < 0) { // Ignore negative time
      console.log("ERROR: received negative time");
      return;
    }

    while(arr.length < graphConfig.nChannels + 1){ // Fill with 0s if received less channels
      arr.push(0.0);
    }

    graph.update(arr);
  }

  const recvConfig = function (e){
      switch(e.data) {
        case "eeg":
          graphConfig = eegGraphConfig;
          break;

        case "waves":
          graphConfig = wavesGraphConfig;
          break;

        case "feel":
          graphConfig = feelRelaxConcGraphConfig;
          break;

        case "feelValAro":
          graphConfig = feelValAroGraphConfig;
          break;

        default:
          console.log("Type of graph received from server not recognized: ", e.data);
          return;
      }
      graph.selectType(graphConfig);
      graph.initEmptyData();
    }

  const stream = new Connection({
      url: DATA_URL,
      statusText: "#status-text",
      statusIcon: "#status-icon",
      recvMsg,
      recvConfig,
    });

  $("#btn-start-conn").click( function(){
    stream.start();
  });

  $("#btn-close-conn").click( function(){
    if(!graph.isReady) return;
    stream.close();
    graph.initEmptyData();
  });

  stream.start();

  console.log("All set");
});
