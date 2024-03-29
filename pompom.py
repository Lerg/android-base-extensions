#!/usr/bin/env python

import urllib
import zipfile
import re
import os
import sys
import shutil
import fnmatch
import json
import tempfile
from xml.dom.minidom import parseString
from xml.dom import minidom
from subprocess import call
from argparse import ArgumentParser
from contextlib import contextmanager


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def cleardirs(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def get_project_dir(args):
    return os.path.join(args.out, args.project_name)


def get_extension_dir(args):
    return os.path.join(get_project_dir(args), args.project_name)


def get_lib_dir(args):
    return os.path.join(get_extension_dir(args), "lib", "android")


def get_manifest_dir(args):
    return os.path.join(get_extension_dir(args), "manifests", "android")


def get_res_dir(args):
    return os.path.join(get_extension_dir(args), "res", "android", "res")


def get_src_dir(args):
    return os.path.join(get_extension_dir(args), "src")


def javac(file):
    javac = "javac -source 1.7 -target 1.7 %s" % (file)
    call(javac, shell=True)


def get_element_value(element):
    if element and element.childNodes:
        return element.childNodes[0].nodeValue
    else:
        return None


def get_child_element(xml_document, tag_name):
    if xml_document is None:
        return None
    for child in xml_document.childNodes:
        if child.nodeName == tag_name:
            return child
    return None


def get_child_value(xml_document, tag_name):
    child = get_child_element(xml_document, tag_name)
    return get_element_value(child)


def get_xml_elements(xml_document, tag_name):
    if xml_document and xml_document.getElementsByTagName(tag_name):
        return xml_document.getElementsByTagName(tag_name)
    else:
        return {}


def get_xml_element(xml_document, tag_name, index=0):
    if xml_document and xml_document.getElementsByTagName(tag_name):
        return xml_document.getElementsByTagName(tag_name)[index]
    else:
        return None


def get_xml_value(xml_document, tag_name, default=None):
    if xml_document and xml_document.getElementsByTagName(tag_name):
        node = xml_document.getElementsByTagName(tag_name)[0]
        return get_element_value(node)
    else:
        return default


def has_duplicate_xml_node(xml_document, node):
    nodes = get_xml_elements(xml_document, node.nodeName)
    for n in nodes:
        if n.toxml() == node.toxml():
            return True
    return False


def prettify_xml(xml_document):
    reparsed = parseString(xml_document.toxml())
    return '\n'.join([line for line in reparsed.toprettyxml(indent=' '*2, encoding="utf-8").split('\n') if line.strip()])


def dump_file(file):
    with open(file, "r") as f:
        print(file, f.read())


def replace_in_file(filename, old, new, flags=None):
    with open(filename) as f:
        if flags is None:
            content = re.sub(old, new, f.read())
        else:
            content = re.sub(old, new, f.read(), flags=flags)

    with open(filename, "w") as f:
        f.write(content)


EMPTY_MANIFEST = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<manifest\n'
    '   xmlns:android="http://schemas.android.com/apk/res/android"\n'
    '   package="{{android.package}}">\n'
    '   <uses-sdk\n'
    '       xmlns:tools="http://schemas.android.com/tools"\n'
    '       android:minSdkVersion="{{android.minimum_sdk_version}}"\n'
    '       android:targetSdkVersion="{{android.target_sdk_version}}" />\n'
    '   <application xmlns:tools="http://schemas.android.com/tools">\n'
    '   </application>\n'
    '</manifest>'
)
def create_empty_manifest(filename):
    with open(filename, "w") as file:
        file.write(EMPTY_MANIFEST)


def merge_manifest_files(src_manifest_name, dst_manifest_name):
    replace_in_file(src_manifest_name, r"\$\{applicationId\}", r"{{android.package}}")
    manifest_merger = "java -jar manifest-merger.jar --main %s --libs %s --out %s" % (dst_manifest_name, src_manifest_name, dst_manifest_name)
    call(manifest_merger, shell=True)


@contextmanager
def tmpdir():
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)


def unzip(zipfile_name, destination):
    print("Unpacking {}".format(zipfile_name))
    zip_ref = zipfile.ZipFile(zipfile_name, 'r')
    zip_ref.extractall(destination)
    zip_ref.close()


