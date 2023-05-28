from flask import Blueprint, jsonify, render_template, request, flash
from flask_login import login_required, current_user
from .models import Note, User 
from . import db
import json
import datetime 

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    current_time = datetime.datetime.now().time()
    
    if current_time < datetime.time(12, 0):
        greeting = 'Good morning'
    elif current_time < datetime.time(18, 0):
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    user = current_user  # Fetch the current user from the database
    first_name = user.first_name if user else ''

    if request.method == 'POST':
        note = request.form.get('note')
        if len(note)<1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note) 
            db.session.commit()
            flash('Note added', category='success')
    return render_template("home.html", user=current_user, greeting=greeting, first_name=first_name)
    
@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
