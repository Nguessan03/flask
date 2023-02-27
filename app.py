from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_mysqldb import MySQL
import os
import hashlib
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import plotly.graph_objs as go
# from plotly.subplots import make_subplots
from datetime import datetime, time
import plotly.offline as pyo


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = 'static/img/'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sante'
db = SQLAlchemy(app)
mysql = MySQL(app)

########################################################################################


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    type = db.Column(db.String(50), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/nourriture', methods=['GET', 'POST'])
def nourriture():
    if request.method == 'POST':
        mealname = request.form['mealname']
        mealdate = request.form['mealdate']
        mealtime = request.form['mealtime']
        mealtype = request.form['mealtype']

        # Validation des données
        if mealname == '' or mealdate == '' or mealtime == '' or mealtype == '':
            return render_template('home.html', message='Tous les champs sont obligatoires.')
        if mealtype not in ['petit-dejeuner', 'dejeuner', 'diner', 'collation']:
            return render_template('home.html', message='Type de repas non valide.')

        # Enregistrement des données en base de données
        meal = Meal(name=mealname, date=mealdate, time=mealtime, type=mealtype)
        db.session.add(meal)
        db.session.commit()

        return redirect(url_for('site'))


##############################################################################


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    types = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/sport', methods=['POST'])
def add_activity():
    activity_type = request.form['activity-type']
    duration = request.form['duration']
    date = request.form['date']
    start_time = request.form['start-time']

    activity = Activity(types=activity_type, duration=duration,
                        date=date, start_time=start_time)
    db.session.add(activity)
    db.session.commit()
    return redirect(url_for('site'))

###################################################################


class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/sleep', methods=['POST'])
def add_spleep():
    if request.method == 'POST':
        datesom = request.form['date']
        time = request.form['time']
        durationsom = request.form['duration']
        quality = request.form['quality']
        notes = request.form['notes']

        sleep = Sleep(date=datesom, start_time=time,
                      duration=durationsom, quality=quality, notes=notes)
        db.session.add(sleep)
        db.session.commit()
        return redirect(url_for('site'))


#################################################################


class Plus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    birthdate = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    poid = db.Column(db.Integer, nullable=False)
    taille = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    confirm = db.Column(db.Text, nullable=False)
    objectif = db.Column(db.Text, nullable=False)
    file = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()

    def __repr__(self):
        return '<Plus %r>' % self.username


@app.route('/insert', methods=['POST'])
def insert():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    birthdate = request.form['birthdate']
    birthdate_hashed = hashlib.sha256(birthdate.encode('utf-8')).hexdigest()
    gender = request.form['gender']
    poid = request.form['poid']
    taille = request.form['taille']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']
    objectif = request.form['objectif']
    file = request.files['file']
    filename = secure_filename(file.filename)
    chemin = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(chemin)
    password_hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

    plus = Plus(firstname=firstname, lastname=lastname, birthdate=birthdate_hashed,
                gender=gender, poid=poid, taille=taille, username=username, email=email,
                password=password_hashed, confirm=password_hashed, objectif=objectif, file=chemin)
    if password_hashed == hashlib.sha256(confirm.encode('utf-8')).hexdigest():
        user = Plus.query.filter_by(
            email=email).first()
        if user:
            f"L'utilisateur {username} déjà"
        else:
            db.session.add(plus)
            db.session.commit()
            return render_template('login.html')
    else:
        return "Le mot de passe et la confirmation ne correspondent pas, veuillez réessayer"


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = Plus.query.filter_by(
            email=email, password=password_hashed).first()
        if user:
            return redirect(url_for('site'))
        else:
            return 'Email ou mot de passe incorrect'
    return render_template('login.html')


@app.route('/site')
def site():
    meal_data = Meal.query.all()
    activity_data = Activity.query.all()
    sleep_data = Sleep.query.all()
    return render_template('home.html', meal_data=meal_data, sleep_data=sleep_data, activity_data=activity_data)


@app.route('/nutrition')
def nutri():
    meals = Meal.query.all()
    dates = [meal.date for meal in meals]
    times = [meal.time for meal in meals]
    names = [meal.name for meal in meals]

    trace = go.Scatter(
        x=dates,
        y=times,
        mode='markers',
        marker=dict(
            size=10,
            color='blue'
        ),
        text=names
    )

    # Créer une mise en page pour le graphique
    layout = go.Layout(
        title='Repas en fonction de la date et de l\'heure',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Heure de repas')
    )

    # Créer une figure pour le graphique
    fig = go.Figure(data=[trace], layout=layout)
    # Générer le code HTML du graphique
    plot = fig.to_html(full_html=False)

    # Analyser les données pour déterminer les habitudes alimentaires
    meal_count = len(meals)
    first_meal_time = min(times)
    last_meal_time = max(times)
    time_range = (datetime.combine(datetime.min, last_meal_time) -
                  datetime.combine(datetime.min, first_meal_time)).total_seconds() / 3600
    meal_frequency = meal_count / time_range

    # Analyser les données pour déterminer les types de repas préférés
    meal_types = {}
    for meal in meals:
        if meal.type in meal_types:
            meal_types[meal.type] += 1
        else:
            meal_types[meal.type] = 1
    # Analyser les données pour déterminer les moments de la journée préférés pour manger
    morning_meal_count = len(
        [meal for meal in meals if meal.time < time(hour=12)])
    afternoon_meal_count = len([meal for meal in meals if meal.time >= time(
        hour=12) and meal.time < time(hour=18)])
    evening_meal_count = len(
        [meal for meal in meals if meal.time >= time(hour=18)])

    # Créer un contexte de rendu pour le modèle HTML
    context = {
        'graph_html': plot,
        'meal_count': meal_count,
        'first_meal_time': first_meal_time,
        'last_meal_time': last_meal_time,
        'meal_frequency': meal_frequency,
        'meal_types': meal_types,
        'morning_meal_count': morning_meal_count,
        'afternoon_meal_count': afternoon_meal_count,
        'evening_meal_count': evening_meal_count
    }

 # Créer un graphique à partir des données contenues dans le contexte
    data = [go.Bar(x=["matin", "après-midi", "soir"], y=[morning_meal_count,
                   afternoon_meal_count, evening_meal_count])]
    layout = go.Layout(
        title='Répartition des repas selon le moment de la journée')
    fig = go.Figure(data=data, layout=layout)
    plots = fig.to_html(full_html=False)

    # Renvoyer le code HTML du graphique dans un fichier HTML et Rendre le modèle HTML avec le contexte de rendu
    return render_template('nutrition.html', context=context, plot=plot, graph_html=plots)


@app.route('/sommeil')
def som():

    return render_template('sommeil.html')


@app.route('/sport')
def spo():

    # Récupérer toutes les entrées de la table "Sport"
    data = db.session.query(
        Activity.types, Activity.date, Activity.duration).all()

    # Initialiser des dictionnaires pour stocker les durées de chaque type d'activité sportive pour chaque date
    data_dict = {}

    for item in data:
        activity_type = item[0]
        date = item[1]
        duration = item[2]
        if activity_type not in data_dict:
            data_dict[activity_type] = {'x': [], 'y': []}
        data_dict[activity_type]['x'].append(date)
        data_dict[activity_type]['y'].append(duration)

    # Créer une liste d'objets Bar de Plotly à partir des données calculées
    bars = []

    for activity_type in data_dict:
        bars.append(go.Bar(
            x=data_dict[activity_type]['x'],
            y=data_dict[activity_type]['y'],
            name=activity_type
        ))

    # Créer un objet Layout de Plotly pour le graphique
    layout = go.Layout(
        title='Durée des activités par type et date',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Durée (min)')
    )

    fig = go.Figure(data=bars, layout=layout)
    plot = fig.to_html(full_html=False)
    return render_template('sport.html', plot=plot)


@app.route('/compte')
def comp():
    return render_template('compte.html')
