#!/usr/bin/python3

import gitlab
import os
import re
import time

MANIFEST_XML = "default.xml"
ROOT = os.getcwd()
ROOT_GROUP = "Android6NewC"
MANIFEST_XML_PATH_NAME_RE = re.compile(r"<project\s+path=\"(?P<path>[^\"]+)\"\s+name=\"(?P<name>[^\"]+)\"\s+/>",
                                       re.DOTALL)

gl = gitlab.Gitlab('http://192.168.50.10/', private_token='xxxxxxx')

manifest_xml_project_paths = []

def parse_repo_manifest():
    with open(os.path.join(ROOT, MANIFEST_XML), "rb") as strReader:
        for line in strReader:
            if line is not None and len(line) != 0:
                this_temp_line = line.decode()
                if line.find("path".encode(encoding="utf-8")):

                    s = MANIFEST_XML_PATH_NAME_RE.search(this_temp_line)

                    if s is not None:
                        manifest_xml_project_paths.append(s.group("path"))

    print("manifest_xml_project_paths=" + str(manifest_xml_project_paths))
    print("manifest_xml_project_paths len=" + str(len(manifest_xml_project_paths)))

def create_group_and_project():
    all_groups = gl.groups.list(all=True)
    print("all_groups=" + str(all_groups))
    group_parent = None

    for g in all_groups:
        if g.name == ROOT_GROUP:
            group_parent = g
            break
    print("group parent=" + str(group_parent))

    for path in manifest_xml_project_paths:
        print("path=" + path)
        paths = path.split("/")
        print("paths=" + str(paths))

        last_path_index = len(paths) - 1

        group = group_parent
        for index in range(0, last_path_index):
            p = paths[index]
            print("p=" + p)
            # is the group exist
            print("parent group=" + group.name)
            try:
                all_groups = group.subgroups.list(all=True)
            except AttributeError:
                all_groups = []
                print("AttributeError: clear all subgroups")

            is_group_exist = False
            for g in all_groups:
                if g.name == p:
                    is_group_exist = True
                    group = g
                    print("group exist=" + g.name)
                    break
            if is_group_exist:
                continue
            # create subgroup
            data = {
                "name": p,
                "path": p,
                "parent_id": group.id
            }

            try:
                group = gl.groups.create(data)
                print("group create success name=" + p)
                time.sleep(1)
            except gitlab.exceptions.GitlabCreateError as e:
                if e.response_code == 400:
                    print("group:" + p + " has already been created")

                    query_groups = gl.groups.list(all=True)
                    print("query_groups:" + str(query_groups))
                    for query_group in query_groups:
                        if query_group.name == p and query_group.parent_id == group.id:
                            group = query_group
                            print("update exit group:" + group.name)
                            break

        project = paths[last_path_index]
        print("group project list group=" + group.name)
        real_group = gl.groups.get(group.id, lazy=True)
        all_projects = real_group.projects.list(all=True)
        print("group all projects=" + str(all_projects))
        is_project_exist = False
        for p in all_projects:
            if p.name == project:
                is_project_exist = True
                print("project exist=" + p.name)
                break
        if not is_project_exist:
            print("create project=" + project)
            gl.projects.create({'name': project, 'path': project, 'namespace_id': group.id})
            print("project create success name=" + project)
            time.sleep(1)

def test_create_project_with_dot_name():
    # need use path field, if don't use path, GitLab url will replace "." to "_"
    gl.projects.create({'name': "xxx.yy.xy", 'path': "xxx.yy.xy"})

if __name__ == '__main__':
    parse_repo_manifest()
    create_group_and_project()

