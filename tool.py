from flask import (Blueprint, redirect, render_template, url_for)

bp = Blueprint('tool', __name__)

@bp.route('/')
def index():
    return render_template('tool/index.html')

@bp.route('/instructions/')
def instructions():
    return render_template('instructions.html')
