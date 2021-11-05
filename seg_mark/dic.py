"""
本文件进行对数据（包括词典数据和HMM维特比算法数据）的整理
"""
import re

def merge_dic(path1, path2, path='data/dict.txt'):
    """
    将词典文件(path1)与完成分词的文章(path2)合并
    """
    dic = {}
    with open(path1, 'r') as f:  # 读取词典，存入dic中
        while True:
            line = f.readline().strip(' ').strip('\n')  # 逐行读入字典，防止内存不够
            if len(line) == 0:
                break
            word, freq, _ = line.split()
            freq = eval(freq)
            dic[word] = freq
    with open(path2, 'r') as f:  # 向dic中加数据
        while True:
            line = f.readline().strip(' ').strip('\n')
            if len(line) == 0:
                break
            line = line.split(' ')
            for word in line:
                if len(word) == 1:
                    continue
                if dic.get(word):
                    dic[word] = dic[word] + 1
                else:
                    dic[word] = 2
    with open(path, 'w') as f:  # 将dic写回文件
        for item in dic.items():
            word = str(item[0])
            freq = str(item[1])
            f.write(word + ' ' + freq + '\n')

def get_prob(path='./data/pos.txt', pos_ch='data/character.txt',\
    pos_start='data/pos_start.txt', pos_trans='data/pos_trans.txt', pos_emit='data/pos_emit.txt',\
    seg_start='data/seg_start.txt', seg_trans='data/seg_trans.txt', seg_emit='data/seg_emit.txt'
    ):
    """
    根据完成分词和标注的文件(path)，计算出未登陆词分词(final_seg)和词性标注(mark)的维特比算法所需要的数据
    """
    character_dic = {}  # P(pos|character)
    pos_start_dic = {}  # P(pos|first word)
    pos_trans_dic = {}  # P(pos|previous pos)
    pos_emit_dic = {}   # P(pos|word)
    seg_start_dic = {}  # P(type|first character)
    seg_trans_dic = {}  # P(type|previous type)
    seg_emit_dic = {}   # P(type|character)
    with open(path, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().strip(' ').strip('\n')
            if len(line) == 0:
                break
            line = line.split(' ')
            first = True
            last_pos = None
            last = 'E'
            for pair in line:
                if len(pair) == 0 or pair[0].isdigit():
                    continue
                if len(pair.split('/')) != 2:
                    continue
                [word, pos] = pair.split('/')
                if len(word) == 0:
                    continue
                pos_emit_dic[(word, pos)] = pos_emit_dic.get((word, pos), 0) + 1
                if first:
                    first = False
                    pos_start_dic[pos] = pos_start_dic.get(pos, 0) + 1
                else:
                    pos_trans_dic[(last_pos, pos)] = pos_trans_dic.get((last_pos, pos), 0) + 1
                last_pos = pos
                for ch in word:
                    character_dic[(ch, pos)] = character_dic.get((ch, pos), 0) + 1
                if len(word) == 1:
                    seg_trans_dic[(last, 'S')] = seg_trans_dic.get((last, 'S'), 0) + 1
                    last = 'S'
                    seg_start_dic['S'] = seg_start_dic.get('S', 0) + 1
                    seg_emit_dic[(word, 'S')] = seg_emit_dic.get((word, 'S'), 0) + 1
                else:
                    seg_trans_dic[(last, 'B')] = seg_trans_dic.get((last, 'B'), 0) + 1
                    last = 'E'
                    seg_start_dic['B'] = seg_start_dic.get('B', 0) + 1
                    seg_emit_dic[(word[0], 'B')] = seg_emit_dic.get((word[0], 'B'), 0) + 1
                    last_type = 'B'
                    for i in range(1, len(word)):
                        if i == len(word) - 1:
                            seg_emit_dic[(word[i], 'E')] = seg_emit_dic.get((word[i], 'E'), 0) + 1 
                            seg_trans_dic[(last_type, 'E')] = seg_trans_dic.get((last_type, 'E'), 0) + 1
                        else:
                            seg_emit_dic[(word[i], 'M')] = seg_emit_dic.get((word[i], 'M'), 0) + 1  
                            seg_trans_dic[(last_type, 'M')] = seg_trans_dic.get((last_type, 'M'), 0) + 1
                        last_type = 'M'
    with open(pos_ch, 'w') as f:
        character_dic = sorted(character_dic.items(), key=lambda x:x[0][0])
        for item in character_dic:
            f.write(str(item[0][0]) + ' ' + str(item[0][1]) + ' ' + str(item[1]) + '\n')
    with open(pos_start, 'w') as f:
        pos_start_dic = sorted(pos_start_dic.items(), key=lambda x:x[0])
        for item in pos_start_dic:
            f.write(str(item[0]) + ' ' + str(item[1]) + '\n')
    with open(pos_trans, 'w') as f:
        pos_trans_dic = sorted(pos_trans_dic.items(), key=lambda x:x[0][0])
        for item in pos_trans_dic:
            f.write(str(item[0][0]) + ' ' + str(item[0][1]) + ' ' + str(item[1]) + '\n')
    with open(pos_emit, 'w') as f:
        pos_emit_dic = sorted(pos_emit_dic.items(), key=lambda x:x[0][0])
        for item in pos_emit_dic:
            f.write(str(item[0][0]) + ' ' + str(item[0][1]) + ' ' + str(item[1]) + '\n')
    with open(seg_start, 'w') as f:
        seg_start_dic = sorted(seg_start_dic.items(), key=lambda x:x[0])
        for item in seg_start_dic:
            f.write(str(item[0]) + ' ' + str(item[1]) + '\n')
    with open(seg_trans, 'w') as f:
        seg_trans_dic = sorted(seg_trans_dic.items(), key=lambda x:x[0][0])
        for item in seg_trans_dic:
            f.write(str(item[0][0]) + ' ' + str(item[0][1]) + ' ' + str(item[1]) + '\n')
    with open(seg_emit, 'w') as f:
        seg_emit_dic = sorted(seg_emit_dic.items(), key=lambda x:x[0][0])
        for item in seg_emit_dic:
            f.write(str(item[0][0]) + ' ' + str(item[0][1]) + ' ' + str(item[1]) + '\n')

get_prob()