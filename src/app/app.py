import sys
import time
import threading
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from models import db
from routes import bp
import services

def loop_lector(app):
    """Loop del lector ACR122U. Se ejecuta en un hilo aparte."""
    print("\n[LECTOR] Buscando ACR122U...")
    while True:
        try:
            from smartcard.System import readers
            if readers():
                print("[LECTOR] ACR122U detectado. Acerca una tarjeta.\n")
                break
        except Exception as e:
            print(f"[LECTOR] {e}")
        time.sleep(3)

    ultimo_uid = None
    ultima_lectura = 0

    with app.app_context():
        while True:
            try:
                uid = services.leer_uid_nfc(timeout=0.5)
                if uid is None:
                    continue

                ahora = time.time()
                if uid == ultimo_uid and (ahora - ultima_lectura) < 3:
                    continue

                ultimo_uid = uid
                ultima_lectura = ahora

                print(f"\n[NFC] Tarjeta: {uid}")
                resultado = services.procesar_uid(uid)

                if resultado["ok"]:
                    print(f"[OK] {resultado['tipo_evento']} - "
                        f"{resultado['usuario']} ({resultado['matricula']})")
                else:
                    print(f"[DENEGADO] {resultado['razon']}")

            except RuntimeError as e:
                print(f"[LECTOR ERROR] {e}")
                time.sleep(2)
            except Exception as e:
                print(f"[LECTOR ERROR] {e}")
                time.sleep(1)
                
def crear_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app)
    app.register_blueprint(bp)

    front_dir = os.path.join(os.path.dirname(__file__), "..", "front")
    front_dir = os.path.abspath(front_dir)

    @app.route("/web")
    @app.route("/web/<path:path>")
    def servir_front(path="index.html"):
        return send_from_directory(front_dir, path)

    with app.app_context():
        db.create_all()

    return app

def correr_todo():
    """API + lector + front, todo en una sola terminal."""
    app = crear_app()

    # Lector en hilo separado para no bloquear la API
    hilo_lector = threading.Thread(target=loop_lector, args=(app,), daemon=True)
    hilo_lector.start()

    print("=" * 50)
    print("  Sistema de Asistencia NFC")
    print("=" * 50)
    print("  API:    http://localhost:5000")
    print("  Front:  http://localhost:5000/web")
    print("  Ctrl+C para salir")
    print("=" * 50)

    # use_reloader=False evita que Flask arranque dos veces el hilo del lector
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def correr_simulador():
    """Modo simulador (sin lector físico)."""
    app = crear_app()

    print("=" * 50)
    print("  Simulador NFC")
    print("=" * 50)
    print("Escribe un UID y Enter. 'salir' para terminar.\n")

    with app.app_context():
        while True:
            try:
                uid = input("UID > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nHasta luego.")
                break

            if uid.lower() in ("salir", "exit", "quit"):
                break
            if not uid:
                continue

            resultado = services.procesar_uid(uid)
            if resultado["ok"]:
                print(f"  [OK] {resultado['tipo_evento']} - "
                      f"{resultado['usuario']} ({resultado['matricula']})\n")
            else:
                print(f"  [DENEGADO] {resultado['razon']}\n")


# ============================================================
#  Selector
# ============================================================

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "todo"

    if modo == "todo":
        correr_todo()
    elif modo == "simulador":
        correr_simulador()
    else:
        print(f"Modo desconocido: {modo}")
        print("Uso: python3 app.py [todo|simulador]")
        sys.exit(1)
