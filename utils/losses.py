# losses.py
# loss functions

import numpy as np

def MAE(y,yhat):
    m = y.shape[1]
    return 1./m*np.sum(np.abs(y-yhat))

def MSE(y,yhat):
    m = y.shape[1]
    return 1./m*np.sum((y-yhat)**2)

def binary_crossentropy(y,yhat):
    m = y.shape[1]
    return -1./m*np.sum((y*np.log(yhat) + (1-y)*np.log(1-yhat)))

def categorical_crossentropy(y,yhat):
    m = y.shape[1]
    return -1./m*np.sum(y*np.log(yhat))