#-*- coding: utf-8 -*-

__author__ = 'Aleum'

from utils.base import *

train_ratio = 0.6
lr = 0.9
k = 192
bsize = 10
epoch = 1000

if __name__ == "__main__":


    train_x, train_y = load_dataset(policy=False)

    # make models
    model = Sequential()
    # input: 100x100 images with 3 channels -> (3, 100, 100) tensors.
    # this applies 32 convolution filters of size 3x3 each.
    model.add(ZeroPadding2D(padding=(1, 1), input_shape=(10, 9, 9)))
    model.add(Convolution2D(k, 5, 5))
    model.add(Activation('relu'))
    
    for i in range(0, 11):
        model = hidden_layers(model, k)
    
    model.add(ZeroPadding2D(padding=(1, 1)))
    model.add(Convolution2D(1, 1, 1))
    model.add(Activation('relu'))
    
    model.add(Flatten())
    model.add(Dense(2))
    model.add(Activation('softmax'))
    
    sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='MSE', optimizer=sgd, class_mode='binary')   
    stop = EarlyStop()
    # model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch, callbacks=[stop], show_accuracy=True)
    model.fit(train_x, train_y, batch_size=bsize, nb_epoch=epoch, show_accuracy=True)
    output = open("SCGo_policy_net.json", "w")
    output.write(model.to_json())
    output.close()
    