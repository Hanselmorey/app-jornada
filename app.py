from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Configuração do banco MySQL do Railway
DB_CONFIG = {
    "host": "mysql.railway.internal",
    "user": "root",
    "password": "iseBLJSCirViXFJXsQwLZqWjYNVCHRRq",
    "database": "railway"
}

# Função para conectar
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Página principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome = request.form.get("nome")
        acao = request.form.get("acao")

        if not nome:
            flash("Digite seu nome!", "error")
            return redirect(url_for("index"))

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if acao == "iniciar":
            cursor.execute("SELECT * FROM jornada WHERE nome_motorista=%s AND status='Ativo'", (nome,))
            if cursor.fetchone():
                flash("Você já tem uma jornada ativa!", "error")
            else:
                cursor.execute(
                    "INSERT INTO jornada (nome_motorista, inicio_jornada, fim_jornada, status) VALUES (%s,%s,%s,%s)",
                    (nome, datetime.now(), None, "Ativo")
                )
                conn.commit()
                flash("Jornada iniciada!", "success")

        elif acao == "encerrar":
            cursor.execute("SELECT id FROM jornada WHERE nome_motorista=%s AND status='Ativo' ORDER BY id DESC", (nome,))
            row = cursor.fetchone()
            if not row:
                flash("Nenhuma jornada ativa encontrada!", "error")
            else:
                cursor.execute(
                    "UPDATE jornada SET fim_jornada=%s, status='Encerrado' WHERE id=%s",
                    (datetime.now(), row["id"])
                )
                conn.commit()
                flash("Jornada encerrada!", "success")

        cursor.close()
        conn.close()
        return redirect(url_for("index"))

    return render_template("index.html")

# Página de registros
@app.route("/registros")
def registros():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM jornada ORDER BY id DESC", conn)
    conn.close()
    registros = df.values.tolist()
    return render_template("registros.html", registros=registros)

# Exportar para Excel
@app.route("/exportar")
def exportar():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM jornada ORDER BY id DESC", conn)
    conn.close()
    excel_file = "jornada_export.xlsx"
    df.to_excel(excel_file, index=False)
    return send_file(excel_file, as_attachment=True)

# Ajuste para o Railway
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
