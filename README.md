# ProyectoInvestigacion

## Sistema de gestión de acceso por medio de tarjetas RFC

Sistema de control de asistencia escolar con lector NFC. Cuando un alumno acerca su tarjeta al lector, el sistema registra automáticamente entrada o salida en la base de datos y lo muestra en tiempo real en una interfaz web.

**Stack:** Python (Flask + SQLAlchemy) · MySQL · HTML/JS · Docker · Lector ACS ACR122U

---

## Tabla de contenidos

* [Características](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#caracter%C3%ADsticas)
* [Estructura del proyecto](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#estructura-del-proyecto)
* [Requisitos](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#requisitos)
* [Instalación y Ejecución en macOS](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#instalaci%C3%B3n-y-ejecuci%C3%B3n-en-macos)
* [Configuración del lector NFC](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#configuraci%C3%B3n-del-lector-nfc)
* [Endpoints de la API](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#endpoints-de-la-api)
* [Esquema de base de datos](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#esquema-de-base-de-datos)
* [Solución de problemas](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#soluci%C3%B3n-de-problemas)

---

## Características

* Lectura automática de tarjetas NFC (MIFARE Classic, NTAG, ISO 14443)
* Registro automático de entrada/salida según el último evento del día
* Interfaz web con actualización en tiempo real
* API REST para integración con otros sistemas
* Modo simulador para desarrollo sin hardware
* Base de datos MySQL en contenedor Docker
* Administración visual de la BD vía phpMyAdmin

---

## Estructura del proyecto

```
ProyectoInvestigacion/
├── docker-compose.yml          MySQL 8.0 + phpMyAdmin
├── Lineamientos
├── README.md
└── src/
    ├── app/
    │   ├── app.py              Punto de entrada (API + lector + front)
    │   ├── config.py           Configuración de Flask + SQLAlchemy
    │   ├── models.py           Modelos SQLAlchemy
    │   ├── routes.py           Endpoints HTTP
    │   ├── services.py         Lógica de acceso + lectura NFC
    │   └── requirements.txt    Dependencias Python
    ├── frontend/
    │   └── index.html          Interfaz web
    └── Schema/
        └── Schema.sql          Esquema de la BD
```

---

## Requisitos

* macOS 11+
* Python 3.10+
* Docker y Docker Compose
* Lector NFC ACS ACR122U (opcional, para el sistema completo)
* Tarjetas NFC compatibles (MIFARE Classic, NTAG, ISO 14443)

---

## Instalación y Ejecución en macOS

### Paso 1: Clonar el repositorio

```bash
git clone git@github.com:DvLeu/ProyectoInvestigacion.git
cd ProyectoInvestigacion
```

### Paso 2: Levantar la base de datos con Docker

```bash
docker compose up -d
```

Esto crea automáticamente:

* **MySQL 8.0** en `localhost:3307` con la BD `asistencia_automation`
* **phpMyAdmin** en `http://localhost:8080` (usuario: `root`, password: `tu_password`)

### Paso 3: Crear entorno virtual Python

```bash
python3 -m venv .Venv
source .Venv/bin/activate
```

### Paso 4: Instalar dependencias

```bash
cd src/app
pip install -r requirements.txt
```

### Paso 5: Ejecutar la aplicación

```bash
python3 app.py todo
```

Luego abre en el navegador: **http://localhost:5000/web**

---

## Configuración del lector NFC (macOS)

El soporte para lectores NFC en macOS requiere bibliotecas específicas:

```bash
# Instalar dependencias si aún no las tienes
brew install pcsc-lite swig

# Verificar que el lector está conectado
system_profiler SPUSBDataType | grep -i "ACR"
```

El driver se detecta automáticamente. Si tienes problemas, reinicia:

```bash
# Reiniciar el servicio de tarjetas inteligentes
sudo killall -9 pcscd
```

### Obtener el UID de una tarjeta

```bash
python3 -c "
from smartcard.System import readers
from smartcard.util import toHexString
r = readers()[0]
c = r.createConnection()
c.connect()
data, sw1, sw2 = c.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
print('UID:', toHexString(data).replace(' ', ''))
"
```

Acerca la tarjeta antes de presionar Enter. Te imprime su UID único.

---

## Endpoints de la API

Base URL: `http://localhost:5000`

| Método  | Ruta           | Descripción             |
| -------- | -------------- | ------------------------ |
| `GET`  | `/`          | Estado del servicio      |
| `GET`  | `/usuarios`  | Lista de usuarios        |
| `POST` | `/usuarios`  | Crear usuario            |
| `GET`  | `/tarjetas`  | Lista de tarjetas        |
| `POST` | `/tarjetas`  | Asociar UID a usuario    |
| `POST` | `/acceso`    | Registrar entrada/salida |
| `GET`  | `/registros` | Historial de accesos     |
| `GET`  | `/salones`   | Lista de salones         |
| `POST` | `/salones`   | Crear salón             |
| `GET`  | `/web`       | Interfaz web             |

### Ejemplos con curl

```bash
# Registrar acceso con un UID
curl -X POST http://localhost:5000/acceso \
  -H 'Content-Type: application/json' \
  -d '{"uid": "B9175303"}'

# Ver últimos 20 registros
curl 'http://localhost:5000/registros?limit=20'

# Crear un usuario
curl -X POST http://localhost:5000/usuarios \
  -H 'Content-Type: application/json' \
  -d '{
    "nombre": "Ana",
    "apellido_paterno": "García",
    "apellido_materno": "López",
    "matricula": "A2024999"
  }'

# Asociar una tarjeta a un usuario
curl -X POST http://localhost:5000/tarjetas \
  -H 'Content-Type: application/json' \
  -d '{"uid": "ABCD1234", "id_usuario": 2}'
```

---

## Esquema de base de datos

```
usuarios          → datos personales (nombre, matrícula)
tarjetas_nfc      → UIDs asociados a usuarios
salones           → ubicaciones donde hay lectores
registros_acceso  → historial de entradas/salidas
```

Relaciones:

* Un usuario puede tener varias tarjetas
* Una tarjeta pertenece a un solo usuario
* Cada registro vincula usuario + tarjeta + salón + tipo de evento (ENTRADA / SALIDA)

El esquema completo está en `src/Schema/Schema.sql`.

---

## Solución de problemas

### El lector no se detecta

```bash
lsusb | grep ACR
```

Si no aparece, revisa el cable USB y prueba otro puerto.

Si aparece pero `pcsc_scan` no lo ve, libera los módulos del kernel:

```bash
sudo rmmod pn533_usb pn533 nfc
sudo systemctl restart pcscd
```

### Error: `Unable to claim USB interface (Device or resource busy)`

El driver del kernel ocupa el lector. Aplica el blacklist permanente de la sección [Configuración del lector NFC](https://claude.ai/chat/0de1e54d-0f41-4a3e-ac66-2ce0f64df579#configuraci%C3%B3n-del-lector-nfc).

### Error: `'cryptography' package is required for caching_sha2_password`

```bash
pip install cryptography
```

### Error: `port is already allocated` al levantar Docker

Otro MySQL está corriendo. Detenlo o cambia el puerto en `docker-compose.yml`:

```yaml
ports:
  - "3307:3306"   # En vez de 3306:3306
```

### El front dice "API no disponible"

1. Verifica que `python3 app.py` esté corriendo
2. Abre `http://localhost:5000/web` (no abras el HTML como archivo)
3. En `index.html`, asegúrate que `const API = '';` (string vacío)

### pyscard no compila al instalar

Faltan los headers de desarrollo:

```bash
sudo apt install libpcsclite-dev swig build-essential python3-dev
pip install pyscard
```

### Datos persistentes en Docker

Los datos se guardan en el volumen `mysql_data`. Para borrar todo y empezar de cero:

```bash
docker compose down -v
docker compose up -d
```

---

## Comandos útiles

```bash
# Detener Docker (los datos se conservan)
docker compose stop

# Reiniciar Docker
docker compose start

# Ver logs en vivo
docker compose logs -f

# Backup de la BD
docker exec nfc_mysql mysqldump -uroot -ptu_password \
  asistencia_automation > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i nfc_mysql mysql -uroot -ptu_password \
  asistencia_automation < backup.sql

# Entrar al MySQL del contenedor
docker exec -it nfc_mysql mysql -uroot -ptu_password asistencia_automation
```

---

## Autores

Proyecto de investigación

* David León Salas
* Issac Benitez
