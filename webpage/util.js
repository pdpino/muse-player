"use strict"

/**
 * Return a randomly generated color
 * source: https://stackoverflow.com/questions/1484506/random-color-generator-in-javascript
 */
function generateRandomColor(){
  const letters = '0123456789ABCDEF';
  let color = '#';

  for (let i = 0; i < 6; i++){
    color += letters[Math.floor(Math.random() * 16)];
  }

  return color;
}

/**
 * Return an array of randomly generated colors
 */
function generateRandomColors(nColors){
  let colorArr = new Array(nColors);

  for(let color = 0; color < nColors; color++){
    colorArr[color] = generateRandomColor();
  }

  return colorArr;
}
