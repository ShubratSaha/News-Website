import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'w\xf7*K\x96\x96=2\xcf\x02\xef\x80\x89\x1d\xc5\x85'