# MegaPersonal - Aplicativo de Gerenciamento para Personal Trainers
# Estrutura principal usando Flask para backend e SQLite para banco de dados

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
from datetime import datetime, timedelta
from math import ceil





# Configurações do banco de dados Supabase
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT', '5432')

# Adicione o parâmetro SSL
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# Para debug, não mostre a senha real nos logs
print(f"Tentando conectar a: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require")



app = Flask(__name__)
app.config['SECRET_KEY'] = 'megapersonal_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///megapersonal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Adicionar funções embutidas ao ambiente Jinja2
app.jinja_env.globals.update(max=max, min=min)

db = SQLAlchemy(app)

# Configuração para upload de arquivos
UPLOAD_FOLDER = 'static/uploads/assessments'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crie a pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Função para verificar extensões de arquivo permitidas
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Modelos do banco de dados
class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Campo para controlar status da conta
    clients = db.relationship('Client', backref='trainer', lazy=True)
    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    goal = db.Column(db.String(200))
    health_notes = db.Column(db.Text)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    workouts = db.relationship('Workout', backref='client', lazy=True)
    assessments = db.relationship('Assessment', backref='client', lazy=True)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(50))
    video_url = db.Column(db.String(200))
    workout_exercises = db.relationship('WorkoutExercise', backref='exercise', lazy=True)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True)

class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.String(50))  # Pode ser "12, 10, 8" para pirâmide
    rest_time = db.Column(db.Integer)  # Em segundos
    notes = db.Column(db.Text)
    order = db.Column(db.Integer)  # Ordem do exercício no treino

class WorkoutTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    exercises = db.relationship('WorkoutTemplateExercise', backref='workout_template', lazy=True)

class WorkoutTemplateExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('workout_template.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.String(50))
    rest_time = db.Column(db.Integer)
    notes = db.Column(db.Text)
    order = db.Column(db.Integer)
    exercise = db.relationship('Exercise', backref='template_exercises', lazy=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Medidas básicas atuais
    weight = db.Column(db.Float)
    body_fat = db.Column(db.Float)
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    hips = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
    
    # Novas medidas antropométricas
    neck = db.Column(db.Float)
    shoulders = db.Column(db.Float)
    forearms = db.Column(db.Float)
    wrists = db.Column(db.Float)
    calves = db.Column(db.Float)
    ankles = db.Column(db.Float)
    abdomen = db.Column(db.Float)
    
    # Dobras cutâneas (em mm)
    skinfold_triceps = db.Column(db.Float)
    skinfold_biceps = db.Column(db.Float)
    skinfold_subscapular = db.Column(db.Float)
    skinfold_suprailiac = db.Column(db.Float)
    skinfold_abdominal = db.Column(db.Float)
    skinfold_thigh = db.Column(db.Float)
    skinfold_calf = db.Column(db.Float)
    
    # Outros campos existentes
    notes = db.Column(db.Text)
    front_photo = db.Column(db.String(255))
    side_photo = db.Column(db.String(255))
    back_photo = db.Column(db.String(255))

class ExerciseLoad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Carga em kg
    reps_done = db.Column(db.String(50))  # Repetições realizadas
    notes = db.Column(db.Text)  # Observações
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    client = db.relationship('Client', backref='exercise_loads')
    exercise = db.relationship('Exercise', backref='loads')   
    
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # "presente", "ausente", "justificado"
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    notes = db.Column(db.Text)
    
    # Adicione estas duas linhas:
    client = db.relationship('Client', backref='attendances', lazy=True)
    workout = db.relationship('Workout', backref='attendances', lazy=True)

# Adicione este modelo ao seu arquivo app.py

class ClientUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    

# notificações para o Telegram
def send_telegram_notification(message):
    bot_token = '7646480970:AAFIYtXFw75ER4cqsidZXV3ZAxTw_BdAEvo'  # Substitua pelo token que você obteve do BotFather
    chat_id = '849913605'  # Substitua pelo seu chat ID 
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'  # Permite formatação básica HTML
    }
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")
        return None

def notify_new_trainer_registration(trainer):
    message = f"<b>🏋️ Novo Personal Trainer Cadastrado!</b>\n\n" \
              f"<b>Nome:</b> {trainer.name}\n" \
              f"<b>Email:</b> {trainer.email}\n" \
              f"<b>Telefone:</b> {trainer.phone}\n" \
              f"<b>Data:</b> {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
    
    return send_telegram_notification(message)

def notify_new_client_added(client, trainer):
    message = f"<b>👤 Novo Aluno Adicionado!</b>\n\n" \
              f"<b>Nome:</b> {client.name}\n" \
              f"<b>Email:</b> {client.email}\n" \
              f"<b>Telefone:</b> {client.phone}\n" \
              f"<b>Objetivo:</b> {client.goal}\n" \
              f"<b>Personal:</b> {trainer.name}\n" \
              f"<b>Data:</b> {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
    
    return send_telegram_notification(message)






# Rotas para API e renderização de páginas
@app.route('/')
def home():
    if 'trainer_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Substitua a rota de login existente por esta versão unificada

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verificar se já está logado
    if 'trainer_id' in session:
        return redirect(url_for('dashboard'))
    if 'client_id' in session:
        return redirect(url_for('client_dashboard'))

    error = None
    user_type = request.form.get('user_type', 'trainer')

    if request.method == 'POST':
        user_type = request.form.get('user_type')

        if user_type == 'trainer':
            email = request.form.get('email')
            password = request.form.get('password')

            trainer = Trainer.query.filter_by(email=email).first()

            if trainer and check_password_hash(trainer.password, password):
                # Verificar se a conta está ativa
                if not trainer.is_active:
                    error = 'Esta conta está desativada. Entre em contato com o administrador.'
                    return render_template('login.html', error=error, user_type=user_type)

                session['trainer_id'] = trainer.id
                session['trainer_name'] = trainer.name
                return redirect(url_for('dashboard'))
            else:
                error = 'Email ou senha incorretos'



        elif user_type == 'student':
             # Login de aluno
             username = request.form.get('username')
             password = request.form.get('password')

             client_user = ClientUser.query.filter_by(username=username).first()

             if client_user and check_password_hash(client_user.password, password):
                 session['client_id'] = client_user.client_id
                 client_user.last_login = datetime.utcnow()
                 db.session.commit()
                 return redirect(url_for('client_dashboard'))
             else:
                 error = 'Nome de usuário ou senha incorretos'


    return render_template('login.html', error=error, user_type=user_type)

# Adicione esta rota para garantir que o logout funcione independente do tipo de usuário

@app.route('/logout')
def logout():
    session.pop('trainer_id', None)
    session.pop('trainer_name', None)
    session.pop('client_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validação básica
        if not name or not email or not phone or not password:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        # Verificar se o email já está em uso
        existing_trainer = Trainer.query.filter_by(email=email).first()
        if existing_trainer:
            flash('Este email já está cadastrado. Por favor, use outro email.', 'error')
            return render_template('register.html')
        
        # Criar novo trainer
        try:
            new_trainer = Trainer(
                name=name,
                email=email,
                phone=phone,
                password=generate_password_hash(password)
            )
            db.session.add(new_trainer)
            db.session.commit()
            
            # Enviar notificação Telegram
            notify_new_trainer_registration(new_trainer)
            
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar trainer: {e}")
            flash('Ocorreu um erro ao processar seu cadastro. Por favor, tente novamente.', 'error')
    
    return render_template('register.html')


@app.route('/admin')
def admin_dashboard():
    # Verificar autenticação de administrador
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Contagens
    trainer_count = Trainer.query.count()
    client_count = Client.query.count()
    workout_count = Workout.query.count()
    assessment_count = Assessment.query.count()
    
    # Listar trainers e clientes
    trainers = Trainer.query.all()
    clients = Client.query.all()
    
    return render_template('admin_dashboard.html',
                          trainer_count=trainer_count,
                          client_count=client_count,
                          workout_count=workout_count,
                          assessment_count=assessment_count,
                          trainers=trainers,
                          clients=clients)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Substitua isso por credenciais reais armazenadas de forma segura
        if username == 'admin' and password == 'mega@010203':
            session['admin_id'] = 1
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/reset_trainer_password', methods=['POST'])
def reset_trainer_password():
    # Verificar autenticação de administrador
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    trainer_id = request.form.get('trainer_id')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validações básicas
    if not trainer_id or not new_password or not confirm_password:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if new_password != confirm_password:
        flash('As senhas não coincidem.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Buscar o personal trainer
    trainer = Trainer.query.get(trainer_id)
    if not trainer:
        flash('Personal trainer não encontrado.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Atualizar a senha com hash
        from werkzeug.security import generate_password_hash
        trainer.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash(f'Senha do personal trainer {trainer.name} foi resetada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao resetar senha: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/trainer/<int:trainer_id>/reset_password', methods=['GET'])
def admin_reset_password_form(trainer_id):
    # Verificar autenticação de administrador
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    trainer = Trainer.query.get_or_404(trainer_id)
    return render_template('admin_reset_password.html', trainer=trainer)


@app.route('/dashboard')
def dashboard():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    trainer = Trainer.query.get(session['trainer_id'])
    clients = Client.query.filter_by(trainer_id=trainer.id).all()
    
    # Contagem de clientes, treinos, etc.
    client_count = len(clients)
    today = datetime.utcnow().date()
    
    # Sessões agendadas para hoje
    attendances_today = Attendance.query.filter(
        Attendance.client_id.in_([client.id for client in clients]),
        db.func.date(Attendance.date) == today
    ).all()
    
    # Calcular taxa de presença
    # Pegue todas as presenças dos últimos 30 dias
    thirty_days_ago = today - timedelta(days=30)
    all_attendances = Attendance.query.filter(
        Attendance.client_id.in_([client.id for client in clients]),
        db.func.date(Attendance.date) >= thirty_days_ago
    ).all()
    
    # Conta quantas presenças foram marcadas como "presente"
    present_count = sum(1 for a in all_attendances if a.status == "presente")
    
    # Calcula a taxa de presença
    attendance_rate = 0
    if all_attendances:
        attendance_rate = (present_count / len(all_attendances)) * 100
    
    return render_template('dashboard.html', 
                          trainer=trainer, 
                          clients=clients, 
                          client_count=client_count,
                          attendances_today=attendances_today,
                          attendance_rate=attendance_rate)


@app.route('/aluno/registrar-treino', methods=['POST'])
def client_register_workout():
    if 'client_id' not in session:
        return redirect(url_for('client_login'))
    
    client_id = session['client_id']
    workout_id = request.form.get('workout_id', type=int)
    notes = request.form.get('notes', '')
    
    if not workout_id:
        flash('Dados incompletos para registrar treino.', 'error')
        return redirect(url_for('client_dashboard'))
    
    try:
        # Criar registro de presença para o treino atual
        attendance = Attendance(
            client_id=client_id,
            date=datetime.utcnow(),
            status='presente',
            workout_id=workout_id,
            notes=notes
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        flash('Treino registrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar treino: {str(e)}', 'error')
    
    return redirect(url_for('client_dashboard'))


@app.route('/attendance')
def attendance_list():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    trainer = Trainer.query.get(session['trainer_id'])
    clients = Client.query.filter_by(trainer_id=trainer.id).all()
    
    # Obter data para filtro (padrão: hoje)
    filter_date_str = request.args.get('date')
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except ValueError:
            filter_date = datetime.utcnow().date()
    else:
        filter_date = datetime.utcnow().date()
    
    # Obter as presenças para a data filtrada
    attendances = Attendance.query.filter(
        Attendance.client_id.in_([client.id for client in clients]),
        db.func.date(Attendance.date) == filter_date
    ).all()
    
    # Criar um mapa cliente_id -> informações de presença
    attendance_dict = {}
    
    for attendance in attendances:
        attendance_dict[attendance.client_id] = {
            'id': attendance.id,
            'status': attendance.status,
            'notes': attendance.notes if attendance.notes else '',
            'workout_id': attendance.workout_id
        }
        
        # Adicionar nome do treino se disponível
        if attendance.workout_id:
            workout = Workout.query.get(attendance.workout_id)
            attendance_dict[attendance.client_id]['workout_name'] = workout.name if workout else "Sem nome"
        else:
            attendance_dict[attendance.client_id]['workout_name'] = ""
    
    return render_template(
        'attendance_list.html', 
        trainer=trainer, 
        clients=clients,
        attendance_map=attendance_dict,
        filter_date=filter_date
    )



@app.route('/attendance/record', methods=['POST'])
def attendance_record():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client_id = request.form.get('client_id', type=int)
    date_str = request.form.get('date')
    status = request.form.get('status')
    workout_id = request.form.get('workout_id', type=int)
    notes = request.form.get('notes', '')
    
    if not client_id or not date_str or not status:
        flash('Dados incompletos para registrar presença.', 'error')
        return redirect(url_for('attendance_list'))
    
    try:
        # Converter string de data para objeto date
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Verificar se já existe registro para este cliente nesta data
        existing = Attendance.query.filter_by(
            client_id=client_id,
            date=attendance_date
        ).first()
        
        if existing:
            # Atualizar registro existente
            existing.status = status
            existing.workout_id = workout_id
            existing.notes = notes
            db.session.commit()
            flash('Registro de presença atualizado com sucesso!', 'success')
        else:
            # Criar novo registro
            attendance = Attendance(
                client_id=client_id,
                date=attendance_date,
                status=status,
                workout_id=workout_id,
                notes=notes
            )
            db.session.add(attendance)
            db.session.commit()
            flash('Presença registrada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar presença: {str(e)}', 'error')
    
    # Redirecionar de volta para a página de presenças com a mesma data
    return redirect(url_for('attendance_list', date=date_str))



@app.route('/attendance/history/<int:client_id>')
def attendance_history(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('client_list'))
    
    # Buscar histórico de presenças (últimos 3 meses)
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    attendances = Attendance.query.filter_by(client_id=client.id)\
                                  .filter(Attendance.date >= three_months_ago)\
                                  .order_by(Attendance.date.desc())\
                                  .all()
    
    # Calcular estatísticas
    total = len(attendances)
    present_count = sum(1 for a in attendances if a.status == 'presente')
    absent_count = sum(1 for a in attendances if a.status == 'ausente')
    justified_count = sum(1 for a in attendances if a.status == 'justificado')
    
    attendance_rate = 0
    if total > 0:
        attendance_rate = (present_count / total) * 100
    
    return render_template('attendance_history.html',
                          client=client,
                          attendances=attendances,
                          total=total,
                          present_count=present_count,
                          absent_count=absent_count,
                          justified_count=justified_count,
                          attendance_rate=attendance_rate)



@app.route('/clients')
def client_list():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    trainer = Trainer.query.get(session['trainer_id'])
    clients = Client.query.filter_by(trainer_id=trainer.id).all()
    
    return render_template('clients.html', trainer=trainer, clients=clients)

@app.route('/client/<int:client_id>')
def client_detail(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    workouts = Workout.query.filter_by(client_id=client.id).all()
    assessments = Assessment.query.filter_by(client_id=client.id).order_by(Assessment.date.desc()).all()
    
    return render_template('client_detail.html', 
                          client=client, 
                          workouts=workouts, 
                          assessments=assessments)

@app.route('/client/new', methods=['GET', 'POST'])
def client_new():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        goal = request.form.get('goal')
        health_notes = request.form.get('health_notes')
        
        client = Client(
            name=name,
            email=email,
            phone=phone,
            age=age,
            height=height,
            weight=weight,
            goal=goal,
            health_notes=health_notes,
            trainer_id=session['trainer_id']
        )
        
        db.session.add(client)
        db.session.commit()


        # Buscar informações do trainer para a notificação
        trainer = Trainer.query.get(session['trainer_id'])
        
        # Enviar notificação Telegram
        notify_new_client_added(client, trainer)


        
        return redirect(url_for('client_detail', client_id=client.id))
    
    return render_template('client_form.html')

@app.route('/workout/new/<int:client_id>', methods=['GET', 'POST'])
def workout_new(client_id):
    
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        workout = Workout(
            name=name,
            description=description,
            client_id=client.id
        )
        
        db.session.add(workout)
        db.session.commit()
        
        return redirect(url_for('workout_edit', workout_id=workout.id))
    
    return render_template('workout_form.html', client=client)

@app.route('/workout/edit/<int:workout_id>', methods=['GET', 'POST'])
def workout_edit(workout_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    workout = Workout.query.get_or_404(workout_id)
    client = Client.query.get(workout.client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    # Obter todos os exercícios disponíveis
    exercises = Exercise.query.all()
    
    # Obter exercícios já adicionados ao treino
    workout_exercises = WorkoutExercise.query.filter_by(workout_id=workout.id).order_by(WorkoutExercise.order).all()
    
    if request.method == 'POST':
        # Verificar se é ação de editar exercício existente
        edit_mode = request.form.get('edit_mode')
        exercise_id_to_edit = request.form.get('exercise_id_to_edit')
        
        if edit_mode == '1' and exercise_id_to_edit:
            # Editar exercício existente
            exercise_id = request.form.get('exercise_id')
            sets = int(request.form.get('sets', 3))
            reps = request.form.get('reps', '12')
            rest_time = int(request.form.get('rest_time', 60))
            notes = request.form.get('notes', '')
            order = int(request.form.get('order', 1))
            
            # Buscar o exercício do treino para editar
            workout_exercise = WorkoutExercise.query.get(int(exercise_id_to_edit))
            
            if workout_exercise and workout_exercise.workout_id == workout.id:
                # Atualizar os dados
                workout_exercise.exercise_id = exercise_id
                workout_exercise.sets = sets
                workout_exercise.reps = reps
                workout_exercise.rest_time = rest_time
                workout_exercise.notes = notes
                workout_exercise.order = order
                
                db.session.commit()
                flash('Exercício atualizado com sucesso!', 'success')
            return redirect(url_for('workout_edit', workout_id=workout.id))
            
        # Verificar se é ação de adicionar exercício
        exercise_id = request.form.get('exercise_id')
        
        if exercise_id:
            exercise_id = int(exercise_id)
            sets = int(request.form.get('sets', 3))
            reps = request.form.get('reps', '12')
            rest_time = int(request.form.get('rest_time', 60))
            notes = request.form.get('notes', '')
            order = int(request.form.get('order', len(workout_exercises) + 1))
            
            # Verificar se o exercício existe
            exercise = Exercise.query.get(exercise_id)
            if not exercise:
                flash('Exercício não encontrado.', 'error')
                return redirect(url_for('workout_edit', workout_id=workout.id))
            
            # Criar novo exercício de treino
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise_id,
                sets=sets,
                reps=reps,
                rest_time=rest_time,
                notes=notes,
                order=order
            )
            
            # Adicionar ao banco de dados
            db.session.add(workout_exercise)
            db.session.commit()
            
            flash('Exercício adicionado com sucesso!', 'success')
            return redirect(url_for('workout_edit', workout_id=workout.id))
        
        # Verificar se é ação de remover exercício
        remove_id = request.form.get('remove_exercise_id')
        if remove_id:
            workout_exercise = WorkoutExercise.query.get(int(remove_id))
            if workout_exercise and workout_exercise.workout_id == workout.id:
                db.session.delete(workout_exercise)
                db.session.commit()
                flash('Exercício removido com sucesso!', 'success')
            return redirect(url_for('workout_edit', workout_id=workout.id))
    
    return render_template('workout_edit.html', 
                          workout=workout, 
                          client=client, 
                          exercises=exercises,
                          workout_exercises=workout_exercises)

@app.route('/assessment/new/<int:client_id>', methods=['GET', 'POST'])
def assessment_new(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    if request.method == 'POST':
        # Campos básicos atuais
        weight = request.form.get('weight')
        body_fat = request.form.get('body_fat')
        chest = request.form.get('chest')
        waist = request.form.get('waist')
        hips = request.form.get('hips')
        arms = request.form.get('arms')
        thighs = request.form.get('thighs')
        notes = request.form.get('notes')
        
        # Novas medidas antropométricas
        neck = request.form.get('neck')
        shoulders = request.form.get('shoulders')
        forearms = request.form.get('forearms')
        wrists = request.form.get('wrists')
        calves = request.form.get('calves')
        ankles = request.form.get('ankles')
        abdomen = request.form.get('abdomen')
        
        # Dobras cutâneas
        skinfold_triceps = request.form.get('skinfold_triceps')
        skinfold_biceps = request.form.get('skinfold_biceps')
        skinfold_subscapular = request.form.get('skinfold_subscapular')
        skinfold_suprailiac = request.form.get('skinfold_suprailiac')
        skinfold_abdominal = request.form.get('skinfold_abdominal')
        skinfold_thigh = request.form.get('skinfold_thigh')
        skinfold_calf = request.form.get('skinfold_calf')
        
        # Criar nova avaliação com todos os campos
        assessment = Assessment(
            client_id=client.id,
            weight=weight,
            body_fat=body_fat,
            chest=chest,
            waist=waist,
            hips=hips,
            arms=arms,
            thighs=thighs,
            
            # Novas medidas antropométricas
            neck=neck,
            shoulders=shoulders,
            forearms=forearms,
            wrists=wrists,
            calves=calves,
            ankles=ankles,
            abdomen=abdomen,
            
            # Dobras cutâneas
            skinfold_triceps=skinfold_triceps,
            skinfold_biceps=skinfold_biceps,
            skinfold_subscapular=skinfold_subscapular,
            skinfold_suprailiac=skinfold_suprailiac,
            skinfold_abdominal=skinfold_abdominal,
            skinfold_thigh=skinfold_thigh,
            skinfold_calf=skinfold_calf,
            
            notes=notes
        )
        
        # Processar uploads de fotos
        # Foto frontal
        if 'front_photo' in request.files and request.files['front_photo'].filename:
            front_photo = request.files['front_photo']
            if allowed_file(front_photo.filename):
                # Criar nome de arquivo seguro usando ID do cliente e timestamp
                filename = f"client_{client.id}_front_{int(datetime.utcnow().timestamp())}"
                extension = front_photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{filename}.{extension}"
                
                # Salvar o arquivo
                front_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                assessment.front_photo = filename
        
        # Foto lateral
        if 'side_photo' in request.files and request.files['side_photo'].filename:
            side_photo = request.files['side_photo']
            if allowed_file(side_photo.filename):
                # Criar nome de arquivo seguro
                filename = f"client_{client.id}_side_{int(datetime.utcnow().timestamp())}"
                extension = side_photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{filename}.{extension}"
                
                # Salvar o arquivo
                side_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                assessment.side_photo = filename
        
        # Foto posterior
        if 'back_photo' in request.files and request.files['back_photo'].filename:
            back_photo = request.files['back_photo']
            if allowed_file(back_photo.filename):
                # Criar nome de arquivo seguro
                filename = f"client_{client.id}_back_{int(datetime.utcnow().timestamp())}"
                extension = back_photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{filename}.{extension}"
                
                # Salvar o arquivo
                back_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                assessment.back_photo = filename
        
        # Salvar a avaliação no banco de dados
        db.session.add(assessment)
        db.session.commit()
        
        # Atualizar o peso do cliente
        client.weight = weight
        db.session.commit()
        
        return redirect(url_for('client_detail', client_id=client.id))
    
    # Passando a data atual para o template
    now = datetime.utcnow()
    
    return render_template('assessment_form.html', client=client, now=now)

# API Endpoints para aplicativo móvel
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    trainer = Trainer.query.filter_by(email=email).first()
    
    if trainer and check_password_hash(trainer.password, password):
        return jsonify({
            'success': True,
            'trainer_id': trainer.id,
            'name': trainer.name
        })
    
    return jsonify({
        'success': False,
        'message': 'Credenciais inválidas'
    })

@app.route('/api/clients/<int:trainer_id>')
def api_clients(trainer_id):
    clients = Client.query.filter_by(trainer_id=trainer_id).all()
    
    client_list = []
    for client in clients:
        client_list.append({
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'goal': client.goal
        })
    
    return jsonify(client_list)

@app.route('/api/workouts/<int:client_id>')
def api_workouts(client_id):
    workouts = Workout.query.filter_by(client_id=client_id).all()
    
    workout_list = []
    for workout in workouts:
        workout_exercises = WorkoutExercise.query.filter_by(workout_id=workout.id).order_by(WorkoutExercise.order).all()
        
        exercises = []
        for we in workout_exercises:
            exercise = Exercise.query.get(we.exercise_id)
            exercises.append({
                'id': exercise.id,
                'name': exercise.name,
                'sets': we.sets,
                'reps': we.reps,
                'rest_time': we.rest_time,
                'notes': we.notes
            })
        
        workout_list.append({
            'id': workout.id,
            'name': workout.name,
            'description': workout.description,
            'exercises': exercises
        })
    
    return jsonify(workout_list)

# Adicione estas rotas ao seu arquivo app.py

#@app.route('/exercises')
# def exercises():
#    if 'trainer_id' not in session:
#        return redirect(url_for('login'))
#    
#    exercises = Exercise.query.all()
#    return render_template('exercises.html', exercises=exercises)
@app.route('/exercises')
def exercises():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of exercises per page
    
    # Get filter parameters
    search_term = request.args.get('search', '')
    muscle_group = request.args.get('muscle', '')
    
    # Build the query
    query = Exercise.query
    
    # Apply filters if provided
    if search_term:
        query = query.filter(Exercise.name.ilike(f'%{search_term}%'))
    if muscle_group:
        query = query.filter(Exercise.muscle_group == muscle_group)
    
    # Get the total number of exercises matching the filters
    total_exercises = query.count()
    
    # Calculate total pages
    total_pages = ceil(total_exercises / per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    # Get paginated exercises
    exercises = query.order_by(Exercise.name).offset((page-1)*per_page).limit(per_page).all()
    
    # Get list of all muscle groups for filter dropdown
    muscle_groups = db.session.query(Exercise.muscle_group).distinct().all()
    muscle_groups = [group[0] for group in muscle_groups]
    
    return render_template(
        'exercises.html', 
        exercises=exercises, 
        page=page, 
        total_pages=total_pages,
        per_page=per_page,
        total_exercises=total_exercises,
        search_term=search_term,
        selected_muscle=muscle_group,
        muscle_groups=muscle_groups
    )





@app.route('/exercise/new', methods=['POST'])
def exercise_new():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        muscle_group = request.form.get('muscle_group')
        
        # Determinar qual URL de mídia usar com base no tipo selecionado
        media_type = request.form.get('media_type')
        if media_type == 'youtube':
            video_url = request.form.get('video_url')
        elif media_type == 'shorts':
            video_url = request.form.get('shorts_url')
        elif media_type == 'gif':
            video_url = request.form.get('gif_url')
        else:
            video_url = ''
        
        exercise = Exercise(
            name=name,
            description=description,
            muscle_group=muscle_group,
            video_url=video_url
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        return redirect(url_for('exercises'))
    
    return redirect(url_for('exercises'))

@app.route('/exercise/<int:exercise_id>')
def exercise_detail(exercise_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify({
        'id': exercise.id,
        'name': exercise.name,
        'description': exercise.description,
        'muscle_group': exercise.muscle_group,
        'video_url': exercise.video_url
    })

@app.route('/exercise/edit/<int:exercise_id>', methods=['GET', 'POST'])
def exercise_edit(exercise_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'POST':
        exercise.name = request.form.get('name')
        exercise.description = request.form.get('description')
        exercise.muscle_group = request.form.get('muscle_group')
        
        # Determinar qual URL de mídia usar com base no tipo selecionado
        media_type = request.form.get('media_type')
        if media_type == 'youtube':
            exercise.video_url = request.form.get('video_url')
        elif media_type == 'shorts':
            exercise.video_url = request.form.get('shorts_url')
        elif media_type == 'gif':
            exercise.video_url = request.form.get('gif_url')
        
        db.session.commit()
        return redirect(url_for('exercises'))
    
    return render_template('exercise_edit.html', exercise=exercise)

# Adicione estas rotas ao seu arquivo app.py

@app.route('/client/user/<int:client_id>', methods=['GET', 'POST'])
def client_user_manage(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    # Buscar usuário existente ou criar um novo
    client_user = ClientUser.query.filter_by(client_id=client_id).first()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificar se o username já existe (exceto para o usuário atual)
        existing_user = ClientUser.query.filter_by(username=username).first()
        if existing_user and existing_user.client_id != client_id:
            return render_template('client_user.html', client=client, client_user=client_user, error='Nome de usuário já existe')
        
        if client_user:
            # Atualizar usuário existente
            client_user.username = username
            if password:  # Só atualiza a senha se uma nova for fornecida
                client_user.password = generate_password_hash(password)
        else:
            # Criar novo usuário
            client_user = ClientUser(
                username=username,
                password=generate_password_hash(password),
                client_id=client_id
            )
            db.session.add(client_user)
        
        db.session.commit()
        return redirect(url_for('client_detail', client_id=client_id))
    
    return render_template('client_user.html', client=client, client_user=client_user)

# Rotas para login e acesso do cliente
@app.route('/aluno/login', methods=['GET', 'POST'])
def client_login():
    if 'client_id' in session:
        return redirect(url_for('client_dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = ClientUser.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['client_id'] = user.client_id
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('client_dashboard'))
        else:
            error = 'Nome de usuário ou senha incorretos'
    
    return render_template('client_login.html', error=error)

@app.route('/aluno/logout')
def client_logout():
    return redirect(url_for('logout'))

@app.route('/aluno/dashboard')
def client_dashboard():
    if 'client_id' not in session:
        return redirect(url_for('client_login'))
    
    client = Client.query.get(session['client_id'])
    workouts = Workout.query.filter_by(client_id=client.id).all()
    
    return render_template('client_dashboard.html', client=client, workouts=workouts)

@app.route('/aluno/treino/<int:workout_id>')
def client_workout_view(workout_id):
    if 'client_id' not in session:
        return redirect(url_for('client_login'))
    
    workout = Workout.query.get_or_404(workout_id)
    
    # Verifica se o treino pertence ao cliente logado
    if workout.client_id != session['client_id']:
        return redirect(url_for('client_dashboard'))
    
    workout_exercises = WorkoutExercise.query.filter_by(workout_id=workout.id).order_by(WorkoutExercise.order).all()
    
    return render_template('client_workout_view.html', workout=workout, workout_exercises=workout_exercises)

@app.route('/aluno/exercicio/<int:exercise_id>')
def client_exercise_view(exercise_id):
    if 'client_id' not in session:
        return redirect(url_for('client_login'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Buscar exercícios relacionados (mesmo grupo muscular, exceto o atual)
    related_exercises = Exercise.query.filter(
        Exercise.muscle_group == exercise.muscle_group,
        Exercise.id != exercise.id
    ).limit(4).all()
    
    return render_template('client_exercise_view.html', exercise=exercise, related_exercises=related_exercises)

@app.route('/assessment/<int:assessment_id>')
def assessment_view(assessment_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    assessment = Assessment.query.get_or_404(assessment_id)
    client = Client.query.get(assessment.client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    return render_template('assessment_view.html', assessment=assessment, client=client)

@app.route('/client/<int:client_id>/assessments/compare', methods=['GET', 'POST'])
def assessment_compare(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    # Obter todas as avaliações do cliente, ordenadas por data
    assessments = Assessment.query.filter_by(client_id=client.id).order_by(Assessment.date.desc()).all()
    
    before = None
    after = None
    before_id = None
    after_id = None
    
    if request.method == 'POST':
        before_id = request.form.get('before_assessment', type=int)
        after_id = request.form.get('after_assessment', type=int)
        
        if before_id and after_id:
            before = Assessment.query.get(before_id)
            after = Assessment.query.get(after_id)
    
    return render_template('assessment_compare.html', 
                           client=client, 
                           assessments=assessments, 
                           before=before, 
                           after=after, 
                           before_id=before_id, 
                           after_id=after_id)

@app.route('/client/delete/<int:client_id>', methods=['POST'])
def client_delete(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    try:
        # Excluir todas as avaliações e suas fotos
        assessments = Assessment.query.filter_by(client_id=client.id).all()
        for assessment in assessments:
            # Remover arquivos de fotos, se existirem
            if assessment.front_photo:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], assessment.front_photo))
                except Exception as e:
                    print(f"Erro ao excluir foto frontal: {e}")
            
            if assessment.side_photo:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], assessment.side_photo))
                except Exception as e:
                    print(f"Erro ao excluir foto lateral: {e}")
            
            if assessment.back_photo:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], assessment.back_photo))
                except Exception as e:
                    print(f"Erro ao excluir foto posterior: {e}")
            
            db.session.delete(assessment)
        
        # Excluir todos os treinos e exercícios relacionados
        workouts = Workout.query.filter_by(client_id=client.id).all()
        for workout in workouts:
            # Excluir exercícios do treino
            WorkoutExercise.query.filter_by(workout_id=workout.id).delete()
            db.session.delete(workout)
        
        # Excluir registros de presença
        Attendance.query.filter_by(client_id=client.id).delete()
        
        # Excluir credenciais de acesso
        client_user = ClientUser.query.filter_by(client_id=client.id).first()
        if client_user:
            db.session.delete(client_user)
        
        # Por fim, excluir o cliente
        client_name = client.name  # Guarda o nome para usar na mensagem
        db.session.delete(client)
        db.session.commit()
        
        flash(f'Cliente {client_name} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir cliente: {e}")
        flash('Ocorreu um erro ao excluir o cliente.', 'error')
    
    # Redirecionando para a página de clientes
    return redirect(url_for('client_list'))


@app.route('/admin/trainer/<int:trainer_id>/toggle_status', methods=['POST'])
def toggle_trainer_status(trainer_id):
    # Verificar autenticação de administrador
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    trainer = Trainer.query.get_or_404(trainer_id)
    action = request.form.get('action')
    
    if action == 'activate':
        trainer.is_active = True
        message = f'A conta do personal trainer {trainer.name} foi reativada com sucesso.'
    elif action == 'deactivate':
        trainer.is_active = False
        message = f'A conta do personal trainer {trainer.name} foi desativada com sucesso.'
    else:
        flash('Ação inválida.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db.session.commit()
        flash(message, 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))






@app.route('/workout-templates')
def workout_templates():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    trainer_id = session['trainer_id']
    templates = WorkoutTemplate.query.filter_by(trainer_id=trainer_id).all()
    
    return render_template('workout_templates.html', templates=templates)

@app.route('/workout-template/new', methods=['GET', 'POST'])
def workout_template_new():
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        template = WorkoutTemplate(
            name=name,
            description=description,
            trainer_id=session['trainer_id']
        )
        
        db.session.add(template)
        db.session.commit()
        
        return redirect(url_for('workout_template_edit', template_id=template.id))
    
    return render_template('workout_template_form.html')



@app.route('/workout-template/edit/<int:template_id>', methods=['GET', 'POST'])
def workout_template_edit(template_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    template = WorkoutTemplate.query.get_or_404(template_id)
    
    # Verificar se o template pertence ao trainer logado
    if template.trainer_id != session['trainer_id']:
        return redirect(url_for('workout_templates'))
    
    # Obter todos os exercícios disponíveis
    exercises = Exercise.query.all()
    
    # Obter exercícios já adicionados ao template
    template_exercises = WorkoutTemplateExercise.query.filter_by(template_id=template.id).order_by(WorkoutTemplateExercise.order).all()
    
    if request.method == 'POST':
        # Verificar se é ação de adicionar exercício
        exercise_id = request.form.get('exercise_id')
        
        if exercise_id:
            exercise_id = int(exercise_id)
            sets = int(request.form.get('sets', 3))
            reps = request.form.get('reps', '12')
            rest_time = int(request.form.get('rest_time', 60))
            notes = request.form.get('notes', '')
            order = int(request.form.get('order', len(template_exercises) + 1))
            
            # Verificar se o exercício existe
            exercise = Exercise.query.get(exercise_id)
            if not exercise:
                flash('Exercício não encontrado.', 'error')
                return redirect(url_for('workout_template_edit', template_id=template.id))
            
            # Criar novo exercício de template
            template_exercise = WorkoutTemplateExercise(
                template_id=template.id,
                exercise_id=exercise_id,
                sets=sets,
                reps=reps,
                rest_time=rest_time,
                notes=notes,
                order=order
            )
            
            # Adicionar ao banco de dados
            db.session.add(template_exercise)
            db.session.commit()
            
            flash('Exercício adicionado com sucesso!', 'success')
            return redirect(url_for('workout_template_edit', template_id=template.id))
        
        # Verificar se é ação de remover exercício
        remove_id = request.form.get('remove_exercise_id')
        if remove_id:
            template_exercise = WorkoutTemplateExercise.query.get(int(remove_id))
            if template_exercise and template_exercise.template_id == template.id:
                db.session.delete(template_exercise)
                db.session.commit()
                flash('Exercício removido com sucesso!', 'success')
            return redirect(url_for('workout_template_edit', template_id=template.id))
    
    return render_template('workout_template_edit.html', 
                          template=template, 
                          exercises=exercises,
                          template_exercises=template_exercises)


@app.route('/workout-template/update/<int:template_id>', methods=['POST'])
def workout_template_update(template_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    template = WorkoutTemplate.query.get_or_404(template_id)
    
    # Verificar se o template pertence ao trainer logado
    if template.trainer_id != session['trainer_id']:
        return redirect(url_for('workout_templates'))
    
    if request.method == 'POST':
        template.name = request.form.get('name')
        template.description = request.form.get('description')
        template.category = request.form.get('category', '')
        
        db.session.commit()
        flash('Template atualizado com sucesso!', 'success')
    
    return redirect(url_for('workout_template_edit', template_id=template.id))


@app.route('/workout-template/duplicate/<int:template_id>', methods=['POST'])
def workout_template_duplicate(template_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    original_template = WorkoutTemplate.query.get_or_404(template_id)
    
    # Verificar se o template pertence ao trainer logado
    if original_template.trainer_id != session['trainer_id']:
        return redirect(url_for('workout_templates'))
    
    if request.method == 'POST':
        # Criar novo template baseado no original
        new_template = WorkoutTemplate(
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=original_template.category,
            trainer_id=session['trainer_id']
        )
        
        db.session.add(new_template)
        db.session.flush()  # Para obter o ID do novo template
        
        # Copiar os exercícios do template original
        original_exercises = WorkoutTemplateExercise.query.filter_by(template_id=original_template.id).all()
        
        for orig_exercise in original_exercises:
            new_exercise = WorkoutTemplateExercise(
                template_id=new_template.id,
                exercise_id=orig_exercise.exercise_id,
                sets=orig_exercise.sets,
                reps=orig_exercise.reps,
                rest_time=orig_exercise.rest_time,
                notes=orig_exercise.notes,
                order=orig_exercise.order
            )
            db.session.add(new_exercise)
        
        db.session.commit()
        flash(f'Template duplicado com sucesso!', 'success')
        
        return redirect(url_for('workout_template_edit', template_id=new_template.id))
    
    return redirect(url_for('workout_templates'))



@app.route('/apply-template/<int:template_id>/<int:client_id>', methods=['POST'])
def apply_template(template_id, client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    template = WorkoutTemplate.query.get_or_404(template_id)
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o trainer tem permissão
    if template.trainer_id != session['trainer_id'] or client.trainer_id != session['trainer_id']:
        flash('Você não tem permissão para realizar esta ação.', 'error')
        return redirect(url_for('client_detail', client_id=client_id))
    
    # Criar novo treino baseado no template
    new_workout = Workout(
        name=template.name,
        description=template.description,
        client_id=client_id
    )
    db.session.add(new_workout)
    db.session.flush()  # Para obter o ID do novo treino
    
    # Copiar os exercícios do template para o novo treino
    for template_exercise in template.exercises:
        workout_exercise = WorkoutExercise(
            workout_id=new_workout.id,
            exercise_id=template_exercise.exercise_id,
            sets=template_exercise.sets,
            reps=template_exercise.reps,
            rest_time=template_exercise.rest_time,
            notes=template_exercise.notes,
            order=template_exercise.order
        )
        db.session.add(workout_exercise)
    
    db.session.commit()
    flash(f'Template "{template.name}" aplicado com sucesso ao cliente {client.name}!', 'success')
    
    return redirect(url_for('workout_edit', workout_id=new_workout.id))


@app.route('/workout-template/delete/<int:template_id>', methods=['POST'])
def workout_template_delete(template_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    template = WorkoutTemplate.query.get_or_404(template_id)
    
    # Verificar se o template pertence ao trainer logado
    if template.trainer_id != session['trainer_id']:
        flash('Você não tem permissão para excluir este template.', 'error')
        return redirect(url_for('workout_templates'))
    
    try:
        # Primeiro excluir todos os exercícios relacionados a este template
        WorkoutTemplateExercise.query.filter_by(template_id=template.id).delete()
        
        # Agora excluir o próprio template
        template_name = template.name  # Guardar o nome para usar na mensagem
        db.session.delete(template)
        db.session.commit()
        
#        flash(f'Template "{template_name}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
#        flash(f'Erro ao excluir template: {str(e)}', 'error')
    
    return redirect(url_for('workout_templates'))



@app.route('/api/exercise-load/<int:exercise_id>', methods=['GET'])
def get_exercise_loads(exercise_id):
    if 'client_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    client_id = session['client_id']
    
    try:
        # Buscar o histórico de cargas para este exercício específico
        loads = ExerciseLoad.query.filter_by(
            client_id=client_id, 
            exercise_id=exercise_id  # Este filtro é crucial para mostrar apenas cargas do exercício atual
        ).order_by(ExerciseLoad.date.desc()).limit(10).all()
        
        loads_data = []
        for load in loads:
            loads_data.append({
                'id': load.id,
                'date': load.date.strftime('%d/%m/%Y'),
                'weight': load.weight,
                'reps_done': load.reps_done,
                'notes': load.notes
            })
        
        return jsonify({'success': True, 'loads': loads_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exercise-load/save', methods=['POST'])
def save_exercise_load():
    if 'client_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
    data = request.json
    client_id = session['client_id']
    exercise_id = data.get('exercise_id')
    weight = data.get('weight')
    reps_done = data.get('reps_done', '')
    notes = data.get('notes', '')
    
    if not exercise_id or not weight:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    
    try:
        exercise_load = ExerciseLoad(
            client_id=client_id,
            exercise_id=exercise_id,
            weight=weight,
            reps_done=reps_done,
            notes=notes
        )
        
        db.session.add(exercise_load)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Carga registrada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    




@app.route('/client/edit/<int:client_id>', methods=['GET', 'POST'])
def client_edit(client_id):
    if 'trainer_id' not in session:
        return redirect(url_for('login'))
    
    client = Client.query.get_or_404(client_id)
    
    # Verificar se o cliente pertence ao trainer logado
    if client.trainer_id != session['trainer_id']:
        return redirect(url_for('clients'))
    
    if request.method == 'POST':
        # Obter os dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age') or None
        height = request.form.get('height') or None
        weight = request.form.get('weight') or None
        goal = request.form.get('goal')
        health_notes = request.form.get('health_notes')
        
        # Validação básica
        if not name or not email or not phone:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('client_edit.html', client=client)
        
        try:
            # Atualizar os dados do cliente
            client.name = name
            client.email = email
            client.phone = phone
            client.age = age
            client.height = height
            client.weight = weight
            client.goal = goal
            client.health_notes = health_notes
            
            # Salvar no banco de dados
            db.session.commit()
            
            # Mensagem de sucesso
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('client_detail', client_id=client.id))
            
        except Exception as e:
            # Em caso de erro, desfaz as alterações
            db.session.rollback()
            print(f"Erro ao atualizar cliente: {e}")
            flash('Erro ao atualizar os dados do cliente.', 'error')
    
    # Se for uma requisição GET ou em caso de erro, mostra o formulário
    return render_template('client_edit.html', client=client)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)