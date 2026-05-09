"""
Lógica de negocio.
- procesar_uid(): valida y registra entrada/salida automáticamente
- leer_uid_nfc(): lee del lector ACR122U vía PC/SC
"""

from datetime import date
from sqlalchemy import func

from models import db, Usuario, TarjetaNFC, RegistroAcceso


# Configuración de runtime (la setea app.py al inicio)
SALON_ID = 1
ORIGEN = "lector_principal"


def configurar(salon_id: int, origen: str):
    """Permite cambiar el salón y origen sin reiniciar."""
    global SALON_ID, ORIGEN
    SALON_ID = salon_id
    ORIGEN = origen

#  Lógica de control de acceso

def procesar_uid(uid: str) -> dict:
    """
    Recibe un UID, valida, registra entrada o salida, devuelve resultado.
    La usan tanto el lector físico como la API REST.
    """
    uid = uid.upper().replace(":", "").replace(" ", "").strip()

    if not uid:
        return {"ok": False, "razon": "UID vacío"}

    tarjeta = TarjetaNFC.query.filter_by(uid=uid).first()

    if tarjeta is None:
        return {"ok": False, "razon": "Tarjeta no registrada", "uid": uid}

    if not tarjeta.activa:
        return {"ok": False, "razon": "Tarjeta dada de baja", "uid": uid}

    usuario = tarjeta.usuario
    if not usuario.activo:
        return {"ok": False, "razon": "Usuario inactivo", "uid": uid}

    # Último evento del usuario hoy
    ultimo = (
        db.session.query(RegistroAcceso.tipo_evento)
        .filter(
            RegistroAcceso.id_usuario == usuario.id_usuario,
            func.date(RegistroAcceso.fecha_hora) == date.today(),
        )
        .order_by(RegistroAcceso.fecha_hora.desc())
        .first()
    )

    tipo_evento = "SALIDA" if (ultimo and ultimo[0] == "ENTRADA") else "ENTRADA"

    nuevo = RegistroAcceso(
        id_usuario=usuario.id_usuario,
        id_tarjeta=tarjeta.id_tarjeta,
        id_salon=SALON_ID,
        tipo_evento=tipo_evento,
        origen=ORIGEN,
    )
    db.session.add(nuevo)
    db.session.commit()

    return {
        "ok": True,
        "uid": uid,
        "tipo_evento": tipo_evento,
        "usuario": usuario.nombre_completo,
        "matricula": usuario.matricula,
    }


#  Lectura física del ACR122U

_GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]


def leer_uid_nfc(timeout=None):
    """
    Espera una tarjeta en el lector y devuelve su UID en hex.
    Import diferido para que la API funcione en máquinas sin pyscard.
    """
    from smartcard.System import readers
    from smartcard.util import toHexString
    from smartcard.Exceptions import NoCardException, CardConnectionException
    import time

    lista = readers()
    if not lista:
        raise RuntimeError("No se detectó ningún lector NFC")

    lector = lista[0]
    inicio = time.time()

    while True:
        if timeout is not None and (time.time() - inicio) > timeout:
            return None

        try:
            conn = lector.createConnection()
            conn.connect()
            data, sw1, sw2 = conn.transmit(_GET_UID_APDU)
            conn.disconnect()

            if sw1 == 0x90 and sw2 == 0x00:
                return toHexString(data).replace(" ", "")
        except (NoCardException, CardConnectionException):
            time.sleep(0.3)
