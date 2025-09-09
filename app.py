import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd

app = Flask(__name__)

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
    motorista = request.form["motorista"]
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO jornada (motorista, inicio) VALUES (%s, NOW())", (motorista,))
    conexao.commit()
    cursor.close()
    conexao.close()
    return redirect(url_for("index"))

@app.route("/encerrar", methods=["POST"])
def encerrar_jornada():
    motorista = request.form["motorista"]
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
    return redirect(url_for("index"))

@app.route("/registros")
def registros():
    conexao = get_connection()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jornada ORDER BY inicio DESC")
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template("registros.html", registros=dados)

@app.route("/exportar")
def exportar():
    conexao = get_connection()
    df = pd.read_sql("SELECT * FROM jornada", conexao)
    conexao.close()
    caminho = "jornadas.xlsx"
    df.to_excel(caminho, index=False)
    return send_file(caminho, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
