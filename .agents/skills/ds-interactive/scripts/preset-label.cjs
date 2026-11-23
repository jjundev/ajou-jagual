const preset = '<select data-action="preset" aria-label="사례">';
const label = '<label>';
const legacy = label + '사례' + preset;
// The legacy tree player removes the first child of the label.
const blankLegacy = label + ' ' + preset;

function addLegacyPresetLabel(html) {
  return html.replace(blankLegacy, legacy).replace(label + preset, legacy);
}

function removeLegacyPresetLabel(html) {
  return html.replace(legacy, blankLegacy);
}

module.exports = {addLegacyPresetLabel, removeLegacyPresetLabel};
