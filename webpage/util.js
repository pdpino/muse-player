"use strict"

/**
 * Return an array of randomly generated colors
 * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
 */
function generateRandomColors(nColors){
  function genRandColor(){
    const letters = '0123456789ABCDEF';
    let color = '#';

    for (let i = 0; i < 6; i++){
      color += letters[Math.floor(Math.random() * 16)];
    }

    return color;
  }
  let colorArr = new Array(nColors);

  for(let color = 0; color < nColors; color++){
    colorArr[color] = genRandColor();
  }

  return colorArr;
}
