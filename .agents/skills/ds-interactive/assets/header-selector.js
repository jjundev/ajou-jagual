(() => {
  const app = document.querySelector('#app');
  const header = app.querySelector('.topbar');
  const preset = app.querySelector('[data-action=preset]');
  const fields = [...app.querySelectorAll('[data-input]')];

  // Graph traversal already exposes its single setup selector in the header.
  if (preset.closest('label').hidden) return;

  const label = preset.closest('label');
  if (!header.contains(preset)) {
    label.classList.add('header-case-moved');
    header.insertBefore(label, header.querySelector('[data-action=theme]'));
  }

  const enums = fields.filter(field => field.tagName === 'SELECT' && !field.closest('[hidden]'));
  const {inputs, presets} = DSInteractive.scenario;
  const defaults = Object.fromEntries(inputs.map(field => [field.key, field.default]));
  const cases = new Map([['default', defaults], ...presets.map(item => [item.id, item.input])]);
  const combinations = new Map();
  const savedLabels = new Set([...preset.options].map(option => option.label));
  let nextChoice = 0;

  if (enums.length) {
    const configuration = enums[0].closest('.configuration');
    const addOptions = (index, values, names, parent) => {
      if (index === enums.length) {
        let id;
        do { id = 'header-choice-' + nextChoice++; } while (cases.has(id));
        combinations.set(id, values);
        const caption = names.join(' · ');
        const option = new Option(savedLabels.has(caption) ? caption + ' · 입력 유지' : caption, id);
        option.dataset.headerChoice = '';
        parent.append(option);
        return;
      }
      const field = enums[index];
      for (const option of field.options) {
        addOptions(index + 1, [...values, option.value], [...names, option.label], parent);
      }
    };

    if (enums.length === 1) {
      const group = document.createElement('optgroup');
      group.label = enums[0].getAttribute('aria-label');
      addOptions(0, [], [], group);
      preset.append(group);
    } else {
      for (const option of enums[0].options) {
        const group = document.createElement('optgroup');
        group.label = option.label;
        addOptions(1, [option.value], [option.label], group);
        preset.append(group);
      }
    }

    for (const field of enums) field.closest('label').hidden = true;
    if (!fields.some(field => configuration.contains(field) && !field.closest('[hidden]'))) {
      configuration.hidden = true;
    }
  }

  if (!fields.some(field => !field.closest('[hidden]')) && !combinations.size) return;
  let custom = [...preset.options].find(option => option.disabled && option.value === 'custom');
  if (!custom) {
    let id = 'custom';
    while (cases.has(id)) id += '-';
    custom = new Option('직접 설정', id);
    custom.disabled = true;
    preset.append(custom);
  }

  const matchesInput = input => input && fields.every(field =>
    field.value === String(input[field.dataset.input]));

  function sync(preferred = preset.value) {
    if (matchesInput(cases.get(preferred))) {
      preset.value = preferred;
      return;
    }
    const match = [...cases].find(([, input]) => matchesInput(input));
    const context = enums.map(field => field.selectedOptions[0]?.label).filter(Boolean);
    custom.textContent = ['직접 설정', ...context].join(' · ');
    preset.value = match?.[0] ?? custom.value;
  }

  preset.addEventListener('change', event => {
    const choice = preset.value;
    const values = combinations.get(choice);
    if (!values) return;
    event.stopImmediatePropagation();
    for (const [index, field] of enums.entries()) {
      if (field.value === values[index]) continue;
      field.value = values[index];
      field.dispatchEvent(new Event('change', {bubbles: true}));
    }
    preset.value = choice;
  }, {capture: true});

  // The player updates the backing controls synchronously before these listeners.
  app.addEventListener('change', event => {
    if (event.target.matches('[data-input]')) sync();
  });
  app.addEventListener('input', event => {
    if (event.target.matches('input[data-input]')) sync();
  });
  app.addEventListener('click', event => {
    if (event.target.closest('[data-mode-value]')) sync();
  });
})();
