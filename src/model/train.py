import sys
import csv
import json
from itertools import count
from tqdm import tqdm
from models import seq2seq, seq2seq_attention
from keras.optimizers import SGD, Adagrad, Adam

sys.path.append('src/utils')
from batch_utils import BatchIterator

if __name__ == '__main__':
    sequence_length = 16
    vocabulary_size = 2000
    hidden_size = 256
    model = seq2seq_attention(sequence_length, vocabulary_size, hidden_size)

    data_file = 'data/processed/opus11/filtered_pairs.txt'
    with open(data_file) as handle:
        reader = csv.reader(handle)
        questions, answers = zip(*reader)

    vocabulary_file = 'data/processed/opus11/vocabulary.txt'
    with open(vocabulary_file) as handle:
        vocabulary = json.load(handle)

    batch_size = 64
    n_iter = 1024 # 16384
    n_epoch = 2
    iterator = BatchIterator(questions, answers, vocabulary, batch_size, sequence_length, one_hot_target=True)
    # generator = (iterator.next_batch() for _ in count(start=0, step=1)) # infinite generator
    # model.fit_generator(generator, epochs=2, steps_per_epoch=n_iter * batch_size)
    # 
    bar_format = '{n_fmt}/{total_fmt}|{bar}|ETA: {remaining} - {desc}'
    for epoch in range(n_epoch):
        print ('-' * 80)
        print ('Epoch {0}'.format(epoch))
        print ('-' * 80)
        bar = tqdm(range(1, n_iter+1), total=n_iter, bar_format=bar_format, ncols=80)
        loss = 0.0
        for i in bar:
            batch = iterator.next_batch()
            loss += model.train_on_batch(*batch)
            bar.set_description('loss: {0:.2f}'.format( float(loss)/i ))
            bar.refresh()
    
    model.save_weights('models/seq2seq_weights.h5')
