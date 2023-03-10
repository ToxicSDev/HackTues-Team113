from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_login import LoginManager, current_user, login_user, login_required, UserMixin, logout_user
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os
from dotenv import dotenv_values

app = Flask(__name__, static_url_path="/static")
config = dotenv_values("../.env")
app.config['SECRET_KEY'] = config['secret_key']
app.config['UPLOAD_FOLDER'] = '../whitelist'
app.config['EVIDENCE_FOLDER'] = '../evidence'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        return User(user_id)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        config = dotenv_values("../.env")
        if username == config['username'] and password == config['password']:
            user = User(username)
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class UploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[FileRequired(), FileAllowed(
        {'jpg', 'jpeg', 'png', 'gif'}, 'Images only!')])


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('server.html', form=form)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/whitelist')
@login_required
def whitelist():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('whitelist.html', files=file_list)


@app.route('/whitelist/<filename>')
@login_required
def whitelist_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/whitelist/delete/<filename>', methods=['GET', 'POST'])
@login_required
def whitelist_delete_file(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('home'))

@app.route('/evidence')
@login_required
def evidence():
    file_list = os.listdir(app.config['EVIDENCE_FOLDER'])
    return render_template('whitelist.html', files=file_list)


@app.route('/evidence/<filename>')
@login_required
def evidence_file(filename):
    return send_from_directory(app.config['EVIDENCE_FOLDER'], filename)


@app.route('/evidence/delete/<filename>', methods=['GET', 'POST'])
@login_required
def evidence_delete_file(filename):
    os.remove(os.path.join(app.config['EVIDENCE_FOLDER'], filename))
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)