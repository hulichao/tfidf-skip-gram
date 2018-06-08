N=4774
# ��ȡͣ�ʱ�
def stop_words():
    stop_words_file = open('stop_words_ch.txt', 'r')
    stopwords_list = []
    for line in stop_words_file.readlines():
        stopwords_list.append(line.decode('gbk')[:-1])
    return stopwords_list

def jieba_fenci(raw, stopwords_list):
    # ʹ�ý�ͷִʰ��ļ������з�
    word_list = list(jieba.cut(raw, cut_all=False))
    for word in word_list:
        if word in stopwords_list:
            word_list.remove(word)
    # word_set����ͳ��A[nClass]
    word_list.remove('\n')
    word_set = set(word_list)
    return word_list, word_set

def process_file(train_path, test_path):
    '''
    ���������ڴ����������е������ļ��������ش��������õ��ı���
    :param floder_path: ������·��
    :return: A��CHI��ʾ�е�Aֵ��Ƕ���ֵ䡣���ڼ�¼ĳһ���а�������t���ĵ���������һ���ܹ�9��key����Ӧ9�����ŷ���
                �ڶ�������ĳһ�������е��ʼ�������õ��ʵ��ĵ����������ǳ��ִ�������{{1��{��hello����8����hai����7}}��{2��{��apple����8}}}
            TFIDF�����ڼ���TFIDFȨֵ������Ƕ���ֵ䡣��һ���Aһ����keyΪ��𡣵ڶ����keyΪ�ļ���������ʹ���ļ���Ŵ���0-99��.������
                    keyΪ���ʣ�valueΪ�ǵ����ڱ��ļ��г��ֵĴ��������ڼ�¼ÿ��������ÿ���ļ��г��ֵĴ�����
            train_set:ѵ�����������������������7:3�����ֿ�����Ԫ�飨�ĵ��ĵ��ʱ�����ļ���ţ�
            test_set:��������������Ԫ�飨�ĵ��ĵ��ʱ�����ļ���ţ�
    '''
    stopwords_list = stop_words()
    # ���ڼ�¼CHI��ʾ�е�Aֵ
    A = {}
    tf = []
    i=0
    # �洢ѵ����/���Լ�
    count = [0]*11
    train_set = []
    test_set = []
    with open(train_path, 'r') as f:
        for line in f:
            tf.append({})
            label = int(line.split(',')[0])-1
            if label not in A:
                A[label] = {}
            count[label] += 1
            content = ""
            for aa in line.split(',')[1:]:
                content += aa
            word_list, word_set = jieba_fenci(content, stopwords_list)
            train_set.append((word_list, label))
            for word in word_set:
                if A[label].has_key(word):
                    A[label][word] += 1
                else:
                    A[label][word] = 1
            for word in word_list:
                if tf[i].has_key(word):
                    tf[i][word] += 1
                else:
                    tf[i][word] = 1
            i += 1
        print "����������"

    tf2 = []
    j = 0
    with open(test_path, 'r') as g:
        for line in g:
            tf2.append({})
            label = int(line.split(',')[0])-1
            content = ""
            for aa in line.split(',')[1:]:
                content += aa
            word_list, word_set = jieba_fenci(content, stopwords_list)
            test_set.append((word_list, label))
            for word in word_list:
                if tf2[j].has_key(word):
                    tf2[j][word] += 1
                else:
                    tf2[j][word] = 1
            j += 1
    return A, tf, tf2, train_set, test_set, count


def calculate_B_from_A(A):
    '''
    :param A: CHI��ʽ�е�Aֵ
    :return: B��CHI��ְ�е�Bֵ������ĳһ�൫��Ҳ��������t���ĵ���
    '''
    B = {}
    for key in A:
        B[key] = {}
        for word in A[key]:
            B[key][word] = 0
            for kk in A:
                if kk != key and A[kk].has_key(word):
                    B[key][word] += A[kk][word]
    return B

def feature_select_use_new_CHI(A, B, count):
    '''
    ����A��B��C��D��CHI���㹫ʽ���������е��ʵ�CHIֵ���Դ���Ϊ����ѡ������ݡ�
    CHI��ʽ��chi = N*��AD-BC��^2/((A+C)*(B+D)*(A+B)*(C+D))����N,(A+C),(B+D)���ǳ�������ʡȥ��
    :param A:
    :param B:
    :return: ����ѡ�����1000��ά�����б�
    '''
    word_dict = []
    word_features = []
    for i in range(0, 11):
        CHI = {}

        M = N - count[i]
        for word in A[i]:
            #print word, A[i][word], B[i][word]
            temp = (A[i][word] * (M - B[i][word]) - (count[i] - A[i][word]) * B[i][word]) ^ 2 / (
            (A[i][word] + B[i][word]) * (N - A[i][word] - B[i][word]))
            CHI[word] = log(N / (A[i][word] + B[i][word])) * temp
        #ÿһ��������ֻѡ��150��CHI���ĵ�����Ϊ����
        a = sorted(CHI.iteritems(), key=lambda t: t[1], reverse=True)[:100]
        b = []
        for aa in a:
            b.append(aa[0])
        word_dict.extend(b)
        for word in word_dict:
            if word not in word_features:
                word_features.append(word)
    return word_features

def document_features(word_features, TF, data, num):
    '''
    ����ÿһƪ���ŵ���������Ȩ�ء������ļ��ӷִ��б�ת��Ϊ����������ʶ��������������롣
    :param word_features:
    :param TFIDF:
    :param document: �ִ��б��洢��train_set,test_set��
    :param cla: ���
    :param num: �ļ����
    :return: ���ظ��ļ�����������Ȩ��
    '''
    document_words = set(data)
    features = {}
    for i, word in enumerate(word_features):
        if word in document_words:
            features[word] = 1#TF[num][word]#*log(N/(A[cla][word]+B[cla][word]))
        else:
            features[word] = 0
    return features

A, tf, tf2, train_set, test_set, count = process_file('data/training.csv', 'data/testing.csv')
B = calculate_B_from_A(A)
print "��ʼѡ��������"
word_features = feature_select_use_new_CHI(A, B, count)
#print word_features
print len(word_features)
for word in word_features:
    print word

print "��ʼ�����ĵ�����������"
documents_feature = [(document_features
                      (word_features, tf, data[0], i), data[1])
                     for i, data in enumerate(train_set)]

print "���Լ�"
test_documents_feature = [document_features(word_features, tf2, data[0], i)
                          for i, data in enumerate(test_set)]
#�����Ǵ���֮��Ľ�����棬������֮��ѵ��ģ����ֱ�Ӷ�ȡ���ݼ��ɣ�ʡȥ�ظ������ݴ���
json.dump(documents_feature, open('tmp/documents_feature.txt', 'w'))
json.dump(test_documents_feature, open('tmp/test_documents_feature.txt', 'w'))