from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app.extensions import mail, db
from app.models import SentEmail, User
from app.forms import RegistrationForm, LoginForm
import smtplib

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/send_email', methods=['POST'])
def send_email():
    email = request.form.get('email')
    name = request.form.get('name')
    subject = "Follow-Up Email"
    body = f"Hello {name}, this is your automated follow-up email."

    msg = Message(subject, sender='nakole.9597@gmail.com', recipients=[email])
    msg.body = body
    
    try:
        mail.send(msg)
        
        # Save to database
        new_email = SentEmail(
            recipient=email,
            subject=subject,
            body=body
        )
        db.session.add(new_email)
        db.session.commit()
        
        return redirect(url_for('main.emails'))
    except smtplib.SMTPException as e:
        print(f"Email sending error: {e}")
        flash("An error occurred while sending the email. Please try again later.", "danger")
        return redirect(url_for('main.home'))

@bp.route('/success')
def success():
    return render_template('success.html')

@bp.route('/emails')
@login_required
def emails():
    all_emails = SentEmail.query.order_by(SentEmail.timestamp.desc()).all()
    return render_template('emails.html', emails=all_emails)

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@bp.route('/templates')
@login_required
def templates():
    # everyone always sees the built-in free templates
    free_templates = EmailTemplate.query.filter_by(is_pro=False).all()

    # Pro users additionally see Pro templates (and any they’ve created)
    if current_user.is_pro:
        pro_templates = EmailTemplate.query.filter_by(is_pro=True).all()
    else:
        pro_templates = []

    return render_template(
        'templates.html',
        free_templates=free_templates,
        pro_templates=pro_templates
    )