import os
import webbrowser
import threading
import time
import socket
import sys
import mimetypes
import random
import string
import json
import requests
from flask import Flask, render_template_string, send_from_directory, request, jsonify, redirect
from datetime import datetime
from waitress import serve

# Mengatur tipe MIME yang tidak terdefinisi secara default
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/jpg', '.jpg')
mimetypes.add_type('image/png', '.png')

app = Flask(__name__)
server_thread = None
current_directory = ""
host = "0.0.0.0"
port = 5000
is_running = False
start_time = datetime.now()
shutdown_code = None
main_html_file = None
selected_variant = None

# Variants configuration
VARIANTS = {
    "Profesional": {
        "name": "Profesional",
        "description": "Dengan desain baru dan ada app store",
        "html_url": "https://raw.githubusercontent.com/Files2012/MISE/refs/heads/main/OS/MIOS%20Profesional.html"
    },
    "Basic": {
        "name": "Basic",
        "description": "Sederhana ringan",
        "html_url": "https://raw.githubusercontent.com/Files2012/MISE/refs/heads/main/OS/MIOS%20Basic.html"
    }
}

# HTML Template untuk Admin Panel (fallback jika tidak bisa mendownload)
ADMIN_PANEL = r"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MIOS</title>
    <style>
        /* Styles akan diisi oleh template yang didownload */
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
    <!-- Konten lainnya akan diisi oleh template yang didownload -->
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

def format_file_size(size_in_bytes):
    if size_in_bytes is None:
        return ""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 ** 3):.2f} GB"

def shutdown_server():
    print("\n[INFO] Mematikan server...")
    os._exit(0)

def download_variant_html(variant_name):
    """Mendownload HTML template untuk varian yang dipilih."""
    global selected_variant
    
    if variant_name not in VARIANTS:
        print(f"[ERROR] Varian '{variant_name}' tidak ditemukan!")
        return None
    
    variant = VARIANTS[variant_name]
    url = variant["html_url"]
    
    try:
        print(f"[INFO] Mendownload template untuk varian {variant_name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        selected_variant = variant_name
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gagal mendownload template: {e}")
        print("[INFO] Menggunakan template fallback...")
        return ADMIN_PANEL

# ------------------------------
# Routes
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    """Menyajikan halaman utama atau halaman default."""
    if main_html_file:
        try:
            return send_from_directory(current_directory, main_html_file)
        except Exception:
            return redirect("/admin")
    return redirect("/admin")

@app.route("/admin", methods=["GET"])
def admin_panel():
    """Menyajikan halaman admin panel."""
    # Gunakan template yang sudah didownload atau fallback
    global selected_variant
    if selected_variant:
        variant_html = download_variant_html(selected_variant)
        return render_template_string(variant_html)
    return render_template_string(ADMIN_PANEL)

@app.route("/<path:filename>", methods=["GET"])
def serve_file(filename):
    """Menyajikan file statis dari direktori."""
    try:
        return send_from_directory(current_directory, filename)
    except Exception as e:
        return str(e), 404

@app.route("/api/files", methods=["GET"])
def api_files():
    """Mengembalikan daftar file dan folder."""
    requested_path = request.args.get('path', '')
    base_path = current_directory
    
    # Normalisasi path dan verifikasi keamanan
    full_path = os.path.normpath(os.path.join(base_path, requested_path))
    if not full_path.startswith(base_path):
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403

    if not os.path.isdir(full_path):
        return jsonify({"status": "error", "message": "Path bukan direktori"}), 400

    files_list = []
    try:
        # Menambahkan "..." untuk kembali ke direktori induk
        if full_path != base_path:
            parent_path = os.path.dirname(full_path)
            # Pastikan path induk masih di dalam base_path
            if parent_path.startswith(base_path):
                files_list.append({
                    'name': '..',
                    'is_dir': True,
                    'is_parent': True,
                    'path': os.path.relpath(parent_path, base_path)
                })

        # Urutkan folder di atas
        items = sorted(os.listdir(full_path), key=lambda x: (not os.path.isdir(os.path.join(full_path, x)), x.lower()))

        for filename in items:
            filepath = os.path.join(full_path, filename)
            is_dir = os.path.isdir(filepath)
            size = None
            if not is_dir:
                size = format_file_size(os.path.getsize(filepath))
            
            files_list.append({
                'name': filename,
                'is_dir': is_dir,
                'is_parent': False,
                'path': os.path.relpath(filepath, base_path),
                'size': size
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "files": files_list})

@app.route("/api/preview_file", methods=["GET"])
def api_preview_file():
    """Mengembalikan isi file teks."""
    requested_path = request.args.get('path', '')
    base_path = current_directory

    full_path = os.path.normpath(os.path.join(base_path, requested_path))
    
    if not full_path.startswith(base_path) or not os.path.isfile(full_path):
        return "File tidak ditemukan atau akses ditolak.", 404

    # Cek MIME type sederhana untuk keamanan
    try:
        mimetype, _ = mimetypes.guess_type(full_path)
        if not mimetype or not mimetype.startswith('text/'):
            return "Pratinjau hanya tersedia untuk file teks.", 403
    except:
        return "Gagal menentukan jenis file.", 500
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return str(e), 500

@app.route("/api/file/open", methods=["GET"])
def api_file_open():
    """Membuka dan mengembalikan konten file."""
    requested_path = request.args.get('path', '')
    base_path = current_directory
    
    full_path = os.path.normpath(os.path.join(base_path, requested_path))
    
    if not full_path.startswith(base_path):
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403
    
    if not os.path.isfile(full_path):
        return jsonify({"status": "error", "message": "File tidak ditemukan"}), 404

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"status": "success", "content": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/file/save", methods=["POST"])
def api_file_save():
    """Menyimpan konten ke file."""
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or content is None:
        return jsonify({"status": "error", "message": "Nama file dan konten diperlukan"}), 400
        
    base_path = current_directory
    full_path = os.path.normpath(os.path.join(base_path, filename))
    
    if not full_path.startswith(base_path):
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/media", methods=["GET"])
def api_media():
    """Menyajikan file media."""
    filename = request.args.get('filename')
    base_path = current_directory
    
    full_path = os.path.normpath(os.path.join(base_path, filename))
    if not full_path.startswith(base_path) or not os.path.isfile(full_path):
        return "File tidak ditemukan atau akses ditolak.", 404
        
    return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))

