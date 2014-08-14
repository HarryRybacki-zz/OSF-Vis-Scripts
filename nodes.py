import json
with open('users.json', 'r') as f:
    db_users = json.load(f)
with open('nodes.json', 'r') as f:
    db_components = json.load(f)

import itertools

from collections import defaultdict

USER = 1
COMPONENT = 2

NODE_FULLNAME = 'name'
NODE_NUMBER_CONTRIBUTIONS = 'radius'

LINK_NUMBER_COCONTRIBUTIONS = 'value'

STARTING_LINK_WEIGHT = 1

PROJECT_SIZE_CUTOFF = 7
PERSON_CONTRIBUTION_CUTOFF = 10

#todo html entities in node titles

people_dict = defaultdict(lambda: {NODE_NUMBER_CONTRIBUTIONS: 1, 'group': USER}) # default person as callable
components_dict = defaultdict(lambda: {NODE_NUMBER_CONTRIBUTIONS: 0, 'group': COMPONENT}) # default component
components_as_nodes_dict = defaultdict(lambda: {NODE_NUMBER_CONTRIBUTIONS: 1, 'group': COMPONENT})# default component (but as person)

nodes = [] # d3/network
links = [] # "

# Name our users
for user in db_users:
    people_dict[user['_id']].update({
        NODE_FULLNAME: user['fullname']
    })

for node in db_components:
    # if not node['category'] == 'project:
    #    break

    components_dict[node['_id']].update({
        NODE_NUMBER_CONTRIBUTIONS: len(node['contributors']),
        NODE_FULLNAME: node['title'],
        'to': node['contributors']
    })
    for contributor_id in node['contributors']:
        people_dict[contributor_id][NODE_NUMBER_CONTRIBUTIONS] += 1 # number of nodes contributed to

for person_key, person in people_dict.items():
    if person[NODE_NUMBER_CONTRIBUTIONS] < PERSON_CONTRIBUTION_CUTOFF:
        del people_dict[person_key]

# Generating numeric ids for people to save space in the json
numeric_id = 0
for user_id in people_dict.keys():
    people_dict[user_id].update({
        'numeric_id': numeric_id,
    })
    numeric_id += 1

# Aggregate each large project as a single node based on PROJECT_SIZE_CUTOFF
for node_id, node in components_dict.items():
    if node[NODE_NUMBER_CONTRIBUTIONS] > PROJECT_SIZE_CUTOFF:
        components_as_nodes_dict[node_id].update(node)
        components_as_nodes_dict[node_id]['numeric_id'] = numeric_id
        del components_dict[node_id]
        numeric_id += 1

# adjacency list for components as nodes

for component_id, component in components_as_nodes_dict.iteritems():
    fro = component['numeric_id']
    for contributor_id in component['to']:
        if contributor_id in people_dict: # because we manipulated people_dict
            to = people_dict[contributor_id]['numeric_id']
            to_insert = {
                'source': fro,
                'target': to,
                LINK_NUMBER_COCONTRIBUTIONS: STARTING_LINK_WEIGHT
            }
            links.append(to_insert)

for component_id, component in components_dict.iteritems():
    to = component['to']

    for grp in list(itertools.permutations(to, 2)):
        if grp[0] in people_dict and grp[1] in people_dict: # because we manipulated people_dict
            to_insert = {
                'source': people_dict[grp[0]]['numeric_id'],
                'target': people_dict[grp[1]]['numeric_id'],
                LINK_NUMBER_COCONTRIBUTIONS: STARTING_LINK_WEIGHT
            }
            links.append(to_insert)


NUMBER_OF_CONTRIBUTIONS = 'r'
NUMBER_OF_COCONTRIBUTIONS = 'weight'

# for person in people_dict; nodes.append(person)
for node in people_dict.values() + components_as_nodes_dict.values():
    if 'to' in node:
        del node['to']
    del node['numeric_id']
    nodes.append(node)

output = {'nodes': nodes, 'links':links}

import os

with open('nodes_20140131_indents.json', 'w') as f:
    json.dump(output, f, indent=4)
