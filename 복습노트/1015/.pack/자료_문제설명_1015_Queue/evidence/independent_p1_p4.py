"""Independent circular queue trace for explanations p1-p4."""
M = 8

def trace(values, remove, more=()):
    front = rear = 0
    slots = [None] * M
    rows = []
    for value in values:
        assert (rear + 1) % M != front
        rear = (rear + 1) % M
        slots[rear] = value
        rows.append((f'enqueue({value})', front, rear, slots.copy()))
    for _ in range(remove):
        assert front != rear
        front = (front + 1) % M
        value = slots[front]
        slots[front] = None
        rows.append((f'dequeue()={value}', front, rear, slots.copy()))
    for value in more:
        assert (rear + 1) % M != front
        rear = (rear + 1) % M
        slots[rear] = value
        rows.append((f'enqueue({value})', front, rear, slots.copy()))
    assert sum(x is not None for x in slots) == (rear-front+M)%M
    return rows

for name, rows in [
    ('p1', trace(['10','20','30','04','50','60'], 4, ['70','80','90','100'])),
    ('p2a', trace(['10','20','30','40','50'], 3)),
    ('p2b', trace(['10','20','30','40','50'], 3, ['60','70','80','90'])),
]:
    print(name)
    for op, f, r, slots in rows:
        print(op, 'front=', f, 'rear=', r, 'slots=', slots)
print('p3 count=', (5-3+8)%8)
print('p4 empty examples=', [(f,r,f==r) for f,r in [(0,0),(7,7),(3,3),(3,4)]])
print('p4 full example=', ((2+1)%8==3))