@app.route("/api/shutdown", methods=["POST"])
def api_shutdown():
    """Mematikan server."""
    global shutdown_code
    shutdown_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(f"\n[INFO] Kode untuk mematikan server: {shutdown_code}")
    threading.Thread(target=lambda: (time.sleep(15), shutdown_server()), daemon=True).start()
    return jsonify({"status": "success", "code": shutdown_code}), 200

# ------------------------------
# Main: jalankan server
# ------------------------------
def start_server(directory=None, selected_port=5000, variant_name="Profesional"):
    """Fungsi utama untuk memulai server."""
    global current_directory, is_running, port, selected_variant
    
    # Download template untuk varian yang dipilih
    variant_html = download_variant_html(variant_name)
    if variant_html:
        global ADMIN_PANEL
        ADMIN_PANEL = variant_html
    
    if directory:
        current_directory = os.path.abspath(directory)
    is_running = True
    port = selected_port
    
    local_ip = get_local_ip()
    print(f"\n[INFO] Server dimulai di http://{local_ip}:{port}")
    print(f"[INFO] Melayani direktori: {current_directory}")
    print(f"[INFO] Menggunakan varian: {selected_variant}")
    print(f"[INFO] Admin Panel tersedia di http://localhost:{port}/admin")
    if main_html_file:
        print(f"[INFO] Halaman utama tersedia di http://localhost:{port}/")
    else:
        print("[INFO] Halaman utama (/) mengarah ke Admin Panel.")

    try:
        serve(app, host=host, port=port)
    except Exception as e:
        print(f"Error saat memulai server: {e}")
        is_running = False

def main():
    """Fungsi utama program"""
    print("=" * 60)
    print("MISE - Mini Server dengan Admin Panel Sederhana")
    print("=" * 60)
    print("Server ini dapat diakses dari perangkat lain dalam jaringan")
    print("yang sama atau melalui internet (jika terkoneksi langsung).")
    print("")
    
    global main_html_file, selected_variant

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

            main_html_file = input("Masukkan nama file HTML yang akan dijadikan halaman utama (kosongkan jika tidak ada): ").strip()
            
            if main_html_file and not os.path.isfile(os.path.join(directory, main_html_file)):
                print(f"File '{main_html_file}' tidak ditemukan di direktori tersebut. Server akan tetap berjalan, tetapi halaman utama tidak akan berfungsi.")
                main_html_file = None
            
            # Pilih varian MIOS
            print("\nPilih varian MIOS:")
            variants = list(VARIANTS.keys())
            for i, variant in enumerate(variants, 1):
                print(f"{i}. {variant} - {VARIANTS[variant]['description']}")
            
            variant_choice = input(f"Masukkan pilihan (1-{len(variants)}): ").strip()
            
            try:
                variant_index = int(variant_choice) - 1
                if 0 <= variant_index < len(variants):
                    selected_variant_name = variants[variant_index]
                else:
                    print("Pilihan tidak valid, menggunakan varian Profesional secara default.")
                    selected_variant_name = "Profesional"
            except ValueError:
                print("Input tidak valid, menggunakan varian Profesional secara default.")
                selected_variant_name = "Profesional"
                
            port_input = input("Masukkan port (default 5000): ").strip()
            port = int(port_input) if port_input.isdigit() else 5000
            
            global server_thread
            server_thread = threading.Thread(target=start_server, args=(directory, port, selected_variant_name))
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
