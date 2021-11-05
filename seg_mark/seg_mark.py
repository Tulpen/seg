"""
本文件实现了从文件导入词典、分词和词性标注的基本功能，并定义了其接口
"""
from math import log
import re

class Dictionary(object):

    def __init__(self, path = 'data/dict.txt'):
        self.dic = {}
        self.read(path)
        self.seg_start = {}
        self.seg_trans = {}
        self.seg_emit = {}
        self.pos_start = {}
        self.pos_trans = {}
        self.pos_emit = {}

    def read(self, path='data/dict.txt'):
        """
        从文件中读取词典到self.dic中
        """
        with open(path, 'r') as f:
            while True:
                line = f.readline().strip(' ').strip('\n')  # 逐行读入字典，防止内存不够
                if len(line) == 0:
                    break
                word, freq = line.split()
                freq = eval(freq)
                # print(word, freq, pos)
                self.dic[word] = freq
    
    def read_seg_HMM(self, seg_start='data/seg_start.txt', seg_trans='data/seg_trans.txt', seg_emit='data/seg_emit.txt'):
        """
        从文件中读取用于分词的HMM模型
        """
        with open(seg_start, 'r') as f:
            sum = 0
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break 
                pow, freq = line.split()
                freq = eval(freq)
                sum = sum + freq
                self.seg_start[pow] = freq
            for item in self.seg_start.items():
                self.seg_start[item[0]] = log(item[1]) - log(sum)
                # print(self.seg_start[item[0]])
        with open(seg_trans, 'r') as f:
            sum = 0
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break 
                pre, now, freq = line.split()
                freq = eval(freq)
                sum = sum + freq
                # print(pow, freq)
                self.seg_trans[(pre, now)] = freq
            for item in self.seg_trans.items():
                self.seg_trans[item[0]] = log(item[1]) - log(sum)
                # print(self.seg_trans[item[0]])
        with open(seg_emit, 'r') as f:
            freq_dic = {}
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break 
                ch, pow, freq = line.split()
                freq = eval(freq)
                freq_dic[ch] = freq_dic.get(ch, 0) + freq
                # print(pow, freq)
                self.seg_emit[(ch, pow)] = freq
            for item in self.seg_emit.items():
                self.seg_emit[item[0]] = log(item[1]) - log(freq_dic[item[0][0]])
                # print(item[0][0], item[0][1], self.seg_emit[item[0]])

    def read_pos_HMM(self, pos_start='data/pos_start.txt', pos_trans='data/pos_trans.txt', pos_emit='data/pos_emit.txt'):
        """
        从文件中读取用于词性标注的HMM模型
        """
        with open(pos_start, 'r') as f:
            sum = 0
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break
                if len(line) != 2:
                    continue
                pow, freq = line.split()
                freq = eval(freq)
                sum = sum + freq
                self.pos_start[pow] = freq
            for item in self.pos_start.items():
                self.pos_start[item[0]] = log(item[1]) - log(sum)
                # print(item[0], self.pos_start[item[0]])
        with open(pos_trans, 'r') as f:
            sum = 0
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break
                if len(line.split()) < 3:
                    continue
                pre, now, freq = line.split()
                freq = eval(freq)
                sum = sum + freq
                # print(pow, freq)
                self.pos_trans[(pre, now)] = freq
            for item in self.pos_trans.items():
                self.pos_trans[item[0]] = log(item[1]) - log(sum)
                # print(item[0][0], item[0][1], self.pos_trans[item[0]])
        with open(pos_emit, 'r') as f:
            freq_dic = {}
            while True:
                line = f.readline().strip(' ').strip('\n')
                if len(line) == 0:
                    break
                if len(line.split()) != 3:
                    continue
                ch, pow, freq = line.split()
                freq = eval(freq)
                freq_dic[ch] = freq_dic.get(ch, 0) + freq
                # print(pow, freq)
                self.pos_emit[(ch, pow)] = freq
            for item in self.pos_emit.items():
                self.pos_emit[item[0]] = log(item[1]) - log(freq_dic[item[0][0]])
                # print(item[0][0], item[0][1], self.pos_emit[item[0]])

    def stats(self, word=None):
        """
        获取单词再字典中出现的次数
        返回：
            单词出现的次数
        """
        if word == None:  # 总词数
            return sum(x for x in self.dic.values())
        else:  # 某一词语的数量
            return self.dic[word]

    def seg(self, sentence):
        """
        查找句子中所有在字典里的词
        返回：
            一个列表，其所有元素为一个2元元组，记录词的开始和结束位置
        """
        seg_set = []
        l = len(sentence)
        for i in range(l):
            for j in range(i, l):
                seg = sentence[i:j+1]
                # print(seg)
                if(self.dic.get(seg) is not None):  # 若词在字典中，则添加
                    seg_set.append((i, j))
        return seg_set

