import tempfile
from pathlib import Path
from browser_acceptance import discover_pages
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 for count in [1,2,4]:
  group=root/str(count);group.mkdir()
  for n in range(count):
   d=group/str(n);d.mkdir();(d/'preview.html').write_text('page')
  assert len(discover_pages(group))==count
  assert discover_pages(group/'0/preview.html')==[(group/'0/preview.html').resolve()]
 course=root/'복습노트/1005';course.mkdir(parents=True);(course/'인터렉티브_01_연결.html').write_text('page');assert len(discover_pages(root))==1
print('browser discovery 1/2/4, direct HTML, date-independent repo: pass')
