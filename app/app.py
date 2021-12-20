#./app/app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from funciones import *
import time
import sys
import re
from pickleshare import *
import pymongo
from pymongo import MongoClient
from array import array
from bson import ObjectId
from flask_restful import reqparse, abort, Api, Resource
import json
from flask_cors import CORS, cross_origin

#Creamos la variable pagina, que primero tendra 3 paginas vacias
paginas = ['','','']
app = Flask(__name__)
app.secret_key = 'esto-es-una-clave-muy-secreta'
client = MongoClient("mongo", 27017)
db = client.SampleCollections
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#------------------------- API FLASK-RESTFULL----------------#

parser = reqparse.RequestParser()
parser.add_argument('nombre')
parser.add_argument('altura')
parser.add_argument('peso')
parser.add_argument('tipo')
parser.add_argument('debilidad')


# Función para cuando el id indicado no existe
def abort_if_todo_doesnt_exist(id):
    if not db.samples_pokemon.find_one({'_id':ObjectId(id)}):
        abort(404, message="Pokemon {} doesn't exist".format(id))


# Metodo GET: devolver todos los Pokemons
# curl http://localhost:5000/apirest
# Método POST: inserta registro si se meten todos los datos
# curl -X POST -d 'nombre=PokeNuevoApi' -d 'tipo=Water' -d 'altura=2.4' -d 'peso=5.5' -d 'debilidad=Electric' http://localhost:5000/apirest
class apirestTodos(Resource):
    def get(self):
        lista = []
        pokemons = db.samples_pokemon.find()
        for pokemon in pokemons:
            lista.append({
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')
                })
        return lista

    def post(self):
        #Recogemos los argumetnos
        args = parser.parse_args()
        tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
        try:
            # Si el tipo o la debilidad no esta disponible => error de tipos
            if args['tipo'] in tipos and args['debilidad'] in tipos :
                db.samples_pokemon.insert({
                    'name': args['nombre'],
                    'height': args['altura'],
                    'weight': args['peso'],
                    'type': args['tipo'],
                    'weaknesses': args['debilidad'],
                    'img': 'https://images-na.ssl-images-amazon.com/images/I/619FF-ONnuL._AC_SL1100_.jpg'
                })
                #Tras insertar, obtenemos el último documento y lo devolvemos
                pok = db.samples_pokemon.find({}).sort('_id',pymongo.DESCENDING).limit(1)
                pokemon = pok[0]
                return {
                      'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                      'name': pokemon.get('name'),
                      'tipo':  pokemon.get('type'),
                      'altura':  pokemon.get('height'),
                      'peso':  pokemon.get('weight'),
                      'debilidad':  pokemon.get('weaknesses')
                }
            else:
                e = "Tipo o debilidad no conocida. Tipos disponibles: Water,Fire,Normal,Flying,Poison,Fighting,Psychic,Grass,Bug,Electric,Ground,Rock,Ice,Ghost,Dragon "
                return e
        except:
            e = 'Falta o error en los argumentos. '
            e+="Debe pasar como argumentos obligartorios 'nombre', 'altura', 'peso', 'tipo' y 'debilidad'"
            return e

# Este método es para encontrar un pokemon por su nombre, así se podrá obtener el id para modificar o borrar un pokemon
# Metodo GET: devolver pokemon con ese nombre
# curl http://localhost:5000/apirest/nombre/Krabby
class apirestNombre(Resource):
    def get(self, nombre):
        try:
            pokemon = db.samples_pokemon.find_one({'name':nombre})
            return {
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')
            }
        except:
          return {'error':'Not found'}

# Metodo GET: devolver pokemon con ese id
# curl http://localhost:5000/apirest/58f56171ee9d4bd5e610d6a5
# Método PUT  => Actualiza en pokemon del id indicado con las datos nuevos. Si no se indica un dato se deja el que estaba
# curl -X PUT -d 'altura=0.42' http://localhost:5000/apirest/58f56171ee9d4bd5e610d6a5
# Método DELETE: borra el pokemon con el id indicado
# curl -X DELETE http://localhost:5000/apirest/58f56171ee9d4bd5e610d6a5

