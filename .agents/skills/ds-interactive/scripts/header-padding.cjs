const fs = require('node:fs');
const path = require('node:path');

const HEADER_PADDING_VERSION = 1;
const marker = '<!-- ds-interactive:header-padding:v1 -->';
const end = '</body></html>';

function addHeaderPadding(html) {
  const position = html.lastIndexOf(end);
  if (position < 0 || html.includes(marker)) throw Error('HEADER_PADDING_MARKUP');
  const styles = ['header.css', 'archived-header.css'].map(file =>
    fs.readFileSync(path.join(__dirname, '../assets/ui/v7', file), 'utf8')).join('\n');
  return html.slice(0, position) + marker + '\n<style>' + styles + '</style>\n' + html.slice(position);
}

function removeHeaderPadding(html) {
  const position = html.lastIndexOf(marker);
  const closing = html.lastIndexOf(end);
  if (position < 0 || closing < position) throw Error('HEADER_PADDING_MISSING');
  return html.slice(0, position) + html.slice(closing);
}

module.exports = {HEADER_PADDING_VERSION, addHeaderPadding, removeHeaderPadding};
