import os
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'6\xe9\xda\xead\x81\xf7\x8d\xbbH\x87\xe8m\xdd3%'
    MONGODB_SETTINGS = { 'db' : 'bank' , 'host': 'mongodb://vijay:vijay18399@ds149676.mlab.com:49676/chat?retryWrites=false' }


    