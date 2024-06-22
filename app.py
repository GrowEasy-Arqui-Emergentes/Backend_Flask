from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/greengrow'
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

@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        preload_courses()
        app.db_initialized = True

def preload_courses():
    courses = [
        {
            "name": "Fundamentos de Hidroponia",
            "price": 50,
            "description": "Curso introductorio sobre hidroponia.",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Catharanthus_roseus_white_CC-BY-SA.jpg/640px-Catharanthus_roseus_white_CC-BY-SA.jpg",
            "videoUrl": "https://youtu.be/lr7iXNrvH1I?list=PLoP3Y_C2ydwtxTBGa_2BNav8dQeEsfjcl"
        },
        {
            "name": "Hidroponia Avanzada",
            "price": 60,
            "description": "Curso avanzado de técnicas de hidroponia.",
            "image": "https://algoritmomag.com/wp-content/uploads/2024/02/hidroponia-casera.jpg",
            "videoUrl": "https://youtu.be/8zSjyk96ggM?list=PLXaMdWFW_yNNYS1RYYUVhlFLvKXHGVtNd"
        },
        {
            "name": "Cultivo Hidropónico de Tomates",
            "price": 40,
            "description": "Cómo cultivar tomates usando hidroponia.",
            "image": "https://humusnatural.com/wp-content/uploads/2023/04/Cultivo-tomate-hidroponico-pasos.jpg",
            "videoUrl": "https://youtu.be/mTr7itgI12M"
        },
        {
            "name": "Cultivo Hidropónico de Lechugas",
            "price": 56,
            "description": "Cómo cultivar lechugas usando hidroponia.",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRne2VTZ1J9g4KXPcsojsQjSCe_28CZkZDp2w&s",
            "videoUrl": "https://youtu.be/rMaRj-pVcso"
        },
        {
            "name": "Diseño de Sistemas Hidropónicos",
            "price": 47,
            "description": "Diseño y construcción de sistemas hidropónicos.",
            "image": "https://i0.wp.com/ecoinventos.com/wp-content/uploads/2015/06/C%C3%B3mo-crear-un-sistema-hidrop%C3%B3nico-casero-6.jpg?resize=640%2C480&ssl=1",
            "videoUrl": "https://youtu.be/d2sRLaiIh-Q"
        },
        {
            "name": "Mantenimiento de Sistemas Hidropónicos",
            "price": 76,
            "description": "Cómo mantener y optimizar sistemas hidropónicos.",
            "image": "https://i.ytimg.com/vi/QdeJRhI5TGQ/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLCfK4cl5HvIbIZEN-35RV3lpsz7EA",
            "videoUrl": "https://youtu.be/ncxImn3_nVI"
        },
        {
            "name": "Nutrición de Plantas en Hidroponia",
            "price": 80,
            "description": "Gestión de nutrientes en cultivos hidropónicos.",
            "image": "https://cdn.shopk.it/usercontent/grohoespana/media/images/2d2e11d-testes_laboratorio_hidroponia.jpg",
            "videoUrl": "https://youtu.be/hpS_EYBTCeA"
        },
        {
            "name": "Control de Plagas en Hidroponia",
            "price": 40,
            "description": "Métodos de control de plagas para cultivos hidropónicos.",
            "image": "https://i.ytimg.com/vi/0HiN_2DDsZw/maxresdefault.jpg",
            "videoUrl": "https://youtu.be/2QsF-cTSYw4"
        },
        {
            "name": "Hidroponia Urbana",
            "price": 60,
            "description": "Implementación de hidroponia en espacios urbanos.",
            "image": "https://diario.uach.cl/wp-content/uploads/2020/04/Agricultura-Hidrop%C3%B3nica.jpg",
            "videoUrl": "https://youtu.be/geLAWZNthX8"
        },
        {
            "name": "Hidroponia Comercial",
            "price": 30,
            "description": "Escalando hidroponia para producción comercial.",
            "image": "https://i.ytimg.com/vi/F-BW5WR-kaE/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGDsgZSgYMA8=&rs=AOn4CLAY-1Ka_zYQY2gDRiFh7OTOAd0Sag",
            "videoUrl": "https://youtu.be/F-BW5WR-kaE"
        }
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

if __name__ == '__main__':
    app.run(debug=True)
