import http.server
import socket
import socketserver
from pathlib import Path

PORT = 8080
DIRECTORY = str(Path(__file__).resolve().parent)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    ip = get_local_ip()
    url_local = f"http://localhost:{PORT}"
    url_network = f"http://{ip}:{PORT}"
    
    print("=" * 68)
    print("      TJ-PE 2026 · SERVIDOR LOCAL PWA (MAGISTRATURA FGV)")
    print("=" * 68)
    print(f"\n[+] Pasta raiz servida: {DIRECTORY}")
    print(f"[+] Acesso no Computador (Local):     {url_local}")
    print(f"[+] Acesso no Celular/Tablet (Wi-Fi):  {url_network}\n")
    print("-" * 68)
    print("COMO INSTALAR NO SEU DISPOSITIVO ANDROID (CELULAR OU TABLET):")
    print("  1. Conecte o dispositivo Android na mesma rede Wi-Fi deste PC.")
    print(f"  2. Abra o Google Chrome no Android e acesse: {url_network}")
    print("  3. Toque no botão '📲 Instalar App' no topo da tela.")
    print("     (Caso o botão não apareça, toque no menu de 3 pontinhos [⋮]")
    print("     no canto superior direito do Chrome e selecione:")
    print("     'Instalar aplicativo' ou 'Adicionar à tela inicial').")
    print("  4. Pronto! O app fica salvo na sua tela inicial com ícone próprio")
    print("     e funciona 100% offline via Service Worker.")
    print("-" * 68)
    print("\nServidor rodando... Pressione Ctrl+C para encerrar quando desejar.\n")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Servidor PWA finalizado.")

if __name__ == "__main__":
    run()
