# importar la función que devolverá una instancia de una conexión
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_app.models import idea
from flask_bcrypt import Bcrypt 
bcrypt = Bcrypt(app)
BD='ideas_brillantes'

class Usuario:
    def __init__( self , db_data ):
        self.id = db_data['id']
        self.nombre = db_data['nombre']
        self.alias = db_data['alias']
        self.email=db_data['email']
        self.contrasenha = db_data['contrasenha']
        self.created_at = db_data['created_at']
        self.updated_at = db_data['updated_at']
        self.ideas=[]
        self.ideas_like=[]

    @classmethod
    def save( cls , data ):
        query = "INSERT INTO usuarios ( nombre , alias, email,contrasenha, created_at , updated_at ) VALUES (%(nombre_d)s, %(alias_d)s, %(email_d)s ,%(contrasenha_d)s,NOW(),NOW());"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod 
    def get_all(cls):
        query = "SELECT * FROM usuarios;"
        # asegúrate de llamar a la función connectToMySQL con el esquema al que te diriges
        results = connectToMySQL(BD).query_db(query)
        # crear una lista vacía para agregar nuestras instancias de friends
        lista_artistas = []
        # Iterar sobre los resultados de la base de datos y crear instancias de friends con cls
        for artista_aux in results:
            lista_artistas.append( cls(artista_aux) )
        return lista_artistas
    
    @classmethod
    def get_by_id(cls, user_id):
        data = {"id": user_id}
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_by_email(cls,email):
        data = {"email": email}
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        result = connectToMySQL(BD).query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod 
    def update(cls,data):
        query = "UPDATE usuarios SET nombre=%(nombre_d)s, alias=%(alias_d)s, email=%(email_d)s ,contrasenha=%(contrasenha_d)s, updated_at=NOW() WHERE id = %(id_d)s;"
        return connectToMySQL(BD).query_db(query,data)

    @classmethod
    def destroy(cls,data):
        query  = "DELETE FROM usuarios WHERE id = %(id_d)s;"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod
    def add_like(cls,data):
        query = "INSERT INTO likes (usuario_id,idea_id) VALUES (%(usuario_id_d)s,%(idea_id_d)s);"
        return connectToMySQL(BD).query_db(query,data)
    
    @staticmethod
    def validate_usuario(usuario):
        is_valid = True # asumimos que esto es true
        if len(usuario['nombre_f']) < 2:
            flash("El nombre tiene que tener al menos 2 letras.",'register')
            is_valid = False
        if len(usuario['alias_f']) < 2:
            flash("El alias tiene que tener al menos 2 letras.",'register')
            is_valid = False
        if len(usuario['contrasenha_f']) < 8:
            flash("La contrasenha debe de tener al menos 8 digitos",'register')
            is_valid = False
        if not usuario['contrasenha_f']==usuario['contrasenha_c_f']:
            flash("La confirmacion de contrasenha es incorrecta.",'register')
            is_valid = False
        email_already_has_account = Usuario.get_by_email(usuario["email_f"])
        if email_already_has_account:
            flash("Ya existe una cuenta con ese email",'register')
            is_valid = False
        return is_valid
    
    @classmethod
    # fetches an existing user after authenticating
    def authenticated_user_by_input(cls, user_input):
        valid = True
        existing_user = cls.get_by_email(user_input["email_f"])
        password_valid = True
        if not existing_user:
            valid = False   
            flash("Email no existente, registrese por favor!",'login')
        else:
            # Retrieve the hashed password to compare
            data = {
                "email": user_input["email_f"]
            }
            query = "SELECT contrasenha FROM usuarios WHERE email = %(email)s;"
            hashed_pw = connectToMySQL(BD).query_db(query,data)[0]["contrasenha"]
            password_valid = bcrypt.check_password_hash(hashed_pw, user_input['contrasenha_f'])
            if not password_valid:
                valid = False
                flash("Contrasenha invalida, intente de nuevo!",'login')
        if not valid:
            return False
        return existing_user
    
    @classmethod #metodo de la union uno a muchos
    def get_ideas_de_usuario( cls , data ):
        query = "SELECT * FROM usuarios LEFT JOIN ideas ON ideas.usuario_id = usuarios.id WHERE usuarios.id = %(id_d)s;"
        results = connectToMySQL(BD).query_db( query , data )
        # los resultados serán una lista de objetos topping (aderezo) con la hamburguesa adjunta a cada fila 
        usuario = cls( results[0] )
        for row_from_db in results:
            # ahora parseamos los datos de hamburguesa para crear instancias de hamburguesa y agregarlas a nuestra lista
            idea_data = {
                "id" : row_from_db["ideas.id"],
                "comentario" : row_from_db["comentario"],
                "usuario_id":row_from_db["usuario_id"],
                "created_at" : row_from_db["pinturas.created_at"],
                "updated_at" : row_from_db["pinturas.updated_at"]
            }
            usuario.ideas.append( idea.Idea( idea_data ) )
        return usuario

    @classmethod #metodo de la union muchos a muchos
    def get_likes_ideas_de_usuario( cls , data ):
        query = "SELECT * FROM usuarios LEFT JOIN likes ON likes.usuario_id = usuarios.id LEFT JOIN ideas ON likes.idea_id = ideas.id WHERE usuarios.id = %(id_d)s;"
        results = connectToMySQL(BD).query_db( query , data )
        # los resultados serán una lista de objetos topping (aderezo) con la hamburguesa adjunta a cada fila    
        usuario = cls( results[0] )
        for row_from_db in results:
            # ahora parseamos los datos topping para crear instancias de aderezos y agregarlas a nuestra lista
            idea_data = {
                "id" : row_from_db["ideas.id"],
                "comentario" : row_from_db["comentario"],
                "usuario_id":row_from_db["usuario_id"],
                "created_at" : row_from_db["ideas.created_at"],
                "updated_at" : row_from_db["ideas.updated_at"]
            }
            usuario.ideas_like.append( idea.Idea( idea_data ) )
        return usuario
    
    @classmethod
    def get_cantidad_posteos(cls, usuario_id):
        data = {"id": usuario_id}
        query = "SELECT COUNT(*) FROM ideas WHERE usuario_id = %(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        return result[0]['COUNT(*)']
    
    @classmethod
    def get_cantidad_likes(cls, usuario_id):
        data = {"id": usuario_id}
        query = "SELECT COUNT(*) FROM likes WHERE usuario_id = %(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        return result[0]['COUNT(*)']
    
    @classmethod
    def add_amigo(cls,data):
        query = "INSERT INTO amigos (usuario_id, amigo_id) VALUES (%(usuario_id_d)s,%(amigo_id_d)s);"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod
    def eliminar_amigo(cls,data):
        query = "DELETE FROM amigos WHERE usuario_id = %(usuario_id_d)s AND amigo_id = %(amigo_id_d)s;"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod
    def es_amigo(cls,usuario_id,amigo_id):
        data={
            "usuario_id_d": usuario_id,
            "amigo_id_d":amigo_id
            }
        query = "SELECT * FROM amigos WHERE usuario_id = %(usuario_id_d)s AND amigo_id = %(amigo_id_d)s;"
        results = connectToMySQL(BD).query_db(query,data)
        if not results:
            return False
        else:
            return True
    