class Worker(object):

    def __init__(self):
        self.dic = Dictionary()
        self.sum = self.dic.stats()
        self.log_sum = log(self.sum)
    
    def log_prob(self, word):
        """
        求出某一词出现次数的对数值，用于计算该词的概率
        返回：
            出现次数的对数值
        """
        freq = self.dic.stats(word)
        return log(freq)

    def pre_seg(self, sentence):
        """
        使用动态规划算法求最大概率的路径实现分词
        对于未登录的词分解为单字，认定其出现次数为1
        返回：
            一个列表，列表中的每个元素为一个字符串（词），表示输入句子的初步分词结果
        """
        seg_set = self.dic.seg(sentence)
        s = '*' + sentence  # 加入一个开始符号方便进行动态规划
        l = len(sentence)
        max_log_prob = [0] * (l+1)  # 第i个位置前的句子的概率的对数值，max_log_prob[0]=0
        pre = [0] * (l+1)  # 取得最大概率的情况下，前一个词的结束位置
        for i in range(1, l+1):
            # 当前字单独成词
            max_log_prob[i] = -self.log_sum + max_log_prob[i-1]  # 取对数，将除法化为减法
            pre[i] = i - 1
            # 当前字与前面的字组合成词
            for word_pos in seg_set:
                begin = word_pos[0] + 1
                end = word_pos[1] + 1
                word = s[begin : end+1]
                if end != i:
                    continue
                if max_log_prob[i] < max_log_prob[begin-1] + self.log_prob(word) - self.log_sum:
                    max_log_prob[i] = max_log_prob[begin-1] + self.log_prob(word) - self.log_sum 
                    pre[i] = begin - 1
        res = []  # 从后往前输出策略
        word_end = l
        while word_end != 0:
            word = s[pre[word_end]+1 : word_end+1]
            res.append(word)
            word_end = pre[word_end]
        return res[::-1]

    def seg_viterbi(self, chars):
        """
        输入一串连续的汉字，使用HMM模型的维特比算法进行二次分词
        返回：
            一个列表，列表中的每个元素为一个字符串（词），表示字串的二次分词结果
        """
        if len(self.dic.seg_start) == 0:
            self.dic.read_seg_HMM()
        inf = 999999999
        state = ['B', 'M', 'E', 'S']  # 定义所有的状态
        prob = {}  # 每一步的每个状态的最大对数概率
        pre = {}  # 由上一步哪一个状态转移过来，用于回溯最大路径
        c = chars[0]
        for s in state:  # 计算概率
            prob[(0, s)] = self.dic.seg_start.get(s, -100) + self.dic.seg_emit.get((c, s), -100)
            pre[(0, s)] = 'BOS'
        for i in range(1, len(chars)):
            c = chars[i]
            for s in state:
                prob[(i, s)] = -inf
                for pre_s in state:
                    tmp = prob[(i-1, pre_s)] + self.dic.seg_trans.get((pre_s, s), -100) + self.dic.seg_emit.get((c, s), -100)
                    if tmp > prob[(i, s)]:
                        prob[(i, s)] = tmp
                        pre[(i, s)] = pre_s
        pow_list = []
        max_prob = -inf
        now = 'EOS'
        for s in state:  # 回溯路径
            if prob[(len(chars)-1, s)] > max_prob:
                max_prob = prob[(len(chars)-1, s)]
                now = s
        pow_list.append(now)
        for i in range(len(chars)-2, -1, -1):
            now = pre[(i+1, now)]
            pow_list.append(now)
        pow_list.reverse()
        res = []
        tmp = ''
        for i in range(len(chars)):
            tmp = tmp + chars[i]
            if pow_list[i] in ['S', 'E']:
                if len(tmp) > 0:
                    res.append(tmp)
                    tmp = ''
        if len(tmp) > 0:
            res.append(tmp)
        return res

    def final_seg(self, words):
        """
        输入初步分词的结果，进行二次分词
        返回：
            一个列表，列表中的每个元素为一个字符串（词），表示二次分词的结果
        """
        res = []
        tmp = []
        for word in words:
            if len(word) > 1:
                if len(tmp) > 0:
                    new_res = self.seg_viterbi(tmp)  # 调用维特比算法
                    tmp.clear()
                    for new_word in new_res:
                        res.append(new_word)
                res.append(word)
            else:
                tmp.append(word)
        if len(tmp) > 0:
            new_res = self.seg_viterbi(tmp)
            for new_word in new_res:
                res.append(new_word)
        return res

    def seg(self, sentence):
        """
        将输入句子分成几个分句，逐一分词
        返回：
            一个列表，列表中的每个元素都是一个列表，表示一个分句 的分词结果
        """
        sentences = re.split('[\,\.\，\。]', sentence)
        res = [self.pre_seg(x) for x in sentences]
        return res

    def mark(self, sentence):
        """
        使用维特比算法对输入的句子进行词性标注，算法类似分词
        返回：
            一个列表，每个元素表示对应位置词的词性
        """
        if len(self.dic.pos_start) == 0:
            self.dic.read_pos_HMM()
        inf = 999999999
        state = ['n', 'nt', 'nd', 'nl', 'nh', 'nhf', 'nhs', 'ns', 'nn', 'ni', 'nz',\
            'v', 'vd', 'vl', 'vu', 'a', 'f', 'm', 'q', 'd', 'r', 'p', 'c', 'u', 'e',\
                'o', 'i', 'j', 'h', 'k', 'g', 'x', 'w', 'ws', 'wu']
        prob = {}
        pre = {}
        word = sentence[0]
        for s in state:
            prob[(0, s)] = self.dic.pos_start.get(s, -100) + self.dic.pos_emit.get((word, s), -100)
            pre[(0, s)] = 'BOS'
        for i in range(1, len(sentence)):
            word = sentence[i]
            for s in state:
                prob[(i, s)] = -inf
                for pre_s in state:
                    tmp = prob[(i-1, pre_s)] + self.dic.pos_trans.get((pre_s, s), -100) + self.dic.pos_emit.get((word, s), -100)
                    if tmp > prob[(i, s)]:
                        prob[(i, s)] = tmp
                        pre[(i, s)] = pre_s
        pos_list = []
        max_prob = -inf
        now = 'EOS'
        for s in state:
            if prob[(len(sentence)-1, s)] > max_prob:
                max_prob = prob[(len(sentence)-1, s)]
                now = s
        pos_list.append(now)
        for i in range(len(sentence)-2, -1, -1):
            now = pre[(i+1, now)]
            pos_list.append(now)
        pos_list.reverse()
        return pos_list

    def work(self, sentence, HMM=True):
        """
        分词和调用接口
        """
        sentences = self.seg(sentence)
        res = []
        for sentence in sentences:
            if HMM:
                sentence = self.final_seg(sentence)
            res.append((sentence, self.mark(sentence)))
        return res

worker = Worker()

def cut(sentence, HMM=True, out=True):
    """
    外部导入运行时的调用接口
    """
    res = worker.work(sentence, HMM)
    if out:
        for s in res:
            print(s[0])
            print(s[1])
    else:
        return res