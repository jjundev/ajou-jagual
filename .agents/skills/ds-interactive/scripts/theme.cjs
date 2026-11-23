const fs = require('node:fs');

const CURRENT_THEME_VERSION = 1;
const titleEnd = '</title>';
const themeScript = '<script id="interactive-theme">' +
  fs.readFileSync(require.resolve('../assets/theme.js'), 'utf8') + '</script>';

function addTheme(html) {
  if (!html.includes(titleEnd) || html.includes('id="interactive-theme"')) {
    throw Error('THEME_INSERTION_FAILED');
  }
  return html.replace(titleEnd, titleEnd + themeScript);
}

function removeTheme(html) {
  return html.replace(titleEnd + themeScript, titleEnd);
}

module.exports = {CURRENT_THEME_VERSION, addTheme, removeTheme};
