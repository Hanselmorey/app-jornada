from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
import pandas as pd

app = Flask(__name__)
app.secret_key = "secreto123"

# Configuração do MySQL PythonAnywhere
db_config = {
    "host": "yourusername.mysql.pythonanywhere-services.com",
    "user": "yourusername",
    "password": "SUA_SENHA",
    "database": "jornada",
    "port": 3306
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
        flash("Informe o motorista!", "error")
        return redirect(url_for("index"))
    try:
        conexao = get_connection()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO jornada (motorista, inicio) VALUES (%s, NOW())", (motorista,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash(f"Jornada iniciada para {motorista}", "success")
    except mysql.connector.Error as e:
        flash(f"Erro: {str(e)}", "error")
    return redirect(url_for("index"))

@app.route("/encerrar", methods=["POST"])
def encerrar_jornada():
    motorista = request.form.get("motorista")
    if not motorista:
        flash("Informe o motorista!", "error")
        return redirect(url_for("index"))
    try:
        conexao = get_connection()
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
        flash(f"Jornada encerrada para {motorista}", "success")
    except mysql.connector.Error as e:
        flash(f"Erro: {str(e)}", "error")
    return redirect(url_for("index"))

@app.route("/registros")
def registros():
    try:
        conexao = get_connection()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM jornada ORDER BY inicio DESC")
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
    except mysql.connector.Error as e:
        flash(f"Erro: {str(e)}", "error")
        dados = []
    return render_template("registros.html", registros=dados)

@app.route("/exportar")
def exportar():
    try:
        conexao = get_connection()
        df = pd.read_sql("SELECT * FROM jornada", conexao)
        conexao.close()
        caminho = "jornadas.xlsx"
        df.to_excel(caminho, index=False)
        return send_file(caminho, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao exportar: {str(e)}", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
