from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "clave-secreta-123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================
# TABLA USUARIOS
# =========================

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    productos = db.relationship("Producto", backref="usuario", lazy=True)


# =========================
# TABLA CATEGORIAS
# =========================

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    productos = db.relationship("Producto", backref="categoria", lazy=True)


# =========================
# TABLA PRODUCTOS
# =========================

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(250))
    precio = db.Column(db.Float, nullable=False)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categoria.id"),
        nullable=False
    )


# =========================
# CARGAR USUARIO
# =========================

@login_manager.user_loader
def cargar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


# =========================
# INICIO
# =========================

@app.route("/")
def inicio():
    return render_template("index.html")


# =========================
# REGISTRO
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            flash("El correo ya está registrado.")
            return redirect(url_for("register"))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.")

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(
            usuario.password,
            password
        ):

            login_user(usuario)

            return redirect(url_for("inicio"))

        flash("Correo o contraseña incorrectos.")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# =========================
# PRODUCTOS - LEER
# =========================

@app.route("/productos")
@login_required
def productos():

    productos = Producto.query.all()
    categorias = Categoria.query.all()

    return render_template(
        "productos.html",
        productos=productos,
        categorias=categorias
    )


# =========================
# PRODUCTOS - CREAR
# =========================

@app.route("/productos/crear", methods=["POST"])
@login_required
def crear_producto():

    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = float(request.form["precio"])
    categoria_id = int(request.form["categoria_id"])

    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        usuario_id=current_user.id,
        categoria_id=categoria_id
    )

    db.session.add(producto)
    db.session.commit()

    flash("Producto creado correctamente.")

    return redirect(url_for("productos"))


# =========================
# PRODUCTOS - ACTUALIZAR
# =========================

@app.route("/productos/editar/<int:id>", methods=["POST"])
@login_required
def editar_producto(id):

    producto = db.session.get(Producto, id)

    if producto:

        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.categoria_id = int(request.form["categoria_id"])

        db.session.commit()

        flash("Producto actualizado correctamente.")

    return redirect(url_for("productos"))


# =========================
# PRODUCTOS - ELIMINAR
# =========================

@app.route("/productos/eliminar/<int:id>")
@login_required
def eliminar_producto(id):

    producto = db.session.get(Producto, id)

    if producto:

        db.session.delete(producto)
        db.session.commit()

        flash("Producto eliminado correctamente.")

    return redirect(url_for("productos"))


# =========================
# CATEGORIAS
# =========================

@app.route("/categorias")
@login_required
def categorias():

    categorias = Categoria.query.all()

    return render_template(
        "categorias.html",
        categorias=categorias
    )


# =========================
# CREAR BASE DE DATOS
# =========================

with app.app_context():

    db.create_all()

    if Categoria.query.count() == 0:

        db.session.add_all([
            Categoria(nombre="Computación"),
            Categoria(nombre="Accesorios"),
            Categoria(nombre="Software")
        ])

        db.session.commit()


# =========================
# EJECUTAR
# =========================

if __name__ == "__main__":
    app.run(debug=True)