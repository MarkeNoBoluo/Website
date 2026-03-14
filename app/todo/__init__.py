"""Todo blueprint."""
from flask import Blueprint

bp = Blueprint('todo', __name__, template_folder='templates/todo')