from flask import request, redirect, url_for, render_template, Blueprint, current_app, g, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db, celery, mail, Message, login_manager
from app.models import Subscription, User 

subscriptions_blueprint = Blueprint('subscriptions', __name__, template_folder='templates')

@subscriptions_blueprint.route('/subscriptions')
@login_required
def subscriptions():
    subscrs = Subscription.query.filter_by(user_id=current_user.id).all()
    return render_template('subscriptions.html', subscrs = subscrs)


@subscriptions_blueprint.route('/subscriptions/new')
@login_required
def subscriptions_add():
    if current_user.subscr_left > 0:
        newsubscr = Subscription(user_id = current_user.id)
        user = User.query.filter(User.id==current_user.id).first()
        user.subscr_left = current_user.subscr_left - 1
        db.session.add(user)
        db.session.add(newsubscr)
        db.session.commit()
        flash("Subscription {sub} added, you have {numsubscr} subscriptions left".format(sub=newsubscr.id, numsubscr=user.subscr_left), 'success')
    else:
        flash("You have no subscriptions left, upgrade your plan to get more", 'warning')
    return redirect(url_for('subscriptions.subscriptions'))


@subscriptions_blueprint.route('/subscriptions/edit/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def subscriptions_edit(sub_id):
    sub = Subscription.query.filter(Subscription.id == sub_id, Subscription.user_id == current_user.id).first()
    if sub is not None:
        # edit
        # add
        flash("Subscription %s edited" % sub.id, 'success')

        db.session.add(sub)
        db.session.commit()
    else:
        flash("Subscription %s not found" % sub_id, 'info')
    return redirect(url_for('subscriptions.subscriptions'))


@subscriptions_blueprint.route('/subscriptions/delete/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def subscriptions_delete(sub_id):
    sub = Subscription.query.filter(Subscription.id == sub_id, Subscription.user_id == current_user.id).first()
    if sub is not None:
        flash("Subscription %s deleted" % sub.id, 'success')
        db.session.delete(sub)
        db.session.commit()
    else:
        flash("Subscription %s not found" % sub_id, 'info')

    return redirect(url_for('subscriptions.subscriptions'))
