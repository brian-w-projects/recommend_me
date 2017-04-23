from flask import get_template_attribute, jsonify, render_template, request
from . import mod
from .. import db
from ..decorators import is_moderator
from ..models import Comment, Com_Moderation, Rec_Moderation, Recommendation
from flask_login import login_required, current_user
from flask_moment import _moment
from sqlalchemy.sql.expression import asc

@mod.route('/-moderate-comments')
@login_required
@is_moderator
def moderate_com():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = ComModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    com = Comments.query\
        .filter_by(id=id)\
        .first_or_404()
    if verify == 'true':
        com.verification = 2
        db.session.add(com)
        db.session.commit()
    else:
        com.verificition = 0
        db.session.add(com)
        db.session.commit()
    return jsonify({'verify': verify == 'true'})

@mod.route('/-verify-comments')    
@login_required
@is_moderator
def verify_com_ajax():
    page = int(request.args.get('page'))
    display_comments = Comments.query\
        .filter_by(verification=1)\
        .order_by(asc(Comments.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/moderator/mod-comment-macro.html', 'ajax')
    return jsonify({
        'last': display_comments.pages in (0, display_comments.page),
        'ajax_request': to_return(display_comments, _moment, current_user)}) 

@mod.route('/verify-comments')
@login_required
@is_moderator
def verify_comments():
    display_comments = Comments.query\
        .filter_by(verification=1)\
        .order_by(asc(Comments.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-comments.html', d_c=display_comments)

@mod.route('/-moderate-recs')
@login_required
@is_moderator
def moderate_recs():
    id = request.args.get('id')
    verify = request.args.get('verify')
    new_mod = RecModerations(mod_by=current_user.id, mod_on=id, action=verify)
    db.session.add(new_mod)
    rec = Recommendation.query\
            .filter_by(id=id)\
            .first_or_404()
    if verify == 'true':
        rec.verification = 2
        db.session.add(rec)
        db.session.commit()
    else:
        rec.verification = 0
        rec.made_private = True
        db.session.add(rec)
        db.session.commit()
    return jsonify({'verify': verify=='true'})

@mod.route('/-verify-recs')
@login_required
@is_moderator
def verify_recs_ajax():
    page = int(request.args.get('page'))
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(asc(Recommendation.timestamp))\
        .paginate(page, per_page=current_user.display, error_out=False)
    to_return = get_template_attribute('macros/moderator/mod-rec-macro.html', 'ajax')        
    return jsonify({
        'last': display_recs.pages in (0, display_recs.page),
        'ajax_request': to_return(display_recs, _moment, current_user)}) 

@mod.route('/verify-recs')
@login_required
@is_moderator
def verify_recs():
    display_recs = Recommendation.query\
        .filter_by(verification=1)\
        .order_by(asc(Recommendation.timestamp))\
        .paginate(1, per_page=current_user.display, error_out=False)
    return render_template('mod/verify-recs.html', display=display_recs)