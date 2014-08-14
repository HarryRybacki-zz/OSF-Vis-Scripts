# Grabs all 'project' components and creates data structure representing all 'projects' and their relation with 'users' as children

import json

from collections import defaultdict

with open('nodes.json', 'r') as f:
	db_components = json.load(f)

CHILDREN_SIZE = 8 # default size of child elements in the graph
CONTRIBUTOR_SIZE_CUTOFF = 15
output = {'name': 'flare'}

# map contributor ids to their full names
with open('users.json', 'r') as f:
	db_users = json.load(f)

name_map = {}

for user in db_users:
	name_map[user['_id']] = user['fullname']

def clean_contributor_list(contrib_list):
	contributors = []
	for contributor in contrib_list:
		contributors.append({
			'name': name_map[contributor],
			'size': CHILDREN_SIZE
		})
	return contributors


# extrapolate all project components from components json
projects = [component for component in db_components if component['category'] == 'project']

projects_dict = defaultdict(lambda: {'name': '', 'children': [], 'size': 0}) # default project as callable

projects_output = []

for project in projects:
	if len(project['contributors']) > CONTRIBUTOR_SIZE_CUTOFF:
		clean_contributor_list(project['contributors'])
		# get a proper a list of contributors here
		projects_output.append({
			'name': project['title'],
			'children': clean_contributor_list(project['contributors']),
			#'children': project['contributors'],
			'size': len(project['contributors'])
		})

# add projects dict to output
output['children'] = projects_output

#import pprint
#for project_id, project in projects_dict.iteritems():
#	print '###############', project_id
#	pprint.pprint(project)

#for _id, name in name_map.iteritems():
#	print _id, ': ', name

## output to jsonw
with open('collapsable_projects.json', 'w') as f:
	json.dump(output, f, indent=4)