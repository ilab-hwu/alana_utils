
import logging
import subprocess
import datetime

LOG_LEVELS = {'critical': logging.CRITICAL,
              'error': logging.ERROR,
              'warning': logging.WARNING,
              'info': logging.INFO,
              'debug': logging.DEBUG}


def get_short_git_version(path='.'):
    data = subprocess.check_output(['git', '-C', path, 'log', '--pretty=%h-%at', '-1']).strip()
    shorthash, ts = data.split('-')
    date = datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d-%H%M')
    return '%s-%s' % (shorthash, date)
