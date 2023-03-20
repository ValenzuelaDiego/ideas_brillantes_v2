# importar la función que devolverá una instancia de una conexión
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_bcrypt import Bcrypt 
from flask_app.models import usuario
bcrypt = Bcrypt(app)
BD='ideas_brillantes'

class Idea:
    def __init__( self , db_data ):
        self.id = db_data['id']
        self.comentario = db_data['comentario']
        self.usuario_id = db_data['usuario_id']
        self.created_at = db_data['created_at']
        self.updated_at = db_data['updated_at']
        self.usuarios_like = []

    @classmethod
    def save( cls , data ):
        query = "INSERT INTO ideas ( comentario , usuario_id, created_at , updated_at ) VALUES (%(comentario_d)s ,%(usuario_id_d)s,NOW(),NOW());"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod 
    def get_all(cls):
        query = "SELECT * FROM ideas;"
        # asegúrate de llamar a la función connectToMySQL con el esquema al que te diriges
        results = connectToMySQL(BD).query_db(query)
        # crear una lista vacía para agregar nuestras instancias de friends
        lista_ideas = []
        # Iterar sobre los resultados de la base de datos y crear instancias de friends con cls
        for idea_aux in results:
            lista_ideas.append( cls(idea_aux) )
        return lista_ideas
    
    @classmethod
    def get_by_id(cls, idea_id):
        data = {"id": idea_id}
        query = "SELECT * FROM ideas WHERE id = %(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod 
    def update(cls,data):
        query = "UPDATE ideas SET comentario=%(comentario_d)s ,updated_at=NOW() WHERE id = %(id_d)s;"
        return connectToMySQL(BD).query_db(query,data)

    @classmethod
    def destroy(cls,data):
        query  = "DELETE FROM ideas WHERE id = %(id_d)s;"
        return connectToMySQL(BD).query_db(query,data)
    
    @classmethod
    def get_usuarios_like_idea( cls , data ):
        query = "SELECT * FROM ideas LEFT JOIN likes ON likes.idea_id = ideas.id LEFT JOIN usuarios ON likes.usuario_id = usuarios.id WHERE ideas.id = %(id_d)s;"
        results = connectToMySQL(BD).query_db( query , data )
        # los resultados serán una lista de objetos topping (aderezo) con la hamburguesa adjunta a cada fila 
        idea = cls( results[0] )
        for row_from_db in results:
            # ahora parseamos los datos topping para crear instancias de aderezos y agregarlas a nuestra lista
            usuario_data = {
                "id" : row_from_db["usuarios.id"],
                "nombre" : row_from_db["nombre"],
                "alias" : row_from_db["alias"],
                "email" : row_from_db["email"],
                "contrasenha" : row_from_db["contrasenha"],
                "created_at" : row_from_db["usuarios.created_at"],
                "updated_at" : row_from_db["usuarios.updated_at"]
            }
            idea.usuarios_like.append( usuario.Usuario( usuario_data ) )
        return idea
    
    @classmethod
    def get_cantidad_likes(cls, idea_id):
        data = {"id": idea_id}
        query = "SELECT COUNT(*) FROM likes WHERE idea_id = %(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        return result[0]['COUNT(*)']
    
    @classmethod
    def get_duenho_idea(cls, idea_id):
        data = {"id": idea_id}
        query = "SELECT alias FROM usuarios LEFT JOIN ideas ON usuarios.id = ideas.usuario_id WHERE usuarios.id=%(id)s;"
        result = connectToMySQL(BD).query_db(query,data)
        return result[0]['alias']
    
    @classmethod
    def destroy_like(cls,data):
        query  = "DELETE FROM likes WHERE idea_id = %(id_d)s;"
        return connectToMySQL(BD).query_db(query,data)
    