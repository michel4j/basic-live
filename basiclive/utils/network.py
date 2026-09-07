from ipaddress import ip_address, ip_network
from django.conf import settings


class IPAddressList(list):
    def __init__(self, *ips):
        super().__init__()
        self.extend([ip_network(ip, False) for ip in ips])

    def __contains__(self, address):
        ip = ip_address(address)
        return any(ip in net for net in self)


def get_client_address(request):
    depth = getattr(settings, 'TRUSTED_PROXIES', 2)
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        header = request.META['HTTP_X_FORWARDED_FOR']
        levels = [x.strip() for x in header.split(',')]

        if len(levels) >= depth:
            address = ip_address(levels[-depth])
        else:
            address = None
    else:
        address = ip_address(request.META['REMOTE_ADDR'])
    return address and address.exploded or address
