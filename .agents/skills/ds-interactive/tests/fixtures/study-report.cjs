// Synthetic evidence for testing the delivery contract. Browser acceptance
// creates the evidence used for publishing actual lessons.
const fs = require('node:fs');
const path = require('node:path');
const {withoutFontHref} = require('../../scripts/fonts.cjs');
const {hash} = require('../../scripts/review.cjs');

function fixtureReport(run) {
  const preview = fs.readFileSync(path.join(run, 'preview.html'), 'utf8');
  const uiVersion = Number(preview.match(/data-ui-version="(\d+)"/)[1]);
  const traces = Object.values(JSON.parse(fs.readFileSync(path.join(run, 'trace.json'))));
  const snapshots = traces.reduce((total, trace) => total + (trace.lineSteps || trace.snapshots).length, 0);
  const viewports = [[1440,900],[1280,800],[1279,800],[375,812],[320,812]];
  if (uiVersion >= 5) viewports.push([720,812],[721,812],[900,812],[901,812]);
  const results = viewports.flatMap(viewport =>
    ['light','dark'].map(theme => ({
      viewport, theme, status: 'pass', ui_version: uiVersion, kind: traces[0].kind,
      preset_label_checked: uiVersion >= 2,
      header_selector_checked: uiVersion >= 3,
      input_behavior_checked: uiVersion >= 3,
      graph_history_checked: uiVersion >= 4 && traces[0].kind === 'c-graph',
      header_layout_checked: uiVersion >= 5,
      header_padding_checked: uiVersion >= 7,
      sha256: hash(preview), build_sha256: hash(withoutFontHref(preview)),
      layout_checked: true, controls_checked: true, presets: traces.length, snapshots_checked: snapshots,
      mobile_first_screen: viewport[0] === 375 ? ['initial','middle','last'] : null,
    })));
  return {status: 'pass', results, console_errors: [], external_requests: []};
}

function fixtureThemeReport(preview) {
  return {
    status: 'pass', build_sha256: hash(withoutFontHref(preview)),
    system: true, storage: true, storage_unavailable: true, cross_tab: true,
  };
}

module.exports = {fixtureReport, fixtureThemeReport};
