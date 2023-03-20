from flask import Flask, render_template, redirect, request, session, flash
from flask_app.models.usuario import Usuario
from flask_app.models.idea import Idea
from flask_app import app
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)    # estamos creando un objeto llamado bcrypt,
                        # que se realiza invocando la función Bcrypt con nuestra aplicación como argumento
@app.route('/')
def pag_login():
    return render_template("0_index.html")

@app.route('/registro')
def pag_registro():
    return render_template("1_registro.html")

@app.route('/crear_usuario', methods=['POST'])
def registrar_usuario():
    usuario_valido=Usuario.validate_usuario(request.form)
    if not usuario_valido:
        return redirect('/registro')
    data={
        "nombre_d":request.form["nombre_f"],
        "alias_d":request.form["alias_f"],
        "email_d": request.form["email_f"],
        "contrasenha_d": bcrypt.generate_password_hash(request.form['contrasenha_f'])
        }
    Usuario.save(data)
    usuario=Usuario.get_by_email(request.form["email_f"])
    session["usuario_id"] = usuario.id
    return redirect('/dashboard')

@app.route('/ingresar_usuario', methods=['POST'])
def ingresar_usuario():
    usuario_valido=Usuario.authenticated_user_by_input(request.form)
    if not usuario_valido:
        return redirect('/')
    session["usuario_id"] = usuario_valido.id
    return redirect('/dashboard')

@app.route('/cerrar_sesion',methods=['POST'])
def cerrar_sesion():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def pag_dashboard():
    if 'usuario_id' not in session:
        return redirect('/')
    usuario = Usuario.get_by_id(session['usuario_id'])
    data={"id_d":session['usuario_id']}
    return render_template("2_dashboard.html", usuario=usuario, usuarios=Usuario.get_all(), ideas=Idea.get_all(), personas=Usuario.get_all())

@app.route('/like/<int:usuario_id_f>/<int:idea_id_f>')
def dar_like(usuario_id_f,idea_id_f):
    if 'usuario_id' not in session:
        return redirect('/')
    data={
        "usuario_id_d":usuario_id_f,
        "idea_id_d":idea_id_f
    }
    Usuario.add_like(data)
    return redirect('/dashboard')

@app.route('/usuario/<int:usuario_id_f>')
def mostrar_usuario(usuario_id_f):
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        return render_template("3_ver_usuario.html",usuario=Usuario.get_by_id(usuario_id_f))
    
@app.route('/agregar_amigos')
def agregar_amigos():
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        usuario = Usuario.get_by_id(session['usuario_id'])
        return render_template("5_agregar_amigo.html",usuario=usuario,personas=Usuario.get_all())
    
@app.route('/agregar_amigo/<int:usuario_id_f>/<int:amigo_id_f>')
def insertar_amistad(usuario_id_f, amigo_id_f):
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        data={
            "usuario_id_d": usuario_id_f,
            "amigo_id_d":amigo_id_f
            }
        Usuario.add_amigo(data)
        return redirect('/agregar_amigos')
    
@app.route('/eliminar_amigo/<int:usuario_id_f>/<int:amigo_id_f>')
def eliminar_amistad(usuario_id_f, amigo_id_f):
    if 'usuario_id' not in session:
        return redirect('/')
    else:
        data={
            "usuario_id_d": usuario_id_f,
            "amigo_id_d":amigo_id_f
            }
        Usuario.eliminar_amigo(data)
        return redirect('/agregar_amigos')
    

