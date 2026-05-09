"""
Lógica de negocio.
- procesar_uid(): registra una marca de asistencia.
  Una sola por hora de reloj (08:00, 09:00, ...).
  Si marcaste a las 14:55, la próxima es desde las 15:00 en adelante.
- leer_uid_nfc(): lee del lector ACR122U vía PC/SC
"""

from datetime import datetime, date

from models import db, TarjetaNFC, RegistroAcceso


SALON_ID = 1
ORIGEN = "lector_principal"


def configurar(salon_id: int, origen: str):
    global SALON_ID, ORIGEN
    SALON_ID = salon_id
    ORIGEN = origen


def procesar_uid(uid: str) -> dict:
    """
    Recibe un UID y registra una marca de asistencia.
    Regla: solo una marca por usuario por hora de reloj.
    Ej: si marcó a las 14:30, no puede volver a marcar entre 14:00 y 14:59.
        En cuanto den las 15:00, ya puede volver a marcar.
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

    info_usuario = {
        "uid": uid,
        "usuario": usuario.nombre_completo,
        "matricula": usuario.matricula,
    }

    # Hora actual y "hora de reloj" (sin minutos)
    ahora = datetime.now()
    hora_reloj_actual = ahora.hour

    # ¿Ya hay un registro hoy en la misma hora de reloj?
    ya_marco_esta_hora = (
        RegistroAcceso.query
        .filter(
            RegistroAcceso.id_usuario == usuario.id_usuario,
            db.func.date(RegistroAcceso.fecha_hora) == date.today(),
            db.func.hour(RegistroAcceso.fecha_hora) == hora_reloj_actual,
        )
        .first()
    )

    if ya_marco_esta_hora:
        minutos_para_siguiente = 60 - ahora.minute
        return {
            **info_usuario,
            "ok": False,
            "razon": f"Ya registraste asistencia de las {hora_reloj_actual:02d}:00. "
                     f"Próxima marca a las {(hora_reloj_actual + 1) % 24:02d}:00 "
                     f"(en {minutos_para_siguiente} min).",
        }

    # Registrar la asistencia
    nuevo = RegistroAcceso(
        id_usuario=usuario.id_usuario,
        id_tarjeta=tarjeta.id_tarjeta,
        id_salon=SALON_ID,
        tipo_evento="ENTRADA",
        origen=ORIGEN,
    )
    db.session.add(nuevo)
    db.session.commit()

    return {**info_usuario, "ok": True, "tipo_evento": "ENTRADA"}


# ============================================================
#  Lectura física del ACR122U
# ============================================================

_GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]


def leer_uid_nfc(timeout=None):
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