# coding: utf-8
import yaml
import os
import pkg_resources

LOCAL_CONFIG = "{}/mockidp.yaml".format(os.path.curdir)
HOME_DIR_CONFIG = "{}/.mockidp.yaml".format(os.path.expanduser("~"))
GLOBAL_CONFIG = "/etc/mockidp.yaml"

CONFIG = {}


def locate_config_file():
    """ Return a path to a config to use accoding to standard preference rules """

    print(f"Checking if ${LOCAL_CONFIG} is a file")
    if os.path.isfile(LOCAL_CONFIG):
        return LOCAL_CONFIG
    if os.path.isfile(HOME_DIR_CONFIG):
        return HOME_DIR_CONFIG
    if os.path.isfile(GLOBAL_CONFIG):
        return GLOBAL_CONFIG
    resource = pkg_resources.resource_filename('mockidp', 'resources/default_config.yaml')
    return resource


def parse_config(filename):
    global CONFIG
    with open(filename) as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)
        return CONFIG


def get_metadata():
    return CONFIG.get('metadata', {})


def get_service_provider(config, name):
    service_providers = config['service_providers']
    if type(service_providers) != list:
        raise Exception(f"Unexpected obj {service_providers}")

    for service_provider in service_providers:
        print(service_provider.get('name'), name, service_provider.get('name') == name)

    matches = list(filter(lambda x: x['name'] == name, service_providers))
    print('service_providers', matches)
    if len(matches) != 1:
        raise Exception(f"Unable to locate service provider {name}, available {service_providers}")
    return matches[0]
