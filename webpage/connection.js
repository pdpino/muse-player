"use strict"

const StatusEnum = {OFF: 0, CONNECTING: 1, CONNECTED: 2, DISCONNECTED: 3};

class Connection{
  /**
   * Constructor, receives an object with the following attributes
   * @param {String} url url to connect to
   * @param {String} statusText HTML id of the text of the connection message
   * @param {String} statusIcon HTML id of the icon of the connection message
   * @param {function} recvMsg Function to connect to the 'message' event
   * @param {function} recvConfig Function to connect to the 'config' event
   */
  constructor(config){
    this.url = config.url;
    this.stream = null;

    this.statusText = config.statusText;
    this.statusIcon = config.statusIcon;
    this._setStatus(StatusEnum.OFF);

    this.recvMsg = config.recvMsg;
    this.recvConfig = config.recvConfig;
  }

  _isConnecting(){
    return this.status === StatusEnum.CONNECTING;
  }

  _isDisconnected(){
    return this.status === StatusEnum.OFF || this.status === StatusEnum.DISCONNECTED;
  }

  /**
   * Set the status of the connection. Updates the screen with an icon and a text
   */
  _setStatus(status){
    let text = "";
    let icon = "";
    let color = "";

    this.status = status;

    switch (status) {
      case StatusEnum.OFF:
        text = "Off";
        icon = "off";
        color = "black";
        break;
      case StatusEnum.CONNECTING:
        text = "Connecting";
        icon = "hourglass"; // Sand clock
        color = "orange";
        break;
      case StatusEnum.CONNECTED:
        text = "Connected";
        icon = "ok"; // OK ticket
        color = "green";
        break;
      case StatusEnum.DISCONNECTED:
        text = "Disconnected";
        icon = "remove"; // X
        color = "red";
        break;
      default:
        console.log("Status not recognized: ", status);
        return;
    }

    $(this.statusText).text(text);
    $(this.statusText).css("color", color);
    $(this.statusIcon).attr("class", "glyphicon glyphicon-".concat(icon));
  }

  /**
  * Close the connection
  */
  close(){
    if(this._isDisconnected()){ // Ya esta desconectado
      return;
    }

    // Update stream
    if(this.stream !== null){
      if(this.stream.readyState < 2){ // Is not closed
        //States. 0: connecting, 1: ready, 2: closed
        this.stream.close();
      }
    }

    // Change in screen
    this._setStatus(StatusEnum.DISCONNECTED);

    console.log("Connection closed with the server");
  }

  /**
   * Start a connection
   */
  start(){
    if(!this._isDisconnected()){ // Is connecting or connected
      return;
    }

    if(this.stream !== null){
      if(this.stream.readyState === 1){ // Is already connected (but enum not updated)
        //States. 0: connecting, 1: ready, 2: closed
        this._setStatus(StatusEnum.CONNECTED);
        return;
      }
    }

    this._setStatus(StatusEnum.CONNECTING);
    this.stream = new EventSource(this.url);

    this.stream.addEventListener('open', (e) => {
      this._setStatus(StatusEnum.CONNECTED);
      console.log("Connected to the server");
    });

    this.stream.addEventListener('config', (e) => {
      this.recvConfig(e);
    });

    this.stream.addEventListener('message', (e) => {
      this.recvMsg(e);
    });

    this.stream.addEventListener('error', (e) => {
      // TODO: send alert to the user
      if(this._isConnecting()) console.log("Can't connect to the server");
      else console.log("Error in the connection with the server");

      this.close();
    });

  }

}
