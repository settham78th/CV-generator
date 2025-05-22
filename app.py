
import os
import logging
from tempfile import mkdtemp
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from email_validator import validate_email, EmailNotValidError
import uuid
import stripe
from utils.pdf_extraction import extract_text_from_pdf
from utils.openrouter_api import (
    optimize_cv, generate_recruiter_feedback,
    generate_cover_letter, analyze_job_url,
    ats_optimization_check, generate_interview_questions,
    analyze_cv_strengths
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'

# Configuration for file uploads
UPLOAD_FOLDER = mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Walidacja danych
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Wszystkie pola są wymagane.'}), 400
            flash('Wszystkie pola są wymagane.')
            return render_template('register.html')
        
        # Sprawdzenie czy email jest poprawny
        try:
            validate_email(email)
        except EmailNotValidError:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nieprawidłowy adres email.'}), 400
            flash('Nieprawidłowy adres email.')
            return render_template('register.html')
        
        # Sprawdzenie czy użytkownik już istnieje
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nazwa użytkownika już istnieje.'}), 400
            flash('Nazwa użytkownika już istnieje.')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email już jest zarejestrowany.'}), 400
            flash('Email już jest zarejestrowany.')
            return render_template('register.html')
        
        # Utworzenie nowego użytkownika
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Konto zostało utworzone pomyślnie!'})
            flash('Konto zostało utworzone pomyślnie!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': 'Błąd podczas tworzenia konta.'}), 500
            flash('Błąd podczas tworzenia konta.')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nazwa użytkownika i hasło są wymagane.'}), 400
            flash('Nazwa użytkownika i hasło są wymagane.')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': 'Zalogowano pomyślnie!'})
            flash('Zalogowano pomyślnie!')
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nieprawidłowa nazwa użytkownika lub hasło.'}), 401
            flash('Nieprawidłowa nazwa użytkownika lub hasło.')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkout')
@login_required
def checkout():
    stripe_public_key = os.environ.get('VITE_STRIPE_PUBLIC_KEY')
    return render_template('checkout.html', stripe_public_key=stripe_public_key)

@app.route('/payment-success')
@login_required
def payment_success():
    # Sprawdzenie czy płatność została zakończona
    payment_intent_id = request.args.get('payment_intent')
    if payment_intent_id:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                session['payment_verified'] = True
                session['payment_intent_id'] = payment_intent_id
                flash('Płatność zakończona sukcesem! Możesz teraz wygenerować CV.', 'success')
            else:
                flash('Płatność nie została zakończona pomyślnie.', 'error')
        except Exception as e:
            flash('Błąd podczas weryfikacji płatności.', 'error')
    
    return redirect(url_for('index'))

@app.route('/init-db')
def init_db():
    """Inicjalizacja bazy danych"""
    try:
        db.create_all()
        return jsonify({'success': True, 'message': 'Baza danych została zainicjalizowana.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Błąd inicjalizacji: {str(e)}'}), 500

@app.route('/upload-cv', methods=['POST'])
@login_required
def upload_cv():
    if 'cv_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['cv_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Save the file
        file.save(file_path)

        try:
            # Extract text from PDF
            cv_text = extract_text_from_pdf(file_path)

            # Store CV text in session
            session['cv_text'] = cv_text
            session['original_filename'] = filename

            # Remove the file after extraction
            os.remove(file_path)

            return jsonify({
                'success': True,
                'cv_text': cv_text,
                'message': 'CV successfully uploaded and text extracted.'
            })

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                'success': False,
                'message': f"Error processing PDF: {str(e)}"
            }), 500

    return jsonify({
        'success': False,
        'message': 'Invalid file type. Please upload a PDF file.'
    }), 400

@app.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        # Cena za generowanie CV: 9.99 PLN (999 groszy)
        amount = 999  # w groszach
        
        # Tworzenie Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='pln',
            metadata={
                'user_id': current_user.id,
                'user_email': current_user.email,
                'service': 'cv_optimization'
            }
        )
        
        return jsonify({
            'success': True,
            'client_secret': intent.client_secret,
            'amount': amount
        })
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Błąd podczas tworzenia płatności: {str(e)}"
        }), 500

@app.route('/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return jsonify({
                'success': False,
                'message': 'Brak ID płatności'
            }), 400
        
        # Sprawdzenie statusu płatności
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Płatność zakończona sukcesem - zapisz w sesji
            session['payment_verified'] = True
            session['payment_intent_id'] = payment_intent_id
            
            return jsonify({
                'success': True,
                'message': 'Płatność zakończona sukcesem! Możesz teraz wygenerować CV.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Płatność nie została zakończona'
            }), 400
            
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Błąd podczas weryfikacji płatności: {str(e)}"
        }), 500

@app.route('/process-cv', methods=['POST'])
@login_required
def process_cv():
    # Sprawdzenie czy płatność została zweryfikowana
    if not session.get('payment_verified'):
        return jsonify({
            'success': False,
            'message': 'Aby wygenerować CV, musisz najpierw dokonać płatności.',
            'payment_required': True
        }), 402  # Payment Required
    
    data = request.json
    cv_text = data.get('cv_text') or session.get('cv_text')
    job_url = data.get('job_url', '')
    selected_option = data.get('selected_option', '')
    roles = data.get('roles', [])

    if not cv_text:
        return jsonify({
            'success': False,
            'message': 'No CV text found. Please upload a CV first.'
        }), 400

    # Process Job URL if provided
    extracted_job_description = ''
    if job_url:
        try:
            extracted_job_description = analyze_job_url(job_url)
        except Exception as e:
            logger.error(f"Error extracting job description from URL: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Error extracting job description from URL: {str(e)}"
            }), 500

    try:
        job_description = data.get('job_description', extracted_job_description)
        result = None

        options_handlers = {
            'optimize': optimize_cv,
            'feedback': generate_recruiter_feedback,
            'cover_letter': generate_cover_letter,
            'ats_check': ats_optimization_check,
            'interview_questions': generate_interview_questions
        }

        if selected_option not in options_handlers:
            return jsonify({
                'success': False,
                'message': 'Invalid option selected.'
            }), 400

        result = options_handlers[selected_option](cv_text, job_description)

        return jsonify({
            'success': True,
            'result': result,
            'job_description': extracted_job_description if extracted_job_description else None
        })

    except Exception as e:
        logger.error(f"Error processing CV: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error processing request: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
