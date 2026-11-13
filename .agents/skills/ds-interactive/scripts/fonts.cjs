const fs = require('node:fs');
const path = require('node:path');

const stylesheet = path.resolve(__dirname, '../../../../복습노트/_assets/problem-explain/v1/pretendard/pretendard.css');
const fontLink = /(<link rel="stylesheet" data-ds-interactive-font href=")[^"]*(">)/;

function fontHref(directory) {
  const relative = path.relative(fs.realpathSync(directory), fs.realpathSync(stylesheet));
  if (path.isAbsolute(relative)) throw Error('FONT_LINK_DIFFERENT_VOLUME');
  return relative.split(path.sep).map(encodeURIComponent).join('/');
}

function rebaseFont(html, from, to) {
  const link = html.match(fontLink);
  if (!link) return html; // Already-reviewed legacy pages embed their fonts.
  // Refuse to replace a link to a different stylesheet after review.
  if (link[0] !== link[1] + fontHref(from) + link[2]) {
    throw Error('FONT_LINK_MISMATCH');
  }
  return html.replace(fontLink, (_, start, end) => start + fontHref(to) + end);
}

module.exports = {fontHref, rebaseFont};
