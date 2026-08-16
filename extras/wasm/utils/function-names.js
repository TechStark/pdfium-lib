const fs = require('fs');
const xpath = require('xpath');
const { DOMParser } = require('xmldom');

const inputXmlFilename = process.argv[2];
const extraFunctions = process.argv[3] ? process.argv[3].split(',') : [];
const inputXmlContent = fs.readFileSync(inputXmlFilename, 'utf-8');
const inputDom = new DOMParser().parseFromString(inputXmlContent);
const nodes = xpath.select('//member[@kind="function"]/name/text()', inputDom);

// Additional FPDFText functions for accurate text positioning
// These are needed for PDF editors to get character-level bounding boxes
const additionalFunctions = [
  'FPDFText_GetCharBox',
  'FPDFText_GetLooseCharBox',
  'FPDFText_GetCharOrigin',
  'FPDFText_GetFontSize',
  'FPDFText_GetFontInfo',
  'FPDFText_GetCharAngle',
  'FPDFText_GetCharIndexAtPos',
  'FPDFText_GetTextRenderMode',
  'FPDFText_GetMatrix',
];

const allFunctions = [...nodes.map(node => node.toString()), ...extraFunctions, ...additionalFunctions];

console.log(
  JSON.stringify(allFunctions.map(functionName => '_' + functionName))
);