def add_to_zip(zipfile_name, file_to_add, path_in_zip):
    zip_ref = zipfile.ZipFile(zipfile_name, 'a')
    zip_ref.write(file_to_add, path_in_zip)
    zip_ref.close()


def zip_dir(zipfile_name, dir, base_dir):
    shutil.make_archive(zipfile_name, "zip", dir)


def download_file(url, destination):
    filename = os.path.join(destination, url.rsplit('/', 1)[-1])
    if os.path.exists(filename):
        print("File %s already exists" % (filename))
        sys.exit(1)
    print("Downloading {}".format(url))
    urllib.urlretrieve(url, filename)
    return filename


def download_string(url):
    """ Download data from a URL into a string.
    """
    handle = urllib.urlopen(url)
    return handle.read()


def download_from_builtins(filename, destination):
    stable = download_string("http://d.defold.com/stable/info.json")
    stable_json = json.loads(stable)
    builtins_url = "http://d.defold.com/archive/%s/engine/share/builtins.zip" % (stable_json.get("sha1"))
    with tmpdir() as tmp_dir:
        builtins_file = download_file(builtins_url, tmp_dir)
        unzip(builtins_file, tmp_dir)
        shutil.move(os.path.join(tmp_dir, filename), destination)


def download_android_manifest(destination):
    return download_from_builtins("builtins/manifests/android/AndroidManifest.xml", destination)


def copy_merge(src, dst):
    for name in os.listdir(src):
        src_file = os.path.join(src, name)
        dst_file = os.path.join(dst, name)
        if os.path.exists(dst_file) and os.path.isdir(src_file):
            copy_merge(src_file, dst_file)
        else:
            os.rename(src_file, dst_file)

def find_files(root_dir, file_pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, file_pattern):
            matches.append(os.path.join(root, filename))
    return matches


#
# Process an AAR file
# This will unzip it and handle the contents:
# * R.java will get generated from resources
# * Resources will get copied to the output folder
# * classes.jar will get copied to the output folder
# * Manifest stubs will get merged with the main manifest in the output folder
#
def process_aar(name, aar_file, args, manifest_file):
    print("Processing {}".format(aar_file))
    with tmpdir() as zip_dir:
        unzip(aar_file, zip_dir)

        # rename resources to unique filenames
        res_dir = os.path.join(zip_dir, "res")
        if os.path.exists(res_dir):
            for file in find_files(res_dir, "values*.xml"):
                os.rename(file, os.path.join(os.path.dirname(file), name + "-" + os.path.basename(file)))

        r_file = os.path.join(zip_dir, "R.txt")
        if os.path.exists(r_file) and os.path.getsize(r_file) > 0:
            # generate R.java
            manifest_xml = os.path.join(zip_dir, "AndroidManifest.xml")
            if os.path.exists(res_dir):
                aapt = "${ANDROID_HOME}/build-tools/%s/aapt package --non-constant-id -f -m -M %s -S %s -I ${ANDROID_HOME}/platforms/android-%s/android.jar -J %s" % (args.build_tools_version, manifest_xml, res_dir, args.android_platform_version, zip_dir)
            else:
                aapt = "${ANDROID_HOME}/build-tools/%s/aapt package --non-constant-id -f -m -M %s -I ${ANDROID_HOME}/platforms/android-%s/android.jar -J %s" % (args.build_tools_version, manifest_xml, args.android_platform_version, zip_dir)
            print("Running Android Asset Packaging Tool with args '{}'".format(aapt))
            call(aapt, shell=True)

            # compile R.java and add to classes.jar
            for rjava_file in find_files(zip_dir, "R.java"):
                javac(rjava_file)
                for class_file in find_files(zip_dir, "*.class"):
                    add_to_zip(os.path.join(zip_dir, "classes.jar"), class_file, os.path.relpath(class_file, zip_dir))
        else:
            print("Not generating R.java since dependency has no resources")

        # copy resources
        src_res_dir = res_dir
        dst_res_dir = get_res_dir(args)
        if os.path.exists(src_res_dir):
            dst = os.path.join(dst_res_dir, name + "-" + os.path.basename(aar_file).replace(".aar", ""))
            if not os.path.exists(dst):
                os.makedirs(dst)
            copy_merge(src_res_dir, dst)
            if len(os.listdir(dst) ) == 0:
                os.rmdir(dst)

        # copy classes.jar
        classes_jar = os.path.join(zip_dir, "classes.jar")
        if os.path.exists(classes_jar):
            lib_dir = get_lib_dir(args)
            classes_jar_dest = os.path.join(lib_dir, name + "-" + os.path.basename(aar_file).replace(".aar", ".jar"))
            shutil.move(classes_jar, classes_jar_dest)

        # merge manifest
        android_manifest = os.path.join(zip_dir, "AndroidManifest.xml")
        if os.path.exists(android_manifest):
            merge_manifest_files(android_manifest, manifest_file)

        # copy proguard file
        proguard_txt = os.path.join(zip_dir, "proguard.txt")
        if os.path.exists(proguard_txt):
            manifest_dir = get_manifest_dir(args)
            shutil.copy(proguard_txt, os.path.join(manifest_dir, name + ".pro"))


