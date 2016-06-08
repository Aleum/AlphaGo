'''
python prog5.py -mode RL
python prog5.py
'''


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-mode', nargs=1, required=False, dest='mode')
args = parser.parse_args()

if args.mode is not None:
    print 'args.mode : ' + args.mode[0]
else:    
    print 'args.mode is none: '
