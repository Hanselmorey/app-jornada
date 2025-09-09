from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "secreto123"  # necessário para flash funcionar

# Configuração do MySQL usando variáveis de ambiente do Railway
db_config = {
    "host": os.environ.get("MYSQLHOST"),
    "user": os.environ.get("MYSQLUSER"),
    "password": os.environ.get("MYSQLPASSWORD"),
    "database": os.environ.get("MYSQLDATABASE"),
    "port": int(os.environ.get("MYSQLPORT", 3306))
}

def get_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/iniciar", methods=["POST"])
def iniciar_jornada():
    motorista = request.form.get("motorista")
    if not motorista:
        flash("Informe o nome do motorista!", "error")
        return redirect(url_for("index"))
    try:
        conexao = get_connection()           # <-- Aqui
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO jornada (motorista, inicio) VALUES (%s, NOW())", (motorista,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash(f"Jornada do motorista {motorista} iniciada com sucesso!", "success")
    except mysql.connector.Error as e:
        flash(f"Erro ao iniciar jornada: {str(e)}", "error")
    return redirect(url_for("index"))

@app.route("/encerrar", methods=["POST"])
def encerrar_jornada():
    motorista = request.form.get("motorista")
    if not motorista:
        flash("Informe o nome do motorista!", "error")
        return redirect(url_for("index"))
    try:
        conexao = get_connection()           # <-- Aqui
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE jornada
            SET fim = NOW()
            WHERE motorista = %s AND fim IS NULL
            ORDER BY inicio DESC
            LIMIT 1
        """, (motorista,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash(f"Jornada do motorista {motorista} encerrada com sucesso!", "success")
    except mysql.connector.Error as e:
        flash(f"Erro ao encerrar jornada: {str(e)}", "error")
    return redirect(url_for("index"))

@app.route("/registros")
def registros():
    try:
        conexao = get_connection()           # <-- Aqui
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM jornada ORDER BY inicio DESC")
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
    except mysql.connector.Error as e:
        flash(f"Erro ao buscar registros: {str(e)}", "error")
        dados = []
    return render_template("registros.html", registros=dados)

@app.route("/exportar")
def exportar():
    try:
        conexao = get_connection()           # <-- Aqui
        df = pd.read_sql("SELECT * FROM jornada", conexao)
        conexao.close()
        caminho = "jornadas.xlsx"
        df.to_excel(caminho, index=False)
        return send_file(caminho, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao exportar Excel: {str(e)}", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
