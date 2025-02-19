import http.server
import socket
import socketserver
import webbrowser
import pyqrcode
import os
import string
from pathlib import Path

PORT = 8010

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except PermissionError:
            self.send_error(403, "Permission denied")
            return None
        except FileNotFoundError:
            self.send_error(404, "Directory not found")
            return None
        
        # Detect Windows drives at root
        if path == '/' and os.name == 'nt':
            entries = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure File Access</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .file-list {{ max-width: 800px; margin: 20px auto; }}
        .file-item:hover {{ background-color: #f8f9fa; }}
        .icon {{ width: 24px; margin-right: 10px; }}
    </style>
</head>
<body class="bg-light">
    <div class="container py-5">
        <h1 class="mb-4 text-center">🔐 Secure File Access</h1>
        
        <div class="card shadow">
            <div class="card-header d-flex justify-content-between align-items-center">
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb mb-0">'''
        
        # Breadcrumb navigation
        current_path = self.path
        parts = current_path.split('/')
        breadcrumb = []
        for i, part in enumerate(parts):
            if part:
                link = '/'.join(parts[:i+1])
                breadcrumb.append(f'<li class="breadcrumb-item"><a href="{link}">{part}</a></li>')
        html += ''.join(breadcrumb) + '''
                    </ol>
                </nav>
                <input type="text" id="search" class="form-control w-25" placeholder="Search files...">
            </div>
            
            <div class="list-group list-group-flush file-list">'''
        
        # Parent directory link
        if path != os.getcwd() and len(parts) > 1:
            html += f'''
                <a href="../" class="list-group-item list-group-item-action file-item">
                    📁 <strong>Parent Directory</strong>
                </a>'''
        
        # File/directory listings
        for name in sorted(entries, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower())):
            full_path = os.path.join(path, name)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else ''
            icon = '📁' if is_dir else self.get_file_icon(name)
            
            html += f'''
                <a href="{name}{'/' if is_dir else ''}" class="list-group-item list-group-item-action file-item">
                    {icon} {name}
                    <span class="badge bg-secondary float-end">{size if size else 'DIR'}</span>
                </a>'''
        
        html += '''
            </div>
        </div>
        
        <script>
            document.getElementById('search').addEventListener('input', function(e) {{
                const search = e.target.value.toLowerCase();
                document.querySelectorAll('.file-item').forEach(item => {{
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(search) ? 'block' : 'none';
                }});
            }});
        </script>
    </div>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
        return None

    def get_file_icon(self, filename):
        extensions = {
            'pdf': '📄', 'txt': '📝', 'doc': '📎', 'xls': '📊',
            'jpg': '🖼', 'png': '🖼', 'exe': '⚙️', 'zip': '📦'
        }
        ext = filename.split('.')[-1].lower()
        return extensions.get(ext, '📄')

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def generate_qr(ip, port):
    url = pyqrcode.create(f"http://{ip}:{port}")
    home_dir = Path.home()
    qr_path = home_dir / "access_qr.png"
    url.png(qr_path, scale=8)
    webbrowser.open(qr_path)

def start_server():
    # Start at root directory (Windows)
    if os.name == 'nt':
        os.chdir('C:\\')
    
    handler = CustomHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        ip = get_ip_address()
        print(f"\n🔗 Server running at: http://{ip}:{PORT}")
        print("⚠️ Warning: This gives full access to your file system!")
        generate_qr(ip, PORT)
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
