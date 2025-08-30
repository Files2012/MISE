# ====== START OF FILE: MISE.py ======
import os
import webbrowser
import threading
import time
import socket
import requests
from flask import Flask, render_template_string, send_from_directory, request, redirect
from datetime import datetime
from waitress import serve

app = Flask(__name__)
server_thread = None
current_directory = ""
host = "0.0.0.0"
port = 5000
is_running = False
start_time = datetime.now()

# HTML Template untuk Admin Panel
ADMIN_PANEL = r"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MIOS</title>
    <style>
        :root {
            --bg: #0f1115;
            --panel: #151923;
            --panel-2: #1b2030;
            --text: #e7eaf0;
            --muted: #9aa3b2;
            --accent: #5b9cff;
            --accent-2: #7dd3fc;
            --danger: #ef4444;
            --ok: #22c55e;
            --warn: #f59e0b;
            --shadow: 0 8px 30px rgba(0,0,0,.35);
            --radius: 14px;
        }

        .light-theme {
            --bg: #f5f5f5;
            --panel: #ffffff;
            --panel-2: #f0f0f0;
            --text: #333;
            --muted: #666;
            --accent: #007bff;
            --accent-2: #4fc3f7;
            --danger: #d32f2f;
            --ok: #43a047;
            --warn: #ffa000;
        }

        * { box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            margin: 0;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
            color: var(--text);
            background: var(--bg);
            transition: background 0.3s ease;
            overflow: hidden;
            user-select: none;
        }

        .desktop {
            position: fixed;
            inset: 0 0 48px 0;
            padding: 24px;
            backdrop-filter: saturate(120%);
            background-size: cover;
            background-position: center;
            transition: background-image 0.5s ease;
        }

        #login-screen {
            position: fixed;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            backdrop-filter: blur(20px);
            z-index: 10000;
            transition: opacity .3s ease;
        }
        #login-screen.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .login-box {
            width: 340px;
            padding: 30px;
            background: linear-gradient(180deg, var(--panel), var(--panel-2));
            border: 1px solid rgba(255,255,255,.08);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            color: var(--text);
        }
        .login-box h2 {
            margin: 0 0 20px;
            text-align: center;
            font-weight: 700;
        }
        #login-error {
            color: var(--danger);
            font-size: .9rem;
            text-align: center;
            margin-top: 12px;
            min-height: 1.2em;
        }
        #loginForm button {
            width: 100%;
            margin-top: 10px;
            justify-content: center;
        }

        .desktop, .taskbar {
            visibility: hidden;
            opacity: 0;
            transition: opacity .3s ease;
        }
        .desktop.visible, .taskbar.visible {
            visibility: visible;
            opacity: 1;
        }

        .taskbar {
            position: fixed;
            left: 0; right: 0; bottom: 0;
            height: 48px;
            background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
            border-top: 1px solid rgba(255,255,255,.06);
            display: grid;
            grid-template-columns: 220px 1fr 220px;
            align-items: center;
            padding: 0 10px;
            gap: 10px;
            backdrop-filter: blur(10px);
        }
        .tb-left, .tb-center, .tb-right { display: flex; align-items: center; gap: 8px; }

        .btn {
            display: inline-flex; align-items: center; gap: 8px;
            border: 1px solid rgba(255,255,255,.08);
            background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
            color: var(--text);
            height: 34px; padding: 0 12px; border-radius: 10px;
            cursor: pointer;
            box-shadow: 0 1px 0 rgba(255,255,255,.05) inset;
            transition: transform .06s ease, background .2s ease, border-color .2s ease;
        }
        .btn:hover { border-color: rgba(255,255,255,.16); }
        .btn:active { transform: translateY(1px); }
        .btn.small { height: 28px; padding: 0 10px; border-radius: 8px; }
        .btn.ghost { background: transparent; border-color: transparent; }

        .start { font-weight: 700; letter-spacing: .2px; }

        .apps-area { display: flex; align-items: center; gap: 6px; height: 100%; overflow-x: auto; scrollbar-width: thin; padding: 4px 0; }

        .task { min-width: 120px; max-width: 220px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }
        .task.active { outline: 2px solid rgba(91,156,255,.12); }

        .clock { margin-left: auto; opacity: .9; font-variant-numeric: tabular-nums; }

        .start-menu { 
            position: fixed; left: 10px; bottom: 58px; width: 360px; max-width: calc(100% - 20px); background: linear-gradient(180deg, var(--panel), var(--panel-2)); border: 1px solid rgba(255,255,255,.08); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; display: none; animation: pop .12s ease;
            color: var(--text);
            z-index: 9999;
        }
        .start-menu.active { display: block; }
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
        }
        .user-info svg {
            width: 24px;
            height: 24px;
            opacity: 0.8;
        }
        .username-display {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text);
        }

        .menu-item { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 12px; cursor: pointer; transition: background .15s ease; }
        .menu-item:hover { background: rgba(255,255,255,.06); }
        .menu-item .title { font-weight: 600; }
        .menu-item .desc { color: var(--muted); font-size: .9rem; }
        
        .start-menu .divider { height: 1px; background: rgba(255,255,255,.1); margin: 8px 0; }
        
        .window { 
            position: absolute; min-width: 520px; max-width: 860px; width: 720px; min-height: 300px; background: linear-gradient(180deg, var(--panel), var(--panel-2)); border: 1px solid rgba(255,255,255,.08); border-radius: var(--radius); box-shadow: var(--shadow); overflow: clip; display: none;
            transition: transform 0.2s ease-out, opacity 0.2s ease-out, width 0.3s ease, height 0.3s ease, left 0.3s ease, top 0.3s ease;
        }
        .window.active { display: block; }
        .window.minimized {
            transform: scale(0.9) translateY(20px);
            opacity: 0;
            pointer-events: none;
        }

        .titlebar { display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: rgba(255,255,255,.04); border-bottom: 1px solid rgba(255,255,255,.06); cursor: move; }
        .titlebar .title { font-weight: 700; letter-spacing: .2px; }
        .titlebar .actions { margin-left: auto; display: flex; gap: 6px; }
        .icon { width: 18px; height: 18px; opacity: .95; }

        .content { padding: 16px; user-select: text; }

        .tabs { display: flex; gap: 8px; margin-bottom: 12px; }
        .tab { padding: 8px 12px; border-radius: 10px; background: rgba(255,255,255,.05); cursor: pointer; }
        .tab.active { outline: 2px solid rgba(91,156,255,.35); background: rgba(91,156,255,.12); }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        .grid { display: grid; gap: 12px; }
        .grid.cols-2 { grid-template-columns: repeat(2, minmax(0,1fr)); }

        .card { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); border-radius: 12px; padding: 14px; }
        .card h3 { margin: 0 0 8px; font-size: 1rem; }
        .muted { color: var(--muted); font-size: .92rem; }

        label { display: block; font-size: .92rem; margin-bottom: 6px; color: var(--muted); }
        input[type="text"], input[type="password"], input[type="number"], select { width: 100%; height: 36px; padding: 0 10px; border-radius: 10px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.08); color: var(--text); }
        textarea { width: 100%; min-height: 110px; padding: 10px; border-radius: 12px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.08); color: var(--text); resize: vertical; }
        .row { display: flex; gap: 8px; align-items: center; }
        .row > * { flex: 1; }

        .stat { font-weight: 800; font-size: 1.6rem; letter-spacing: .3px; }
        .pill { font-size: .8rem; padding: 4px 8px; border-radius: 999px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); }

        .toast { position: fixed; right: 12px; bottom: 60px; padding: 10px 14px; border-radius: 10px; background: #101418; border: 1px solid rgba(255,255,255,.1); display: none; }
        .toast.show { display: block; animation: fade .18s ease; }
        
        .cmd-content {
            background: #0a0c10;
            height: 320px;
            padding: 10px;
            font-family: Consolas, 'Courier New', monospace;
            font-size: .95rem;
            overflow-y: auto;
            border-radius: 0 0 var(--radius) var(--radius);
        }
        .cmd-output { white-space: pre-wrap; }
        .cmd-line { display: flex; }
        .cmd-prompt { flex-shrink: 0; }
        .cmd-input {
            flex-grow: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text);
            font-family: inherit;
            font-size: inherit;
            padding: 0 0 0 5px;
        }

        .file-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .file-item:hover {
            background: rgba(255,255,255,0.05);
        }
        .file-item.folder .icon {
            color: #ffc107;
        }
        .file-item.file .icon {
            color: var(--muted);
        }

        .resize-handle {
            position: absolute;
            z-index: 100;
            background: transparent;
        }
        .resize-handle.top, .resize-handle.bottom {
            left: 10px; right: 10px; height: 10px; cursor: ns-resize;
        }
        .resize-handle.left, .resize-handle.right {
            top: 10px; bottom: 10px; width: 10px; cursor: ew-resize;
        }
        .resize-handle.corner {
            width: 20px; height: 20px; z-index: 101;
        }
        .resize-handle.top { top: 0; }
        .resize-handle.bottom { bottom: 0; }
        .resize-handle.left { left: 0; }
        .resize-handle.right { right: 0; }
        .resize-handle.top-left { top: 0; left: 0; cursor: nwse-resize; }
        .resize-handle.top-right { top: 0; right: 0; cursor: nesw-resize; }
        .resize-handle.bottom-left { bottom: 0; left: 0; cursor: nesw-resize; }
        .resize-handle.bottom-right { bottom: 0; right: 0; cursor: nwse-resize; }

        /* Gaya untuk layar shutdown */
        #shutdown-screen {
            position: fixed;
            inset: 0;
            z-index: 10001;
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(20px);
            text-align: center;
            color: var(--text);
        }
        #shutdown-screen.active {
            display: flex;
        }
        .shutdown-content {
            padding: 20px;
            background: rgba(0,0,0,0.5);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            max-width: 400px;
            width: 90%;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .shutdown-content h2 {
            margin: 0;
            font-size: 1.5rem;
        }
        .shutdown-input-group {
            margin-top: 15px;
            width: 100%;
        }
        .shutdown-input-group input {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: var(--text);
            text-align: center;
        }
        .countdown-text {
            font-size: 4rem;
            font-weight: 700;
            margin-top: 20px;
            transition: color 0.3s ease, background-color 0.3s ease;
            padding: 10px 20px;
            border-radius: 10px;
        }
        .countdown-text.green { background: #22c55e; color: #fff; }
        .countdown-text.yellow { background: #f59e0b; color: #fff; }
        .countdown-text.red { background: #ef4444; color: #fff; }
        .final-message {
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: 2px;
            color: #fff;
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
        }

        /* Konteks Menu */
        .context-menu {
            position: absolute;
            background: var(--panel);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 8px;
            display: none;
            z-index: 1000;
        }
        .context-menu.active {
            display: block;
            animation: pop .1s ease;
        }
        .context-item {
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            transition: background .15s ease;
            white-space: nowrap;
        }
        .context-item:hover {
            background: rgba(255,255,255,.06);
        }

        .update-available {
            color: var(--ok);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        @keyframes pop { from { transform: translateY(8px) scale(.98); opacity: 0 } to { transform: none; opacity: 1 } }
        @keyframes fade { from { opacity: 0 } to { opacity: 1 } }

        @media (max-width: 760px){ .window { width: calc(100% - 24px); left: 12px !important; right: 12px !important; min-width: auto; } .grid.cols-2 { grid-template-columns: 1fr; } .desktop { padding: 12px; } }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-box">
            <h2>Selamat Datang di MIOS</h2>
            <form id="loginForm">
                <label for="username">Username</label>
                <input type="text" id="username" value="admin" required />
                <label for="password" style="margin-top: 8px;">Password</label>
                <input type="password" id="password" value="1234" required />
                <div id="login-error"></div>
                <button type="submit" class="btn">Login</button>
            </form>
        </div>
    </div>

    <div class="desktop" id="desktop"></div>

    <div class="start-menu" id="startMenu">
        <div class="user-info">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 00-4-4H9a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <div class="username-display" id="usernameDisplay"></div>
        </div>
        <div class="divider"></div>
        <div class="menu-item" id="openAdminFromMenu">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1l3 5 5 .5-3.6 3.4.9 5-5.3-2.7-5.3 2.7.9-5L4 6.5 9 6z"/></svg>
            <div><div class="title">Admin Panel</div><div class="desc">Kelola pengguna, log, dan pengaturan</div></div>
        </div>
        <div class="menu-item" id="openCmd">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17l6-6-6-6"/><path d="M12 19h8"/></svg>
            <div><div class="title">Command Prompt</div><div class="desc">Jalankan perintah sistem</div></div>
        </div>
        <div class="menu-item" id="openExplorer">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h18v13H3z"/><path d="M3 7L6 4h6l3 3"/></svg>
            <div><div class="title">File Explorer</div><div class="desc">Jelajahi file demo</div></div>
        </div>
        <div class="menu-item" id="openMines">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="M2 12h2"/><path d="M20 12h2"/></svg>
            <div><div class="title">Minesweeper</div><div class="desc">Mini game</div></div>
        </div>
        <div class="menu-item" id="openTetris">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="6" height="6"/><rect x="15" y="3" width="6" height="6"/><rect x="3" y="15" width="6" height="6"/><rect x="15" y="15" width="6" height="6"/></svg>
            <div><div class="title">Tetris</div><div class="desc">Mini game</div></div>
        </div>
        <div class="menu-item" id="aboutBtn">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8h.01"/><path d="M11 12h1v4h1"/></svg>
            <div><div class="title">Tentang MIOS</div><div class="desc">Demo UI Taskbar + Admin Panel</div></div>
        </div>

        <div class="divider"></div>
        <div class="menu-item" id="logoutBtn">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/></svg>
            <div><div class="title">Logout</div><div class="desc">Keluar dari sesi ini</div></div>
        </div>
        <div class="menu-item" id="shutdownBtn">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v10"/><path d="M18.36 17.5A9 9 0 1112 2.5a9 9 0 016.36 15z"/></svg>
            <div><div class="title">Shutdown Server</div><div class="desc">Matikan server secara permanen</div></div>
        </div>
    </div>

    <div class="context-menu" id="desktopContextMenu">
        <div class="context-item" id="createTxtFile">Create new Text file</div>
        <div class="context-item" id="deleteFile">Delete this file</div>
    </div>

    <div class="window" id="adminWindow" data-title="Admin Panel" style="left: 80px; top: 80px; width: 860px; min-width: 520px; max-width: 90vw;">
        <div class="titlebar" data-drag>
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v14H3z"/><path d="M7 21h10"/></svg>
            <div class="title">Admin Panel</div>
            <div class="pill" id="rolePill">role: admin</div>
            <div class="actions"><button class="btn small ghost" data-minimize title="Minimize">—</button><button class="btn small ghost" data-maximize title="Maximize">◻</button><button class="btn small ghost" data-close title="Close">✕</button></div>
        </div>
        <div class="content">
            <div class="tabs"><div class="tab active" data-tab="dash">Dashboard</div><div class="tab" data-tab="users">Users</div><div class="tab" data-tab="settings">Settings</div><div class="tab" data-tab="logs">Logs</div></div>

            <div class="tab-panel active" id="tab-dash">
                <div class="grid cols-2">
                    <div class="card"><h3>Status Server</h3><div class="muted">Uptime</div><div class="stat" id="uptime">00:00:00</div><div class="row"><span class="pill">CPU: <span id="cpu">7%</span></span><span class="pill">RAM: <span id="ram">35%</span></span><span class="pill">Users: <span id="usersOnline">2</span></span></div></div>
                    <div class="card"><h3>Aksi Cepat</h3><div class="row"><button class="btn" id="btnRestart">Restart Service</button><button class="btn" id="btnClearCache">Clear Cache</button></div><p class="muted" style="margin-top:8px">Aksi ini hanya simulasi untuk demo.</p></div>
                    <div class="card"><h3>Info</h3><p class="muted">Ini adalah demo Admin Panel berbasis HTML/CSS/JS.</p><div id="update-info-section" style="margin-top:10px;"></div></div>
                    <div class="card"><h3>Notifikasi</h3><div id="notifArea" class="muted">Belum ada notifikasi.</div></div>
                </div>
            </div>
            <div class="tab-panel" id="tab-users"><div class="grid cols-2"><div class="card"><h3>Tambah Pengguna</h3><label>Username</label><input type="text" id="newUser" placeholder="mis. alice" /><div class="row" style="margin-top:8px"><button class="btn" id="addUser">Tambah</button><button class="btn" id="clearUsers">Kosongkan</button></div></div><div class="card"><h3>Daftar Pengguna</h3><div id="userList" class="muted">(kosong)</div></div></div></div>
            <div class="tab-panel" id="tab-settings"><div class="grid cols-2"><div class="card"><h3>Umum</h3><label>Nama Situs</label><input type="text" id="siteName" placeholder="My Awesome App" /><label style="margin-top:8px">Tema</label><select id="themeSelect"><option value="dark" selected>Dark</option><option value="light">Light</option><option value="amoled">AMOLED</option></select><label style="margin-top:8px">Wallpaper</label><select id="wallpaperSelect"><option value="default" selected>Default</option><option value="nature">Nature</option><option value="abstract">Abstract</option></select><label style="margin-top:8px">Format Waktu</label><select id="timeFormatSelect"><option value="24h" selected>24 Jam</option><option value="12h">12 Jam</option></select></div><div class="card"><h3>Keamanan</h3><label>Password Admin</label><input type="password" id="adminPass" placeholder="••••••" /><div class="row" style="margin-top:8px"><button class="btn" id="saveSettings">Simpan</button><button class="btn" id="resetSettings">Reset</button></div></div></div></div>
            <div class="tab-panel" id="tab-logs"><div class="card"><h3>Activity Logs</h3><textarea id="logs" readonly>[boot] system ready\n</textarea></div></div>
        </div>
        <div class="resize-handle top"></div>
        <div class="resize-handle bottom"></div>
        <div class="resize-handle left"></div>
        <div class="resize-handle right"></div>
        <div class="resize-handle top-left"></div>
        <div class="resize-handle top-right"></div>
        <div class="resize-handle bottom-left"></div>
        <div class="resize-handle bottom-right"></div>
    </div>

    <div class="window" id="cmdWindow" data-title="Command Prompt" style="left: 150px; top: 150px; width: 640px; min-height: 200px; max-width: 90vw;">
        <div class="titlebar" data-drag>
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17l6-6-6-6"/><path d="M12 19h8"/></svg>
            <div class="title">Command Prompt</div>
            <div class="actions"><button class="btn small ghost" data-minimize title="Minimize">—</button><button class="btn small ghost" data-maximize title="Maximize">◻</button><button class="btn small ghost" data-close title="Close">✕</button></div>
        </div>
        <div class="content cmd-content" id="cmdContent">
            <div class="cmd-output" id="cmdOutput">MIOS [Version 1.0.0]\n(c) 2025 MIOS Corp. All rights reserved.\n\n</div>
            <div class="cmd-line">
                <span class="cmd-prompt" id="cmdPrompt">C:\Users\Admin></span>
                <input type="text" class="cmd-input" id="cmdInput" autofocus autocomplete="off" />
            </div>
        </div>
        <div class="resize-handle top"></div>
        <div class="resize-handle bottom"></div>
        <div class="resize-handle left"></div>
        <div class="resize-handle right"></div>
        <div class="resize-handle top-left"></div>
        <div class="resize-handle top-right"></div>
        <div class="resize-handle bottom-left"></div>
        <div class="resize-handle bottom-right"></div>
    </div>

    <div class="window" id="explorerWindow" data-title="File Explorer" style="left: 120px; top: 120px; width: 760px; min-width: 420px; max-width: 90vw;">
        <div class="titlebar" data-drag><div class="title">File Explorer</div><div class="actions"><button class="btn small ghost" data-minimize title="Minimize">—</button><button class="btn small ghost" data-maximize title="Maximize">◻</button><button class="btn small ghost" data-close title="Close">✕</button></div></div>
        <div class="content" style="display:flex; gap:12px;"><div style="width:260px;"><div class="card" style="height:100%;"><h3>Folders</h3><div id="folderList" class="muted"></div></div></div><div style="flex:1;"><div class="card" style="height:100%; display:flex; flex-direction:column;"><h3>File Preview</h3><div id="filePreview" style="flex:1; overflow:auto; padding:8px; background:rgba(0,0,0,0.03); border-radius:8px;">Pilih file untuk melihat isinya.</div></div></div></div>
        <div class="resize-handle top"></div>
        <div class="resize-handle bottom"></div>
        <div class="resize-handle left"></div>
        <div class="resize-handle right"></div>
        <div class="resize-handle top-left"></div>
        <div class="resize-handle top-right"></div>
        <div class="resize-handle bottom-left"></div>
        <div class="resize-handle bottom-right"></div>
    </div>
    
    <div class="window" id="minesWindow" data-title="Minesweeper" style="left: 200px; top: 140px; width: 420px; min-width: 320px; max-width: 90vw;">
        <div class="titlebar" data-drag><div class="title">Minesweeper</div><div class="actions"><button class="btn small ghost" data-minimize title="Minimize">—</button><button class="btn small ghost" data-maximize title="Maximize">◻</button><button class="btn small ghost" data-close title="Close">✕</button></div></div>
        <div class="content"><div class="row" style="margin-bottom:8px"><button class="btn" id="restartMines">Restart</button><div class="muted" id="minesStatus">Ready</div></div><div id="minesBoard" style="display:grid; grid-template-columns: repeat(9, 1fr); gap:4px; max-width:360px;"></div></div>
        <div class="resize-handle top"></div>
        <div class="resize-handle bottom"></div>
        <div class="resize-handle left"></div>
        <div class="resize-handle right"></div>
        <div class="resize-handle top-left"></div>
        <div class="resize-handle top-right"></div>
        <div class="resize-handle bottom-left"></div>
        <div class="resize-handle bottom-right"></div>
    </div>

    <div class="window" id="tetrisWindow" data-title="Tetris" style="left: 260px; top: 160px; width: 360px; min-width: 280px; max-width: 90vw;">
        <div class="titlebar" data-drag><div class="title">Tetris</div><div class="actions"><button class="btn small ghost" data-minimize title="Minimize">—</button><button class="btn small ghost" data-maximize title="Maximize">◻</button><button class="btn small ghost" data-close title="Close">✕</button></div></div>
        <div class="content" style="display:flex; flex-direction:column; align-items:center; gap:8px;"><canvas id="tetrisCanvas" width="200" height="400" style="background: rgba(255,255,255,.02); border-radius:8px;"></canvas><div class="row" style="width:100%"><button class="btn" id="restartTetris">Restart</button><div class="muted" id="tetrisStatus">Ready</div></div></div>
        <div class="resize-handle top"></div>
        <div class="resize-handle bottom"></div>
        <div class="resize-handle left"></div>
        <div class="resize-handle right"></div>
        <div class="resize-handle top-left"></div>
        <div class="resize-handle top-right"></div>
        <div class="resize-handle bottom-left"></div>
        <div class="resize-handle bottom-right"></div>
    </div>

    <div class="taskbar"><div class="tb-left"><button class="btn start" id="startBtn">◎ Start</button><button class="btn" id="openAdminBtn" title="Buka Admin Panel"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1l3 5 5 .5-3.6 3.4.9 5-5.3-2.7-5.3 2.7.9-5L4 6.5 9 6z"/></svg>Admin Panel</button></div><div class="tb-center apps-area" id="tasks"></div><div class="tb-right"><div class="btn ghost clock" id="clock">--:--</div></div></div>

    <div class="toast" id="toast"></div>

    <div id="shutdown-screen">
        <div class="shutdown-content">
            <h2 id="shutdown-title">Shutdown MIOS</h2>
            <p id="shutdown-desc">Masukkan kode otentikasi dari konsol utama untuk melanjutkan.</p>
            <div class="shutdown-input-group">
                <input type="password" id="shutdownCodeInput" placeholder="Masukkan kode..." autocomplete="off">
            </div>
            <div id="shutdownCountdown" class="countdown-text"></div>
        </div>
    </div>

    <script>
        const $ = (sel, root = document) => root.querySelector(sel);
        const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
        const toast = (msg) => { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'), 1800); };
        
        const CURRENT_VERSION = '1.0.0';
        let loggedInUser = null;

        const wallpapers = {
            'default': 'radial-gradient(1200px 700px at 70% -10%, #223 0%, #111 55%, #0a0c10 100%)',
            'nature': 'url("https://images.unsplash.com/photo-1547844111-d1c9e8d35f5c?q=80&w=2670&auto=format&fit=crop")',
            'abstract': 'url("https://images.unsplash.com/photo-1622542792686-2a62a9c37e6f?q=80&w=2574&auto=format&fit=crop")'
        };

        const fileSystem = {
            'C:': {
                'Users': {
                    'Admin': {
                        'Documents': {
                            'catatan.txt': { type: 'text', content: 'Ini adalah catatan penting.\nJaga kerahasiaan data.' },
                            'README.md': { type: 'text', content: '# Proyek MIOS\n\nSelamat datang di File Explorer!' },
                        },
                        'Images': {
                            'nature.jpg': { type: 'image', content: 'https://images.unsplash.com/photo-1547844111-d1c9e8d35f5c?q=80&w=2670&auto=format&fit=crop' },
                            'abstract.png': { type: 'image', content: 'https://images.unsplash.com/photo-1622542792686-2a62a9c37e6f?q=80&w=2574&auto=format&fit=crop' },
                        }
                    }
                },
                'Server': {
                    'admin': {
                        'logs.txt': { type: 'text', content: 'Ini adalah log server.' }
                    },
                    'desktop': {}
                }
            }
        };

        let currentPath = fileSystem['C:'];
        let selectedFile = null;

        const loginScreen = $('#login-screen');
        const loginForm = $('#loginForm');
        const loginError = $('#login-error');
        const desktop = $('#desktop');
        const taskbar = $('.taskbar');
        
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = $('#username').value;
            const password = $('#password').value;

            if (username === 'admin' && password === '1234') {
                loggedInUser = username;
                $('#usernameDisplay').textContent = username;
                loginScreen.classList.add('hidden');
                desktop.classList.add('visible');
                taskbar.classList.add('visible');
                $('#rolePill').textContent = `role: ${username}`;
                $('#cmdPrompt').textContent = `C:\\Users\\${username}>`;
                openWindow($('#adminWindow')); 
                log(`[auth] User '${username}' logged in successfully.`);
                checkForUpdates();
            } else {
                loginError.textContent = 'Username atau password salah.';
                setTimeout(() => loginError.textContent = '', 2000);
            }
        });
        
        $('#logoutBtn').addEventListener('click', () => {
            logout();
        });

        function logout() {
            loggedInUser = null;
            $$('.window.active, .window.minimized').forEach(win => closeWindow(win));
            desktop.classList.remove('visible');
            taskbar.classList.remove('visible');
            loginScreen.classList.remove('hidden');
            $('#tasks').innerHTML = '';
            $('#username').value = 'admin';
            $('#password').value = '1234';
            log('[auth] User logged out.');
        }

        const clockEl = $('#clock');
        function updateClock() {
            const d = new Date();
            const format = localStorage.getItem('timeFormat') || '24h';
            let timeString;
            if (format === '12h') {
                timeString = d.toLocaleTimeString('en-US', { hour12: true });
            } else {
                timeString = d.toLocaleTimeString('en-GB', { hour12: false });
            }
            clockEl.textContent = timeString;
        }
        setInterval(updateClock, 1000); updateClock();

        const startBtn = $('#startBtn');
        const startMenu = $('#startMenu');
        startBtn.addEventListener('click', ()=>{ startMenu.classList.toggle('active'); });
        document.addEventListener('click', (e)=>{ if(!startMenu.contains(e.target) && e.target!==startBtn){ startMenu.classList.remove('active'); } });

        const desktopContextMenu = $('#desktopContextMenu');
        desktop.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            desktopContextMenu.style.left = e.clientX + 'px';
            desktopContextMenu.style.top = e.clientY + 'px';
            desktopContextMenu.classList.add('active');
        });

        document.addEventListener('click', () => {
            desktopContextMenu.classList.remove('active');
        });

        $('#createTxtFile').addEventListener('click', () => {
            const userDocs = fileSystem['C:']['Users'][loggedInUser]['Documents'];
            let newFileName = 'New Text File.txt';
            let i = 1;
            while (userDocs[newFileName]) {
                newFileName = `New Text File (${i}).txt`;
                i++;
            }
            userDocs[newFileName] = { type: 'text', content: 'Konten file baru.' };
            toast(`File '${newFileName}' dibuat.`);
            log(`[file-system] new file created: ${newFileName}`);
            renderExplorer();
        });

        $('#deleteFile').addEventListener('click', () => {
            if (selectedFile) {
                delete currentPath[selectedFile];
                toast(`File '${selectedFile}' dihapus.`);
                log(`[file-system] file deleted: ${selectedFile}`);
                selectedFile = null;
                renderExplorer();
            } else {
                toast('Pilih file dulu!');
            }
        });

        const tasks = $('#tasks');

        function createTaskButton(winId, title){ const btn = document.createElement('button'); btn.className = 'btn task'; btn.dataset.for = winId; btn.textContent = title; const targetWin = document.getElementById(winId); btn.addEventListener('click', (e) => { e.stopPropagation(); focusWindow(targetWin); }); return btn; }

        function openWindow(win){ 
            if(!win) return;
            win.classList.remove('minimized');
            win.classList.add('active'); 
            if(!win.style.left || win.style.left.includes('px') === false){
                win.style.left = Math.max(20, innerWidth/2 - win.offsetWidth/2) + 'px'; 
            }
            if(!win.style.top || win.style.top.includes('px') === false){
                win.style.top = Math.max(20, innerHeight/2 - win.offsetHeight/2 - 40) + 'px'; 
            }
            if(!tasks.querySelector('[data-for="'+win.id+'"]')){
                const title = win.dataset.title || win.querySelector('.title')?.textContent || win.id;
                const btn = createTaskButton(win.id, title);
                tasks.appendChild(btn);
            }
            bringToFront(win);
        }

        function closeWindow(win){ 
            if(!win) return; 
            win.classList.remove('active');
            win.classList.add('minimized');
            const taskBtn = tasks.querySelector(`[data-for="${win.id}"]`);
            if(taskBtn) taskBtn.remove();
        }

        function minimizeWindow(win){ 
            if(!win) return; 
            win.classList.remove('active'); 
            win.classList.add('minimized');
            updateTaskButtonState(win); 
        }

        function maximizeWindow(win){ 
            if(!win) return; 
            if(win.dataset.max === '1'){ 
                win.style.left = win.dataset.prevLeft || '80px'; 
                win.style.top = win.dataset.prevTop || '80px'; 
                win.style.width = win.dataset.prevWidth || '720px'; 
                win.style.height = win.dataset.prevHeight || 'auto'; 
                win.dataset.max = '0'; 
            } else { 
                win.dataset.prevLeft = win.style.left; 
                win.dataset.prevTop = win.style.top; 
                win.dataset.prevWidth = win.style.width; 
                win.dataset.prevHeight = win.style.height; 
                win.style.left = '10px'; 
                win.style.top = '10px'; 
                win.style.width = (innerWidth - 20) + 'px'; 
                win.style.height = (innerHeight - 70) + 'px'; 
                win.dataset.max = '1'; 
            } 
            bringToFront(win); 
            updateTaskButtonState(win); 
        }

        function bringToFront(win){ 
            const zList = $$('.window.active, .window.minimized').map(w => { 
                const z = parseInt(getComputedStyle(w).zIndex, 10); 
                return isNaN(z) ? 10 : z; 
            }); 
            const maxZ = zList.length ? Math.max(...zList) : 10; 
            win.style.zIndex = maxZ + 1; 
            
            $$('.task.active').forEach(btn => btn.classList.remove('active'));
            const taskBtn = tasks.querySelector(`[data-for="${win.id}"]`);
            if (taskBtn) taskBtn.classList.add('active');
        }

        function focusWindow(win){ 
            if(!win) return; 
            if(win.classList.contains('active')){
                minimizeWindow(win); 
            } else { 
                openWindow(win); 
            } 
        }

        function updateTaskButtonState(win){ 
            const btn = tasks.querySelector('[data-for="'+win.id+'"]'); 
            if(!btn) return; 
            if(win.classList.contains('active')) btn.classList.add('active'); 
            else btn.classList.remove('active'); 
        }

        function attachResizeListeners(win) {
            const handles = $$('.resize-handle', win);
            handles.forEach(handle => {
                let isResizing = false;
                let startX, startY, startWidth, startHeight, startLeft, startTop;

                handle.addEventListener('mousedown', (e) => {
                    e.stopPropagation();
                    isResizing = true;
                    startX = e.clientX;
                    startY = e.clientY;
                    startWidth = win.offsetWidth;
                    startHeight = win.offsetHeight;
                    startLeft = win.offsetLeft;
                    startTop = win.offsetTop;
                    document.body.style.userSelect = 'none';
                });

                document.addEventListener('mousemove', (e) => {
                    if (!isResizing) return;
                    let newWidth = startWidth;
                    let newHeight = startHeight;
                    let newLeft = startLeft;
                    let newTop = startTop;

                    if (handle.classList.contains('right') || handle.classList.contains('top-right') || handle.classList.contains('bottom-right')) {
                        newWidth = startWidth + (e.clientX - startX);
                    }
                    if (handle.classList.contains('bottom') || handle.classList.contains('bottom-left') || handle.classList.contains('bottom-right')) {
                        newHeight = startHeight + (e.clientY - startY);
                    }
                    if (handle.classList.contains('left') || handle.classList.contains('top-left') || handle.classList.contains('bottom-left')) {
                        newWidth = startWidth - (e.clientX - startX);
                        newLeft = startLeft + (e.clientX - startX);
                    }
                    if (handle.classList.contains('top') || handle.classList.contains('top-left') || handle.classList.contains('top-right')) {
                        newHeight = startHeight - (e.clientY - startY);
                        newTop = startTop + (e.clientY - startY);
                    }
                    
                    if (newWidth > win.dataset.minWidth || newWidth > 320) win.style.width = newWidth + 'px';
                    if (newHeight > win.dataset.minHeight || newHeight > 200) win.style.height = newHeight + 'px';
                    if (handle.classList.contains('left') || handle.classList.contains('top-left') || handle.classList.contains('bottom-left')) win.style.left = newLeft + 'px';
                    if (handle.classList.contains('top') || handle.classList.contains('top-left') || handle.classList.contains('top-right')) win.style.top = newTop + 'px';
                });

                document.addEventListener('mouseup', () => {
                    isResizing = false;
                    document.body.style.userSelect = '';
                });
            });
        }
        
        function attachWindowEvents(win) {
            const bar = win.querySelector('[data-drag]');
            if (bar) {
                let sx, sy, sl, st, dragging = false;
                bar.addEventListener('mousedown', (e) => {
                    if (e.target.closest('.actions')) return;
                    dragging = true;
                    bringToFront(win);
                    sx = e.clientX;
                    sy = e.clientY;
                    sl = parseInt(win.style.left || '80', 10);
                    st = parseInt(win.style.top || '80', 10);
                    document.body.style.userSelect = 'none';
                });
                document.addEventListener('mousemove', (e) => {
                    if (!dragging) return;
                    const nl = sl + (e.clientX - sx);
                    const nt = st + (e.clientY - sy);
                    win.style.left = Math.min(innerWidth-80, Math.max(-win.offsetWidth+80, nl)) + 'px';
                    win.style.top = Math.min(innerHeight-120, Math.max(0, nt)) + 'px';
                });
                document.addEventListener('mouseup', () => {
                    dragging = false;
                    document.body.style.userSelect = '';
                });
            }

            const closeBtn = win.querySelector('[data-close]');
            if (closeBtn) closeBtn.addEventListener('click', () => { closeWindow(win); toast(win.dataset.title || 'Window closed'); });
            const minBtn = win.querySelector('[data-minimize]');
            if (minBtn) minBtn.addEventListener('click', () => { minimizeWindow(win); });
            const maxBtn = win.querySelector('[data-maximize]');
            if (maxBtn) maxBtn.addEventListener('click', () => { maximizeWindow(win); });
            win.addEventListener('mousedown', () => bringToFront(win));
            attachResizeListeners(win);
        }
        
        $$('.window').forEach(attachWindowEvents);

        $('#openAdminBtn').addEventListener('click', ()=> openWindow($('#adminWindow')));
        $('#openAdminFromMenu').addEventListener('click', ()=> { openWindow($('#adminWindow')); startMenu.classList.remove('active'); });
        $('#openCmd').addEventListener('click', ()=> { openWindow($('#cmdWindow')); startMenu.classList.remove('active'); $('#cmdInput').focus(); });
        $('#openExplorer').addEventListener('click', ()=> { openWindow($('#explorerWindow')); startMenu.classList.remove('active'); renderExplorer(); });
        $('#openMines').addEventListener('click', ()=> { openWindow($('#minesWindow')); startMenu.classList.remove('active'); });
        $('#openTetris').addEventListener('click', ()=> { openWindow($('#tetrisWindow')); startMenu.classList.remove('active'); });

        $$('.tab', adminWindow).forEach(tab => { tab.addEventListener('click', ()=>{ $$('.tab', adminWindow).forEach(t=>t.classList.remove('active')); tab.classList.add('active'); $$('.tab-panel', adminWindow).forEach(p=>p.classList.remove('active')); $('#tab-'+tab.dataset.tab).classList.add('active'); }); });

        const startTime = Date.now();
        function fmtUptime(ms){ const s = Math.floor(ms/1000); const h = Math.floor(s/3600); const m = Math.floor((s%3600)/60); const ss = s%60; const pad = (n)=> String(n).padStart(2,'0'); return `${pad(h)}:${pad(m)}:${pad(ss)}`; }
        setInterval(()=>{ $('#uptime').textContent = fmtUptime(Date.now()-startTime); const cpu = (5 + Math.floor(Math.random()*20)); const ram = (30 + Math.floor(Math.random()*25)); $('#cpu').textContent = cpu + '%'; $('#ram').textContent = ram + '%'; }, 1000);

        function log(line){ const ta = $('#logs'); if(!ta) return; ta.value += line + "\n"; ta.scrollTop = ta.scrollHeight; }

        $('#btnRestart').addEventListener('click', ()=>{ log('[action] restart service'); toast('Service di-restart (simulasi)'); });
        $('#btnClearCache').addEventListener('click', ()=>{ log('[action] clear cache'); toast('Cache dibersihkan'); });

        const userStore = [];
        function renderUsers(){ const el = $('#userList'); if(!el) return; if(userStore.length===0){ el.textContent = '(kosong)'; return; } el.innerHTML = ''; userStore.forEach((u,i)=>{ const row = document.createElement('div'); row.className = 'row'; row.innerHTML = `<div>@${u}</div><button class="btn small" data-del="${i}">Hapus</button>`; el.appendChild(row); }); el.querySelectorAll('[data-del]').forEach(btn=>{ btn.addEventListener('click', ()=>{ const idx = +btn.dataset.del; userStore.splice(idx,1); renderUsers(); log(`[users] delete ${userStore[idx] || 'user'}`); }); }); }
        $('#addUser').addEventListener('click', ()=>{ const v = $('#newUser').value.trim(); if(!v) return; if(userStore.includes(v)) return toast('User sudah ada'); userStore.push(v); $('#newUser').value=''; renderUsers(); log(`[users] add ${v}`); });
        $('#clearUsers').addEventListener('click', ()=>{ userStore.length = 0; renderUsers(); log('[users] cleared'); });

        function applyTheme(theme){
            if (theme === 'light') {
                document.body.classList.add('light-theme');
                document.body.style.background = `var(--bg)`;
            } else if (theme === 'amoled') {
                document.body.classList.remove('light-theme');
                document.body.style.background = '#000';
            } else { 
                document.body.classList.remove('light-theme');
                document.body.style.background = `radial-gradient(1200px 700px at 70% -10%, #223 0%, #111 55%, #0a0c10 100%), var(--bg)`;
            }
        }
        function applyWallpaper(wallpaper) {
            desktop.style.backgroundImage = wallpapers[wallpaper] || '';
        }

        $('#saveSettings').addEventListener('click', ()=>{ 
            const theme = $('#themeSelect').value;
            const wallpaper = $('#wallpaperSelect').value;
            const timeFormat = $('#timeFormatSelect').value;

            applyTheme(theme);
            applyWallpaper(wallpaper);
            updateClock();

            localStorage.setItem('theme', theme);
            localStorage.setItem('wallpaper', wallpaper);
            localStorage.setItem('timeFormat', timeFormat);
            
            toast('Pengaturan disimpan'); 
            log(`[settings] saved {theme:${theme}, wallpaper:${wallpaper}, timeFormat:${timeFormat}}`); 
        });

        $('#resetSettings').addEventListener('click', ()=>{ 
            $('#siteName').value = 'My Awesome App'; 
            $('#adminPass').value = ''; 
            $('#themeSelect').value = 'dark';
            $('#wallpaperSelect').value = 'default';
            $('#timeFormatSelect').value = '24h';
            applyTheme('dark');
            applyWallpaper('default');
            updateClock();
            localStorage.clear();
            toast('Pengaturan direset'); 
            log('[settings] reset'); 
        });

        (function loadSettings() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            const savedWallpaper = localStorage.getItem('wallpaper') || 'default';
            const savedTimeFormat = localStorage.getItem('timeFormat') || '24h';

            $('#themeSelect').value = savedTheme;
            $('#wallpaperSelect').value = savedWallpaper;
            $('#timeFormatSelect').value = savedTimeFormat;
            
            applyTheme(savedTheme);
            applyWallpaper(savedWallpaper);
            updateClock();
        })();

        $('#aboutBtn').addEventListener('click', ()=>{ startMenu.classList.remove('active'); toast('Taskbar + Admin Panel demo'); });
        
        const cmdInput = $('#cmdInput');
        const cmdOutput = $('#cmdOutput');
        const cmdContent = $('#cmdContent');
        const cmdPrompt = $('#cmdPrompt');

        cmdContent.addEventListener('click', () => cmdInput.focus());
        cmdInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const command = cmdInput.value.trim();
                cmdInput.value = '';
                
                if (command) {
                    appendCmdOutput(`${cmdPrompt.textContent}${command}\n`);
                    executeCommand(command);
                }
            }
        });

        function appendCmdOutput(text) {
            cmdOutput.textContent += text;
            cmdContent.scrollTop = cmdContent.scrollHeight;
        }

        function executeCommand(command) {
            const parts = command.split(' ');
            const cmd = parts[0].toLowerCase();
            const args = parts.slice(1);
            let output = '';

            switch (cmd) {
                case 'help':
                    output = 'Perintah yang tersedia:\n' +
                             '  help        - Menampilkan bantuan ini\n' +
                             '  echo [teks] - Menampilkan teks\n' +
                             '  date        - Menampilkan tanggal hari ini\n' +
                             '  time        - Menampilkan waktu saat ini\n' +
                             '  cls         - Membersihkan layar\n' +
                             '  user        - Menampilkan user yang login\n' +
                             '  exit        - Menutup Command Prompt\n';
                    break;
                case 'echo':
                    output = args.join(' ') + '\n';
                    break;
                case 'date':
                    output = new Date().toLocaleDateString('id-ID', { dateStyle: 'full' }) + '\n';
                    break;
                case 'time':
                    output = new Date().toLocaleTimeString('id-ID') + '\n';
                    break;
                case 'cls':
                    cmdOutput.textContent = '';
                    return;
                case 'user':
                    output = `User saat ini: ${loggedInUser}\n`;
                    break;
                case 'exit':
                    closeWindow($('#cmdWindow'));
                    return;
                default:
                    output = `'${cmd}' tidak dikenali sebagai perintah.\nKetik 'help' untuk daftar perintah.\n`;
            }
            appendCmdOutput(output);
        }

        function renderExplorer() {
            const folderList = $('#folderList');
            const filePreview = $('#filePreview');
            folderList.innerHTML = '';
            filePreview.innerHTML = 'Pilih file untuk melihat isinya.';
            selectedFile = null;

            // Navigasi ke root direktori
            const rootEl = document.createElement('div');
            rootEl.className = 'file-item folder';
            rootEl.innerHTML = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h4l2 3h10a2 2 0 012 2z"/></svg><span>C:</span>`;
            rootEl.addEventListener('click', () => {
                currentPath = fileSystem['C:'];
                renderExplorer();
            });
            folderList.appendChild(rootEl);

            const path = [];
            let tempPath = fileSystem['C:'];
            for (const key of Object.keys(currentPath)) {
                if (tempPath === currentPath) {
                    break;
                }
                path.push(key);
                tempPath = tempPath[key];
            }

            for (const item in currentPath) {
                const itemData = currentPath[item];
                const isFolder = typeof itemData === 'object' && !itemData.type;
                const type = isFolder ? 'folder' : 'file';
                const icon = isFolder ?
                    `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h4l2 3h10a2 2 0 012 2z"/></svg>` :
                    `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>`;

                const fileEl = document.createElement('div');
                fileEl.className = `file-item ${type}`;
                fileEl.innerHTML = `${icon}<span>${item}</span>`;
                fileEl.addEventListener('click', () => {
                    selectedFile = isFolder ? null : item;
                    if (isFolder) {
                        currentPath = itemData;
                        renderExplorer();
                    } else {
                        openFile(itemData);
                    }
                });
                folderList.appendChild(fileEl);
            }
        }

        function openFile(fileData) {
            const previewEl = $('#filePreview');
            previewEl.innerHTML = '';
            
            if (fileData.type === 'text') {
                const pre = document.createElement('pre');
                pre.textContent = fileData.content;
                previewEl.appendChild(pre);
            } else if (fileData.type === 'image') {
                const img = document.createElement('img');
                img.src = fileData.content;
                img.style.maxWidth = '100%';
                img.style.display = 'block';
                previewEl.appendChild(img);
            } else {
                previewEl.textContent = 'Jenis file tidak didukung.';
            }
        }

        // === LOGIKA SHUTDOWN ===
        const shutdownBtn = $('#shutdownBtn');
        const shutdownScreen = $('#shutdown-screen');
        const shutdownCodeInput = $('#shutdownCodeInput');
        const shutdownCountdown = $('#shutdownCountdown');
        let shutdownCode = null;

        shutdownBtn.addEventListener('click', () => {
            startMenu.classList.remove('active');
            shutdownScreen.classList.add('active');
            
            // Tutup semua jendela
            $$('.window.active').forEach(win => closeWindow(win));
            
            // Buat kode acak untuk shutdown
            shutdownCode = Math.floor(1000 + Math.random() * 9000).toString();
            log(`[system] SHUTDOWN_REQUEST: Masukkan kode ${shutdownCode} untuk otentikasi.`);
            
            shutdownCodeInput.value = '';
            shutdownCodeInput.focus();
        });

        shutdownCodeInput.addEventListener('input', () => {
            if (shutdownCodeInput.value === shutdownCode) {
                shutdownCodeInput.disabled = true;
                startCountdown(5);
            }
        });

        function startCountdown(count) {
            const words = ['Tunggu', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima'];
            const countdownInterval = setInterval(() => {
                let displayValue = count;
                let colorClass = '';

                if (count <= 3) {
                    displayValue = words[count];
                    if (count === 3) colorClass = 'green';
                    else if (count === 2) colorClass = 'yellow';
                    else if (count === 1) colorClass = 'red';
                }

                shutdownCountdown.textContent = displayValue;
                shutdownCountdown.className = 'countdown-text ' + colorClass;

                if (count <= 0) {
                    clearInterval(countdownInterval);
                    shutdownCountdown.textContent = 'Goodbye Forever';
                    shutdownCountdown.classList.add('final-message');
                    setTimeout(() => {
                        shutdownScreen.style.display = 'none';
                        document.body.innerHTML = '<h1 style="color:white; text-align:center; padding-top: 100px;">System Offline</h1>';
                    }, 2000);
                }
                count--;
            }, 1000);
        }

        // === LOGIKA SIMULASI UPDATE ===
        function checkForUpdates() {
            const updateInfoSection = $('#update-info-section');
            const latestVersion = '1.0.1'; // Versi terbaru yang disimulasikan
            
            // Logika untuk membandingkan versi
            const isUpdateAvailable = latestVersion > CURRENT_VERSION;

            updateInfoSection.innerHTML = ''; // Bersihkan konten sebelumnya

            if (isUpdateAvailable) {
                const updateMessage = document.createElement('div');
                updateMessage.className = 'update-available';
                updateMessage.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg><span>Pembaruan v${latestVersion} tersedia!</span>`;
                
                const updateButton = document.createElement('a');
                updateButton.href = 'https://github.com/Files2012/MISE/blob/main/OS/MIOS.html'; // Ganti dengan URL repo Anda
                updateButton.target = '_blank';
                updateButton.className = 'btn small';
                updateButton.textContent = 'Unduh';
                
                updateInfoSection.appendChild(updateMessage);
                updateInfoSection.appendChild(updateButton);
                
                log('[system] Update available: ' + latestVersion);
            } else {
                updateInfoSection.innerHTML = '<span class="muted">Anda menggunakan versi terbaru.</span>';
                log('[system] No updates found.');
            }
        }

    </script>
</body>
</html>
"""

def get_local_ip():
    """Mendapatkan alamat IP lokal"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    """Mendapatkan alamat IP publik"""
    try:
        response = requests.get('https://httpbin.org/ip', timeout=5)
        return response.json()['origin']
    except:
        return "Tidak dapat mendapatkan IP publik"

def format_file_size(size):
    """Format ukuran file menjadi readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def get_file_info(directory):
    """Mendapatkan informasi file dan direktori"""
    files = []
    dir_count = 0
    total_size = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        is_dir = os.path.isdir(filepath)
        
        if is_dir:
            dir_count += 1
            size = "Directory"
            modified = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
        else:
            file_size = os.path.getsize(filepath)
            total_size += file_size
            size = format_file_size(file_size)
            modified = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
        
        files.append({
            'name': filename,
            'is_dir': is_dir,
            'size': size,
            'modified': modified
        })
    
    return files, dir_count, total_size

def start_server(directory, selected_port=5000):
    """Menjalankan server Flask"""
    global app, current_directory, port, is_running, start_time
    current_directory = directory
    port = selected_port
    is_running = True
    start_time = datetime.now()
    
    @app.route('/')
    def index():
        """Halaman utama"""
        files = os.listdir(directory)
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        
        return f"""
        <!doctype html>
        <html lang="id">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>X(</title>
          <style>
            body {{
              margin: 0;
              font-family: Arial, sans-serif;
              background: #fff;
              color: #3c4043;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              text-align: center;
            }}
            .container {{
              max-width: 400px;
              padding: 24px;
            }}
            .emoji {{
              font-size: 64px;
              margin-bottom: 16px;
            }}
            h1 {{
              font-size: 1.8rem;
              font-weight: normal;
              margin: 0 0 8px;
            }}
            p {{
              margin: 4px 0 16px;
              color: #5f6368;
            }}
            .button {{
              display: inline-block;
              margin-top: 20px;
              background: #1a73e8;
              color: white;
              padding: 8px 16px;
              border-radius: 4px;
              font-size: 0.9rem;
              text-decoration: none;
            }}
            .button:hover {{
              background: #1765cc;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="emoji">X(</div>
            <h1>Aw, Snap!</h1>
            <p>Something went wrong with the server. We'll be back soon..</p>
            <p><b>Local IP:</b> {local_ip} <br> <b>Public IP:</b> {public_ip}</p>
            <a href="/" class="button">Reload</a>
            <a href="https://youtube.com" class="button">Youtube</a>
          </div>
        </body>
        </html>
        """
    
    @app.route('/files/<path:filename>')
    def serve_file(filename):
        """Melayani file dari direktori"""
        return send_from_directory(directory, filename)
    
    @app.route('/admin')
    def admin():
        """Panel admin"""
        files, dir_count, total_size = get_file_info(directory)
        total_size_mb = total_size / (1024 * 1024)
        
        # Hitung waktu aktif
        uptime = datetime.now() - start_time
        uptime_str = str(uptime).split('.')[0]
        
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        
        return render_template_string(ADMIN_PANEL,
                                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    directory=directory,
                                    file_count=len(files),
                                    dir_count=dir_count,
                                    total_size=f"{total_size_mb:.2f}",
                                    uptime=uptime_str,
                                    local_ip=local_ip,
                                    public_ip=public_ip,
                                    port=port,
                                    files=files,
                                    start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    @app.route('/admin/settings', methods=['POST'])
    def save_settings():
        """Menyimpan pengaturan server"""
        # Di implementasi nyata, simpan pengaturan ke file konfigurasi
        return redirect('/admin')
    
    @app.route('/shutdown')
    def shutdown():
        """Menghentikan server"""
        global is_running
        is_running = False
        return "Server is shutting down..."
    
    # Jalankan server dengan waitress untuk akses publik
    print(f"Server berjalan di http://{get_local_ip()}:{port}")
    print(f"IP Publik: http://{get_public_ip()}:{port}")
    print(f"Melayani direktori: {directory}")
    print("Tekan Ctrl+C untuk menghentikan server")
    print("\nAkses admin panel di: http://localhost:{port}/admin")
    
    # Buka browser otomatis
    webbrowser.open(f"http://localhost:{port}/admin")
    
    # Jalankan server dengan waitress (production server)
    serve(app, host=host, port=port)

def main():
    """Fungsi utama program"""
    print("=" * 60)
    print("MISE - Mini Server dengan Admin Panel Sederhana")
    print("=" * 60)
    print("Server ini dapat diakses dari perangkat lain dalam jaringan")
    print("yang sama atau melalui internet (jika terkoneksi langsung).")
    print("")
    
    while True:
        print("\nPilihan:")
        print("1. Buat Server")
        print("2. Keluar")
        
        choice = input("Masukkan pilihan (1/2): ").strip()
        
        if choice == "1":
            # Buat server baru
            directory = input("Masukkan path direktori yang akan dilayani: ").strip()
            
            if not os.path.exists(directory):
                print("Direktori tidak ditemukan!")
                continue
                
            port_input = input("Masukkan port (default 5000): ").strip()
            port = int(port_input) if port_input.isdigit() else 5000
            
            # Jalankan server di thread terpisah
            global server_thread
            server_thread = threading.Thread(target=start_server, args=(directory, port))
            server_thread.daemon = True
            server_thread.start()
            
            try:
                # Biarkan server berjalan
                while is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nServer dihentikan.")
                break
                
        elif choice == "2":
            print("Terima kasih telah menggunakan MISE!")
            break
            
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()

# ====== END OF FILE: MISE.py ======

# ====== START OF FILE: misetest.py ======
import os
import sys
import webbrowser
import threading
import time
import socket
import requests
import random
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, send_from_directory, request, redirect, jsonify
from waitress import serve

# ------------------------------
# Konfigurasi dasar
# ------------------------------
app = Flask(__name__, static_folder=None)
HOST = "0.0.0.0"
PORT = 5000

# State global
current_directory = os.getcwd()
is_running = False
start_time = datetime.now()
_shutdown_code = None
_shutdown_lock = threading.Lock()

# ------------------------------
# HTML Admin Panel
# ------------------------------
ADMIN_PANEL = r"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MIOS</title>
    <style>
        :root {
            --bg: #0f1115;
            --panel: #151923;
            --panel-2: #1b2030;
            --text: #e7eaf0;
            --muted: #9aa3b2;
            --accent: #5b9cff;
            --accent-2: #7dd3fc;
            --danger: #ef4444;
            --ok: #22c55e;
            --warn: #f59e0b;
            --shadow: 0 8px 30px rgba(0,0,0,.35);
            --radius: 14px;
        }

        .light-theme {
            --bg: #f5f5f5;
            --panel: #ffffff;
            --panel-2: #f8f8f8;
            --text: #1d1d23;
            --muted: #6b7280;
            --accent: #3b82f6;
            --accent-2: #0ea5e9;
            --danger: #dc2626;
            --ok: #16a34a;
            --warn: #d97706;
            --shadow: 0 8px 30px rgba(0,0,0,.15);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 900px;
            display: grid;
            gap: 20px;
        }

        .panel {
            background-color: var(--panel);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--panel-2);
        }

        h1, h2, h3 {
            margin-top: 0;
            color: var(--text);
        }

        h1 {
            font-size: 2.5em;
        }

        h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .info-item .label {
            color: var(--muted);
            font-size: 0.9em;
            text-transform: uppercase;
        }

        .info-item .value {
            font-weight: bold;
        }

        .action-button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: var(--radius);
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            white-space: nowrap;
            font-size: 1em;
            border: none;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,.2);
        }

        .button-primary {
            background-color: var(--accent);
            color: white;
        }
        
        .button-danger {
            background-color: var(--danger);
            color: white;
        }
        
        .button-neutral {
            background-color: var(--panel-2);
            color: var(--text);
        }
        
        .button-ok {
            background-color: var(--ok);
            color: white;
        }
        
        .button-warn {
            background-color: var(--warn);
            color: white;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .file-list {
            list-style: none;
            padding: 0;
        }
        
        .file-item {
            background-color: var(--panel-2);
            padding: 10px 15px;
            border-radius: var(--radius);
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            word-break: break-all;
            gap: 10px;
        }
        
        .file-item a {
            color: var(--text);
            text-decoration: none;
            word-break: break-all;
            flex-grow: 1;
        }

        .file-item .download-button {
            background-color: var(--accent);
            color: white;
            padding: 5px 10px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            white-space: nowrap;
        }

        #file-path {
            font-family: monospace;
            background-color: #0d1013;
            padding: 10px;
            border-radius: var(--radius);
            border: 1px solid var(--panel-2);
            overflow-x: auto;
        }

        .dialog {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: var(--panel);
            padding: 30px;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            z-index: 1000;
            display: none;
            flex-direction: column;
            gap: 20px;
            width: 90%;
            max-width: 400px;
        }
        
        .dialog input {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid var(--panel-2);
            background-color: var(--bg);
            color: var(--text);
        }

        .dialog-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        #overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 999;
            display: none;
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 2000;
        }

        @media (min-width: 600px) {
            .container {
                grid-template-columns: 2fr 1fr;
            }
            .main-content {
                grid-column: span 2;
            }
            .side-panel {
                grid-column: span 1;
            }
        }
        
        .status-light {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }

        .status-running {
            background-color: var(--ok);
        }

        .status-stopped {
            background-color: var(--danger);
        }
    </style>
</head>
<body>
<!-- ...existing code... -->
</body>
</html>
"""

# ------------------------------
# Fungsi Pembantu
# ------------------------------
def get_local_ip():
    """Mendapatkan alamat IP lokal perangkat."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def do_exit():
    """Mematikan server."""
    global is_running
    time.sleep(1)
    is_running = False
    os._exit(0)

# ------------------------------
# Routes
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    """Menyajikan halaman admin panel."""
    return render_template_string(ADMIN_PANEL)

@app.route("/api/files", methods=["GET"])
def api_files():
    """Mengembalikan daftar file dan folder."""
    base_path = current_directory
    requested_path = request.args.get('path', '/')
    
    # Normalisasi path
    if requested_path.startswith('/'):
        requested_path = requested_path[1:]
    
    full_path = os.path.join(base_path, requested_path)
    
    # Verifikasi keamanan
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_path)):
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403

    if not os.path.isdir(full_path):
        return jsonify({"status": "error", "message": "Direktori tidak ditemukan", "path": requested_path}), 404
        
    try:
        files = []
        with os.scandir(full_path) as entries:
            for entry in sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower())):
                item = {
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if not entry.is_dir() else None
                }
                files.append(item)

        parent_path = os.path.dirname(requested_path) if requested_path else None

        return jsonify({
            "status": "ok",
            "current_path": os.path.normpath(requested_path),
            "parent_path": os.path.normpath(parent_path) if parent_path else None,
            "files": files
        })
    except Exception as e:
        print(f"Error reading directory: {e}")
        return jsonify({"status": "error", "message": f"Gagal membaca direktori: {e}"}), 500

@app.route("/download", methods=["GET"])
def download_file():
    """Mengunduh file dari server."""
    file_path_rel = request.args.get('path')
    if not file_path_rel:
        return "Parameter 'path' diperlukan", 400

    safe_path = os.path.join(current_directory, file_path_rel.strip('/'))

    if not os.path.abspath(safe_path).startswith(os.path.abspath(current_directory)):
        return "Akses Ditolak", 403

    if not os.path.exists(safe_path) or os.path.isdir(safe_path):
        return "File tidak ditemukan", 404

    return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path), as_attachment=True)

@app.route("/api/shutdown", methods=["POST"])
def api_shutdown():
    """Mematikan server dari permintaan API."""
    global _shutdown_code
    with _shutdown_lock:
        if _shutdown_code is None:
            # Generate code and display to console
            _shutdown_code = str(random.randint(1000, 9999))
            print(f"\n[INFO] Kode pemadaman server (4 digit): {_shutdown_code}\n")
            sys.stdout.flush()
            return jsonify({"status": "info", "message": "Kode pemadaman dikirim ke konsol. Masukkan di sini."}), 202

        data = request.json
        client_code = data.get("code")
        
        if client_code == _shutdown_code:
            print("[INFO] Kode cocok. Mematikan server...")
            sys.stdout.flush()
            threading.Thread(target=do_exit, daemon=True).start()
            return jsonify({"status": "ok", "message": "Server sedang dimatikan."})
        else:
            print("[SECURITY] Kode pemadaman tidak cocok.")
            sys.stdout.flush()
            return jsonify({"status": "error", "message": "Kode tidak valid"}), 403

@app.route("/api/info", methods=["GET"])
def api_info():
    """Mengembalikan informasi server."""
    return jsonify({
        "local_ip": get_local_ip(),
        "cwd": current_directory,
        "start_time": start_time.isoformat()
    })

# ------------------------------
# Main: jalankan server
# ------------------------------
def start_server(directory=None, host=HOST, port=PORT):
    """Fungsi utama untuk memulai server."""
    global current_directory, is_running, start_time
    if directory:
        current_directory = directory
    is_running = True
    start_time = datetime.now()
    local_ip = get_local_ip()
    print(f"\n[INFO] Server dimulai di: http://{local_ip}:{port}")
    print(f"[INFO] Direktori yang dilayani: {current_directory}")
    print("[INFO] Buka tautan di atas untuk mengakses panel admin.")
    print("[INFO] Untuk mematikan server dari antarmuka, klik 'Matikan Server'.")
    print("[INFO] Kode pemadaman akan muncul di konsol ini.")
    sys.stdout.flush()
    serve(app, host=host, port=port)

def main():
    """Fungsi utama untuk antarmuka baris perintah."""
    print("Selamat datang di MISE - MIOS Server.")
    print("Aplikasi ini memungkinkan Anda berbagi file dari perangkat Anda")
    print("ke perangkat lain dalam jaringan yang sama atau melalui internet.")
    
    while True:
        print("\nPilihan:")
        print("1. Buat Server")
        print("2. Keluar")
        
        choice = input("Masukkan pilihan (1/2): ").strip()
        
        if choice == "1":
            directory = input("Masukkan path direktori yang akan dilayani: ").strip()
            
            if not os.path.exists(directory):
                print("Direktori tidak ditemukan!")
                continue
            
            if not os.path.isdir(directory):
                print("Path yang dimasukkan bukan direktori!")
                continue
                
            port_input = input("Masukkan port (default 5000): ").strip()
            port = int(port_input) if port_input.isdigit() else 5000
            
            global server_thread
            server_thread = threading.Thread(target=start_server, args=(directory, port))
            server_thread.daemon = True
            server_thread.start()
            
            try:
                while is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nServer dihentikan.")
                break
                
        elif choice == "2":
            print("Terima kasih telah menggunakan MISE!")
            break
            
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
# ====== END OF FILE: misetest.py ======
