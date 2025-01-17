def step(add=False, define=None):
    if define is not None:
        with open("step.txt", mode="wt") as f:
            STEP = 1
            f.write(f"{1}\n")
    try:
        STEP = int(open("step.txt", mode="rt").readline())
    except FileNotFoundError:
        STEP = 1

    if add:
        STEP += 1
        with open("step.txt", mode="wt") as f:
            f.write(f"{STEP}\n")
    return STEP


def yield_scipt_lines():
    with open("data/scipt.txt", mode="rt", encoding='utf-8') as scipt:
        lines = scipt.readlines()
        n = len(lines)
        i = 0
        step(define=1)
        while i < n:
            number, action, who, what = lines[i].split()
            print(lines[i].split())
            if step() < int(number):
                yield []
            if action == 'ADD' and who.isdigit():
                if what == 'LINE':
                    i += 3
                    yield {
                        'who': who,
                        'what': 'LINE',
                        'line': lines[i - 2],
                        'reaction': lines[i - 1]
                    }
                elif what == 'GIFT':
                    i += 4
                    yield {
                        'who': who,
                        'what': 'item',
                        'item': lines[i - 1],
                        'line': lines[i - 3],
                        'reaction': lines[i - 2]
                    }


if __name__ == '__main__':
    for line in yield_scipt_lines():
        pass