#
# Process a single dependency
# This will download the dependency (.jar or .aar). In the case of an .aar file
# it will get unpacked.
#
def process_dependency(name, url, args, manifest_file):
    print("\nProcessing dependency {} {}".format(name, url))
    with tmpdir() as tmp_dir:
        dependency_file = download_file(url, tmp_dir)
        if dependency_file.endswith(".jar"):
            # copy jar
            lib_dir = get_lib_dir(args)
            dst_file = os.path.join(lib_dir, name + "-" + os.path.basename(dependency_file))
            if not os.path.exists(dst_file):
                print("Moving %s to %s" % (dependency_file, dst_file))
                shutil.move(dependency_file, dst_file)
        elif dependency_file.endswith(".aar"):
            process_aar(name, dependency_file, args, manifest_file)


#
# Process a list of dependencies
# This will download the dependencies one by one
#
def process_dependencies(dependencies, args, exceptions):
    print("Downloading and unpacking Android dependencies")

    manifest_file = os.path.join(get_manifest_dir(args), "AndroidManifest.xml")
    if os.path.exists(manifest_file):
        os.remove(manifest_file)

    create_empty_manifest(manifest_file)

    for name, data in dependencies.iteritems():
        if not exceptions or not name in exceptions:
            process_dependency(data["group_id"], data["url"], args, manifest_file)



maven_url_cache = {}

#
# Translate a group into a URL
#
def maven_url(group_id, artifact_id, version, extension):
    filename = artifact_id + "-" + version + "." + extension
    if maven_url_cache.get(filename):
        return maven_url_cache.get(filename)

    REPOS = ["https://maven.google.com", "http://central.maven.org/maven2", "http://repo.spring.io/libs-release"]
    for repo in REPOS:
        url = "/".join([repo, group_id.replace(".", "/"), artifact_id, version, filename])
        if urllib.urlopen(url).code == 200:
            maven_url_cache[filename] = url
            return url
    print("Unable to find a url for group {} artifact {} version {} and extension {}".format(url, group_id, artifact_id, version, extension))
    exit(1)


pom_cache = {}

#
# Recurseively download a POM and all its parents
#
def download_pom(pom_url):
    if pom_cache.get(pom_url):
        print("  Ignoring artifact '{}' since it has already been downloaded".format(pom_url))
        return
    print("Downloading artifact '{}'".format(pom_url))

    # download and parse pom
    with tmpdir() as tmp_dir:
        pom_file = download_file(pom_url, tmp_dir)
        xmldoc = minidom.parse(pom_file)

    pom_cache[pom_url] = xmldoc

    # download and parse parent POMs recursively
    project = get_xml_element(xmldoc, "project")
    parent = get_xml_element(project, "parent")
    if parent:
        parent_group_id = get_child_value(parent, "groupId")
        parent_artifact_id = get_child_value(parent, "artifactId")
        parent_version_id = get_child_value(parent, "version")
        parent_pom_url = maven_url(parent_group_id, parent_artifact_id, parent_version_id, "pom")
        print("  Downloading parent artifact '{}'".format(parent_pom_url))
        download_pom(parent_pom_url)


