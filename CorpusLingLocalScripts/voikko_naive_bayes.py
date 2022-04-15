import voikko_string_lemmatizer as fi_str
import voikko_file_lemmatizer as fi_file
import random

pos_lemma = fi_file.lemmatize('pos_list.txt')
neg_lemma = fi_file.lemmatize('neg_list.txt')
#neu_lemma = fi_file.lemmatize('neu_list.txt')


def get_word_counts(word_list):
    """
    Takes as input a lemma list and returns a dictionary with the
    number of times each word occurred in that file.
    :param list: The file to be counted
    :return: A dictionary containing the number of occurrences for each word
    """

    dictionary = {}
    # word_list = []

    # for l in listname:
    # word_list += l.split()

    for word in word_list:
        word_stemmed = word  # No stemming
        # word_stemmed = fistemmer.stem(word)  # stemming
        if word_stemmed not in dictionary:
            dictionary[word_stemmed] = 1
        else:
            dictionary[word_stemmed] += 1

    return dictionary


def counts_to_probs(dictionary, num):
    """
    Takes a dictionary and a number and generates a new dictionary with
    the same keys where each value has been divided by the input number.
    :param dictionary: The dictionary to be operated on
    :param num: The number to be divided
    :return: A dictionary in which all values for each key have been divided by num
    """
    for word in dictionary:
        dictionary[word] /= num

    return dictionary


def train_model(listname, word_list):
    """
    Takes as input a listname containing examples and returns a dictionary with the word probabilities.
    :param listname: The name of the list to be counted and calculated
    :return: A dictionary containing the probability of the occurrences of each word type
    """
    lines = len(listname)
    counts = get_word_counts(word_list)
    probs = counts_to_probs(counts, lines)
    return probs


def get_probability(dictionary, string):  # This is why it's finnish specific!
    """
    Takes as input two parameters, a dictionary of word probabilities and a
    string (representing a review), and returns the probability of that review
    by multiplying the probabilities of each of the words in the review.
    :param dictionary: The dictionary containing the probability data
    :param string: The string to be evaluated on
    :return: The product of teh probability of each of the words in the string
    """
    string = string.lower()
    word_list = fi_str.lemmatize(string)  # Create a list of words from the input str, fi specific
    probs = 1  # Initialise

    for word in word_list:
        if word in dictionary:
            probs *= dictionary[word]
        else:
            probs *= 1 / 11000.

    return probs


def classify(string, pos_dict, neg_dict):
    """
    Takes a string (a review), a positive and a negative model. Returns “positive” or
    “negative” depending on which model has the highest probability for the review.
    Ties goes to positive.
    :param string: The review to be classified
    :param pos_dict: The positive model (dict)
    :param neg_dict: The negative model (dict)
    :return: “positive” or “negative” depending on which model has the highest probability for the review.
    """
    pos_probs = get_probability(pos_dict, string)
    neg_probs = get_probability(neg_dict, string)

    string = string.lower()
    word_list = fi_str.lemmatize(string)  # Create a list of words from the input str

    if (pos_probs - neg_probs) > 0: #(1 / 11000) / len(word_list):
        return 'positive'
    elif abs(pos_probs - neg_probs) <= 0: #(1 / 11000) / len(word_list):
        return 'neutral'
    else:
        return 'negative'


def polarity(string, pos_dict, neg_dict):
    pos_probs = get_probability(pos_dict, string)
    neg_probs = get_probability(neg_dict, string)

    string = string.lower()
    word_list = fi_str.lemmatize(string)  # Create a list of words from the input str

    return {'pol': (pos_probs - neg_probs) * len(word_list),
            'pos_probs': pos_probs, 'neg_probs': neg_probs,
            'sent_len': len(word_list)}


def sentiment_analyzer_interactive(pos_list, neg_list):
    """
    DEPRECATED for now.
    An interactive function that takes two files as input, a positive
    examples file and a negative examples file. It would train a positive
    and negative model using these files and then repeatedly ask the user
    to enter a sentence and then output the classification of that sentence
    (as positive or negative). A blank line/sentence should terminate the function.
    :param pos_file: File name of the positive training data
    :param neg_file: File name of the negative training data
    """
    pos_dict = train_model(pos_list, pos_lemma)
    neg_dict = train_model(neg_list, neg_lemma)  # Train the models

    print('Blank line terminates.')
    string = input('Enter a sentence: ')
    while string != '':
        print(classify(string, pos_dict, neg_dict))
        string = input('Enter a sentence: ')


def get_accuracy(pos_train, neg_train, pos_test, neg_test):
    """
    A function that would train the model (i.e., both positive and negative counts) and then classify
    all of the test examples (both positive and negative) and keep track of the accuracy of the
    model. It would print out three scores: the accuracy on the positive test examples,
    the accuracy on the negative test examples, and the accuracy on all of the test examples.
    :param pos_test_name: File name of the positive testing data
    :param neg_test_name: File name of the negative testing data
    :param pos_train: File name of the positive training data
    :param neg_train: File name of the negative training data
    """
    pos_dict = train_model(pos_train, pos_lemma)
    neg_dict = train_model(neg_train, neg_lemma)  # Train the models

    pos_total = len(pos_test)
    neg_total = len(neg_test)  # Total num of pos & neg reviews

    pos_actual = 0
    neg_actual = 0  # Initialise

    for l in pos_test:
        if classify(l, pos_dict, neg_dict) == 'positive':
            pos_actual += 1

    for l in neg_test:
        if classify(l, pos_dict, neg_dict) == 'negative':
            neg_actual += 1

    pos_accuracy = pos_actual / pos_total
    neg_accuracy = neg_actual / neg_total
    total_accuracy = (pos_actual + neg_actual) / (pos_total + neg_total)

    print('Positive recall: ', pos_accuracy)
    print('Negative recall: ', neg_accuracy)
    print('Total accuracy: ', total_accuracy)

    data = {'pos_rec': pos_accuracy,
            'neg_rec': neg_accuracy,
            'tot_acc': total_accuracy}

    return data


