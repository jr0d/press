import json
import logging
import requests

# Disabled pesky warnings
requests.packages.urllib3.disable_warnings()

LOG = logging.getLogger('')


class KserverLogHandler(logging.Handler):
    def __init__(self, base_url, object_id):
        logging.Handler.__init__(self)
        self.object_id = object_id
        self.url = base_url.rstrip('/') + '/press/log/' + self.object_id
        self.headers = {'Content-type': 'application/json', 'Connection': 'close'}

    def emit(self, record):
        data = json.dumps(record.__dict__)
        try:
            r = requests.post(self.url, data=data, headers=self.headers, verify=False)
            r.raise_for_status()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def plugin_init(configuration):
    LOG.info('kserver plugin initializing')
    kserver_data = configuration.get('kserver')
    # suppress requests logging messages
    logging.getLogger('requests').setLevel(logging.WARNING)

    from requests.packages import urllib3
    urllib3.disable_warnings()

    if not kserver_data:
        LOG.info('kserver data missing from configuration, doing nothing')
        return

    url = kserver_data['url']
    object_id = kserver_data['object_id']

    LOG.info('Kserver info: url = %s object_id = %s' % (url, object_id))
    LOG.info('Attempting to inject KserverLogHandler')

    klh = KserverLogHandler(url, object_id)

    LOG.addHandler(klh)