#
# Get an element from a POM
# This will take inheritance into consideration by first looking at any parent POMs
#
def get_pom_element(pom_url, tag_name):
    # some values are never inherited from parent POMs
    NOT_INHERITED = ["artifactId", "name", "prerequisites", "packaging"]

    xmldoc = pom_cache[pom_url]
    project = get_xml_element(xmldoc, "project")

    element = get_child_element(project, tag_name)
    if element:
        return element
    elif tag_name in NOT_INHERITED:
        return None

    parent = get_xml_element(project, "parent")
    if parent:
        parent_group_id = get_child_value(parent, "groupId")
        parent_artifact_id = get_child_value(parent, "artifactId")
        parent_version_id = get_child_value(parent, "version")
        parent_pom_url = maven_url(parent_group_id, parent_artifact_id, parent_version_id, "pom")
        return get_pom_element(parent_pom_url, tag_name)
    else:
        return None


#
# Get a value from a POM
# This will take inheritance into consideration by first looking at any parent POMs
#
def get_pom_value(pom_url, tag_name, default=None):
    element = get_pom_element(pom_url, tag_name)
    value = ""
    if element:
        value = get_element_value(element)
    else:
        value = default
    return value


#
# Recursivley process POM files adding each to the output dictionary
#
def process_pom(pom_url, parent_id, dependencies_out):
    # Replace a template value ${foo} with the actual value read from a list of properties
    def replace_property(value, properties):
        if value and value.startswith("${"):
            value = value.replace("${", "").replace("}", "")
            value = get_child_value(properties, value)
        return value

    # Get the version tag value from an element
    def get_version(element):
        version = get_child_value(element, "version")
        if version:
            version = version.replace("[", "").replace("]", "").split(",", 1)[0]
        return version

    # Get the version of this pom (will traverse parents)
    def get_project_version():
        return get_pom_value(pom_url, "version")

    download_pom(pom_url)

    properties = get_pom_element(pom_url, "properties")
    group_id = get_pom_value(pom_url, "groupId")
    artifact_id = get_pom_value(pom_url, "artifactId")
    packaging = get_pom_value(pom_url, "packaging", "jar")
    if packaging == "bundle":
        packaging = "jar"
    version = replace_property(get_project_version(), properties)
    url = maven_url(group_id, artifact_id, version, packaging)
    group_formatted = group_id.replace(".", "-")
    dependency_id = group_formatted + "-" + artifact_id
    if dependencies_out.get(dependency_id):
        print("  Ignoring artifact '{}' since it has already been processed".format(dependency_id))
        return
    dependencies_out[dependency_id] = {"url":url, "group_id":group_formatted, "parent_id":parent_id}
    # process artifact dependencies
    dependencies = get_pom_element(pom_url, "dependencies")
    if dependencies:
        for dependency in get_xml_elements(dependencies, "dependency"):
            dependency_artifact_id = get_child_value(dependency, "artifactId")
            dependency_scope = get_child_value(dependency, "scope")
            if dependency_scope and dependency_scope != "test":
                print("  Including artifact dependency '{}' with scope '{}'".format(dependency_artifact_id, dependency_scope))
                dependency_group_id = get_child_value(dependency, "groupId")
                dependency_version = replace_property(get_version(dependency), properties) or version
                dependency_pom_url = maven_url(dependency_group_id, dependency_artifact_id, dependency_version, "pom")
                process_pom(dependency_pom_url, dependency_id, dependencies_out)
            else:
                print("  Ignoring artifact dependency '{}' with scope '{}'".format(dependency_artifact_id, dependency_scope))


def read_exceptions(exps):
    result = None
    if exps:
        for path in exps:
            if os.path.exists(path):
                with open(path, "r") as ex_file:
                    if not result:
                        result = json.loads(ex_file.read())
                    else:
                        data = json.loads(ex_file.read())
                        for att, val in data.iteritems():
                            result[att] = val
            else:
                print("File {} do not exist".format(path))
                os._exit(1)
    return result


