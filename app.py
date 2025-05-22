
import os
import logging
from tempfile import mkdtemp
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from werkzeug.utils import secure_filename
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

# Configuration for file uploads
UPLOAD_FOLDER = mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkout')
def checkout():
    stripe_public_key = os.environ.get('VITE_STRIPE_PUBLIC_KEY')
    return render_template('checkout.html', stripe_public_key=stripe_public_key)

@app.route('/payment-success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/upload-cv', methods=['POST'])
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
def create_payment_intent():
    try:
        # Cena za generowanie CV: 9.99 PLN (999 groszy)
        amount = 999  # w groszach
        
        # Tworzenie Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='pln',
            metadata={
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
