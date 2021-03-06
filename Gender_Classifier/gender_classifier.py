# -*- coding: utf-8 -*-
"""Genderv2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16r9m5Ob9fWg-4apoluxihcsJRijEiBzz
"""

# Importing requirements and modules
import tensorflow as tf
from keras.layers.core import Dense, Activation, Dropout
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout, Conv1D, MaxPooling1D
from sklearn.preprocessing import OneHotEncoder
from pathlib import Path

# Helper libraries
import numpy as np
import pandas as pd 

data_dir = Path("Gender_Classifier")
df = pd.read_csv(data_dir /'name_gender.csv')
df.columns = ['Name','Gender','Score']

# Parameters
predictor_col = 'Name'
result_col = 'Gender'
accepted_chars = 'abcdefghijklmnopqrstuvwxyz'

word_vec_length = min(df[predictor_col].apply(len).max(), 25) # Length of the input vector
char_vec_length = len(accepted_chars) # Length of the character vector
output_labels = 2 # Number of output labels

# Define a mapping of chars to integers
char_to_int = dict((c, i) for i, c in enumerate(accepted_chars))
int_to_char = dict((i, c) for i, c in enumerate(accepted_chars))

# Removes all non accepted characters
def normalize(line):
    return [c.lower() for c in line if c.lower() in accepted_chars]

# Returns a list of n lists with n = word_vec_length
def name_encoding(name):

    # Encode input data to int, e.g. a->1, z->26
    integer_encoded = [char_to_int[char] for i, char in enumerate(name) if i < word_vec_length]
    
    # Start one-hot-encoding
    onehot_encoded = list()
    
    for value in integer_encoded:
        # create a list of n zeros, where n is equal to the number of accepted characters
        letter = [0 for _ in range(char_vec_length)]
        letter[value] = 1
        onehot_encoded.append(letter)
        
    # Fill up list to the max length. Lists need do have equal length to be able to convert it into an array
    for _ in range(word_vec_length - len(name)):
        onehot_encoded.append([0 for _ in range(char_vec_length)])
        
    return onehot_encoded

# Encode the output labels
def lable_encoding(gender_series):
    labels = np.empty((0, 2))
    for i in gender_series:
        if i == 'M':
            labels = np.append(labels, [[1,0]], axis=0)
        else:
            labels = np.append(labels, [[0,1]], axis=0)
    return labels

def main() :
    print("Starting to train Deep Learning Model")
    # Split dataset in 60% train, 20% test and 20% validation
    print("Splitting dataset...")
    train, validate, test = np.split(df.sample(frac=1), [int(.6*len(df)), int(.8*len(df))])
    # Convert both the input names as well as the output lables into the discussed machine readable vector format
    train_x =  np.asarray([np.asarray(name_encoding(normalize(name))) for name in train[predictor_col]])
    train_y = lable_encoding(train.Gender)

    validate_x = np.asarray([name_encoding(normalize(name)) for name in validate[predictor_col]])
    validate_y = lable_encoding(validate.Gender)

    test_x = np.asarray([name_encoding(normalize(name)) for name in test[predictor_col]])
    test_y = lable_encoding(test.Gender)

    hidden_nodes = int(2/3 * (word_vec_length * char_vec_length))

    # Build the model
    print('Build model...')
    model = Sequential()
    model.add(LSTM(hidden_nodes, return_sequences=True, input_shape=(word_vec_length, char_vec_length)))
    model.add(Dropout(0.2))
    model.add(LSTM(hidden_nodes, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=output_labels))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
    
    print("Training Model..")
    batch_size=1000
    model.fit(train_x, train_y, batch_size=batch_size, epochs=50, validation_data=(validate_x, validate_y))

    print("Testing model...")
    score, acc = model.evaluate(test_x, test_y)

    print('Test score:', score)
    print('Test accuracy:', acc)
    
    print("Saving Model...")
    model.save('Gender_Classifier/gender_model.h5',overwrite=True)
    
    print("Model Created")

def retrainModel():
    main()
    
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()