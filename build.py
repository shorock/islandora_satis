#!/usr/bin/env python3

import yaml
from sys import argv, stderr
from github import Github
import os
import re
import json

class Repository:
    def __init__(self, fullname):
        self.name = fullname
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)
    pass

class Tag:
    def __init__(self, tagname):
        self.name = tagname
        self.dependencies={}

    def add_dependency(self, dependency, constraint):
        self.dependencies[dependency]=constraint

    pass

class Dependency:
    def __init__(self, name, version):
        pass

with open(argv[1], 'r') as fh:
    ymldata = yaml.safe_load(fh)
pass

user = os.environ.get('GH_USER')
token = os.environ.get('GH_TOKEN')

gh = Github(user,token)
islandora = gh.get_organization('islandora')

repolist = {}

for repo_name in ymldata['islandora_modules'].keys():
    print(repo_name, file=stderr)
    ghrepo = islandora.get_repo(repo_name)
    newrepo = Repository(ghrepo.full_name)
    if repo_name != 'tuque':
        pattern = re.compile("^7\.x-(1\.\d+)$")
    elif repo_name == 'tuque':
        pattern = re.compile("^(1\.\d+)$")
    tags = filter(lambda x: pattern.match(x.name), ghrepo.get_tags())
    for tag in tags:
        newtag=Tag(tag.name)
        newtag.download = "https://github.com/islandora/" + repo_name + "/archive/" + tag.commit.sha +".zip"
        newtag.sha=tag.commit.sha
        m=pattern.match(tag.name)
        newtag.normalized = m.group(1) + ".0"
        if ymldata['islandora_modules'][repo_name] != None:
            for dependencies in ymldata['islandora_modules'][repo_name]:
                for k,v in dependencies.items():
                    if v == '=':
                        v = "^" + newtag.normalized
                    newtag.add_dependency(k,v)
        if repo_name != 'islandora' and repo_name != 'tuque':
            newtag.add_dependency('islandora/islandora', newtag.normalized)
        elif repo_name == 'islandora':
            newtag.add_dependency('islandora/tuque', newtag.normalized)
        newrepo.add_tag(newtag)
    repolist[newrepo.name]=newrepo

    # Now, to output
repositories = []

for repo_name, repo in repolist.items():
    for tag in repo.tags:
        p = {}
        p['type'] = "package"
        p['package'] = {}
        p['package']['name'] = repo.name
        p['package']['version'] = tag.normalized
        if repo.name == 'Islandora/tuque':
            p['package']['type'] = "drupal-library"
        else:
            p['package']['type'] = "drupal-module"
        p['package']['dist'] = {}
        p['package']['dist']['url'] = tag.download
        p['package']['dist']['type'] = 'zip'
        p['package']['source']={}
        p['package']['source']['url']="https://github.com/" + repo.name
        p['package']['source']['type']='git'
        p['package']['source']['reference'] = tag.sha
        p['package']['require'] = {}
        for dependency, constraint in tag.dependencies.items():
            p['package']['require'][dependency] = constraint
        repositories.append(p)

    p = {}
    p['type'] = "package"
    p['package'] = {}
    p['package']['name'] = repo.name
    p['package']['version'] = "1.x-dev"
    if repo.name == 'Islandora/tuque':
        p['package']['type'] = "drupal-library"
    else:
        p['package']['type'] = "drupal-module"
    p['package']['source'] = {}
    p['package']['source']['url'] = "https://github.com/" + repo.name
    p['package']['source']['type'] = 'git'
    if repo.name == 'Islandora/tuque':
        p['package']['source']['reference'] = '1.x'
    else:
        p['package']['source']['reference'] = '7.x'
    p['package']['require'] = {}
    for dependency, constraint in tag.dependencies.items():
        if constraint == tag.normalized:
            constraint = "1.*"
        p['package']['require'][dependency] = constraint
    repositories.append(p)

satis = {}
satis['require-all']=True
satis['output-dir']="output"
satis['name']=ymldata['name']
satis['homepage']=ymldata['homepage']
satis['repositories']=repositories

print(json.dumps(satis))