class apirest(Resource):
    def get(self, id):
        abort_if_todo_doesnt_exist(id)
        try:
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            return {
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')
            }
        except:
          return {'error':'Not found'}

    def delete(self, id):
        abort_if_todo_doesnt_exist(id)
        try:
            db.samples_pokemon.remove({'_id': ObjectId(id) })
            c = "Eliminado el registro: "
            c += str(id)
            return {'resultado':c}
        except:
          return jsonify({'error':'Not found'}), 404

    def put(self, id):
        args = parser.parse_args()
        abort_if_todo_doesnt_exist(id)
        tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
        try:
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            #Guardamos los valores antiguos del pokemon
            nombre = pokemon.get('name'),
            tipo =  pokemon.get('type'),
            altura =  pokemon.get('height'),
            peso =  pokemon.get('weight'),
            debilidad =   pokemon.get('weaknesses')

            # Si se ha actualizado algun valor, guardar para actualizar
            # Si el tipo o la debilidad no son validas, no los actualiza
            if(args['nombre']):
                nombre = args['nombre']
            if(args['tipo']):
                if(args['tipo'] in tipos):
                    tipo= args['tipo']
            if(args['altura']):
                altura = args['altura']
            if(args['peso']):
                peso = args['peso']
            if(args['debilidad']):
                if(args['debilidad'] in tipos):
                    debilidad = args['debilidad']

            db.samples_pokemon.update(
                    {'_id': ObjectId(id)},
                    {'name': nombre,
                    'img': pokemon.get('img'),
                    'height': altura,
                    'weight': peso,
                    'type': tipo,
                    'weaknesses': debilidad,
                    'img': pokemon.get('img')
                    })
            #Recuperamos los nuevos datos del pokemon
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            return {
                  'id':    str(id), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')}
        except:
            return {'error':'Not found'}, 404


#Añadimos las clases con sus path
api.add_resource(apirestTodos, '/apirest')
api.add_resource(apirestNombre, '/apirest/nombre/<nombre>')
api.add_resource(apirest, '/apirest/<id>')




#--------------------------------- API -----------------------------------------#

# Metodo GET: devolver todos los Pokemons
# curl -O  http://localhost:5000/api/pokemons
# Método GET con argumento tipo => Devuelve pokemons de ese tipo
# curl -O  http://localhost:5000/api/pokemons?tipo=Water
# Método POST: inserta registro si se meten todos los datos
# curl -X POST -d 'nombre=PokeNuevo' -d 'tipo=Water' -d 'altura=2.4' -d 'peso=5.5' -d 'debilidad=Electric' http://localhost:5000/api/pokemons
@app.route('/api/pokemons', methods=['GET', 'POST'])
@cross_origin()
def api_1():
    tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
    if request.method == 'GET':
        lista = []
        #Si han introducido tipo (y ademas tipo disponible), buscar solo tipo
        if(request.args.get('tipo') ):
            if(request.args.get('tipo') in tipos ):
                pokemons = db.samples_pokemon.find({'type': request.args.get('tipo') })
            else:
                return jsonify('Tipo de pokemon no admitido')
        else:
            pokemons = db.samples_pokemon.find()

        for pokemon in pokemons:
            lista.append({
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses'),
                  'img': pokemon.get('img')
                })
        return jsonify(lista)

    elif(request.method == 'POST'):
        #Si no se insertan todos los datos => error
        try:
            # Si el tipo o la debilidad no esta disponible => error de tipos
            if request.form['tipo'] in tipos and request.form['debilidad'] in tipos :
                db.samples_pokemon.insert({
                    'name': request.form['nombre'],
                    'height': request.form['altura'],
                    'weight': request.form['peso'],
                    'type': request.form['tipo'],
                    'weaknesses': request.form['debilidad'],
                    'img': 'https://images-na.ssl-images-amazon.com/images/I/619FF-ONnuL._AC_SL1100_.jpg'
                })
                #Tras insertar, obtenemos el último documento y lo devolvemos
                pok = db.samples_pokemon.find({}).sort('_id',pymongo.DESCENDING).limit(1)
                pokemon = pok[0]
                return jsonify({
                      'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                      'name': pokemon.get('name'),
                      'tipo':  pokemon.get('type'),
                      'altura':  pokemon.get('height'),
                      'peso':  pokemon.get('weight'),
                      'debilidad':  pokemon.get('weaknesses')
                })
            else:
                e = "Tipo o debilidad no conocida. Tipos disponibles: Water,Fire,Normal,Flying,Poison,Fighting,Psychic,Grass,Bug,Electric,Ground,Rock,Ice,Ghost,Dragon "
                return jsonify({'error':e})
        except:
            e = 'Falta o error en los argumentos. '
            e+="Debe pasar como argumentos obligartorios 'nombre', 'altura', 'peso', 'tipo' y 'debilidad'"
            return jsonify({'error':e})


# Este método es para encontrar un pokemon por su nombre, así se podrá obtener el id para modificar o borrar un pokemon
# Metodo GET: devolver pokemon con ese nombre
# curl -O  http://localhost:5000/api/pokemons/nombre/Seaking

@app.route('/api/pokemons/nombre/<nombre>', methods=['GET', 'PUT', 'DELETE'])
def api_2(nombre):
    if request.method == 'GET':
        try:
            pokemon = db.samples_pokemon.find_one({'name':nombre})
            return jsonify({
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')
            })
        except:
          return jsonify({'error':'Not found'}), 404


# Metodo GET: devolver pokemon con ese id
# curl http://localhost:5000/api/pokemons/58f56171ee9d4bd5e610d6ba
# Método PUT  => Actualiza en pokemon del id indicado con las datos nuevos. Si no se indica un dato se deja el que estaba
# curl -X PUT -d 'altura=1.31' http://localhost:5000/api/pokemons/58f56171ee9d4bd5e610d6ba
# Método DELETE: borra el pokemon con el id indicado
# curl -X DELETE http://localhost:5000/api/pokemons/58f56171ee9d4bd5e610d6ba
@app.route('/api/pokemons/<id>', methods=['GET', 'PUT', 'DELETE'])
def api_3(id):

    if request.method == 'GET':
        try:
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            return jsonify({
                  'id':    str(pokemon.get('_id')), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses'),
                  'img': pokemon.get('img')
            })
        except:
          return jsonify({'error':'Not found'}), 404

    elif request.method == 'PUT':
        tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
        try:
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            #Guardamos los valores antiguos del pokemon
            nombre = pokemon.get('name'),
            tipo =  pokemon.get('type'),
            altura =  pokemon.get('height'),
            peso =  pokemon.get('weight'),
            debilidad =   pokemon.get('weaknesses')

            #Si se ha actualizado algun valor, guardar para actualizar
            if(request.form.get('nombre')):
                nombre = request.form['nombre']
            if(request.form.get('tipo') ):
                if(request.form['tipo'] in tipos):
                    tipo= request.form['tipo']
            if(request.form.get('altura')):
                altura = request.form['altura']
            if(request.form.get('peso')):
                peso = request.form['peso']
            if(request.form.get('debilidad')):
                if(request.form['debilidad'] in tipos):
                    debilidad = request.form['debilidad']

            db.samples_pokemon.update(
                    {'_id': ObjectId(id)},
                    {'name': nombre,
                    'img': pokemon.get('img'),
                    'height': altura,
                    'weight': peso,
                    'type': tipo,
                    'weaknesses': debilidad,
                    'img': pokemon.get('img')
                    })
            #Recuperamos los nuevos datos del pokemon
            pokemon = db.samples_pokemon.find_one({'_id':ObjectId(id)})
            return jsonify({
                  'id':    str(id), # pasa a string el ObjectId
                  'name': pokemon.get('name'),
                  'tipo':  pokemon.get('type'),
                  'altura':  pokemon.get('height'),
                  'peso':  pokemon.get('weight'),
                  'debilidad':  pokemon.get('weaknesses')
            })
        except:
            return jsonify({'error':'Not found'}), 404

    elif request.method == 'DELETE':
        try:
            db.samples_pokemon.remove({'_id': ObjectId(id) })
            c = "Eliminado el registro: "
            c += str(id)
            return jsonify({'resultado':c})
        except:
          return jsonify({'error':'Not found'}), 404


#Pagina inicial
@app.route('/')
@app.route('/static')
def index():
    #Si hay usuario logueado, pasar el usuario
    username = None
    if 'username' in session:
        username = session['username']
    return render_template('index.html', user= username, paginas = paginas)


#Pagina de login
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    username = None
    #Si se ha logueado, comprobar usuario. Si hay usuario, comprobar contraseña.
    #Si algo falla, mostrar error. Si no, establecer sesión y mandar a pag principal
    if (request.method == 'POST'):
        db = PickleShareDB('miBD')
        usuario_buscar = request.form['username'] in  db
        if usuario_buscar:
            usuario = db[request.form['username']]
            if (usuario['Pass'] == request.form['password']):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            else:
                error = 'Contraseña incorrecta'
        else:
            error = 'Usuario incorrecto'

    return render_template('login.html',error = error, paginas = paginas)


#Función para el logout
@app.route('/logout', methods=['GET','POST'])
def logout():
    #Si se desloguea, quitar usuario de la sesión y mandar a pag principal
    if request.method == 'POST':
        session.pop('username', None)
    return redirect(url_for('index'))


#Página de registro
@app.route('/registro',methods=['GET','POST'])
def registro():
    #Si hay rellenado el registro, guardarlo
    if (request.method == 'POST'):
        db = PickleShareDB('miBD')
        db[request.form['username']] = {'User': request.form['username'],
                                        'Pass': request.form['password'],
                                        'Nombre': request.form['nombre'],
                                        'Apellidos': request.form['apellidos'],
                                        'Email': request.form['email'],
                                        'Direccion': request.form['direccion']}
        #Una vez guardado, establecemos esa sesión y vamos a página principal
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('registro.html',paginas = paginas)


#Página del perfil
@app.route('/perfil', methods=['GET','POST'])
def perfil():
    #Obtenemos los datos del perfil a traves de la sesión
    username = session['username']
    db = PickleShareDB('miBD')
    perfil = db[username]
    return render_template('perfil.html', perfil = perfil, user = username, paginas = paginas)


#Página de modificación del perfil
@app.route('/modificarPerfil', methods=['GET','POST'])
def modificarPerfil():
    #Obtenemos los datos del perfil y los mandamos para que aparezcan en el formulario
    username = session['username']
    db = PickleShareDB('miBD')
    perfil = db[username]
    return render_template('modificarPerfil.html', user= username, perfil = perfil,paginas = paginas)


#Función para guardar el perfil
@app.route('/guardarPerfil', methods=['GET','POST'])
def guardarPerfil():
    #Si se ha modificado la contraseña, coger la nueva. Si no, quedarnos con la antigua
    if request.form['new_password']:
        p = request.form['new_password']
    else:
        p = request.form['old_password']
    #Creamos nuevo usuario borrando el anterior
    username = session['username']
    db = PickleShareDB('miBD')
    del db[username]
    db[request.form['username']] = {'User': request.form['username'],
                                    'Pass': p,
                                    'Nombre': request.form['nombre'],
                                    'Apellidos': request.form['apellidos'],
                                    'Email': request.form['email'],
                                    'Direccion': request.form['direccion']}
    #Establecemos sesión del usuario modificado y vamos a página del perfil con nuevos datos
    session['username'] = request.form['username']
    return redirect(url_for('perfil'))


#Función para ver el listado de pokemons y la búsqueda por tipo
@app.route('/pokemons', methods=['GET','POST'])
def pokemons():
    username = None
    #Definimos la búsqueda a cualquiera y establecemos los tipos
    busqueda = "Cualquiera"
    tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
    if 'username' in session:
        username = session['username']
    pokemons = db.samples_pokemon.find()
    #Añadimos cada pokemon a una lista desde el puntero
    lista_pokemons = []
    for pokemon in pokemons:
        lista_pokemons.append(pokemon)

	# Pasamos la busqueda y el tipo
    return render_template('pokemons.html', pokemons=lista_pokemons,busqueda=busqueda,tipos=tipos,paginas = paginas, user=username)


#Función para ver el listado de pokemons propios, pudiendo añadir uno nuevo o modificar y borrar los existentes
@app.route('/mispokemons', methods=['GET','POST'])
def mispokemons():
    username = None
    tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
    if 'username' in session:
        username = session['username']
    #Si la accion es modificar, buscamos el pokemon por su nombre y lo seleccionamos en el puntero que pasa mongo
    if(request.method == 'POST' and request.form['accion']=="Modificar"):
        pokemon = db.samples_pokemon.find_one({'_id': ObjectId(request.form['id']) })
        #Pasamos el pokemon y permitimos que se modifiquen los datos
        return render_template('modificarpokemon.html', tipos=tipos,paginas = paginas, user=username, pokemon = pokemon, read="", dis="")
    #Si la acción es insertar, llevar a la página de inserción
    elif request.method == 'POST' and request.form['accion']=="Insertar":
        return render_template('insertarpokemon.html',tipos=tipos,paginas = paginas, user=username)
    #Si la acción es borrar, seleccionamos el pokemon por el nombre
    elif request.method == 'POST' and request.form['accion']=="Borrar":
        pokemon = db.samples_pokemon.find_one({'_id': ObjectId(request.form['id']) })
        #Pasamos el pokemon con los datos no modificables
        return render_template('modificarpokemon.html', tipos=tipos,paginas = paginas, user=username, pokemon = pokemon, read="readonly", dis="disabled")
    #Buscamos solo los pokemons del usuario logueado
    pokemons = db.samples_pokemon.find({'author': session['username'] })
    lista_pokemons = []
    for pokemon in pokemons:
        lista_pokemons.append(pokemon)
    return render_template('mispokemons.html', pokemons=lista_pokemons,paginas = paginas, user=username)


# Función para insertar pokemon
@app.route('/insertarpokemon', methods=['GET','POST'])
def insertarpokemon():
    username = None
    tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
    if 'username' in session:
        username = session['username']
    #Si se ha rellenado el formulario, insertamos el pokemon con los datos
    if(request.method == 'POST'):
        db.samples_pokemon.insert({
            'name': request.form['nombre'],
            'img': request.form['imagen'],
            'height': request.form['altura'],
            'weight': request.form['peso'],
            'type': request.form.getlist('tipo[]'),
            'weaknesses': request.form.getlist('debilidades[]'),
            'author': session['username']
        })
        return redirect(url_for('mispokemons'))
    return render_template('insertarpokemon.html',tipos=tipos,paginas = paginas, user=username)


#Función para modificar o borrar pokemons
@app.route('/modificarpokemon', methods=['GET','POST'])
def modificarpokemon():
    username = None
    tipos = ["Water","Fire","Normal","Flying","Poison","Fighting","Psychic","Grass","Bug","Electric","Ground","Rock","Ice","Ghost","Dragon"]
    if 'username' in session:
        username = session['username']
    #Si se ha confirmado el borrado, borrar el pokemon con ese nombre
    if(request.method == 'POST' and request.form['accion'] == "Confirmar borrado"):
        db.samples_pokemon.remove({'_id': ObjectId(request.form['id']) })
        return redirect(url_for('mispokemons'))
    #Si se ha confirmado la modificacion, modificamos el pokemon con el nombre antiguo con los nuevos datos
    elif(request.method == 'POST' and request.form['accion'] == "Confirmar modificacion"):
        db.samples_pokemon.update(
            {'_id': ObjectId(request.form['id'])},
            {'name': request.form['nombre'],
            'img': request.form['imagen'],
            'height': request.form['altura'],
            'weight': request.form['peso'],
            'type': request.form.getlist('tipo[]'),
            'weaknesses': request.form.getlist('debilidades[]'),
            'author': session['username']
        })
        return redirect(url_for('mispokemons'))
    return render_template('insertarpokemon.html',tipos=tipos,paginas = paginas, user=username)



#Función para guardar páginas
@app.before_request
def before_request():
    #Guardamos la url
    url = request.url
    #Cramos expresion regular para que no guarde la url de los elementos de static
    ex = re.compile("(http://localhost:5000/static)+.*")
    #Si no es pagina static, damos la vuelta a la lista para meter la nueva pagina al final y volvemos a dar la vuelta a la pagina
    if( not ex.match(url)):
        paginas.reverse()
        paginas.append(url)
        paginas.reverse()



#Pagina de error
@app.errorhandler(404)
def pagina_no_definida(error):
    return render_template('error.html', err = error)




#--------------------------------- Interfaces de los ejercicios -----------------------------------------#
# En ellas debemos de establecer el usuario para mandarlo a index.html ya que son extensiones
# En ellas se recoge el dato introducido en el formulario, se procesa dependiendo del ejercicio y se manda el resultado


#Ejercicio ordenación de listas
@app.route('/ordena', methods=['GET','POST'])
def ordenacion():
    username = None
    if 'username' in session:
        username = session['username']
    lista = None
    m1 = None
    t1 = None
    t2 = None
    if(request.method == 'POST'):
        lista = request.form['lista']
        m1 = m2 = list(map(int,lista.replace(',', ' ').split(' ')))
        start = time.process_time()
        burbuja(m1)
        end = time.process_time()
        t1=start-end
        start = time.process_time()
        burbujaCorto(m2)
        end = time.process_time()
        t2=start-end
    return render_template('ordena.html', lista = lista, m = str(m1).strip('[]') , t1 = t1 , t2 = t2, paginas = paginas, user=username )

#Ejercicio de criba de Erastótenes
@app.route('/criba', methods=['GET','POST'])
def criba():
    username = None
    if 'username' in session:
        username = session['username']
    limite = None
    primos = None
    if(request.method == 'POST' and request.form['limite']!=''):
        limite = int(request.form['limite'])
        numeros = list(range(limite))
        primos = [ ]
        for i in range(2, limite):
        	if numeros[i] != -1:
        		primos.append(numeros[i])
        	for j in range(i, limite, i):
        		numeros[j] = -1
    return render_template('criba.html', limite = limite, primos = str(primos).strip('[]'),paginas = paginas, user = username)

#Ejercicio de sucesión de Fibonacci
@app.route('/fibonacci', methods=['GET','POST'])
def fibonacci():
    username = None
    if 'username' in session:
        username = session['username']
    n = None
    a = None
    if(request.method == 'POST' and request.form['n']!=''):
        n = int(request.form['n'])
        a = fibonacci_f(n)
    return render_template('fibonacci.html', n = n , a = a, paginas = paginas, user=username)

#Ejercicio del balanceo de cadenas de corchetes
@app.route('/cbalanceada', methods=['GET','POST'])
def cbalanceada():
    username = None
    if 'username' in session:
        username = session['username']
    c = ""
    cadena = None
    if(request.method == 'POST' and request.form['cadena']!=''):
        total=0
        error=""
        cadena = request.form['cadena']
        for i in range(len(cadena)):
        	# Cuando sean de apertura sumar, si no restar, si la cuenta negativa, mal formato
        	if (cadena[i] == "["):
        		total += 1
        	else:
        		total -= 1
        	if (total < 0):
        		error = ". Corchete mal puesto en posición " + str(i+1)

        if (total > 0 or error!=""):
            c += "CADENA NO BALANCEADA O INCORRECTA"
            if (error!=""):
                c += error
        else:
        	c += "CADENA BALANCEADA"
    return render_template('cbalanceada.html', cadena = cadena , resultado = c, paginas = paginas, user = username)

#Ejercicio de expresiones regulares
@app.route('/exreg', methods=['GET','POST'])
def exreg():
    username = None
    if 'username' in session:
        username = session['username']
    cadena= ""
    c = None
    if(request.method == 'POST' and request.form['cadenaex']!=''):
            cadena = request.form['cadenaex']
            c=""
            if palabraYMayuscula(cadena):
                c+="Es primer apellido"
            elif email(cadena):
                c+="Es un email"
            elif tarjetaCredito(cadena):
                c+="Es un nº de tarjeta de crédito"
            else:
                c+="No es ni primer apellido, ni email ni un nº de tarjeta de crédito"
    return render_template('exreg.html', cadena = cadena, resultado = c, paginas = paginas, user=username)
