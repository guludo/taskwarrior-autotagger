#!/usr/bin/env python3

import collections
import configparser
import json
import pathlib
import sys

hook_path = pathlib.Path(__file__)

hook_type = 'modify' if hook_path.name.startswith('on-modify') else 'add'

task_dir = hook_path.parent.parent

config_file = task_dir / 'autotagger.cfg'

if hook_type == 'modify':
    _ = json.loads(sys.stdin.readline())

new_task = json.loads(sys.stdin.readline())

config = configparser.ConfigParser()
config.read(config_file)

tag_to_tags = collections.defaultdict(set)
project_to_tags = collections.defaultdict(set)
for name in config.sections():
    if not name.startswith('tag.'):
        continue

    target = name[4:]
    for tag in config[name].get('tags', '').strip().split():
        tag_to_tags[tag].add(target)

    for project in config[name].get('projects', '').strip().split():
        project_to_tags[project].add(target)


existing_tags = set(new_task.get('tags', []))
added_tags = set()

for tag in existing_tags:
    added_tags.update(tag_to_tags[tag])


task_project = new_task.get('project')
if task_project:
    added_tags.update(project_to_tags[task_project])

added_tags -= existing_tags

new_task['tags'] = new_task.get('tags', []) + list(added_tags)

print(json.dumps(new_task))
if added_tags:
    print(f'autotagger: added the following tags: {" ".join(added_tags)}')
