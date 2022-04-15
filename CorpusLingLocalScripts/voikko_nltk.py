import nltk
import random
from nltk.sentiment import SentimentAnalyzer
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC

import voikko_string_lemmatizer as fi_str
import voikko_file_lemmatizer as fi_file


# This file uses the nltk classifiers instead of the self-built one
# This does not contain the 'neutral' classifier


# Finnish-specific data!
def get_nltk_training_doc(sent_list, label, ran=2000):
    training_doc = []
    for sent in sent_list[:ran]:
        lemmas = fi_str.lemmatize(sent)
        training_doc.append((lemmas, label))
    print(f'For label {label} training docs fetched, in total {len(training_doc)}.')
    return training_doc


pos_list = fi_file.to_list('pos_list.txt')
neg_list = fi_file.to_list('neg_list.txt')
#neu_list = fi_file.to_list('neu_list.txt')
print('Raw files fetched')

neg_doc = get_nltk_training_doc(neg_list, 'neg')
pos_doc = get_nltk_training_doc(pos_list, 'pos')
#neu_doc = get_nltk_training_doc(neu_list, 'neu')

#pos_lemma = fi_file.lemmatize('pos_list.txt')
#neg_lemma = fi_file.lemmatize('neg_list.txt')
#neu_lemma = fi_file.lemmatize('neu_list.txt')
#print('Lemma list created')
# End of Finnish-specific data


all_training_docs = neg_doc + pos_doc #+ neu_doc
print('Training docs fetched')

#print(all_training_docs[:10])


sentim_analyzer = SentimentAnalyzer()


# Get all words in the dataset
all_words = sentim_analyzer.all_words(all_training_docs)
#all_words = fi_file.to_list('positive_words_fi.txt') + fi_file.to_list('negative_words_fi.txt')
tokens = set(all_words)
print('Tokens created')


# Aux func
# def occurrences_list(search_for_list, word_list):
#     """
#     Tells how many times the word appeared in the word list.
#     :param word: the word to search for
#     :param word_list: list of words to search from
#     :return: int number of occurrences
#     """
#     counter = 0
#     for word in search_for_list:
#         counter += word_list.count(word)
#     print(counter)  # Inspection
#     return counter


# Training data
# train = [({word: int(x[0].count(word) * 10 / len(x[0])) for word in tokens},
#           x[1]) for x in all_training_docs]  # Counting
train = [({word: (word in x[0]) for word in tokens}, x[1]) for x in all_training_docs]  # Binary decision
#train = [({'pos': occurrences_list(x[0], pos_lemma),
           #'neg': occurrences_list(x[0], neg_lemma),
           #'neu': occurrences_list(x[0], neu_lemma)
           #}, x[1]) for x in all_training_docs]
print(f'Training data created, length {len(train)}')


# Creating testing data
random.shuffle(train)
length = len(train)
train_x = train[0:int(0.9 * length)]
test_x = train[int(0.9 * length):]
print('Testing data created, now training model...')


# Training
model_nb = nltk.NaiveBayesClassifier.train(train_x)  # Naïve bayes by nltk
#model_skl = SklearnClassifier(BernoulliNB()).train(train_x)  # Naïve bayes by skl
#model_svm = SklearnClassifier(SVC(), sparse=False).train(train_x)  # Support Vector Machine
print('Model trained')

# Viewing the model
model_nb.show_most_informative_features()
acc_nltk = nltk.classify.accuracy(model_nb, test_x)
print("Accuracy of NB by nltk:", acc_nltk)

#acc_skl = nltk.classify.accuracy(model_skl, test_x)
#print("Accuracy of NB by skl:", acc_skl)

#acc_svm = nltk.classify.accuracy(model_svm, test_x)
#print("Accuracy of NB by SVM:", acc_svm)


# Actual predicting
def process_testing_data(filename: str, tokens: set) -> list:
    """
    Takes a file and make it ready for nltk classifiers.
    :param filename:
    :param tokens: the entirety of the tokens used in the training data
    :return: list containing dicts of the number of occurrences
    of each word in the token in the corresponded sentence to be analysed.
    """
    sent_list = fi_file.to_list(filename)
    print(f'File {filename} converted to list.')
    testing_doc = []
    for sent in sent_list:
        lemmas = fi_str.lemmatize(sent)
        testing_doc.append(lemmas)
    print(f'First 3 lemmas list: {testing_doc[:3]}')
    test = [({word: (word in x) for word in tokens}) for x in testing_doc]  # Binary decision
    print(f'Data prepared, length {len(test)}')

    return test


test = process_testing_data('1_Suomi.txt', tokens)
res_list = model_nb.classify_many(test)
#res_list = model_skl.classify_many(test)
#res_list = model_svm.classify_many(test)


def res_stats(res_list):
    pos_count = 0
    neg_count = 0
    for res in res_list:
        if res == 'pos':
            pos_count += 1
        elif res == 'neg':
            neg_count += 1
    proportion = pos_count / (pos_count + neg_count)

    print('Positives (Normalised): ' + str(pos_count))
    print('Negatives (Normalised): ' + str(neg_count))
    print('Portion Positive (Normalised): ' + str(proportion))

    data = {'pos_norm': pos_count, 'neg_norm': neg_count,
            'prop': proportion,
            }

    return data


res_stats(res_list)
