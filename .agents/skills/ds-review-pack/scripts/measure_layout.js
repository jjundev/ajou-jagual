(root, scroller) => {
  const excluded = '.katex-mathml, svg.icon, button svg[aria-hidden="true"]';
  const localScroll = '.figure-scroll, .table-wrap, pre, .katex-display';
  const visible = element => element.getClientRects().length > 0 &&
    getComputedStyle(element).visibility === 'visible' && !element.closest(excluded);
  const hasIndependentScroll = element => {
    const wrapper = element.closest(localScroll);
    return wrapper && root.contains(wrapper) && /^(auto|scroll)$/.test(getComputedStyle(wrapper).overflowX);
  };

  const boundary = scroller.getBoundingClientRect();
  const left = Math.max(0, boundary.left + scroller.clientLeft);
  const right = Math.min(document.documentElement.clientWidth, boundary.left + scroller.clientLeft + scroller.clientWidth);
  let overflow = 0;
  const compare = rect => {
    if (rect.width > 0) overflow = Math.max(overflow, left - rect.left, rect.right - right);
  };
  for (const element of [root, ...root.querySelectorAll('*')]) {
    if (!visible(element) || element.parentElement.closest('svg') || hasIndependentScroll(element.parentElement)) continue;
    for (const rect of element.getClientRects()) compare(rect);
  }

  // Unwrapped text can leave a block without making the block itself wider.
  const range = document.createRange();
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const parent = node.parentElement;
    if (!node.data.trim() || !visible(parent) || parent.closest('svg') || hasIndependentScroll(parent)) continue;
    range.selectNodeContents(node);
    for (const rect of range.getClientRects()) compare(rect);
  }

  let state = 'no-figure';
  const heights = [];
  const widgetMins = new Map();
  for (const widget of root.querySelectorAll('.widget[id]')) {
    if (visible(widget)) widgetMins.set(widget.id, null);
  }
  for (const figure of root.querySelectorAll('svg, img, canvas, object, embed')) {
    if (!visible(figure)) continue;
    if (figure.tagName !== 'svg' || figure.querySelector('image, foreignObject, use')) state = 'visual-only';
    if (state === 'no-figure') state = 'measured';
    const labels = document.createTreeWalker(figure, NodeFilter.SHOW_TEXT);
    while (labels.nextNode()) {
      const node = labels.currentNode;
      const parent = node.parentElement;
      if (!node.data.trim() || !parent.closest('text') || parent.closest('svg') !== figure || !visible(parent)) continue;
      range.selectNodeContents(node);
      const height = range.getBoundingClientRect().height;
      if (height <= 0) {
        state = 'visual-only';
        continue;
      }
      heights.push(height);
      const widget = parent.closest('.widget[id]');
      if (widget && widgetMins.has(widget.id)) {
        widgetMins.set(widget.id, Math.min(widgetMins.get(widget.id) ?? Infinity, height));
      }
    }
  }
  return {
    state,
    overflow_px: overflow,
    svg_text_count: heights.length,
    min_svg_text_height_px: heights.length ? Math.min(...heights) : null,
    widget_min_svg_text_height_px: Object.fromEntries(widgetMins),
  };
}
