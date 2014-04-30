import urllib
import json
from .errors import IpernityError, IpernityAPIError


def call_api(method, **kwargs):
    ''' file request to ipernity API

    Parameters:
        method: The API method you want to call

    Default:
        * always send request with POST method
        * format is JSON
    '''
    data = urllib.urlencode(kwargs)
    url = "http://api.ipernity.com/api/%s/%s" % (method, 'json')
    # send the request
    try:
        resp_raw = urllib.urlopen(url, data).read()
    except Exception, e:
        raise IpernityError(str(e))

    # parse the result
    resp = json.loads(resp_raw)
    # check the response, if error happends, raise exception
    api = resp['api']
    if api['status'] == 'error':
        err_mesg = api['message']
        err_code = int(api['code'])
        raise IpernityAPIError(err_code, err_mesg)

    return resp
