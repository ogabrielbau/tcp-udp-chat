#!/usr/bin/env python3
"""
Servidor TCP multiclientes usando threads.
Agora com timestamp em cada mensagem.
"""
import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000

clients = []  # lista de tuples (conn, addr, nome)
lock = threading.Lock()

def _timestamped(text: str) -> bytes:
    """Anexa [HH:MM:SS] antes do texto e retorna em bytes."""
    ts = datetime.now().strftime("%H:%M:%S")
    return f"[{ts}] {text}".encode()

def broadcast(raw_bytes: bytes, exclude_conn=None):
    """Envia raw_bytes para todos, exceto exclude_conn."""
    with lock:
        for conn, _, _ in clients:
            if conn is not exclude_conn:
                try:
                    conn.sendall(raw_bytes)
                except:
                    pass

def handle_client(conn, addr):
    """Thread que gerencia um cliente."""
    try:
        # 1) pede nome
        conn.sendall(b'Informe seu nome: ')
        nome = conn.recv(1024).decode().strip()
        if not nome:
            conn.close()
            return

        # 2) registra e anuncia entrada
        with lock:
            clients.append((conn, addr, nome))
        broadcast(_timestamped(f">>> {nome} entrou no chat.\n"))

        # 3) loop de mensagens
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            if msg.lower() == '/sair':
                break
            # 4) envia com timestamp e nome
            broadcast(_timestamped(f"[{nome}] {msg}\n"), exclude_conn=conn)

    finally:
        # remove e anuncia saída
        with lock:
            clients[:] = [(c,a,n) for (c,a,n) in clients if c is not conn]
        broadcast(_timestamped(f">>> {nome} saiu do chat.\n"))
        conn.close()

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(5)
    print(f"[TCP] Servidor ouvindo em {HOST}:{PORT}...")
    try:
        while True:
            conn, addr = srv.accept()
            print(f"Conexão de {addr}")
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
    finally:
        srv.close()

if __name__ == "__main__":
    main()
