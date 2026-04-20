# klyuch_v16.py
import ctypes
import sys
import os
import time
import requests
import json
import re
import random
import urllib3
import webbrowser
import threading
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# PyQt5 для визуального редактора
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
    from PyQt5.QtGui import QFont, QColor, QTextCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("[ОШИБКА] Установите PyQt5: pip install PyQt5 PyQtWebEngine")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== АВТО-ПОВЫШЕНИЕ ПРАВ ====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_and_run():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "".join(sys.argv), None, 1)
        sys.exit(0)

elevate_and_run()

# ==================== ЦВЕТА ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

# ==================== ПРОКСИ МЕНЕДЖЕР ====================
class ProxyManager:
    FALLBACK_PROXIES = [
        "185.199.228.220:80", "20.111.54.16:8123", "138.68.60.8:3128",
        "159.65.77.168:8585", "188.166.211.99:8080", "167.71.5.83:3128",
        "134.209.29.120:8080", "157.245.97.63:80", "165.22.56.186:8080",
        "139.59.1.14:3128", "51.38.185.214:3128", "54.37.141.122:8800",
        "45.155.205.233:8080", "193.29.187.201:3128", "94.102.61.78:8080",
        "185.217.70.133:80", "185.130.5.253:80", "185.220.101.1:8080",
        "45.86.186.1:3128", "103.152.112.120:80", "47.88.67.145:3128",
        "13.250.45.98:8080", "54.169.98.147:80", "18.138.188.236:3128",
    ]
    
    def __init__(self):
        self.working_proxies = []
        self.current_index = 0
        self.user_proxy = None
    
    def set_user_proxy(self, proxy):
        if proxy and ':' in proxy:
            self.user_proxy = proxy
            return True
        return False
    
    def test_proxy(self, proxy):
        try:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            resp = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5, verify=False)
            return resp.status_code == 200
        except:
            return False
    
    def get_working(self):
        print(f"{Colors.CYAN}[ПРОКСИ] Поиск рабочих прокси...{Colors.END}")
        
        if self.user_proxy:
            if self.test_proxy(self.user_proxy):
                print(f"{Colors.GREEN}✅ Ваш прокси работает{Colors.END}")
                self.working_proxies = [self.user_proxy]
                return self.working_proxies
            else:
                print(f"{Colors.RED}❌ Ваш прокси не работает{Colors.END}")
                return []
        
        working = []
        for proxy in self.FALLBACK_PROXIES[:30]:
            if self.test_proxy(proxy):
                working.append(proxy)
                print(f"{Colors.GREEN}✅ {proxy}{Colors.END}")
            else:
                print(f"{Colors.RED}❌ {proxy}{Colors.END}")
        
        self.working_proxies = working
        print(f"{Colors.GREEN}[ПРОКСИ] Найдено: {len(working)}{Colors.END}")
        
        if not working:
            print(f"{Colors.YELLOW}[ПРОКСИ] Использую fallback список{Colors.END}")
            self.working_proxies = self.FALLBACK_PROXIES[:20]
        
        return self.working_proxies
    
    def get_next(self):
        if not self.working_proxies:
            return None
        p = self.working_proxies[self.current_index % len(self.working_proxies)]
        self.current_index += 1
        return p

