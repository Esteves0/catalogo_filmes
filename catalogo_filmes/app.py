import json

from flask import Flask, request, jsonify, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import get_connection
import uuid


import os
from werkzeug.utils import secure_filename

app = Flask(__name__)



# Pasta onde as fotos vão morar (crie essa pasta no seu projeto!)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Teste API
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de catalogo de filmes"}), 200

# Ping
@app.route('/ping', methods=['GET'])
def ping():
    conn = get_connection()
    conn.close()
    return jsonify({"message": "pong! API Rodando!", "db": str(conn)}), 200


# Listar todos os filmes
@app.route('/filmes', methods=['GET'])
def listar_filmes():
    sql = "SELECT * FROM filmes"
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        filmes = cursor.fetchall()
        print('filmes: --------------------------', filmes)
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao listar filmes"}), 500

@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    sql = "INSERT INTO filmes (titulo, genero, ano, file_capa) VALUES (%s, %s, %s, %s)"
    try:
        if request.method == "POST":
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]
            file_capa = request.files['file_capa']

            if file_capa and file_capa.filename != '':
                filename = secure_filename(file_capa.filename)
                extensao = os.path.splitext(file_capa.filename)[1]

                novo_nome = uuid.uuid4().hex + extensao
                file_capa.save(os.path.join(app.config['UPLOAD_FOLDER'],novo_nome))

                img_capa = novo_nome
            else:
                img_capa = "default.png"

            params = [titulo, genero, ano, img_capa]

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        return render_template("novo_filme.html")
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao cadastrar filme"}), 500


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_filme(id):
    try:
        conn = get_connection()
        if request.method == "POST":
            titulo = request.form["titulo"]
            genero = request.form["genero"]
            ano = request.form["ano"]
            url_capa = request.form["url_capa"]

            sql_update = "UPDATE filmes SET titulo = %s, genero = %s, ano = %s, url_capa = %s WHERE id = %s"
            params = [titulo, genero, ano, url_capa, id]

            cursor = conn.cursor()
            cursor.execute(sql_update, params)
            conn.commit()
            conn.close()
            return redirect(url_for("listar_filmes"))

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql = "SELECT * FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        filme = cursor.fetchone()
        conn.close()

        if filme is None:
            return redirect(url_for("listar_filmes"))
        return render_template("editar_filme.html", filme=filme)
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao editar filme"}), 500


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM filmes WHERE id = %s"
        params = [id]
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print('erro: ', str(ex))
        return jsonify({"message": "erro ao deletar filme"}), 500


if __name__ == '__main__':
    app.run(debug=True)