#
# Process a list of POMs
#
def process_poms(poms):
    print("Downloading and processing POMs", poms)
    dependencies = {}
    for pom in poms:
        process_pom(pom, None, dependencies)
    return dependencies


GAME_PROJECT = (
    '[library]\n'
    'include_dirs = {}\n'
)
EXT_MANIFEST = "name: {}\n"
EXTENSION_CPP = 'extern "C" void %s() {}'
def create_project(args):
    if not os.path.exists(get_project_dir(args)):
        os.makedirs(get_project_dir(args))
    makedirs(get_lib_dir(args))
    makedirs(get_manifest_dir(args))
    makedirs(get_res_dir(args))
    makedirs(get_src_dir(args))
    project_name = args.project_name
    fixed_project_name = project_name.replace("-", " ").title().replace(" ", "_").replace(".", "_")
    with open(os.path.join(get_project_dir(args), "game.project"), "w") as file:
        file.write(GAME_PROJECT.format(project_name))
    with open(os.path.join(get_extension_dir(args), "ext.manifest"), "w") as file:
        file.write(EXT_MANIFEST.format(fixed_project_name))
    with open(os.path.join(get_src_dir(args), "extension.cpp"), "w") as file:
        file.write(EXTENSION_CPP % (fixed_project_name))


def clear_project(args):
    cleardirs(get_lib_dir(args))
    cleardirs(get_manifest_dir(args))
    cleardirs(get_res_dir(args))
    cleardirs(get_src_dir(args))


def zip_project(args):
    print("\nZipping project {} to {}".format(args.project_name, args.project_name + ".zip"))
    zip_filename = os.path.join(args.out, args.project_name)
    zip_file = zip_filename + ".zip"
    if os.path.exists(zip_file):
        os.remove(zip_file)
    zip_dir(zip_filename, get_project_dir(args), args.out)


def add_argument(parser, short, long, dest, help, default=None, required=False, action="store"):
    # parser.add_argument(short, dest=dest, help=help, default=default, required=required, action=action)
    parser.add_argument(short, long, dest=dest, help=help, default=default, required=required, action=action)


parser = ArgumentParser()
parser.add_argument('commands', nargs="+", help='Commands (poms, deps, help)')
add_argument(parser, "-o", "--out", "out", "Path to generate files in", default="out")
add_argument(parser, "-d", "--deps", "deps", "Filename to read/write dependencies json from", default="dependencies.json")
add_argument(parser, "-p", "--pom", "poms", "Path to POM file to process. For use with the 'poms' command.", action="append")
add_argument(parser, "-btv", "--build-tools-version", "build_tools_version", "Android build tools version. Optional, for use with 'deps' command.", default="28.0.2")
add_argument(parser, "-apv", "--android-platform-version", "android_platform_version", "Android platform version. Optional, for use with 'deps' command.", default="26")
add_argument(parser, "-ex", "--exclude", "exceptions", "JSON file with dependencies you want to exclude", action="append")
add_argument(parser, "-pn", "--project-name", "project_name", "Name of the project to create", required=True)
args = parser.parse_args()

help = """
COMMANDS:
poms = Process POMs. This will download, parse and generate a list of all dependencies (direct and transitive) to the file specified by [-d|--deps].

deps = Process dependencies and create a project. This will parse the file specified by [-d|--deps], download the .aar or .jar files, copy resources and generate an AndroidManifest.xml.

zip = Zip generated project files.
"""


if not os.path.exists(args.out):
    os.makedirs(args.out)

create_project(args)

deps_file = os.path.join(get_project_dir(args), args.deps)

exceptions = read_exceptions(args.exceptions)

for command in args.commands:
    if command == "help":
        parser.print_help()
        print(help)
        sys.exit(0)

    if command == "poms":
        with open(deps_file, "w") as file:
            file.write(json.dumps(process_poms(args.poms), indent=2, sort_keys=True))

    if command == "deps":
        if not os.path.exists(deps_file):
            print("File %s does not exist" % (deps_file))
            sys.exit(1)
        clear_project(args)
        create_project(args)
        with open(deps_file, "r") as file:
            dependencies = json.loads(file.read())
            process_dependencies(dependencies, args, exceptions)

    if command == "zip":
        zip_project(args)

# Success!
print("Done")
