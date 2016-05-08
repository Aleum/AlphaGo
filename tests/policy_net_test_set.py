#-*- coding: utf-8 -*-

from nets.policy_net import load_dataset
from keras.models import model_from_json
import time

if __name__ == "__main__":
    cor, uncor = 0, 0
    
    X, Y = load_dataset("test_pro/")
    model = model_from_json(open('20160502_pro/policy_net_model_99.json').read())
    model.load_weights('20160502_pro/policy_net_weights_99.h5')
    before = time.time()
    pResult = model.predict(X)
    after = time.time()
    print "걸린 시간", after-before
    for i in range(0, len(pResult)):
        pred = pResult[i].argmax()
        real = Y[i].argmax()
        if pred == real:
            cor += 1
        else:
            uncor += 1
    ACC = 100.0 * cor / len(Y)
    print "맞은 개수:", cor
    print "틀린 개수:", uncor
    print "정확도: %.5f" % ACC