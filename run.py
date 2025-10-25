import sys
import heapq
from typing import List, Tuple, Dict, Optional

HALL_LEN = 11
ROOM_POS = [2, 4, 6, 8]
TYPES = ('A', 'B', 'C', 'D')
COST = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}

def parse_input(lines: List[str]):
    # Собираем строки комнат между 3-й строкой и нижней "#########"
    room_rows: List[str] = []
    bottom_idx: Optional[int] = None
    for i, row in enumerate(lines):
        if row.strip() == "#########":
            bottom_idx = i
            break
    if bottom_idx is None:
        bottom_idx = len(lines)
    for row in lines[2:bottom_idx]:
        if any(ch in row for ch in TYPES):
            room_rows.append(row)

    depth = len(room_rows)
    if depth == 0:
        raise ValueError("Некорректный ввод: не найдены строки комнат")

    rooms = [[] for _ in range(4)]
    for r in range(depth):
        row = room_rows[r]
        for j, idx in enumerate((3, 5, 7, 9)):
            rooms[j].append(row[idx])
    rooms_t = tuple(tuple(col) for col in rooms)

    hallway_row = lines[1]
    hallway = tuple(hallway_row[1:1 + HALL_LEN])
    return hallway, rooms_t, depth

def is_room_clean(room_idx: int, room: Tuple[str, ...]) -> bool:
    target = TYPES[room_idx]
    return all(ch == '.' or ch == target for ch in room)

def target_room_idx(ch: str) -> int:
    return TYPES.index(ch)

def path_clear(hall: Tuple[str, ...], i: int, j: int) -> bool:
    if i == j:
        return True
    if i < j:
        rng = range(i + 1, j + 1)
    else:
        rng = range(j, i)
    for k in rng:
        if hall[k] != '.':
            return False
    return True

def solved_state(depth: int) -> Tuple:
    hall = tuple('.' for _ in range(HALL_LEN))
    rooms = tuple(tuple(TYPES[i] for _ in range(depth)) for i in range(4))
    return (hall, rooms)

def moves_from_state(hall: Tuple[str, ...], rooms: Tuple[Tuple[str, ...], ...]):
    res = []
    depth = len(rooms[0])

    # 1) Ходы из коридора в целевые комнаты
    for hpos, ch in enumerate(hall):
        if ch == '.':
            continue
        r_idx = target_room_idx(ch)
        door = ROOM_POS[r_idx]
        if path_clear(hall, hpos, door) and is_room_clean(r_idx, rooms[r_idx]):
            room = rooms[r_idx]
            if '.' in room:
                dest_depth = depth - 1 - room[::-1].index('.')
                steps = abs(hpos - door) + dest_depth + 1
                energy = steps * COST[ch]
                new_hall = list(hall)
                new_hall[hpos] = '.'
                new_rooms = [list(r) for r in rooms]
                new_rooms[r_idx][dest_depth] = ch
                res.append((energy, (tuple(new_hall), tuple(tuple(r) for r in new_rooms))))

    # 2) Ходы из комнат в коридор
    for r_idx in range(4):
        room = rooms[r_idx]
        door = ROOM_POS[r_idx]
        target = TYPES[r_idx]

        # Находим верхнего амфипода, которого нужно двигать
        top_idx = None
        for i in range(depth):
            if room[i] != '.':
                top_idx = i
                break
        if top_idx is None:
            continue  # пусто

        ch = room[top_idx]
        # Если сверху до низа стоят только целевые (и текущий — целевой), не двигаем
        if ch == target and all((c == target) for c in room[top_idx:]):
            continue

        # Влево
        for hpos in range(door - 1, -1, -1):
            if hall[hpos] != '.':
                break
            if hpos in ROOM_POS:
                continue
            steps = (top_idx + 1) + abs(hpos - door)
            energy = steps * COST[ch]
            new_hall = list(hall)
            new_hall[hpos] = ch
            new_rooms = [list(r) for r in rooms]
            new_rooms[r_idx][top_idx] = '.'
            res.append((energy, (tuple(new_hall), tuple(tuple(r) for r in new_rooms))))

        # Вправо
        for hpos in range(door + 1, HALL_LEN):
            if hall[hpos] != '.':
                break
            if hpos in ROOM_POS:
                continue
            steps = (top_idx + 1) + abs(hpos - door)
            energy = steps * COST[ch]
            new_hall = list(hall)
            new_hall[hpos] = ch
            new_rooms = [list(r) for r in rooms]
            new_rooms[r_idx][top_idx] = '.'
            res.append((energy, (tuple(new_hall), tuple(tuple(r) for r in new_rooms))))

    return res

def dijkstra(start_state: Tuple, depth: int) -> int:
    goal = solved_state(depth)
    pq = [(0, start_state)]
    best: Dict[Tuple, int] = {start_state: 0}
    while pq:
        cost, state = heapq.heappop(pq)
        if state == goal:
            return cost
        if cost != best.get(state, float('inf')):
            continue
        hall, rooms = state
        for move_cost, new_state in moves_from_state(hall, rooms):
            new_cost = cost + move_cost
            if new_cost < best.get(new_state, float('inf')):
                best[new_state] = new_cost
                heapq.heappush(pq, (new_cost, new_state))
    return -1

def solve(lines: List[str]) -> int:
    hall, rooms, depth = parse_input(lines)
    start = (hall, rooms)
    return dijkstra(start, depth)

def main():
    lines = [line.rstrip("\n") for line in sys.stdin]
    print(solve(lines))

if __name__ == "__main__":
    main()
