from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, Message
from celery import Celery
import click



app = Flask(__name__, instance_relative_config=True)
app.config.from_envvar('APPSETTINGS')
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db) 
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
mail = Mail(app)

from app.users.views import users_blueprint
from app.subscriptions.views import subscriptions_blueprint
from app.main.views import mainpage_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(subscriptions_blueprint)
app.register_blueprint(mainpage_blueprint)


@app.cli.command()
@click.option('--price', default=0, help='Tariff price')
@click.option('--name', default="Default tariff plan", help='Tariff plan name')
@click.option('--descr', default="Description", help='Tariff plan description')
@click.option('--numsubscr', default=4, help='Number of subscriptions included')
def add_tariff(price, name, descr, numsubscr):
    """ Create new tariff plan"""
    from app.models import TariffPlan
    newplan = TariffPlan(name=name, price=price, description=descr, subscr_num=numsubscr)
    db.session.add(newplan)
    db.session.commit()
    print("New tariff plan added", newplan)

@app.cli.command()
@click.option('--userid', help='User id')
@click.option('--numsubscr', default=1, help='Number of subscriptions to add')
def add_subscr(userid, numsubscr):
    from app.models import User
    user = User.query.filter(User.id==userid).first()
    if user is not None:
        user.subscr_left =  user.subscr_left + numsubscr
        db.session.add(user)
        db.session.commit()
        print("%s subscriptions added" % numsubscr)
