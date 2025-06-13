#!/usr/bin/env python3
"""
Cliente TCP para chat.
Mostra as próprias mensagens à direita e as dos outros à esquerda,
com uma linha em branco entre cada mensagem.
"""
import socket
import threading
import shutil
import sys
from datetime import datetime

HOST = '127.0.0.1'  # ou IP do servidor
PORT = 5000

def recv_messages(sock):
    """Thread que imprime tudo que chega do servidor (alinhado à esquerda)."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[!] Conexão encerrada pelo servidor.")
                break
            # antes de mostrar a mensagem do outro, pulo uma linha
            print()
            sys.stdout.write(data.decode())
            sys.stdout.flush()
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # descarta prompt inicial do servidor
    sock.recv(1024)

    nome = input("Informe seu nome: ").strip()
    if not nome:
        print("Nome inválido. Encerrando.")
        sock.close()
        return

    sock.sendall(nome.encode())
    print(f"\n>>> Olá, {nome}! Você entrou no chat. Para sair, digite '/sair'.\n")

    # inicia thread de recepção
    threading.Thread(target=recv_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            if not msg:
                continue

            sock.sendall(msg.encode())

            # apaga o "echo" do input
            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()

            # quebra de linha antes da nossa mensagem
            print()

            # monta e imprime alinhado à direita
            ts   = datetime.now().strftime("%H:%M:%S")
            cols = shutil.get_terminal_size((80, 20)).columns
            texto = f"[{ts}] [{nome}] {msg}"
            print(texto.rjust(cols))

            if msg.strip().lower() == '/sair':
                break

    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    main()