def normalized_polarity(string, pos_dict, neg_dict, accuracy_data):
    """
    Returns a polarity that is normalised against the accuracy data of the model.
    :param string: the string to calculate polarity with
    :param pos_dict:
    :param neg_dict:
    :param accuracy_data: Accuracy data used for training
    :return: the overall normalised polarity
    """
    initial = polarity(string, pos_dict, neg_dict)
    pos_norm = initial['pos_probs'] / accuracy_data['pos_rec']
    neg_norm = initial['neg_probs'] / accuracy_data['neg_rec']
    overall = (pos_norm - neg_norm) * initial['sent_len']

    return overall


def sentiment_analyzer_batch(filename: str, pos_list: list, neg_list: list) -> dict:
    """
    Take a file with multiple lines of strings to analyse and print out the count of positive lines,
    negative lines and the proportion of the lines that are positive. Returns a data dict that contains
    the count of positive lines, negative lines and the proportion of the lines that are positive, as
    well as the positive and negative lemma dictionary sorted by the number of occurrence.
    :param filename: the file that contains the lines to be classified
    :param pos_list: a list of positive sentences
    :param neg_list: a list of negative sentences
    :return: a data dictionary of this analysis
    """
    pos_dict = train_model(pos_list, pos_lemma)
    neg_dict = train_model(neg_list, neg_lemma)  # Train the models

    # Classify the tone of each line of the file
    file = open(filename, 'r')
    pos_count = 0
    neg_count = 0
    pos_posts = []
    neg_posts = []
    neu_posts = []
    polarity_all_posts = []

    # Get accuracy data of the model to normalise the polarity
    boundary = 0.9  # the boundary set for training vs testing
    accuracy_data = get_accuracy(pos_list[: int(len(pos_list) * boundary)],
                                 neg_list[: int(len(neg_list) * boundary)],
                                 pos_list[int(len(pos_list) * boundary):],
                                 neg_list[int(len(neg_list) * boundary):]
                                 )

    for l in file:
        polarity_all_sentences = []  # Initialise
        for sentence in l.split('.'):
            #polarity_sent = normalized_polarity(sentence, pos_dict, neg_dict, accuracy_data)
            polarity_sent = polarity(sentence, pos_dict, neg_dict)['pol']
            polarity_all_sentences.append(polarity_sent)
            polarity_all_posts.append(polarity_sent)
            # if polarity_sent > 0:
            #     pos_count += 1
            # else:
            #     neg_count += 1

        average_polarity = sum(polarity_all_sentences) / len(polarity_all_sentences)
        if average_polarity < 0:
            neg_count += 1
            neg_posts.append(l)
        if average_polarity > 0:
            pos_count += 1
            pos_posts.append(l)
        else:
            neu_posts.append(l)
    file.close()

    # Calculate the proportion of positive posts
    pos_count = pos_count / accuracy_data['pos_rec']
    neg_count = neg_count / accuracy_data['neg_rec']
    proportion = pos_count / (pos_count + neg_count)
    #avg_polarity = (sum(polarity_all_posts) / len(polarity_all_posts)) \
                   #* (-1 / accuracy_data['neg_rec'] + 1 / accuracy_data['pos_rec'])

    # Print the data of the file analysed
    print(filename)
    print('Positives (Normalised): ' + str(pos_count))
    print('Negatives (Normalised): ' + str(neg_count))
    #print(f'Positives (Not Normalised): {len(pos_posts)}')
    #print(f'Negatives (Not Normalised): {len(neg_posts)}')
    print('Portion Positive (Normalised): ' + str(proportion))
    #print(f'Average Polarity: {avg_polarity}')

    # Sort dictionaries of the training data
    pos_dict = {k: v for k, v in sorted(pos_dict.items(),
                                        key=lambda item: item[1], reverse=True)}
    neg_dict = {k: v for k, v in sorted(neg_dict.items(),
                                        key=lambda item: item[1], reverse=True)}

    # Sort a dict of data
    data = {'pos_norm': pos_count, 'neg_norm': neg_count,
            'prop': proportion, #'pol': avg_polarity,
            #'pos_no_norm': len(pos_posts), 'neg_no_norm': len(neg_posts),
            'pos_posts': pos_posts, 'neg_posts': neg_posts, 'neu_posts': neu_posts,
            'pos_dict': pos_dict, 'neg_dict': neg_dict,
            }
    data.update(accuracy_data)

    return data


# Testing
pos_list = fi_file.to_list('pos_list.txt')
neg_list = fi_file.to_list('neg_list.txt')
random.shuffle(pos_list)
random.shuffle(neg_list)
#neu_list = fi_file.to_list('neu_list.txt')
#"""
#get_accuracy(pos_list[:1800], neg_list[:1800], pos_list[1800:2000], neg_list[1800:2000])
#"""

#sentiment_analyzer_interactive(pos_list, neg_list)

suomi = sentiment_analyzer_batch('1_Suomi.txt', pos_list[:2000], neg_list[:2000])
#suomi = sentiment_analyzer_batch('neg_list.txt', pos_list[:1000], neg_list[:1000])

print(suomi['prop'], suomi['neg_norm'])

#data = sentiment_analyzer_batch('1_Suomi.txt', pos_list, neg_list)
#print(data['neg_dict'])
#"""