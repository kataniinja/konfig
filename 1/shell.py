import tarfile
import sys
import posixpath
import os
import subprocess
from datetime import datetime
import csv
import platform

class VirtualFile:
    def __init__(self, name, is_dir=False):
        self.name = name
        self.is_dir = is_dir
        self.children = {}  # Для директорий
        self.content = ""   # Для файлов

class VirtualFileSystem:
    def __init__(self, tar_path):
        self.root = VirtualFile("/", is_dir=True)
        self.current_path = "/"
        self.load_tar(tar_path)
    
    def load_tar(self, tar_path):
        if not tarfile.is_tarfile(tar_path):
            print(f"Tar archive {tar_path} does not exist or is not a valid tar file.")
            sys.exit(1)
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                if member.name in ['.', './', '']:
                    continue
                path = '/' + member.name.strip('/')
                parts = path.split('/')

                if parts[-1] == '':
                    continue

                current = self.root
                for part in parts[1:-1]:
                    if part not in current.children:
                        current.children[part] = VirtualFile(part, is_dir=True)
                    current = current.children[part]
                if member.isdir():
                    current.children[parts[-1]] = VirtualFile(parts[-1], is_dir=True)
                else:
                    vf = VirtualFile(parts[-1], is_dir=False)
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        try:
                            vf.content = file_obj.read().decode('utf-8')
                        except UnicodeDecodeError:
                            vf.content = ""
                    current.children[parts[-1]] = vf
    
    def get_node(self, path):
        if posixpath.isabs(path):
            path = path.lstrip('/')
            current = self.root
        else:
            current = self.root
            if self.current_path != "/":
                parts = self.current_path.strip('/').split('/')
                for part in parts:
                    current = current.children.get(part)
                    if current is None:
                        return None
        if path == "":
            return current
        parts = path.split('/')
        for part in parts:
            if part == "..":
                if current == self.root:
                    continue
                parent = self.root
                parent_path = posixpath.dirname(self.current_path)
                if parent_path != '/':
                    parts_parent = parent_path.strip('/').split('/')
                    for p in parts_parent:
                        if p:
                            parent = parent.children.get(p)
                            if parent is None:
                                break
                current = parent if parent else self.root
            elif part == "." or part == "":
                continue
            else:
                current = current.children.get(part)
                if current is None:
                    return None
        return current
    
    def list_dir(self, path):
        node = self.get_node(path)
        if node and node.is_dir:
            return sorted(node.children.keys())
        else:
            return None
    
    def change_dir(self, path):
        node = self.get_node(path)
        if node and node.is_dir:
            if posixpath.isabs(path):
                self.current_path = posixpath.normpath(path)
            else:
                self.current_path = posixpath.normpath(posixpath.join(self.current_path, path))
            if not self.current_path.startswith('/'):
                self.current_path = '/' + self.current_path
            return True
        else:
            return False

class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.vfs = VirtualFileSystem(self.config['archive_path'])
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'clear': self.cmd_clear
        }
        self.running = True
        if self.config.get('startup_script'):
            self.run_startup_script(self.config['startup_script'])

    def load_config(self, config_path):
        if not os.path.exists(config_path) or not os.path.isfile(config_path):
            print(f"Configuration file {config_path} does not exist.")
            sys.exit(1)
        with open(config_path, 'r') as f:
            reader = csv.DictReader(f)
            self.config = next(reader)  # Предполагаем, что конфигурация есть только одна строка

    def run_startup_script(self, script_path):
        if os.path.exists(script_path):
            with open(script_path, 'r') as script_file:
                for line in script_file:
                    cmd_input = line.strip()
                    if cmd_input:
                        parts = cmd_input.split()
                        cmd = parts[0]
                        args = parts[1:]
                        if cmd in self.commands:
                            self.commands[cmd](args)

    def run(self):
        while self.running:
            try:
                cmd_input = input(f"{self.config['username']}@shell:{self.vfs.current_path}$ ").strip()
                if not cmd_input:
                    continue
                parts = cmd_input.split()
                cmd = parts[0]
                args = parts[1:]
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"{cmd}: command not found")
            except (EOFError, KeyboardInterrupt):
                print()
                break

    def cmd_ls(self, args):
        path = args[0] if args else "."
        listing = self.vfs.list_dir(path)
        if listing is not None:
            print('  '.join(listing))
        else:
            print(f"ls: cannot access '{path}': No such directory")

    def cmd_cd(self, args):
        if not args:
            print("cd: missing operand")
            return
        path = args[0]
        success = self.vfs.change_dir(path)
        if not success:
            print(f"cd: no such file or directory: {path}")

    def cmd_exit(self, args):
        self.running = False

    def cmd_whoami(self, args):
        print(self.config['username'])

    def cmd_date(self, args):
        print(datetime.now().strftime('%a %b %d %H:%M:%S %Y'))

    def cmd_clear(self, args):
        if platform.system() == "Windows":
            subprocess.run('cls', shell=True)  # Для Windows
        else:
            subprocess.run('clear', shell=True)  # Для UNIX-подобных систем

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <config.csv>")
        sys.exit(1)
    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    emulator.run()
