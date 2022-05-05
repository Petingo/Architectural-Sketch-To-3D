MODEL_NUM = 5000
START = 0

SETS = ['train', 'val', 'test']
PORTION = [0.8, 0.1, 0.1]


for i, s in enumerate(SETS):
    with open('Building-Dataset/{}.lst'.format(s), 'w') as file:
        for id in range(START, START + int(MODEL_NUM * PORTION[i])):
            file.write(str(id) + '\n')
    START = START + int(MODEL_NUM * PORTION[i])