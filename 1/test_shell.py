import os
import tempfile
import unittest
from unittest.mock import patch
import csv
from io import StringIO
from datetime import datetime

from shell import ShellEmulator, VirtualFileSystem, VirtualFile

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # Создаем временный CSV-файл с конфигурацией
        tar_path = os.path.join(os.getcwd(), "virtual_fs.tar")
        self.temp_csv_path = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
        with open(self.temp_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['username', 'archive_path', 'startup_script']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'username': 'user1',
                'archive_path': tar_path,
                'startup_script': ''
            })
        # Создаем экземпляр эмулятора
        self.shell = ShellEmulator(self.temp_csv_path)

    def tearDown(self):
        # Удаляем временный CSV-файл после тестов
        os.unlink(self.temp_csv_path)

    # Упрощенные тесты для команды ls
    def test_ls_empty_root(self):
        """Тест для ls в пустой корневой директории"""
        # Создаем виртуальный файл или каталог в корне, если необходимо
        self.shell.vfs.root.children["virtual_fs"] = VirtualFile("virtual_fs", is_dir=True)
        
        # Проверяем, что в корне есть только один каталог "virtual_fs"
        self.assertEqual(self.shell.vfs.list_dir("/"), ["virtual_fs"], "Ошибка в test_ls_empty_root")

    def test_ls_root_with_content(self):
        """Тест для ls в корневой директории с файлами и папками"""
        # Создаем файлы и папки вручную
        dir1 = VirtualFile("dir1", is_dir=True)
        file1 = VirtualFile("file1.txt", is_dir=False)
        self.shell.vfs.root.children["dir1"] = dir1
        self.shell.vfs.root.children["file1.txt"] = file1
        
        # Удаляем virtual_fs, если он существует
        if "virtual_fs" in self.shell.vfs.root.children:
            del self.shell.vfs.root.children["virtual_fs"]
        
        # Проверяем, что файлы и папки появились
        self.assertEqual(sorted(self.shell.vfs.list_dir("/")), ["dir1", "file1.txt"], "Ошибка в test_ls_root_with_content")

    # Упрощенные тесты для команды cd
    def test_cd_valid_directory(self):
        """Тест для cd в существующую директорию"""
        dir1 = VirtualFile("dir1", is_dir=True)
        self.shell.vfs.root.children["dir1"] = dir1
        self.assertTrue(self.shell.vfs.change_dir("/dir1"), "Ошибка в test_cd_valid_directory")

    def test_cd_invalid_directory(self):
        """Тест для cd в несуществующую директорию"""
        self.assertFalse(self.shell.vfs.change_dir("/nonexistent"), "Ошибка в test_cd_invalid_directory")

    # Тесты для команды whoami
    def test_whoami(self):
        """Тест для команды whoami"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.shell.cmd_whoami([])
            output = mock_stdout.getvalue().strip()
            self.assertEqual(output, "user1", "Ошибка в test_whoami")

    # Тесты для команды date
    def test_date(self):
        """Тест для команды date"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.shell.cmd_date([])
            output = mock_stdout.getvalue().strip()
            # Проверим, что дата имеет правильный формат
            try:
                datetime.strptime(output, '%a %b %d %H:%M:%S %Y')
            except ValueError:
                self.fail("Ошибка в test_date: Неверный формат даты")

    # Тесты для команды clear
    @patch('subprocess.run')
    def test_clear_unix(self, mock_run):
        """Тест для команды clear на UNIX-подобной системе"""
        with patch('platform.system', return_value='Linux'):  # Убедитесь, что система Linux
            self.shell.cmd_clear([])
            mock_run.assert_called_with('clear', shell=True)

    @patch('subprocess.run')
    def test_clear_windows(self, mock_run):
        """Тест для команды clear на Windows"""
        with patch('platform.system', return_value='Windows'):
            self.shell.cmd_clear([])
            mock_run.assert_called_with('cls', shell=True)

if __name__ == "__main__":
    unittest.main()
