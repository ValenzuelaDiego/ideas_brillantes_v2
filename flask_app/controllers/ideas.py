from flask import Flask, render_template, redirect, request, session, flash
from flask_app.models.usuario import Usuario
from flask_app.models.idea import Idea
from flask_app import app

@app.route('/crear_idea', methods=['POST'])
def registrar_idea():
    data={
        "comentario_d":request.form["comentario_f"],
        "usuario_id_d": request.form["usuario_id_f"]
        }
    Idea.save(data)
    return redirect('/dashboard')

@app.route('/idea/<int:idea_id_f>')
def mostrar_idea(idea_id_f):
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        data={"id_d":idea_id_f}
        return render_template("4_ver_idea.html",idea=Idea.get_by_id(idea_id_f),personas=Idea.get_usuarios_like_idea(data).usuarios_like)

@app.route('/borrar_idea/<int:idea_id>')
def borrar_idea(idea_id):
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        data={"id_d":idea_id}
        Idea.destroy_like(data)
        Idea.destroy(data)
        return redirect('/dashboard')
