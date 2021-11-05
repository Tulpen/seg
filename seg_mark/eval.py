"""
本文件实现对分词和词性标注模型的评价
"""
import seg_mark
from seg_mark import cut

def read(path='data/eval_data.txt'):
    """
    读取测试语料库，使用yield函数完成格式化输出
    返回：
        sentence 整句
        words 正确的分词结果
        types B、M、E、S类型
        pos 正确的词性
    """
    with open(path, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().strip(' ').strip('\n')
            if len(line) == 0:
                break
            line = line.split(' ')
            sentence = ''
            words = []
            types = []
            POS = []
            for pair in line:
                if len(pair) == 0 or pair[0].isdigit():
                    continue
                if len(pair.split('/')) != 2:
                    continue
                [word, pos] = pair.split('/')
                if len(word) == 0:
                    continue
                if word in [',', '.', '，', '。']:
                    continue
                sentence = sentence + word
                words.append(word)
                POS.append(pos)
                if len(word) == 1:
                    types.append('S')
                else:
                    types.append('B')
                    for i in range(len(word) - 2):
                        types.append('M')
                    types.append('E')
            yield sentence, words, types, POS

seg_eval = {}  # seg_eval['B', 'B'] 模型判断是B，真值是'B‘的汉字出现的次数
pos_eval = {}  # pos_eval['n', 'n'] 模型判断是n，真值是'n'的词出现的次数

def get_stats(path='data/eval_data.txt'):
    '''
    调用read函数并分析统计数据，求得seg_eval和pos_eval的值
    '''
    cnt = 0
    for sentence, t_words, t_types, t_pos in read(path):
        print(cnt)
        cnt = cnt + 1
        if cnt == 1000:
            break
        words = seg_mark.worker.pre_seg(sentence)
        words = seg_mark.worker.final_seg(sentence)
        types = []
        for word in words:
            if len(word) == 1:
                types.append('S')
            else:
                types.append('B')
                for i in range(len(word) - 2):
                    types.append('M')
                types.append('E') 
        pos = seg_mark.worker.mark(t_words)
        for test, predict in zip(t_types, types):
            seg_eval[(test, predict)] = seg_eval.get((test, predict), 0) + 1
        for test, predict in zip(t_pos, pos):
            pos_eval[(test, predict)] = pos_eval.get((test, predict), 0) + 1

def evaluate_seg():
    state = ['B', 'M', 'E', 'S']
    for s in state:
        correct = 0
        real = 0
        judge = 0
        for item in seg_eval.items():
            test, predict, freq = item[0][0], item[0][1], item[1]
            if predict == s:
                judge = judge + freq
            if test == s:
                real = real + freq
            if test == s and predict == s:
                correct = correct + freq
        judge = max(judge, 1)
        real = max(real, 1)
        correct = max(correct, 1)
        P = correct / judge
        R = correct / real
        F1 = P * R * 2 / (P + R)
        print(s + ':')
        print('P = {}, R = {}, F1 = {}'.format(P, R, F1))

def evaluate_pos():
    state = ['n', 'nt', 'nd', 'nl', 'nh', 'nhf', 'nhs', 'ns', 'nn', 'ni', 'nz',\
            'v', 'vd', 'vl', 'vu', 'a', 'f', 'm', 'q', 'd', 'r', 'p', 'c', 'u', 'e',\
            'o', 'i', 'j', 'h', 'k', 'g', 'x', 'w', 'ws', 'wu']
    for s in state:
        correct = 0
        real = 0
        judge = 0
        for item in pos_eval.items():
            test, predict, freq = item[0][0], item[0][1], item[1]
            if predict == s:
                judge = judge + freq
            if test == s:
                real = real + freq
            if test == s and predict == s:
                correct = correct + freq
        judge = max(judge, 1)
        real = max(real, 1)
        correct = max(correct, 1)
        P = correct / judge
        R = correct / real
        F1 = P * R * 2 / (P + R)
        print(s + ':')
        print('P = {}, R = {}, F1 = {}'.format(P, R, F1))

get_stats()
evaluate_seg() 
evaluate_pos()