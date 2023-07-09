#!/usr/bin/python3

import os
import re,subprocess

MANIFEST_XML = "./default.xml"
ROOT = os.getcwd()
LOG_FILE_PATH = os.path.join(ROOT, "push.log")

MANIFEST_XML_PATH_NAME_RE = re.compile(r"<project\s+path=\"(?P<path>[^\"]+)\"\s+name=\"(?P<name>[^\"]+)\"\s+",
                                       re.DOTALL)
SOURCE_CODE_ROOT = "~/android_src/aosp12_rom/"
REMOTE = "git@192.168.2.189:aosp12/"
manifest_xml_project_paths = []

def parse_repo_manifest():
    with open(os.path.join(ROOT, MANIFEST_XML), "rb") as strReader:
        for line in strReader:
            if line is not None and len(line) != 0:
                this_temp_line = line.decode()
                if line.find("path".encode(encoding="utf-8")):

                    s = MANIFEST_XML_PATH_NAME_RE.search(this_temp_line)

                    if s is not None:
                        manifest_xml_project_paths.append({"path":s.group("path"),"name":s.group("name")})

    print("manifest_xml_project_paths=" + str(manifest_xml_project_paths))
    print("manifest_xml_project_paths len=" + str(len(manifest_xml_project_paths)))

def exec(cmd):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE
    )
    proc.stdin.close()
    result = proc.stdout.read()
    proc.stdout.close()
    return result.decode(encoding="utf-8")

def push_source_code_by_folder(str_writer):
    for path in manifest_xml_project_paths:
        print("path=" + path["path"])
        abs_path = SOURCE_CODE_ROOT +  path["path"]

        if os.path.exists(abs_path):
            # change current work dir
            os.chdir(abs_path + "/")
            res= exec("git remote -v")
            print(res)
            if path["name"] in res:
                continue
            # 1\. delete .git & .gitignore folder
            rm_git_cmd = "rm -rf .git"
            rm_gitignore_cmd = "rm -rf .gitignore"
            os.system(rm_git_cmd)
            os.system(rm_gitignore_cmd)

            # 2\. list dir
            dir_data = os.listdir(os.getcwd())

            cmd_list = []

            print("changed cwd=" + os.getcwd())

            if len(dir_data) == 0:
                echo_cmd = "echo \"This is a empty repository.\" > ReadMe.md"
                str_writer.write(f"empty repository:{abs_path}".encode() )
                str_writer.write("\r\n".encode())
                cmd_list.append(echo_cmd)

            git_init_cmd = "git init"
            cmd_list.append(git_init_cmd)

            git_remote_cmd = "git remote add origin " + REMOTE +  path["name"] + ".git"
            cmd_list.append(git_remote_cmd)

            git_add_dot_cmd = "git add ."
            cmd_list.append(git_add_dot_cmd)

            git_commit_cmd = "git commit -m \"Initial commit\""
            cmd_list.append(git_commit_cmd)

            git_push_cmd = "git push -u origin master"
            cmd_list.append(git_push_cmd)

            for cmd in cmd_list:
                print("begin exec cmd=" + cmd)
                os.system(cmd)
                print("end exec cmd=" + cmd)
        else:
            print("abs_path=" + abs_path + " is not exist.")
            str_writer.write(f"folder not exist:{abs_path}".encode() )
            str_writer.write("\r\n".encode())

def wrapper_push_source_code_write_log():
    with open(LOG_FILE_PATH, 'wb+') as strWriter:
        push_source_code_by_folder(strWriter)
        strWriter.close()

# def test_only_dot_git_folder():
#     subdir_and_file = os.listdir(os.getcwd())
#     print("subdir_and_file=" + str(subdir_and_file))
#     with open(LOG_FILE_PATH, 'wb+') as strWriter:
#         strWriter.write(str(subdir_and_file).encode())
#         strWriter.write("\r\n".encode())
#         strWriter.write(str(subdir_and_file).encode())
#         strWriter.close()

if __name__ == '__main__':
    parse_repo_manifest()
    wrapper_push_source_code_write_log()
