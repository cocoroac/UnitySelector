import sys, os, argparse
import pathlib
import subprocess

UNITY_INSTALL_PATH_ENVIRONMENT_KEY = "UNITY_HUB_INSTALL_PATH"


def find_unity_path_for_window():
    import winreg as reg
    key = reg.HKEY_CURRENT_USER
    key_value = "Software\\Unity Technologies\\Installer\\Unity"
    open_key = reg.OpenKey(key, key_value, 0, reg.KEY_READ)
    value, _ = reg.QueryValueEx(open_key, "Location x64")
    return str(pathlib.PureWindowsPath(value) / "Hub" / "Editor")


def find_unity_path_for_macos():
    unity_path = pathlib.PurePosixPath('/Applications/Unity/Hub/Editor')
    if os.path.isdir(unity_path):
        return unity_path.as_posix()
    raise


def find_unity_path_for_environment():
    return os.getenv(UNITY_INSTALL_PATH_ENVIRONMENT_KEY)


def unity_versions_list(unity_hub_path):
    list_subfolders_with_paths = [os.path.basename(os.path.normpath(f.path)) for f in os.scandir(unity_hub_path) if f.is_dir()]
    return list_subfolders_with_paths

def unity_runtime_execute(unity_hub_path, unity_version):
    if sys.platform.startswith('win32'):
        executefile = pathlib.PureWindowsPath(unity_hub_path) / unity_version / "Unity.exe"
    elif sys.platform.startswith('darwin'):
        executefile = pathlib.PurePosixPath(unity_hub_path) / unity_version / "Unity.app/Contents/MacOS/Unity"
    else:
        raise
    return str(executefile)

unity_hub_path = ""
if sys.platform.startswith('win32'):
    try:
        unity_hub_path = find_unity_path_for_window()
    except:
        print('not found unity path for window reg')
elif sys.platform.startswith('darwin'):
    try:
        unity_hub_path = find_unity_path_for_macos()
    except:
        print('not found unity path for directories')
else:
    print('not support platform', file=sys.stderr)
    sys.exit(1)

if not unity_hub_path:
    unity_hub_path = find_unity_path_for_environment()

if not unity_hub_path:
    print('unity not found. try set environment variable to', UNITY_INSTALL_PATH_ENVIRONMENT_KEY, 'or install unity', file=sys.stderr)
    sys.exit(1)

parser = argparse.ArgumentParser(prog='Unity Execute Wrapper')
parser.add_argument('-gv', '--getVersion', action='store_true', help='print installed unity versions')
parser.add_argument('-uv', '--unityVersion', type=str, help='set unity version when execute unity batchmode')
parser.add_argument('-ua', '--unityArgs', type=str, help='set unity args when execute unity batchmode')
args = parser.parse_args()

get_version = args.getVersion

if get_version is True:
    version_list = unity_versions_list(unity_hub_path)
    version_list.sort()
    version_list.reverse()
    for v in version_list:
        print (v)
else:
    try:
        unity_version = args.unityVersion
        unity_args = args.unityArgs
    except:
        print('inavlid arguments', file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if not unity_version:
        print('Unity version is empty', file=sys.stderr)
        sys.exit(1)

    if not unity_args:
        print('Unity args is empty', file=sys.stderr)
        sys.exit(1)

    try:
        executable_file = unity_runtime_execute(unity_hub_path, unity_version)
        subprocess.run([executable_file, unity_args])
    except:
        print('cant get unity executable. check install!', file=sys.stderr)
        sys.exit(1)