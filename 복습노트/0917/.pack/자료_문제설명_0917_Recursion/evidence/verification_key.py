"""Source-key mapping without authoring side effects."""
import re
def key(q):
    s = q['source']
    txt = q['conditions_html']
    if s.startswith('textbook-'):
        return s.removeprefix('textbook-')
    if s == '2019-mid-q8':
        return 'foo'
    if s == '2018-mid-c024-q15':
        return 'gcd'
    if s == '2018-mid-c102-q1':
        return 'recursion'
    if s == '2017-mid-c050-q11':
        return 'binary'
    if s == '2019-mid-q9':
        return 'broken-loop'
    if s == '2018-mid-c024-q8':
        return 'tri' + re.search('k\\s*&lt;\\s*(\\d+)', txt)[1] if '&lt;' in txt else 'tri' + re.search('k\\s*<\\s*(\\d+)', txt)[1]
    if s == 'unk-final-ltk-q1':
        return 'four' + re.search('k\\s*(?:&lt;|<)\\s*(\\d+)', txt)[1]
    return s