# ==================== МАССОВАЯ АТАКА ====================
class MassiveAttack:
    def __init__(self, target, proxy_manager, attack_count=100):
        self.target = target
        self.proxy_manager = proxy_manager
        self.attack_count = max(35, min(200, attack_count))
        self.completed = 0
        self.successful = 0
        self.start_time = None
        self.lock = threading.Lock()
        self.results = []
    
    def _attack_one(self, attack_id):
        proxy = self.proxy_manager.get_next()
        session = requests.Session()
        session.verify = False
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
        
        if proxy:
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        paths = ["/admin", "/login", "/wp-admin", "/phpmyadmin", "/config.php",
                 "/.env", "/backup.zip", "/robots.txt", "/admin/login.php",
                 "/administrator", "/cpanel", "/info.php", "/.git/config"]
        
        path = random.choice(paths)
        url = self.target.rstrip('/') + path
        
        start = time.time()
        try:
            resp = session.get(url, timeout=8)
            elapsed = time.time() - start
            success = resp.status_code in [200, 403, 401]
            
            with self.lock:
                self.completed += 1
                if success:
                    self.successful += 1
                print(f"{Colors.GREEN if success else Colors.RED}[{self.completed}/{self.attack_count}] {'✅' if success else '❌'} {path} | {resp.status_code} | {elapsed:.1f}s{Colors.END}")
            
            return {"id": attack_id, "path": path, "status": resp.status_code, "time": elapsed, "success": success}
        except:
            with self.lock:
                self.completed += 1
                print(f"{Colors.RED}[{self.completed}/{self.attack_count}] ❌ {path} | ОШИБКА{Colors.END}")
            return {"id": attack_id, "path": path, "status": "ERROR", "time": 0, "success": False}
    
    def run(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}🔥 МАССИВНАЯ АТАКА 🔥{Colors.END}")
        print(f"{Colors.CYAN}🎯 {self.target}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ ПОТОКОВ: {self.attack_count}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.attack_count) as executor:
            futures = [executor.submit(self._attack_one, i+1) for i in range(self.attack_count)]
            for future in as_completed(futures):
                self.results.append(future.result())
        
        total_time = time.time() - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}📊 СТАТИСТИКА{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.YELLOW}⏱️  Время: {total_time:.1f} сек{Colors.END}")
        print(f"{Colors.GREEN}✅ Успешно: {self.successful}{Colors.END}")
        print(f"{Colors.RED}❌ Неудачно: {self.attack_count - self.successful}{Colors.END}")
        print(f"{Colors.CYAN}📈 Процент: {(self.successful/self.attack_count)*100:.1f}%{Colors.END}")
        
        return self.results

