(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function graphHistoryRows(trace, entries, list) {
    const locations = entries.map(entry => entry.executed?.at ?? entry.at);
    const sources = new Map(trace.sources.map(source => [source.id, source.label || source.id]));
    const sourceIds = new Set(locations.map(location => location?.sourceId).filter(Boolean));
    const header = list.previousElementSibling;
    header.hidden = sourceIds.size !== 1;
    header.textContent = header.hidden ? '' : sources.get(sourceIds.values().next().value);

    return entries.map((entry, index) => {
      const location = locations[index];
      const source = sources.get(location?.sourceId);
      const line = location ? location.line + '행' : '';
      const button = D.el('button', 'btn');
      button.type = 'button';
      button.dataset.action = 'step';
      button.dataset.stepIndex = index;
      button.setAttribute('aria-label', [index, source, line, entry.title].filter(value => value != null && value !== '').join(' '));

      const text = D.el('span', 'step-txt');
      const detail = D.el('span', 'graph-history-detail');
      detail.append(D.el('span', 'graph-history-action', entry.title));
      if (source && sourceIds.size > 1) detail.append(D.el('span', 'graph-history-row-source', source));
      text.append(D.el('b', 'graph-history-line', line), detail);
      button.append(D.el('span', 'step-num num', index), text);
      return button;
    });
  }

  function attachGraphHistory(list, syncHistory, signal) {
    const source = D.el('p', 'graph-history-source');
    source.hidden = true;
    list.before(source);
    const observer = new ResizeObserver(syncHistory);
    observer.observe(list);
    signal.addEventListener('abort', () => observer.disconnect(), {once: true});
  }

  D.graphHistoryRows = graphHistoryRows;
  D.attachGraphHistory = attachGraphHistory;
})(globalThis);
