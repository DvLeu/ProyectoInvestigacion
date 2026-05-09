"""
Endpoints HTTP de la API.
"""

from flask import Blueprint, request, jsonify

from models import db, Usuario, TarjetaNFC, Salon, RegistroAcceso
import services


bp = Blueprint("api", __name__)


@bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "servicio": "asistencia_nfc",
        "estado": "ok",
        "endpoints": [
            "GET  /usuarios",
            "POST /usuarios",
            "GET  /tarjetas",
            "POST /tarjetas",
            "POST /acceso",
            "GET  /registros",
            "GET  /salones",
            "POST /salones",
        ],
    })


#Usuarios 

@bp.route("/usuarios", methods=["GET"])
def get_usuarios():
    usuarios = Usuario.query.order_by(Usuario.apellido_paterno, Usuario.nombre).all()
    return jsonify([u.to_dict() for u in usuarios])


@bp.route("/usuarios", methods=["POST"])
def post_usuarios():
    data = request.get_json(silent=True) or {}
    try:
        u = Usuario(
            nombre=data["nombre"],
            apellido_paterno=data["apellido_paterno"],
            apellido_materno=data.get("apellido_materno"),
            matricula=data["matricula"],
        )
    except KeyError as e:
        return jsonify({"error": f"Falta campo: {e.args[0]}"}), 400

    db.session.add(u)
    db.session.commit()
    return jsonify(u.to_dict()), 201


#Tarjetas

@bp.route("/tarjetas", methods=["GET"])
def get_tarjetas():
    return jsonify([t.to_dict() for t in TarjetaNFC.query.all()])


@bp.route("/tarjetas", methods=["POST"])
def post_tarjeta():
    data = request.get_json(silent=True) or {}
    try:
        uid = data["uid"].upper().replace(":", "").replace(" ", "")
        t = TarjetaNFC(uid=uid, id_usuario=data["id_usuario"])
    except KeyError as e:
        return jsonify({"error": f"Falta campo: {e.args[0]}"}), 400

    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


#Acceso

@bp.route("/acceso", methods=["POST"])
def post_acceso():
    """Recibe un UID y registra entrada/salida automáticamente."""
    data = request.get_json(silent=True) or {}
    resultado = services.procesar_uid(data.get("uid", ""))
    status = 200 if resultado["ok"] else 403
    return jsonify(resultado), status


#Registros

@bp.route("/registros", methods=["GET"])
def get_registros():
    limit = int(request.args.get("limit", 50))
    registros = (
        RegistroAcceso.query.order_by(RegistroAcceso.fecha_hora.desc())
        .limit(limit)
        .all()
    )
    return jsonify([r.to_dict() for r in registros])


#Salones

@bp.route("/salones", methods=["GET"])
def get_salones():
    return jsonify([s.to_dict() for s in Salon.query.filter_by(activo=True).all()])


@bp.route("/salones", methods=["POST"])
def post_salon():
    data = request.get_json(silent=True) or {}
    try:
        s = Salon(nombre=data["nombre"], ubicacion=data.get("ubicacion"))
    except KeyError as e:
        return jsonify({"error": f"Falta campo: {e.args[0]}"}), 400

    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201
