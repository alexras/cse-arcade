import os
import sys

from ConfigParser import ConfigParser
from optparse import OptionParser

AFFIRMATIVE = set(['true', '1', 'yes', 'on'])

class FrontendConfig(object):
    def __init__(self, section):
        self.options = {}

        parser = OptionParser()
        parser.add_option('-c', '--config_file', dest='config_file', help='Configuration file.')

        (options, args) = parser.parse_args()

        config = ConfigParser()
        config_locations = [os.path.expanduser('~/frontend.cfg')]
        if options.config_file is not None:
            config_locations.append(options.config_file)

        if len(config.read(config_locations)) < 1:
            print 'No config found.  Populate %s or use the -c flag.' % os.path.expanduser('~/frontend.cfg')
            sys.exit(1)

        # Common options
        self.options['RootDir'] = os.path.expanduser(config.get('config', 'RootDir'))
        self.options['DataDir'] = os.path.expanduser(config.get('config', 'DataDir'))
        self.options['HidePointer'] = config.get('config', 'HidePointer').lower() in AFFIRMATIVE
        self.options['Fullscreen'] = config.get('config', 'Fullscreen').lower() in AFFIRMATIVE
        self.options['Launch'] = config.get('config', 'Launch').lower() in AFFIRMATIVE
        self.options['PrintKeys'] = config.get('config', 'PrintKeys').lower() in AFFIRMATIVE

        # Frontend-specific options.
        self.options['BaseDir'] = os.path.expanduser(config.get(section, 'BaseDir'))
        self.options['UP'] = set(config.get(section, 'UP').split(','))
        self.options['DOWN'] = set(config.get(section, 'DOWN').split(','))
        self.options['LEFT'] = set(config.get(section, 'LEFT').split(','))
        self.options['RIGHT'] = set(config.get(section, 'RIGHT').split(','))
        self.options['GO'] = set(config.get(section, 'GO').split(','))

    def __getitem__(self, item):
        return self.options[item]
