# -*- coding:utf-8 -*-
import random

from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from functools import wraps
from models.user_manager import UserManager
from models.user_type_manager import UserTypeManager
from models.base_manager import SNBaseManager
from flask_mail import Mail, Message
import os

# створюємо головний об'єкт сайту класу Flask
from models.post_manager import PostManager

app = Flask(__name__)
# добавляємо секретний ключ для сайту щоб шифрувати дані сессії
# при кожнаму сапуску фласку буде генечитись новий рандомний ключ з 24 символів
# app.secret_key = os.urandom(24)
app.secret_key = '121212121212'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            if UserManager.load_models.get(session['username'], None):
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrap
# app.secret_key = '125'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'vovatrap@gmail.com'
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)

@app.route('/email')
def email():
    # mail.connect()
    msg = Message('hello',sender='vovatrap@gmail.com', recipients=['vovatrap@gmail.com'])
    # msg.send(mail)
    app.logger.debug('msg = {}'.format(msg))
    app.logger.info('hello')
    app.logger.error('hello')
    app.logger.warning('hello')
    return 'ok'

# описуємо логін роут
# вказуємо що доступні методи "GET" і "POST"
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # якщо метод пост дістаємо дані з форми і звіряємо чи є такий користвач в базі данних
        # якшо є то в дану сесію добавляєм ключ username
        # і перекидаємо користувача на домашню сторінку
        user = UserManager()
        if user.loginUser(request.form):
            addToSession(user)
            return redirect(url_for('home'))

    return render_template('login.html')



# описуємо роут для вилогінення
# сіда зможуть попадати тільки GET запроси
@app.route('/logout')
@login_required
def logout():
    user = session.get('username', None)
    if user:
        # якщо в сесії є username тоді видаляємо його
        del session['username']
    return redirect(url_for('login'))

@app.route('/add_friend', methods=['GET'])
@login_required
def add_friend():
    user_id = int(request.args.get('id',0))
    user = UserManager.load_models[session['username']]
    user.add_friend(id=user_id)
    return redirect(request.referrer)

@app.route('/<nickname>',methods=['GET'])
@login_required
def user_page(nickname):
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        context['loginUser'] = user

    selectUser = UserManager()
    selectUser.select().And([('nickname','=',nickname)]).run()
    context['user'] = selectUser

    return render_template('home.html', context=context)

# описуємо домашній роут
# сіда зможуть попадати тільки GET запроси
@app.route('/')
@login_required
def home():
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        # якщо в сесії є username тоді дістаємо його дані
        # добавляємо їх в словник для передачі в html форму
        context['user'] = user
        context['loginUser'] = user
    return render_template('home.html', context=context)


def addToSession(user):
    session['username'] = user.object.nickname


@app.route('/registration', methods=["GET", "POST"])
def registr():
    context = {'Error': []}
    user_type = UserTypeManager()
    user_type.getTypeUser()
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        user_type.getTypeGroup()
        context['user'] = user
    context['type'] = user_type

    if request.method == 'POST':
        user = UserManager().getModelFromForm(request.form)
        if user.check_user():
            context['Error'].append('wrong name or email')
        if user.object.type.type_name == 'user':
            if not user.object.password:
                context['Error'].append('incorrect password')
        if context['Error']:
            return render_template('registration.html', context=context)
        if user.save():
            UserManager.load_models[user.object.nickname] = user
            addToSession(user)
            return redirect(url_for('home'))
        context['Error'].append('incorrect data')
    return render_template('registration.html', context=context)

@app.route('/add_post', methods=['GET','POST'])
@login_required
def add_post():
    if request.method == 'POST':
        post = PostManager()
        print(list(request.form.keys()))
        user = UserManager.load_models[session['username']]
        post.save_post(request.form, user)
    return render_template('add_post.html')

@app.route('/add_like', methods=['POST'])
@login_required
def add_like():
    app.logger.debug('request.is_xhr = {}'.format(request.is_xhr))
    if request.is_xhr:
        # print(str(request.json['id']))
        user = UserManager.load_models[session['username']]
        app.logger.debug('user = {} like post with id = {}'.format(user.object.first_name, request.json['id']))
        ok =random.choice([True,False])
        print(ok)
        if ok:
            return jsonify({'status':'ok'})
        return jsonify({'status':'error','message':'something wrong'})


@app.route('/like_example')
@login_required
def like_example():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
