const fs = require('node:fs');
const path = require('node:path');

const RIGHT_PANEL_UI_VERSION = 6;
const marker = '<!-- ds-interactive:right-panel:v1 -->';
const end = '</body></html>';
const read = name => fs.readFileSync(path.join(__dirname, '../assets', name), 'utf8');

// Replace the existing view at build time and recover the exact reviewed bundle on rollback.
const changeRenderers = [
  [`changesList.replaceChildren(...snapshot.writes.map(write => {
        const row = D.el('div', 'change');
        row.append(D.el('strong', '', snapshot.state.cells[write.cellId]?.name || write.cellId),
          D.el('div', '', D.format(write.before) + ' → ' + D.format(write.after)));
        return row;
      }));
      if (!snapshot.writes.length) changesList.append(D.el('p', 'trace-message', '이 단계에서는 저장 값이 바뀌지 않았습니다.'));`,
    'D.renderPanelChanges(changesList, snapshot);'],
  ["q('.changes').replaceChildren(...s.writes.map(w=>{const row=D.el('div','change');row.append(D.el('strong','',s.state.cells[w.cellId]?.name||w.cellId),D.el('div','',`${D.format(w.before)} → ${D.format(w.after)}`));return row;}));if(!s.writes.length)q('.changes').append(D.el('p','trace-message','이 단계에서는 저장 값이 바뀌지 않았습니다.'));", "D.renderPanelChanges(q('.changes'), s);"],
];
const playerMount = '<script>DSInteractive.player=DSInteractive.mount';
const changesMarker = '<!-- ds-interactive:panel-changes -->';

function addPanelChanges(html) {
  const mount = html.lastIndexOf(playerMount);
  const renderer = changeRenderers.find(([original]) => html.includes(original));
  if (mount < 0 || !renderer || html.includes(changesMarker)) throw Error('PANEL_CHANGES_MARKUP');
  const [original, updated] = renderer;
  return html.slice(0, mount).replace(original, updated) + changesMarker + '\n<script>' +
    read('panel-changes.js') + '</script>\n' + html.slice(mount);
}

function removePanelChanges(html) {
  const position = html.lastIndexOf(changesMarker);
  const mount = html.lastIndexOf(playerMount);
  const renderer = changeRenderers.find(([,updated]) => html.includes(updated));
  if (position < 0 || mount < position || !renderer) throw Error('PANEL_CHANGES_MISSING');
  const [original, updated] = renderer;
  return html.slice(0, position).replace(updated, () => original) + html.slice(mount);
}

function addRightPanel(html, summary = '') {
  const position = html.lastIndexOf(end);
  if (position < 0 || html.includes(marker)) throw Error('RIGHT_PANEL_MARKUP');

  const copy = summary.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  const markup = marker + '\n<style>' + read('right-panel.css') + '</style>\n' +
    '<span id="interactive-example-copy" hidden>' + copy + '</span>\n<script>' +
    read('right-panel.js') + '</script>\n';
  return addPanelChanges(html.slice(0, position)) + markup + html.slice(position);
}

function removeRightPanel(html) {
  const position = html.lastIndexOf(marker);
  const closing = html.lastIndexOf(end);
  if (position < 0 || closing < position) throw Error('RIGHT_PANEL_MISSING');
  return removePanelChanges(html.slice(0, position)) + html.slice(closing);
}

module.exports = {RIGHT_PANEL_UI_VERSION, addRightPanel, removeRightPanel};
