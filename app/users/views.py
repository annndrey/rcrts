import datetime
from flask import request, redirect, url_for, render_template, Blueprint, current_app, g, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db, celery, mail, Message, login_manager
from app.models import User, TariffPlan
from passlib.hash import sha512_crypt
from itsdangerous import URLSafeTimedSerializer

users_blueprint = Blueprint('users', __name__, template_folder='templates')

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('subscriptions.subscriptions'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(login = username).first()
        if not user:
            error = 'Invalid user'
            flash(error, 'warning')
        elif not user.verify_password(password):
            error = 'Wrong password'
            flash(error, 'warning')
        else:
            if user.is_confirmed and user.is_active:
                login_user(user)
                return redirect(url_for('subscriptions.subscriptions'))
            else:
                error = 'User is not confirmed, check your mail'
                flash(error, 'warning')

    return render_template('login.html')

@users_blueprint.route("/register", methods=['GET', 'POST',])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('subscriptions.subscriptions'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 4:
            error = 'Password too short'
            flash(error, 'warning')
            return render_template('register.html')

        user = User.query.filter_by(login = username).first()
        if user is not None:
            error = 'Login already taken'
            flash(error, 'warning')
        else:
            try:
                freeplan = TariffPlan.query.filter(TariffPlan.price==0).first()
                user = User(login=username, plan_id = freeplan.id, subscr_left=freeplan.subscr_num)
                user.hash_password(password)
                user.registered_on = datetime.datetime.now()
                db.session.add(user)
                db.session.commit()
                token = generate_confirmation_token(user.login)
                flash('Confirmation link is sent to your email', 'info')
                # send confirmation email with celery
                send_async_email.delay([user.login,], url_for('users.activate', token=token, _external=True))
                
                return redirect(url_for('users.login'))

            except AssertionError as er:
                flash(er, 'warning')

    return render_template('register.html')


@users_blueprint.route("/confirm/<token>", methods=['GET',])
def activate(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(login=email).first_or_404()
    if user.is_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('users.login'))


@users_blueprint.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        
    return redirect(url_for('users.login'))


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False

    return email

@celery.task
def send_async_email(recipients, link):
    """Background task to send an email with Flask-Mail."""
    subject = "Confirmation email for trololo.info"
    sender = 'noreply@trololo.info'
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = 'You can activate your account here: %s' % link
    with app.app_context():
        mail.send(msg)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

