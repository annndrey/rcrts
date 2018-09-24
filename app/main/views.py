from flask import render_template, Blueprint

mainpage_blueprint = Blueprint('main', __name__, template_folder='templates')

@mainpage_blueprint.route('/')
def index():
    return render_template('main.html')
