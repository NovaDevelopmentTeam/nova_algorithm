import hashlib
import socket
import json

# Mining-Funktion: Berechnet einen Hash, der die Difficulty erfüllt
def mine_share(header, share_difficulty):
    nonce = 0
    target = 2 ** (256 - share_difficulty)  # Zielwert basierend auf Difficulty
    while True:
        data = f"{header}{nonce}".encode()
        hash_result = hashlib.sha256(data).hexdigest()
        if int(hash_result, 16) < target:  # Wenn Hash kleiner als Ziel ist
            print(f"[Mining] Share gefunden! Nonce: {nonce}, Hash: {hash_result}")
            return nonce, hash_result
        nonce += 1

# Verbindung zu einem Mining-Pool herstellen
def connect_to_pool(pool_address, port):
    try:
        pool_socket = socket.create_connection((pool_address, port))
        print(f"[Netzwerk] Verbunden mit Pool: {pool_address}:{port}")
        return pool_socket
    except Exception as e:
        print(f"[Fehler] Verbindung zum Pool fehlgeschlagen: {e}")
        return None

# Login beim Mining-Pool (Stratum)
def send_login(pool_socket, username):
    login_request = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
    }
    pool_socket.sendall(json.dumps(login_request).encode() + b"\n")
    response = pool_socket.recv(1024).decode()
    print(f"[Pool] Antwort auf Subscribe: {response}")

    auth_request = {
        "id": 2,
        "method": "mining.authorize",
        "params": [username, ""]
    }
    pool_socket.sendall(json.dumps(auth_request).encode() + b"\n")
    response = pool_socket.recv(1024).decode()
    print(f"[Pool] Antwort auf Autorisierung: {response}")

# Arbeitspakete verarbeiten und Shares zurücksenden
def process_work(pool_socket):
    try:
        while True:
            work_request = pool_socket.recv(1024).decode()
            work_data = json.loads(work_request)

            if "method" in work_data and work_data["method"] == "mining.notify":
                print(f"[Arbeit] Neues Arbeitspaket erhalten: {work_data}")
                params = work_data["params"]
                header = params[0]  # Blockheader
                difficulty = 24    # Beispiel-Schwierigkeitsgrad

                # Mining ausführen
                nonce, result_hash = mine_share(header, difficulty)

                # Share zurücksenden
                submit_request = {
                    "id": 3,
                    "method": "mining.submit",
                    "params": ["miner_name", nonce, result_hash]
                }
                pool_socket.sendall(json.dumps(submit_request).encode() + b"\n")
                print(f"[Share] Share gesendet: Nonce {nonce}, Hash {result_hash}")
    except Exception as e:
        print(f"[Fehler] Problem beim Verarbeiten von Arbeit: {e}")

# Hauptprogramm
def main():
    pool_address = "pool.minexmr.com"  # Beispiel-Pool (Monero)
    pool_port = 4444
    username = "dein_username"  # Ersetze mit deinem Mining-Benutzernamen

    pool_socket = connect_to_pool(pool_address, pool_port)
    if pool_socket:
        send_login(pool_socket, username)
        process_work(pool_socket)
    else:
        print("[Abbruch] Keine Verbindung zum Pool möglich.")

if __name__ == "__main__":
    main()
