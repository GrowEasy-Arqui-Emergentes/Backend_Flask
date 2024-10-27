from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://grow_easy_user:r9mbC0HmUqWGPnvPAfm3nOAADL0azbU6@dpg-cserblbtq21c738g42q0-a.oregon-postgres.render.com/grow_easy')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    videoUrl = db.Column(db.String(255), nullable=False)

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.Integer, nullable=False)

class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.Integer, nullable=False)

@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        preload_courses()
        app.db_initialized = True

def preload_courses():
    courses = [
        # tus cursos predeterminados aquí
    ]

    if Course.query.count() == 0:
        for course in courses:
            new_course = Course(name=course['name'], price=course['price'], description=course['description'], image=course['image'], videoUrl=course['videoUrl'])
            db.session.add(new_course)
        db.session.commit()

def send_email(to_email, username, password):
    from_email = "yancefranco@gmail.com"
    from_password = "kuph wcru rwqk xlrv"

    subject = "Registro Exitoso"
    body = f"Usuario: {username}\nContraseña: {password}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    dni = data.get('dni')
    role = data.get('role')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    country = data.get('country')
    city = data.get('city')
    image_path = data.get('image_url', None)

    if not dni or not role or not first_name or not last_name or not email or not username or not password or not country or not city:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(
        dni=dni,
        role=role,
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        password_hash=password_hash,
        country=country,
        city=city,
        image_path=image_path
    )

    db.session.add(new_user)
    db.session.commit()

    send_email(email, username, password)

    return jsonify({'message': 'Usuario registrado con éxito y correo enviado'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            'username': user.username,
            'password_hash': user.password_hash
        })
    return jsonify(users_list), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Nombre de usuario y contraseña son requeridos'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    return jsonify({'message': 'Inicio de sesión exitoso'}), 200

@app.route('/profile', methods=['POST'])
def get_profile():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username es requerido'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    user_data = {
        'dni': user.dni,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'country': user.country,
        'city': user.city,
        'image_path': user.image_path
    }

    return jsonify(user_data), 200

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()

    dni = data.get('dni')
    if not dni:
        return jsonify({'error': 'DNI es requerido'}), 400

    user = User.query.filter_by(dni=dni).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    user.role = data.get('role', user.role)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.country = data.get('country', user.country)
    user.city = data.get('city', user.city)
    user.image_path = data.get('image_path', user.image_path)

    db.session.commit()

    return jsonify({'message': 'Perfil actualizado con éxito'}), 200

@app.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()

    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    image = data.get('image')
    videoUrl = data.get('videoUrl')

    if not name or not price or not description or not image or not videoUrl:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    new_course = Course(name=name, price=price, description=description, image=image, videoUrl=videoUrl)
    db.session.add(new_course)
    db.session.commit()

    return jsonify({'message': 'Curso añadido con éxito'}), 201

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    courses_list = []
    for course in courses:
        courses_list.append({
            'id': course.id,
            'name': course.name,
            'price': course.price,
            'description': course.description,
            'image': course.image,
            'videoUrl': course.videoUrl
        })
    return jsonify(courses_list), 200

@app.route('/get_user_role', methods=['POST'])
def get_user_role():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username es requerido'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'role': user.role}), 200

@app.route('/users/<string:username>/courses', methods=['GET'])
def get_user_courses(username):
    # Buscar todos los registros de UserCourse para el usuario dado
    user_courses = UserCourse.query.filter_by(username=username).all()

    courses_list = []
    for user_course in user_courses:
        course = Course.query.get(user_course.course_id)
        if course:
            courses_list.append({
                'id': course.id,
                'name': course.name,
                'price': course.price,
                'description': course.description,
                'image': course.image,
                'videoUrl': course.videoUrl
            })

    return jsonify(courses_list), 200


@app.route('/shopping_cart', methods=['POST'])
def add_to_shopping_cart():
    data = request.get_json()
    username = data.get('username')
    course_id = data.get('course_id')

    if not username or not course_id:
        return jsonify({'error': 'Nombre de usuario y ID de curso son requeridos'}), 400

    # Verificar si el usuario y el curso existen
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Curso no encontrado'}), 404

    # Agregar al carrito de compras
    new_item = ShoppingCart(username=username, course_id=course_id)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'message': 'Curso añadido al carrito de compras correctamente'}), 201

@app.route('/shopping_cart', methods=['DELETE'])
def remove_from_shopping_cart():
    data = request.get_json()
    username = data.get('username')
    course_id = data.get('course_id')

    if not username or not course_id:
        return jsonify({'error': 'Nombre de usuario y ID de curso son requeridos'}), 400

    # Verificar y eliminar del carrito de compras
    item = ShoppingCart.query.filter_by(username=username, course_id=course_id).first()
    if not item:
        return jsonify({'error': 'No se encontró la combinación de usuario y curso en el carrito de compras'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Curso eliminado del carrito de compras correctamente'}), 200

@app.route('/process_shopping_cart', methods=['POST'])
def process_shopping_cart():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Nombre de usuario es requerido'}), 400

    # Obtener todos los elementos del carrito de compras para el usuario dado
    items = ShoppingCart.query.filter_by(username=username).all()

    if not items:
        return jsonify({'message': 'El carrito de compras está vacío'}), 200

    try:
        # Agregar los cursos al usuario y limpiar el carrito de compras
        for item in items:
            new_user_course = UserCourse(username=username, course_id=item.course_id)
            db.session.add(new_user_course)
            db.session.delete(item)

        db.session.commit()
        return jsonify({'message': 'Cursos agregados al usuario y carrito de compras limpiado correctamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al procesar el carrito de compras: {str(e)}'}), 500
    
@app.route('/shopping_cart/<username>', methods=['GET'])
def get_courses_in_shopping_cart(username):
    if not username:
        return jsonify({'error': 'Username es requerido'}), 400

    # Obtener los cursos en el carrito de compras del usuario
    cart_items = ShoppingCart.query.filter_by(username=username).all()

    if not cart_items:
        return jsonify({'message': 'El carrito de compras está vacío para este usuario'}), 200

    # Obtener los detalles de cada curso en el carrito de compras
    courses_in_cart = []
    for item in cart_items:
        course = Course.query.get(item.course_id)
        if course:
            courses_in_cart.append({
                'id': course.id,
                'name': course.name,
                'price': course.price,
                'description': course.description,
                'image': course.image,
                'videoUrl': course.videoUrl
            })

    return jsonify(courses_in_cart), 200
    
@app.route('/')
def home():
    return jsonify({'message': 'Bienvenido a la API de GreenGrow'})

if __name__ == '__main__':
    app.run(debug=True)
