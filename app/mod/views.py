from flask import render_template, request, redirect, url_for, session, flash
from . import mod
# from .forms import 
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Users, Recommendation, Comments, RecModerations, ComModerations
from .. import db
from ..email import send_email
from ..decorators import is_moderator
import json

@mod.route('/_moderate')
@login_required
@is_moderator
def moderate_ajax():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    if verify == 'true':
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 2
        db.session.add(rec)
        db.session.commit()
        return json.dumps({'verified':True}), 200, {'ContentType':'application/json'} 
    else:
        rec = Recommendation.query.filter_by(id=id).first_or_404()
        rec.verification = 0
        rec.made_private = True
        db.session.add(rec)
        db.session.commit()
        return json.dumps({'verified':False}), 200, {'ContentType':'application/json'} 

@mod.route('/_verify')
@login_required
@is_moderator
def verify_ajax():
    session['offset'] += current_user.display
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .offset(session['offset'])\
        .limit(current_user.display)
    return render_template('ajax/modpostajax.html', display = display_recs)

@mod.route('/verify')
@login_required
@is_moderator
def verify():
    session['offset'] = 0
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(Recommendation.timestamp.asc())\
        .limit(current_user.display)
    return render_template('mod/verify_recs.html', display=display_recs)

@mod.route('/_moderate_com')
@login_required
@is_moderator
def moderate_com_ajax():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    if verify == 'true':
        com = Comments.query.filter_by(id=id).first_or_404()
        com.verification = 2
        db.session.add(com)
        db.session.commit()
        return json.dumps({'verified':True}), 200, {'ContentType':'application/json'} 
    else:
        com = Comments.query.filter_by(id=id).first_or_404()
        com.verificition = 0
        db.session.add(com)
        db.session.commit()
        return json.dumps({'verified':False}), 200, {'ContentType':'application/json'} 

@mod.route('/_verify_comments')    
@login_required
@is_moderator
def verify_com_ajax():
    session['offset'] += current_user.display
    display_comments = Comments.query\
        .filter(Comments.verification == 1)\
        .order_by(Comments.timestamp.asc())\
        .offset(session['offset'])\
        .limit(current_user.display)
    return render_template('ajax/modcommentajax.html', d_c = display_comments)

@mod.route('/verify_comments')
@login_required
@is_moderator
def verify_comments():
    session['offest'] = 0
    display_comments = Comments.query\
        .filter(Comments.verification == 1)\
        .order_by(Comments.timestamp.asc())\
        .limit(current_user.display)
    return render_template('mod/verify_comments.html', d_c=display_comments)