# ==================== ВСТРОЕННЫЙ ВИЗУАЛЬНЫЙ РЕДАКТОР ====================
class VisualEditor(QMainWindow):
    def __init__(self, target_url, proxy=None):
        super().__init__()
        self.target_url = target_url
        self.proxy = proxy
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(f"KLYUCH V16 - ВИЗУАЛЬНЫЙ РЕДАКТОР: {self.target_url}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QTextEdit, QLineEdit { background-color: #0a0a0a; color: #0f0; border: 1px solid #f00; font-family: monospace; }
            QPushButton { background-color: #e74c3c; color: white; border: none; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #c0392b; }
            QLabel { color: #ecf0f1; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(10)
        
        # Левая панель (инструменты)
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_panel.setStyleSheet("background-color: #0a0a0a; border-right: 1px solid #f00;")
        left_layout = QVBoxLayout(left_panel)
        
        # Заголовок
        title = QLabel("🔑 KLYUCH V16 - РЕДАКТОР")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f00; padding: 10px;")
        left_layout.addWidget(title)
        
        # URL
        url_label = QLabel("Целевой URL:")
        left_layout.addWidget(url_label)
        self.url_input = QLineEdit(self.target_url)
        left_layout.addWidget(self.url_input)
        
        load_btn = QPushButton("🔄 ЗАГРУЗИТЬ СТРАНИЦУ")
        load_btn.clicked.connect(self.load_url)
        left_layout.addWidget(load_btn)
        
        # HTML редактор
        html_label = QLabel("HTML код для внедрения:")
        left_layout.addWidget(html_label)
        self.html_editor = QTextEdit()
        self.html_editor.setPlaceholderText("""
Примеры:
<div style='color:red; font-size:30px;'>САЙТ ВЗЛОМАН!</div>
<script>alert('Hacked by KLYUCH!');</script>
<img src='https://i.imgur.com/xxx.jpg'>
        """.strip())
        self.html_editor.setMinimumHeight(200)
        left_layout.addWidget(self.html_editor)
        
        # Кнопки действий
        inject_btn = QPushButton("💉 ВНЕДРИТЬ HTML КОД")
        inject_btn.clicked.connect(self.inject_html)
        left_layout.addWidget(inject_btn)
        
        inject_panel_btn = QPushButton("🔑 ВНЕДРИТЬ ПАНЕЛЬ УПРАВЛЕНИЯ")
        inject_panel_btn.clicked.connect(self.inject_panel)
        left_layout.addWidget(inject_panel_btn)
        
        inject_alert_btn = QPushButton("⚠️ ВНЕДРИТЬ ALERT")
        inject_alert_btn.clicked.connect(self.inject_alert)
        left_layout.addWidget(inject_alert_btn)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #f00;")
        left_layout.addWidget(line)
        
        # Извлечение данных
        extract_label = QLabel("📊 ИЗВЛЕЧЕНИЕ ДАННЫХ:")
        extract_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(extract_label)
        
        extract_emails_btn = QPushButton("📧 ИЗВЛЕЧЬ EMAILS")
        extract_emails_btn.clicked.connect(self.extract_emails)
        left_layout.addWidget(extract_emails_btn)
        
        extract_passwords_btn = QPushButton("🔑 ИЗВЛЕЧЬ ПАРОЛИ")
        extract_passwords_btn.clicked.connect(self.extract_passwords)
        left_layout.addWidget(extract_passwords_btn)
        
        extract_links_btn = QPushButton("🔗 ИЗВЛЕЧЬ ССЫЛКИ")
        extract_links_btn.clicked.connect(self.extract_links)
        left_layout.addWidget(extract_links_btn)
        
        # Лог
        log_label = QLabel("📋 ЛОГ ДЕЙСТВИЙ:")
        left_layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        left_layout.addWidget(self.log_text)
        
        # Правая панель (браузер)
        self.browser = QWebEngineView()
        self.load_url()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.browser, 1)
        
        self.log("✅ Визуальный редактор запущен")
        self.log(f"🎯 Цель: {self.target_url}")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def load_url(self):
        url = self.url_input.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.target_url = url
        self.log(f"Загрузка: {url}")
        
        # Настройка прокси для браузера (QWebEngine не поддерживает прокси напрямую)
        self.browser.setUrl(QUrl(url))
    
    def inject_html(self):
        html_code = self.html_editor.toPlainText()
        if not html_code:
            self.log("❌ Введите HTML код для внедрения")
            return
        
        # Инъекция через JavaScript
        js_code = f"""
        (function() {{
            var div = document.createElement('div');
            div.innerHTML = `{html_code.replace('`', '\\`')}`;
            div.style.position = 'fixed';
            div.style.bottom = '10px';
            div.style.right = '10px';
            div.style.zIndex = '999999';
            div.style.background = '#000';
            div.style.color = '#0f0';
            div.style.border = '2px solid #0f0';
            div.style.padding = '10px';
            div.style.fontFamily = 'monospace';
            document.body.appendChild(div);
            console.log('KLYUCH: HTML injected');
        }})();
        """
        self.browser.page().runJavaScript(js_code)
        self.log(f"✅ HTML код внедрён на страницу")
    
    def inject_panel(self):
        panel_code = """
        (function() {
            var panel = document.createElement('div');
            panel.id = 'klyuchPanel';
            panel.innerHTML = `
                <div style="position:fixed; bottom:10px; right:10px; background:#000; color:#0f0; z-index:999999; padding:15px; border:3px solid #0f0; border-radius:10px; font-family:monospace; width:280px;">
                    <b style="color:#f00;">🔑 KLYUCH V16 CONTROL PANEL</b><br>
                    <textarea id="klyuchText" rows="3" style="width:100%; background:#111; color:#0f0; border:1px solid #0f0;" placeholder="Введите текст..."></textarea><br>
                    <button id="klyuchBtn" style="background:#0f0; color:#000; border:none; padding:5px; margin-top:5px;">✏️ ИЗМЕНИТЬ САЙТ</button>
                    <button id="klyuchClose" style="background:#f00; color:#fff; border:none; padding:5px; margin-top:5px;">❌ ЗАКРЫТЬ</button>
                    <br><span style="font-size:10px; color:#666;">САЙТ ВЗЛОМАН ЧЕРЕЗ KLYUCH V16</span>
                </div>
            `;
            document.body.appendChild(panel);
            
            document.getElementById('klyuchBtn').onclick = function() {
                var text = document.getElementById('klyuchText').value;
                var msg = document.createElement('div');
                msg.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#000;color:#0f0;border:2px solid #0f0;padding:20px;z-index:1000000;font-size:20px;';
                msg.innerHTML = text || 'САЙТ ВЗЛОМАН!';
                document.body.appendChild(msg);
                setTimeout(function() { msg.remove(); }, 3000);
            };
            document.getElementById('klyuchClose').onclick = function() {
                document.getElementById('klyuchPanel').remove();
            };
        })();
        """
        self.browser.page().runJavaScript(panel_code)
        self.log("✅ Панель управления внедрена на сайт")
    
    def inject_alert(self):
        js_code = "alert('🔑 KLYUCH V16 - САЙТ ВЗЛОМАН! 🔑');"
        self.browser.page().runJavaScript(js_code)
        self.log("✅ Alert внедрён")
    
    def extract_emails(self):
        js_code = """
        (function() {
            var text = document.body.innerText;
            var emails = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g) || [];
            return emails.join('\\n');
        })();
        """
        self.browser.page().runJavaScript(js_code, self.show_extracted_data)
        self.log("📧 Извлечение email адресов...")
    
    def extract_passwords(self):
        js_code = """
        (function() {
            var inputs = document.querySelectorAll('input[type="password"]');
            var passwords = [];
            inputs.forEach(function(input) {
                if(input.value) passwords.push(input.value);
            });
            return passwords.join('\\n');
        })();
        """
        self.browser.page().runJavaScript(js_code, self.show_extracted_data)
        self.log("🔑 Поиск паролей в формах...")
    
    def extract_links(self):
        js_code = """
        (function() {
            var links = document.querySelectorAll('a');
            var urls = [];
            links.forEach(function(link) {
                if(link.href) urls.push(link.href);
            });
            return urls.join('\\n');
        })();
        """
        self.browser.page().runJavaScript(js_code, self.show_extracted_data)
        self.log("🔗 Извлечение ссылок...")
    
    def show_extracted_data(self, data):
        if data:
            msg = QMessageBox()
            msg.setWindowTitle("Извлечённые данные")
            msg.setText(data[:1000] if len(data) > 1000 else data)
            msg.setStyleSheet("QLabel{min-width: 500px;}")
            msg.exec_()
            self.log(f"✅ Извлечено {len(data.split(chr(10)))} записей")
        else:
            self.log("❌ Данные не найдены")

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
class KlyuchApp:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.target = None
        self.attack_count = 100
        self.results = []
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self):
        print(f"""{Colors.RED}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     ██╗  ██╗██╗  ██╗██╗   ██╗██╗   ██╗ ██████╗██╗  ██╗            ║
║     ██║ ██╔╝██║  ██║██║   ██║██║   ██║██╔════╝██║  ██║            ║
║     █████╔╝ ███████║██║   ██║██║   ██║██║     ███████║            ║
║     ██╔═██╗ ██╔══██║██║   ██║██║   ██║██║     ██╔══██║            ║
║     ██║  ██╗██║  ██║╚██████╔╝╚██████╔╝╚██████╗██║  ██║            ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝            ║
║                                                                   ║
║                    K L Y U C H   V 1 6                           ║
║              VISUAL EDITOR EDITION                               ║
║          ВСТРОЕННЫЙ РЕДАКТОР | РЕАЛЬНОЕ ИЗМЕНЕНИЕ САЙТА          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.END}""")
    
    def setup(self):
        self.clear_screen()
        self.banner()
        
        print(f"{Colors.BOLD}{Colors.GREEN}⚙️  НАСТРОЙКА{Colors.END}")
        print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
        
        self.target = input(f"{Colors.YELLOW}[?] URL цели: {Colors.END}").strip()
        if not self.target.startswith(("http://", "https://")):
            self.target = "https://" + self.target
        
        print(f"\n{Colors.CYAN}[!] Количество атак (35-200):{Colors.END}")
        print(f"  1 - 50 | 2 - 100 | 3 - 150 | 4 - 200 | 5 - Своё")
        
        choice = input(f"{Colors.YELLOW}[?] Выбор: {Colors.END}").strip()
        choices = {'1': 50, '2': 100, '3': 150, '4': 200}
        self.attack_count = choices.get(choice, 100)
        if choice == '5':
            self.attack_count = int(input(f"{Colors.YELLOW}[?] Количество: {Colors.END}"))
            self.attack_count = max(35, min(200, self.attack_count))
        
        print(f"\n{Colors.CYAN}[!] Прокси:{Colors.END}")
        print(f"  1 - Авто (загрузка из списка)")
        print(f"  2 - Свой прокси")
        print(f"  3 - Без прокси")
        
        proxy_choice = input(f"{Colors.YELLOW}[?] Выбор: {Colors.END}").strip()
        
        if proxy_choice == '1':
            self.proxy_manager.get_working()
        elif proxy_choice == '2':
            user_proxy = input(f"{Colors.YELLOW}[?] Прокси (IP:PORT): {Colors.END}").strip()
            if self.proxy_manager.set_user_proxy(user_proxy):
                self.proxy_manager.get_working()
        else:
            print(f"{Colors.YELLOW}Атака без прокси{Colors.END}")
        
        return True
    
    def run_attack(self):
        print(f"\n{Colors.GREEN}[ГОТОВО] Цель: {self.target}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Атак: {self.attack_count}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Прокси: {len(self.proxy_manager.working_proxies)} шт{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Нажмите Enter для атаки...{Colors.END}")
        
        attack = MassiveAttack(self.target, self.proxy_manager, self.attack_count)
        self.results = attack.run()
        
        return attack.successful > 0
    
    def open_editor(self):
        if not PYQT_AVAILABLE:
            print(f"{Colors.RED}[ОШИБКА] PyQt5 не установлен!{Colors.END}")
            print(f"{Colors.YELLOW}Установка: pip install PyQt5 PyQtWebEngine{Colors.END}")
            return
        
        print(f"\n{Colors.GREEN}[РЕДАКТОР] Запуск встроенного визуального редактора...{Colors.END}")
        
        proxy = self.proxy_manager.get_next() if self.proxy_manager.working_proxies else None
        app = QApplication(sys.argv)
        editor = VisualEditor(self.target, proxy)
        editor.show()
        sys.exit(app.exec_())
    
    def run(self):
        if not self.setup():
            input(f"\n{Colors.RED}Нажмите Enter...{Colors.END}")
            return
        
        has_vulns = self.run_attack()
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📊 ЗАВЕРШЕНО{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        if has_vulns:
            print(f"{Colors.GREEN}🔥 Найдены уязвимости!{Colors.END}")
        
        print(f"\n{Colors.YELLOW}[!] Запустить визуальный редактор? (y/n){Colors.END}")
        if input().lower() == 'y':
            self.open_editor()
        else:
            print(f"{Colors.CYAN}До свидания!{Colors.END}")

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    try:
        app = KlyuchApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Прервано{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[ОШИБКА] {e}{Colors.END}")
        input("\nНажмите Enter...")
