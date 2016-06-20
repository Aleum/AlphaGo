#-*- coding: utf-8 -*-

from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.convolutional import Convolution2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD
from keras.callbacks import Callback
from keras import backend as K
from keras.models import model_from_json
import sys

def save_weights(self, filepath, overwrite=False):
    '''Dumps all layer weights to a HDF5 file.
    The weight file has:
        - `layer_names` (attribute), a list of strings
            (ordered names of model layers)
        - for every layer, a `group` named `layer.name`
            - for every such layer group, a group attribute `weight_names`,
                a list of strings (ordered names of weights tensor of the layer)
            - for every weight in the layer, a dataset
                storing the weight value, named after the weight tensor
    '''
    import h5py
    import os.path
    # if file exists and should not be overwritten
    if not overwrite and os.path.isfile(filepath):
        import sys
        get_input = input
        if sys.version_info[:2] <= (2, 7):
            get_input = raw_input
        overwrite = get_input('[WARNING] %s already exists - overwrite? '
                              '[y/n]' % (filepath))
        while overwrite not in ['y', 'n']:
            overwrite = get_input('Enter "y" (overwrite) or "n" (cancel).')
        if overwrite == 'n':
            return
        print('[TIP] Next time specify overwrite=True in save_weights!')

    if hasattr(self, 'flattened_layers'):
        # support for legacy Sequential/Merge behavior
        flattened_layers = self.flattened_layers
    else:
        flattened_layers = self.layers

    f = h5py.File(filepath, 'w')
    f.attrs['layer_names'] = [layer.name.encode('utf8') for layer in flattened_layers]

    for layer in flattened_layers:
        g = f.create_group(layer.name)
        symbolic_weights = layer.trainable_weights + layer.non_trainable_weights
        weight_values = K.batch_get_value(symbolic_weights)
        weight_names = []
        for i, (w, val) in enumerate(zip(symbolic_weights, weight_values)):
            if hasattr(w, 'name') and w.name:
                name = str(w.name)
            else:
                name = 'param_' + str(i)
            weight_names.append(name.encode('utf8'))
        g.attrs['weight_names'] = weight_names
        for name, val in zip(weight_names, weight_values):
            param_dset = g.create_dataset(name, val.shape,
                                          dtype=val.dtype)
            param_dset[:] = val
    f.flush()
    f.close()
    
if __name__ == "__main__":
    
    MODEL_FILE_JSON = sys.argv[1]
    MODEL_FILE_H5 = sys.argv[2]
    
    model = model_from_json(open(MODEL_FILE_JSON).read())
    model.load_weights(MODEL_FILE_H5)  
    
 
    
    