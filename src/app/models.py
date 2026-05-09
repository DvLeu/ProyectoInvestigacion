"""
Modelos SQLAlchemy.
Cada clase mapea una tabla del Schema.sql sin modificar nada.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=True)
    matricula = db.Column(db.String(30), nullable=False, unique=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    tarjetas = db.relationship("TarjetaNFC", backref="usuario", lazy=True)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "matricula": self.matricula,
            "activo": bool(self.activo),
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }

    @property
    def nombre_completo(self):
        partes = [self.nombre, self.apellido_paterno]
        if self.apellido_materno:
            partes.append(self.apellido_materno)
        return " ".join(partes)


class TarjetaNFC(db.Model):
    __tablename__ = "tarjetas_nfc"

    id_tarjeta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(50), nullable=False, unique=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    activa = db.Column(db.Boolean, nullable=False, default=True)
    fecha_alta = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id_tarjeta": self.id_tarjeta,
            "uid": self.uid,
            "id_usuario": self.id_usuario,
            "activa": bool(self.activa),
            "fecha_alta": self.fecha_alta.isoformat() if self.fecha_alta else None,
        }


class Salon(db.Model):
    __tablename__ = "salones"

    id_salon = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(150), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id_salon": self.id_salon,
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "activo": bool(self.activo),
        }


class RegistroAcceso(db.Model):
    __tablename__ = "registros_acceso"

    id_registro = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    id_tarjeta = db.Column(
        db.Integer,
        db.ForeignKey("tarjetas_nfc.id_tarjeta", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    id_salon = db.Column(
        db.Integer,
        db.ForeignKey("salones.id_salon", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    fecha_hora = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    tipo_evento = db.Column(db.Enum("ENTRADA", "SALIDA"), nullable=False)
    origen = db.Column(db.String(50), nullable=True)
    observacion = db.Column(db.String(255), nullable=True)

    usuario = db.relationship("Usuario", backref="registros")
    tarjeta = db.relationship("TarjetaNFC", backref="registros")
    salon = db.relationship("Salon", backref="registros")

    def to_dict(self):
        return {
            "id_registro": self.id_registro,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "tipo_evento": self.tipo_evento,
            "origen": self.origen,
            "observacion": self.observacion,
            "usuario": self.usuario.nombre_completo if self.usuario else None,
            "matricula": self.usuario.matricula if self.usuario else None,
            "uid": self.tarjeta.uid if self.tarjeta else None,
            "salon": self.salon.nombre if self.salon else None,
        }