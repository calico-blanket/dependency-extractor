import os
import re
import ast
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

class DependencyAnalyzer:
    """Pythonファイル内のインポート文を静的解析するクラス"""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = set()
        self.standard_libs = self._get_standard_libs()
    
    def _get_standard_libs(self):
        """Python標準ライブラリのより包括的なリストを返す"""
        return {
            # 基本的なPython標準ライブラリ (Python 3.6〜3.13をカバー)
            "abc", "aifc", "argparse", "array", "ast", "asyncio", "atexit", "audioop", 
            "base64", "bdb", "binascii", "binhex", "bisect", "builtins", 
            "bz2", "cProfile", "calendar", "cgi", "cgitb", "chunk", "cmath", "cmd", 
            "code", "codecs", "codeop", "collections", "colorsys", "compileall", 
            "concurrent", "configparser", "contextlib", "contextvars", "copy", 
            "copyreg", "crypt", "csv", "ctypes", "curses", "dataclasses",
            "datetime", "dbm", "decimal", "difflib", "dis", "distutils", 
            "doctest", "email", "encodings", "ensurepip", "enum", "errno", 
            "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "formatter", 
            "fractions", "ftplib", "functools", "gc", "getopt", "getpass", "gettext", 
            "glob", "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac", "html", 
            "http", "idlelib", "imaplib", "imghdr", "imp", "importlib", "inspect", 
            "io", "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache", 
            "locale", "logging", "lzma", "macpath", "mailbox", "mailcap", "marshal", 
            "math", "mimetypes", "mmap", "modulefinder", "msilib", "msvcrt", 
            "multiprocessing", "netrc", "nis", "nntplib", "numbers", "operator", 
            "optparse", "os", "ossaudiodev", "parser", "pathlib", "pdb", "pickle", 
            "pickletools", "pipes", "pkgutil", "platform", "plistlib", "poplib", 
            "posix", "pprint", "profile", "pstats", "pty", "pwd", "py_compile", 
            "pyclbr", "pydoc", "queue", "quopri", "random", "re", "readline", 
            "reprlib", "resource", "rlcompleter", "runpy", "sched", "secrets", 
            "select", "selectors", "shelve", "shlex", "shutil", "signal", "site", 
            "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd", 
            "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", 
            "struct", "subprocess", "sunau", "symbol", "symtable", "sys", 
            "sysconfig", "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile", 
            "termios", "test", "textwrap", "threading", "time", "timeit", "tkinter", 
            "token", "tokenize", "trace", "traceback", "tracemalloc", "tty", 
            "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest", 
            "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref", 
            "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", 
            "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib", "zoneinfo",
            
            # Python 3.9+ の新しいライブラリ
            "graphlib", "zoneinfo",
            
            # Python 3.10+ の新しいライブラリ
            "tomllib",
            
            # Python 3.11+ の新しいライブラリ
            "tomli", "wsgiref.types", "asyncio.taskgroups", "asyncio.timeouts",
            
            # Python 3.12+ の新しいライブラリ
            "contextlib.chdir", "pathlib.posixpath", "typing.override",
            
            # Python 3.13+ の新しいライブラリと予定されているもの
            "expat", "typing.assert_type", "typing.assert_never", "typing.reveal_type",
            
            # 特殊なモジュール (非公式だが標準)
            "_abc", "_ast", "_bisect", "_blake2", "_bootlocale", "_bz2", "_codecs", 
            "_collections", "_collections_abc", "_compat_pickle", "_compression", 
            "_contextvars", "_csv", "_ctypes", "_curses", "_datetime", "_decimal", 
            "_dummy_thread", "_elementtree", "_frozen_importlib", "_functools", 
            "_gdbm", "_hashlib", "_heapq", "_imp", "_io", "_json", "_locale", 
            "_lsprof", "_lzma", "_markupbase", "_md5", "_multibytecodec", 
            "_multiprocessing", "_opcode", "_operator", "_osx_support", "_pickle", 
            "_posixsubprocess", "_py_abc", "_pydecimal", "_pyio", "_queue", 
            "_random", "_re", "_sha1", "_sha256", "_sha3", "_sha512", "_signal", 
            "_sitebuiltins", "_socket", "_sqlite3", "_sre", "_ssl", "_stat", 
            "_string", "_strptime", "_struct", "_symtable", "_thread", "_threading_local", 
            "_tracemalloc", "_warnings", "_weakref", "_weakrefset", "_xxsubinterpreters", 
            
            # Pythonインタープリタとのやり取りに関するモジュール
            "__future__", "__main__", "_dummy_thread", "_thread",
            
            # 内部で使用される特殊なモジュール
            "antigravity", "this"
        }
    
    def analyze_file(self, file_path):
        """ファイルを解析し、インポート文を抽出する"""
        self.imports = set()
        self.from_imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                
            # ASTを使用してインポート文を解析
            try:
                tree = ast.parse(file_content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            self.imports.add(name.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:  # 'from x import y'
                            self.from_imports.add(node.module.split('.')[0])
            except SyntaxError:
                # ASTパースに失敗した場合は正規表現を使用
                self._analyze_with_regex(file_content)
                
            return True
        except Exception as e:
            messagebox.showerror("Error / エラー", f"File analysis error / ファイル解析中にエラーが発生しました: {str(e)}")
            return False
    
    def _analyze_with_regex(self, content):
        """正規表現を使用してインポート文を抽出"""
        # import文の抽出
        import_pattern = r'^import\s+([\w\.,\s]+)'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        
        for imp in imports:
            modules = imp.split(',')
            for module in modules:
                # 'as'キーワードの処理
                module = module.split('as')[0].strip()
                # '.'の処理
                base_module = module.split('.')[0].strip()
                if base_module:
                    self.imports.add(base_module)
        
        # from import文の抽出
        from_pattern = r'^from\s+([\w\.]+)\s+import'
        froms = re.findall(from_pattern, content, re.MULTILINE)
        
        for module in froms:
            base_module = module.split('.')[0].strip()
            if base_module:
                self.from_imports.add(base_module)
    
    def get_external_dependencies(self):
        """標準ライブラリ以外の依存関係を返す"""
        all_imports = self.imports.union(self.from_imports)
        external_deps = all_imports - self.standard_libs
        return sorted(list(external_deps))

class App:
    """GUI アプリケーション"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Python Library Detector / Pythonライブラリ検出ツール")
        self.root.geometry("650x550")  # ウィンドウサイズを少し大きくする
        self.root.resizable(True, True)
        
        self.analyzer = DependencyAnalyzer()
        self.setup_ui()
    
    def setup_ui(self):
        """UIコンポーネントの設定"""
        # フレーム
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Please select a file / ファイルを選択してください。")
        
        # ファイル選択部分
        file_frame = tk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(file_frame, text="Python file / Pythonファイル:").pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = tk.Button(file_frame, text="Browse... / 参照...", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # 解析ボタン
        analyze_button = tk.Button(frame, text="Detect Libraries / ライブラリを検出", command=self.analyze)
        analyze_button.pack(pady=10)
        
        # 結果表示部分
        result_frame = tk.Frame(frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="Detected Libraries / 検出されたライブラリ:").pack(anchor=tk.W)
        
        # スクロールバー付きテキストエリア
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(result_frame, height=12, width=70, yscrollcommand=scrollbar.set)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.result_text.yview)
        
        # ボタンフレーム
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        # コマンド全体コピーボタン
        copy_button = tk.Button(button_frame, text="Copy Install Command\nインストールコマンドをコピー", 
                               command=self.copy_to_clipboard, width=30, height=2)
        copy_button.pack(pady=8)
        
        # ライブラリ名のみコピーボタン
        copy_libs_button = tk.Button(button_frame, 
                                   text="Copy Library Names Only\nライブラリ名のみコピー", 
                                   command=self.copy_libs_only, width=30, height=2)
        copy_libs_button.pack(pady=8)
        
        # 保存ボタン
        save_button = tk.Button(button_frame, text="Save Results\n結果を保存", 
                              command=self.save_results, width=30, height=2)
        save_button.pack(pady=8)
    
    def browse_file(self):
        """ファイル選択ダイアログを表示"""
        file_path = filedialog.askopenfilename(
            title="Select Python file / Pythonファイルを選択",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def show_status(self, message):
        """ステータスバーにメッセージを表示"""
        self.status_var.set(message)
        # ステータスバーの色を一時的に変更して注目を集める
        original_bg = self.status_bar["background"]
        self.status_bar.config(background="#e6f2ff")  # 薄い青色
        # 2秒後に元の色に戻す
        self.root.after(2000, lambda: self.status_bar.config(background=original_bg))
    
    def analyze(self):
        """ファイルを解析し、結果を表示"""
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("Warning / 警告", "Please select a Python file / Pythonファイルを選択してください。")
            return
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Warning / 警告", "Selected file does not exist / 選択されたファイルが存在しません。")
            return
        
        # テキストエリアをクリア
        self.result_text.delete(1.0, tk.END)
        self.show_status("Analyzing file... / ファイルを解析しています...")
        
        if self.analyzer.analyze_file(file_path):
            dependencies = self.analyzer.get_external_dependencies()
            
            if dependencies:
                self.result_text.insert(tk.END, "Detected external libraries / 検出された外部ライブラリ:\n\n")
                for dep in dependencies:
                    self.result_text.insert(tk.END, f"- {dep}\n")
                
                if 'pip' in dependencies:
                    dependencies.remove('pip')
                
                self.result_text.insert(tk.END, "\n\nInstallation command / インストール用コマンド:\n")
                if dependencies:
                    cmd = "pip install " + " ".join(dependencies)
                    self.result_text.insert(tk.END, cmd)
                else:
                    self.result_text.insert(tk.END, "No external libraries need to be installed / インストールが必要な外部ライブラリはありません。")
            else:
                self.result_text.insert(tk.END, "No external libraries detected / インストールが必要な外部ライブラリは検出されませんでした。")
            
            self.show_status("Analysis complete / 解析が完了しました。")
    
    def save_results(self):
        """結果をテキストファイルとして保存"""
        results = self.result_text.get(1.0, tk.END).strip()
        if not results:
            messagebox.showwarning("Warning / 警告", "No results to save. Please analyze a file first / 保存する結果がありません。先にファイルを解析してください。")
            return
        
        # ファイル名の生成
        file_path = self.file_path_var.get().strip()
        if file_path:
            base_name = os.path.basename(file_path).split('.')[0]
        else:
            base_name = "python_libraries"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_dependencies_{timestamp}.txt"
        
        # デスクトップパスの取得
        desktop_path = str(Path.home() / "Desktop")
        full_path = os.path.join(desktop_path, filename)
        
        # ファイルの保存 - 画面と同じ内容をそのまま保存
        try:
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(results)
            self.show_status(f"Results saved / 結果を保存しました: {full_path}")
        except Exception as e:
            messagebox.showerror("Error / エラー", f"Error saving file / ファイル保存中にエラーが発生しました: {str(e)}")
    
    def _get_dependencies_from_text(self):
        """テキスト領域から外部ライブラリのリストを取得"""
        text_content = self.result_text.get(1.0, tk.END)
        if "Installation command / インストール用コマンド:" not in text_content:
            self.show_status("No installation command to copy. Please analyze a file first / コピーするインストールコマンドがありません。先にファイルを解析してください。")
            return None
        
        # インストールコマンドの行を抽出
        command_line = ""
        for line in text_content.split('\n'):
            if line.startswith("pip install "):
                command_line = line
                break
        
        if not command_line:
            self.show_status("No external libraries need to be installed / インストールが必要な外部ライブラリはありません。")
            return None
            
        # コマンドからライブラリリストを抽出
        libs = command_line.replace("pip install ", "")
        return command_line, libs
    
    def copy_to_clipboard(self):
        """インストール用コマンド全体をクリップボードにコピー"""
        result = self._get_dependencies_from_text()
        if result is None:
            return
            
        command_line, _ = result
        
        # クリップボードにコピー
        self.root.clipboard_clear()
        self.root.clipboard_append(command_line)
        self.root.update()  # クリップボードの更新を確実にするため
        
        self.show_status(f"Installation command copied to clipboard / インストールコマンドをクリップボードにコピーしました: {command_line}")
    
    def copy_libs_only(self):
        """ライブラリ名のみをクリップボードにコピー"""
        result = self._get_dependencies_from_text()
        if result is None:
            return
            
        _, libs = result
        
        # クリップボードにコピー
        self.root.clipboard_clear()
        self.root.clipboard_append(libs)
        self.root.update()  # クリップボードの更新を確実にするため
        
        self.show_status(f"Library names copied to clipboard / ライブラリ名のみをクリップボードにコピーしました: {libs}")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()