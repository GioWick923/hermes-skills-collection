// antvis_infographic runner (skill copy) — renders an AntV Infographic DSL string to SVG (Node, no browser)
// Modules resolved from the canonical install at tools/antv_infographic/node_modules
const INSTALL = 'C:/Users/<USER>/AppData/Local/hermes/tools/antv_infographic';
const linkedom = require(INSTALL + '/node_modules/linkedom');
const { document, window } = linkedom.parseHTML('<!DOCTYPE html><html><body></body></html>');
for (const [k, v] of Object.entries(linkedom)) { if (!(k in global)) global[k] = v; }
global.document = document; global.window = window || global;
global.SVGElement = linkedom.SVGElement; global.HTMLElement = linkedom.HTMLElement;
const { Infographic, getTemplates } = require(INSTALL + '/node_modules/@antv/infographic');
const fs = require('fs');

function renderInfographic(dsl, outPath) {
  const info = new Infographic();
  info.render(dsl);                 // pass DSL string directly
  const node = info.node;
  if (!node || !node.outerHTML) throw new Error('Infographic.render produced no SVG node');
  const svg = node.outerHTML;
  fs.writeFileSync(outPath, svg);
  return svg.length;
}

module.exports = { renderInfographic, getTemplates };

if (require.main === module) {
  const dsl = process.argv[2], out = process.argv[3] || 'out.svg';
  if (!dsl) { console.error('usage: node render_infographic.js <dsl-file|.dsl-string> <out.svg>'); process.exit(2); }
  const src = fs.existsSync(dsl) ? fs.readFileSync(dsl, 'utf8') : dsl;
  try {
    const len = renderInfographic(src, out);
    console.log('OK svg length=' + len + ' -> ' + out);
  } catch (e) { console.error('ERR', e.message); process.exit(1); }
}
