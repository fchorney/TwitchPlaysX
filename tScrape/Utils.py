def read_config(config_path):
    # Import simplejson or json
    try:
        import simplejson as json
    except ImportError:
        import json

    # Load json file into dict
    with open(config_path) as f:
        data = json.load(f)

    # Create a dynamic Config class with our json data
    class Config:
        def __init__(self, d):
            for a, b in d.items():
                if isinstance(b, (list, tuple)):
                    setattr(
                        self,
                        a,
                        [Config(x) if isinstance(x, dict) else x for x in b]
                    )
                else:
                    setattr(
                        self,
                        a,
                        Config(b) if isinstance(b, dict) else b
                    )
        def __repr__(self):
            return '<%s>' % str(
                '\n '.join(
                    '%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.iteritems()
                )
            )

    return Config(data)

def pERR(msg):
    from sys import stderr
        print >> stderr, msg

def pOUT(msg):
    from sys import stdout
        print >> stdout, msg
