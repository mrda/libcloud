#!/usr/bin/env python

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import libcloud.security
import q
import re

NODE_RE=re.compile(r'node_(?P<id>\d+)')
desired_number_of_nodes = 5
node_prefix = 'node_'

def get_nodes(driver):
    nodes = []
    for node in driver.list_nodes():
        nodes.append(node.name)
    return nodes

def get_next_node_name(nodes):
    next_id = 0
    for node in nodes:
        m = NODE_RE.match(node)
        if m:
            id = m.group('id')
            if id > next_id:
                next_id = id
        else:
            print "Non-matching node found - yikes!"
    next_id += 1
    return node_prefix + next_id

def get_next_n_node_names(nodes, desired_min):
    next_id = 0
    for node in nodes:
        m = NODE_RE.match(node)
        if m:
            id = int(m.group('id'))
            if id > next_id:
                next_id = int(id)
        else:
            print "Non-matching node found - yikes!"
    new_nodes = []
    for i in xrange(len(nodes)):
        next_id += 1
        new_nodes.append(node_prefix + str(next_id))

    if len(new_nodes) < desired_min:
        for i in xrange(desired_min-len(new_nodes)):
            next_id += 1
            new_nodes.append(node_prefix + str(next_id))

    return new_nodes

def get_node(driver, node_name):
    for node in driver.list_nodes():
        if node.name == node_name:
            return node

def create_node(driver, node_name, node_image, node_size):
    node = driver.create_node(name=node_name, image=node_image, size=node_size)
    print "Successfully created %s" % node.name
    return node

def delete_node(driver, node_name):
    node = get_node(driver, node_name)
    if driver.destroy_node(node):
        print "Successfully deleted %s" % node_name
    else:
        print "*** Failed deleting %s" % node_name

def get_image(driver):
    node_image = None
    images = driver.list_images()
    for image in images:
        if image.name == 'cirros-0.3.1-x86_64-uec-kernel':
            node_image = image
    return node_image

def get_size(driver):
    node_size = None
    sizes = driver.list_sizes()
    for size in sizes:
        if size.name == 'm1.tiny':
            node_size = size
    return node_size

def main():
    libcloud.security.VERIFY_SSL_CERT = False

    OpenStack = get_driver(Provider.OPENSTACK)

    driver = OpenStack('admin', 'devstack',
                   #ex_force_auth_url='http://192.168.1.145:5000/v2.0/tokens',
                   ex_force_auth_url='http://192.168.1.36:5000/v2.0/tokens',
                   ex_force_auth_version='2.0_password',
                   ex_tenant_name='demo')

    current_nodes = get_nodes(driver)
    new_nodes = get_next_n_node_names(current_nodes, desired_number_of_nodes)

    img = get_image(driver)
    sze = get_size(driver)

    for c in current_nodes:
        delete_node(driver, c)

    for c in new_nodes:
        create_node(driver, c, img, sze)

if __name__ == '__main__':
    main()

