(function () {
  const panel = document.querySelector('#panel-right');
  const changes = panel.querySelector('.changes');
  if (changes) {
    const container = changes.parentElement;
    const title = document.createElement('h3');
    title.className = 'panel-changes-title';
    title.textContent = container.firstElementChild.textContent;

    if (container.matches('details')) {
      const section = document.createElement('section');
      section.className = 'panel-changes';
      section.append(title, changes);
      container.replaceWith(section);
    } else {
      container.firstElementChild.replaceWith(title);
    }
  }

  const example = panel.querySelector('.tree-example, .provenance');
  const summary = example.querySelector('summary');
  const oldTakeaway = panel.querySelector('.takeaway');
  const copy = document.querySelector('#interactive-example-copy').textContent.trim() ||
    DSInteractive.scenario.takeaway?.trim();

  oldTakeaway?.closest('section').remove();
  if (!copy) {
    example.remove();
    return;
  }

  summary.textContent = '예제 정보';
  const message = document.createElement('p');
  message.className = 'example-summary';
  message.textContent = copy;
  example.replaceChildren(summary, message);
}());
