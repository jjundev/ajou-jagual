const fs = require('node:fs');
const path = require('node:path');

const HEADER_SELECTOR_VERSION = 1;
const marker = '<!-- ds-interactive:header-selector:v1 -->';
const end = '</body></html>';
const read = name => fs.readFileSync(path.join(__dirname, '../assets', name), 'utf8');

function addHeaderSelector(html) {
  const index = html.lastIndexOf(end);
  if (index < 0 || html.includes(marker)) throw Error('HEADER_SELECTOR_MARKUP');
  const addition = marker + '\n<style>' + read('header-selector.css') + '</style>\n<script>' +
    read('header-selector.js') + '</script>\n';
  return html.slice(0, index) + addition + html.slice(index);
}

function removeHeaderSelector(html) {
  const index = html.lastIndexOf(marker);
  const closing = html.lastIndexOf(end);
  if (index < 0 || closing < index) throw Error('HEADER_SELECTOR_MISSING');
  return html.slice(0, index) + html.slice(closing);
}

module.exports = {HEADER_SELECTOR_VERSION, addHeaderSelector, removeHeaderSelector};
