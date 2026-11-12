from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "clave-demo-cambiar-en-produccion"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "habi.db"


def conectar():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def crear_tablas():
    with conectar() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                saldo INTEGER NOT NULL DEFAULT 0 CHECK (saldo >= 0)
            );

            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                valor INTEGER NOT NULL,
                fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
            );

            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pagador_id INTEGER NOT NULL,
                concepto TEXT NOT NULL,
                total INTEGER NOT NULL CHECK (total > 0),
                fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pagador_id) REFERENCES cuentas(id)
            );

            CREATE TABLE IF NOT EXISTS participantes_gasto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gasto_id INTEGER NOT NULL,
                cuenta_id INTEGER NOT NULL,
                parte INTEGER NOT NULL CHECK (parte >= 0),
                estado TEXT NOT NULL,
                FOREIGN KEY (gasto_id) REFERENCES gastos(id),
                FOREIGN KEY (cuenta_id) REFERENCES cuentas(id),
                UNIQUE (gasto_id, cuenta_id)
            );
        """)


def registrar_movimiento(db, cuenta_id, tipo, descripcion, valor):
    db.execute(
        """INSERT INTO movimientos (cuenta_id, tipo, descripcion, valor)
           VALUES (?, ?, ?, ?)""",
        (cuenta_id, tipo, descripcion, valor)
    )


@app.route("/")
def inicio():
    with conectar() as db:
        cuentas = db.execute("SELECT * FROM cuentas ORDER BY nombre").fetchall()
        movimientos = db.execute("""
            SELECT movimientos.*, cuentas.nombre AS nombre_cuenta
            FROM movimientos
            JOIN cuentas ON cuentas.id = movimientos.cuenta_id
            ORDER BY movimientos.id DESC
            LIMIT 20
        """).fetchall()
        gastos = db.execute("""
            SELECT gastos.*, cuentas.nombre AS pagador
            FROM gastos
            JOIN cuentas ON cuentas.id = gastos.pagador_id
            ORDER BY gastos.id DESC
        """).fetchall()

        deudas = db.execute("""
            SELECT participantes_gasto.*, gastos.concepto, gastos.pagador_id,
                   cuentas.nombre AS deudor, pagadores.nombre AS nombre_pagador
            FROM participantes_gasto
            JOIN gastos ON gastos.id = participantes_gasto.gasto_id
            JOIN cuentas ON cuentas.id = participantes_gasto.cuenta_id
            JOIN cuentas AS pagadores ON pagadores.id = gastos.pagador_id
            WHERE participantes_gasto.estado = 'Pendiente'
            ORDER BY participantes_gasto.id DESC
        """).fetchall()

    return render_template(
        "index.html", cuentas=cuentas, movimientos=movimientos,
        gastos=gastos, deudas=deudas
    )


@app.post("/crear-cuenta")
def crear_cuenta():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("Escribe el nombre de la persona.")
        return redirect(url_for("inicio"))

    try:
        with conectar() as db:
            db.execute("INSERT INTO cuentas (nombre) VALUES (?)", (nombre,))
        flash("La cuenta fue creada con saldo inicial de $0.")
    except sqlite3.IntegrityError:
        flash("Ya existe una cuenta con ese nombre.")
    return redirect(url_for("inicio"))


@app.post("/recargar")
def recargar():
    try:
        cuenta_id = int(request.form.get("cuenta_id", ""))
        valor = int(request.form.get("valor", ""))
    except ValueError:
        flash("Selecciona una cuenta e ingresa un valor válido.")
        return redirect(url_for("inicio"))

    if valor <= 0:
        flash("La recarga debe ser mayor que cero.")
        return redirect(url_for("inicio"))

    with conectar() as db:
        cuenta = db.execute("SELECT id FROM cuentas WHERE id = ?", (cuenta_id,)).fetchone()
        if cuenta is None:
            flash("La cuenta seleccionada no existe.")
            return redirect(url_for("inicio"))

        db.execute("UPDATE cuentas SET saldo = saldo + ? WHERE id = ?", (valor, cuenta_id))
        registrar_movimiento(db, cuenta_id, "Recarga", "Recarga de saldo", valor)

    flash("La recarga se realizó correctamente.")
    return redirect(url_for("inicio"))


@app.post("/transferir")
def transferir():
    try:
        origen_id = int(request.form.get("origen_id", ""))
        destino_id = int(request.form.get("destino_id", ""))
        valor = int(request.form.get("valor", ""))
    except ValueError:
        flash("Revisa las cuentas y el valor de la transferencia.")
        return redirect(url_for("inicio"))

    if origen_id == destino_id:
        flash("Debes elegir dos cuentas diferentes.")
        return redirect(url_for("inicio"))
    if valor <= 0:
        flash("La transferencia debe ser mayor que cero.")
        return redirect(url_for("inicio"))

    db = conectar()
    try:
        db.execute("BEGIN IMMEDIATE")
        origen = db.execute("SELECT * FROM cuentas WHERE id = ?", (origen_id,)).fetchone()
        destino = db.execute("SELECT * FROM cuentas WHERE id = ?", (destino_id,)).fetchone()

        if origen is None or destino is None:
            db.rollback()
            flash("Una de las cuentas no existe.")
            return redirect(url_for("inicio"))
        if origen["saldo"] < valor:
            db.rollback()
            flash("Saldo insuficiente. No se hizo ningún cambio.")
            return redirect(url_for("inicio"))

        db.execute("UPDATE cuentas SET saldo = saldo - ? WHERE id = ?", (valor, origen_id))
        db.execute("UPDATE cuentas SET saldo = saldo + ? WHERE id = ?", (valor, destino_id))
        registrar_movimiento(db, origen_id, "Transferencia enviada",
                             "Transferencia a " + destino["nombre"], -valor)
        registrar_movimiento(db, destino_id, "Transferencia recibida",
                             "Transferencia de " + origen["nombre"], valor)
        db.commit()
        flash("La transferencia se realizó correctamente.")
    except Exception:
        db.rollback()
        flash("No se pudo realizar la transferencia. No se guardaron cambios.")
    finally:
        db.close()

    return redirect(url_for("inicio"))


@app.post("/crear-gasto")
def crear_gasto():
    concepto = request.form.get("concepto", "").strip()
    try:
        pagador_id = int(request.form.get("pagador_id", ""))
        total = int(request.form.get("total", ""))
        participantes_ids = [int(x) for x in request.form.getlist("participantes")]
    except ValueError:
        flash("Revisa los datos del gasto.")
        return redirect(url_for("inicio"))

    if not concepto or total <= 0:
        flash("Escribe un concepto y un total mayor que cero.")
        return redirect(url_for("inicio"))

    # El pagador se incluye automáticamente porque también participó.
    participantes_ids = list(dict.fromkeys([pagador_id] + participantes_ids))
    if len(participantes_ids) < 2:
        flash("Agrega al menos otra persona para dividir el gasto.")
        return redirect(url_for("inicio"))

    db = conectar()
    try:
        db.execute("BEGIN IMMEDIATE")
        cuentas_encontradas = db.execute(
            "SELECT id FROM cuentas WHERE id IN ({})".format(
                ",".join("?" for _ in participantes_ids)
            ), participantes_ids
        ).fetchall()

        if len(cuentas_encontradas) != len(participantes_ids):
            db.rollback()
            flash("Una de las cuentas seleccionadas no existe.")
            return redirect(url_for("inicio"))

        # Se divide en pesos enteros. El pagador asume el sobrante.
        parte_base = total // len(participantes_ids)
        sobrante = total % len(participantes_ids)

        cursor = db.execute(
            "INSERT INTO gastos (pagador_id, concepto, total) VALUES (?, ?, ?)",
            (pagador_id, concepto, total)
        )
        gasto_id = cursor.lastrowid

        for cuenta_id in participantes_ids:
            parte = parte_base + sobrante if cuenta_id == pagador_id else parte_base
            estado = "Pagado" if cuenta_id == pagador_id else "Pendiente"
            db.execute("""
                INSERT INTO participantes_gasto
                    (gasto_id, cuenta_id, parte, estado)
                VALUES (?, ?, ?, ?)
            """, (gasto_id, cuenta_id, parte, estado))

        # No se descuenta el total al pagador: el gasto ya fue pagado por fuera.
        db.commit()
        flash("Gasto dividido. Las demás personas ya pueden pagar su parte.")
    except Exception:
        db.rollback()
        flash("No se pudo registrar el gasto. No se guardaron cambios.")
    finally:
        db.close()

    return redirect(url_for("inicio"))


@app.post("/pagar-parte")
def pagar_parte():
    try:
        participante_id = int(request.form.get("participante_id", ""))
    except ValueError:
        flash("No se pudo identificar la deuda.")
        return redirect(url_for("inicio"))

    db = conectar()
    try:
        db.execute("BEGIN IMMEDIATE")
        deuda = db.execute("""
            SELECT participantes_gasto.*, gastos.pagador_id, gastos.concepto,
                   cuentas.nombre AS nombre_deudor,
                   pagadores.nombre AS nombre_pagador
            FROM participantes_gasto
            JOIN gastos ON gastos.id = participantes_gasto.gasto_id
            JOIN cuentas ON cuentas.id = participantes_gasto.cuenta_id
            JOIN cuentas AS pagadores ON pagadores.id = gastos.pagador_id
            WHERE participantes_gasto.id = ?
        """, (participante_id,)).fetchone()

        if deuda is None or deuda["estado"] != "Pendiente":
            db.rollback()
            flash("Esta deuda ya fue pagada o no existe.")
            return redirect(url_for("inicio"))

        deudor_id = deuda["cuenta_id"]
        pagador_id = deuda["pagador_id"]
        valor = deuda["parte"]

        if deudor_id == pagador_id:
            db.rollback()
            flash("El pagador ya tiene su parte marcada como pagada.")
            return redirect(url_for("inicio"))

        deudor = db.execute("SELECT * FROM cuentas WHERE id = ?", (deudor_id,)).fetchone()
        pagador = db.execute("SELECT * FROM cuentas WHERE id = ?", (pagador_id,)).fetchone()

        if deudor["saldo"] < valor:
            db.rollback()
            flash("La persona no tiene saldo suficiente. No se hizo ningún cambio.")
            return redirect(url_for("inicio"))

        db.execute("UPDATE cuentas SET saldo = saldo - ? WHERE id = ?", (valor, deudor_id))
        db.execute("UPDATE cuentas SET saldo = saldo + ? WHERE id = ?", (valor, pagador_id))
        db.execute(
            "UPDATE participantes_gasto SET estado = 'Pagado' WHERE id = ?",
            (participante_id,)
        )
        registrar_movimiento(db, deudor_id, "Pago de gasto compartido",
                             "Pago de: " + deuda["concepto"], -valor)
        registrar_movimiento(db, pagador_id, "Pago recibido de gasto compartido",
                             "Pago de " + deuda["nombre_deudor"] + ": " + deuda["concepto"], valor)
        db.commit()
        flash("La parte del gasto fue pagada correctamente.")
    except Exception:
        db.rollback()
        flash("No se pudo completar el pago. No se guardaron cambios.")
    finally:
        db.close()

    return redirect(url_for("inicio"))


@app.route("/historial/<int:cuenta_id>")
def historial(cuenta_id):
    with conectar() as db:
        cuenta = db.execute("SELECT * FROM cuentas WHERE id = ?", (cuenta_id,)).fetchone()
        if cuenta is None:
            flash("La cuenta no existe.")
            return redirect(url_for("inicio"))
        movimientos = db.execute("""
            SELECT * FROM movimientos
            WHERE cuenta_id = ?
            ORDER BY id DESC
        """, (cuenta_id,)).fetchall()
    return render_template("historial.html", cuenta=cuenta, movimientos=movimientos)


if __name__ == "__main__":
    crear_tablas()
    app.run(debug=True)
