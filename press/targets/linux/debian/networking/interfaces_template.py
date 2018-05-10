
INTERFACES_TEMPLATE = """#
# https://wiki.debian.org/NetworkConfiguration
#

# The loopback network interface.
auto lo
iface lo inet loopback

# Additional network interfaces go below.
{% for network in networks %}
{% if network.vlan %}
auto {{ network.device }}
iface {{ network.device }} {{'inet6' if network.type == 'AF_INET6' else 'inet'}} manual

auto {{ network.device }}{{'.' ~ network.vlan}}
iface {{ network.device }}{{'.' ~ network.vlan}} {{'inet6' if network.type == 'AF_INET6' else 'inet'}} static
    vlan-raw-device {{ network.device }}
    vlan-id {{ network.vlan }}
    address {{ network.ip_address }}
    netmask {{ network.prefix or network.netmask }}
{% if network.gateway %}
    gateway {{ network.gateway }}
{% endif %}
{% for route in network.routes %}
        post-up route add -net {{ route.cidr }} gw {{ route.gateway }}
        post-down route del -net {{ route.cidr }} gw {{ route.gateway }}
{% endfor %}
{% else %}
auto {{ network.device }}
iface {{ network.device }} {{'inet6' if network.type == 'AF_INET6' else 'inet'}} static
    address {{ network.ip_address }}
    netmask {{ network.prefix or network.netmask }}
{% if network.gateway %}
    gateway {{ network.gateway }}
{% endif %}
{% for route in network.routes %}
        post-up route add -net {{ route.cidr }} gw {{ route.gateway }}
        post-down route del -net {{ route.cidr }} gw {{ route.gateway }}
{% endfor %}
{% endif %}
{% endfor %}
"""
