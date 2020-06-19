from flask import render_template, jsonify, flash, url_for, redirect, request, session, abort
from application.forms import RegisterForm, LoginForm, AddNewsForm
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

from application import app

@app.route('/index')
@app.route('/home')
@app.route('/')
def index():
    return render_template('index.html', index=True)

@app.route('/news')
def news():
    with open('news.json') as read_file:
        newscoll = json.load(read_file)

    return render_template('news.html',newscoll=newscoll, news=True)

@app.route('/contact')
def contact():
    return render_template('contact.html', contact=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))

    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form=form,  register=True)
    if form.validate_on_submit():
        with open('users.json') as read_file:
            users = json.load(read_file)
        ctr = len(users)
        user = {
            'user_id' : ctr + 1,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'password': generate_password_hash(form.password.data),
            'admin': False
        }

        if ctr == 0:
            user['admin'] = True

        users.append(user)
        with open('users.json', 'w') as writefile:
            json.dump(users, writefile)
        flash('You have successfully registered. Login Now !!!', 'success')
        return redirect(url_for('login'))
    else:
        flash('Something Went Wrong !!!', 'danger')
    return render_template('register.html', form=form,  register=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    flag = False
    if request.method == 'GET':
        return render_template('login.html', form=form,  login=True)
    if form.validate_on_submit():
        with open('users.json') as read_file:
            users = json.load(read_file)
        for user in users:
            if user['email'] == form.email.data and check_password_hash(user['password'], form.password.data):
                session['id'] = user['user_id']
                session['username'] = user['first_name'] + " " + user['last_name']
                session['email'] = user['email']
                session['admin'] = user['admin']
                with open('loginLogs.json') as read_file:
                    logs = json.load(read_file)
                currtime = datetime.now()
                log = {
                    'user_id': session.get('id'),
                    'email': session.get('email'),
                    'action': 'login',
                    'datetime': currtime.strftime("%H:%M, %d %b %Y")
                }
                logs.append(log)
                with open('loginLogs.json', 'w') as writefile:
                    json.dump(logs, writefile)
                flash(f'Welcome, {session.get("username")}', 'success')
                return redirect(url_for('index'))
                flag = True
        if flag == False:
            flash('Wrong Credentials. Check Please !!!', 'danger')
    else:
        flash('Something Went Wrong !!!', 'danger')
    return render_template('login.html', form=form, login=True)

@app.route('/logout')
def logout():
    if session.get('username'):
        with open('loginLogs.json') as read_file:
            logs = json.load(read_file)
        currtime = datetime.now()
        session.pop('id', None)
        session.pop('username', None)
        log = {
            'user_id': session.get('id'),
            'email': session.get('email'),
            'action': 'logout',
            'datetime': currtime.strftime("%H:%M, %d %b %Y")
        }
        logs.append(log)
        with open('loginLogs.json', 'w') as writefile:
            json.dump(logs, writefile)
        flash('You have successfully logged out!!!', 'success')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/addnews', methods=['GET', 'POST'])
def addnews():
    if not session.get('username'):
        abort(404)

    form = AddNewsForm()
    if request.method == 'GET':
        return render_template('addnews.html', form=form)
    if form.validate_on_submit():
        with open('news.json') as read_file:
            news = json.load(read_file)
        ctr = 0
        for n in news:
            if ctr < n['news_id']:
                ctr = n['news_id']
        currtime = datetime.now()
        data = {
            'news_id' : ctr + 1,
            'headline': form.headline.data,
            'category': form.category.data,
            'author_name': form.author_name.data,
            'description': list(form.description.data.split("\r\n")),
            'datetime': currtime.strftime("%H:%M, %d %b %Y")
        }
        news.append(data)
        with open('news.json', 'w') as writefile:
            json.dump(news, writefile)
        currtime = datetime.now()
        with open('newsLogs.json') as read_file:
            logs = json.load(read_file)
        log = {
            'news_id': ctr + 1,
            'email': session.get('email'),
            'action': 'add',
            'datetime': currtime.strftime("%H:%M, %d %b %Y")
        }
        logs.append(log)
        with open('newsLogs.json', 'w') as writefile:
            json.dump(logs, writefile)
        flash('News added successfully !!!', 'success')
        return redirect(url_for('news'))
    else:
        flash('Something Went Wrong !!!', 'danger')
    return render_template('addnews.html', form=form)


@app.route('/newsdetail/<idx>')
def newsdetail(idx):
    with open('news.json') as read_file:
        news = json.load(read_file)
    flag = False
    newsdata = {}
    try:
        for data in news:
            if data['news_id'] == int(idx):
                newsdata = data
                flag = True
                break
    except:
        pass
    finally:
        return render_template('newsdetail.html', newsdata=newsdata, flag=flag)
    

@app.route('/updatenews/<idx>', methods=['GET', 'POST'])
def updatenews(idx):
    if not session.get('username'):
        abort(404)

    if not session.get('admin'):
        abort(404)

    form = AddNewsForm()
    if request.method == 'GET':
        with open('news.json') as read_file:
            news = json.load(read_file)
        flag = False
        newsdata = {}
        try:
            for data in news:
                if data['news_id'] == int(idx):
                    newsdata = data
                    flag = True
                    break
            form.description.data = ""
            for item in newsdata['description']:
                form.description.data += item + '\n'
            form.submit.label.text = "Edit"
        except:
            pass
        finally:
            return render_template('updatenews.html', form=form, newsdata=newsdata, flag=flag)

    if form.validate_on_submit():
        newsdata = {}
        flag = False
        with open('news.json') as read_file:
            news = json.load(read_file)
        news_id = request.form.get('news_id')
        for n in news:
            if n['news_id'] == int(news_id):
                currtime = datetime.now()
                n['headline'] = form.headline.data
                n['description'] = list(form.description.data.split('\r\n'))
                n['author_name'] = form.author_name.data
                n['category'] = form.category.data
                flag = True
        if flag == False:
            return render_template('updatenews.html', form=form, newsdata=newsdata, flag=flag)
        with open('news.json', 'w') as writefile:
            json.dump(news, writefile)
        with open('newsLogs.json') as read_file:
            logs = json.load(read_file)
        log = {
            'news_id': news_id,
            'email': session.get('email'),
            'action': 'update',
            'datetime': currtime.strftime("%H:%M, %d %b %Y")
        }
        logs.append(log)
        with open('newsLogs.json', 'w') as writefile:
            json.dump(logs, writefile)
        flash('News edited successfully !!!', 'success')
        return redirect(url_for('newsdetail', idx=news_id))
    else:
        flash('Something Went Wrong !!!', 'danger')
    return render_template('newsupdate.html', form=form)

@app.route('/deletenews/<idx>')
def deletenews(idx):
    if not session.get('username'):
        abort(404)

    if not session.get('admin'):
        abort(404)

    with open('news.json') as read_file:
        news = json.load(read_file)
    
    ctr = 0
    flag = False

    for n in news:
        if n['news_id'] == int(idx):
            flag = True
            break
        ctr += 1
    
    if flag == False:
        flash('Something went wrong', 'danger')
        return redirect(url_for('news'))

    del news[ctr]
    currtime = datetime.now()

    with open('news.json', 'w') as writefile:
        json.dump(news, writefile)
    with open('newsLogs.json') as read_file:
        logs = json.load(read_file)
    log = {
        'news_id': idx,
        'email': session.get('email'),
        'action': 'delete',
        'datetime': currtime.strftime("%H:%M, %d %b %Y")
    }
    logs.append(log)
    with open('newsLogs.json', 'w') as writefile:
        json.dump(logs, writefile)
    flash('News removed successfully !!!', 'success')
    return redirect(url_for('news'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('pagenotfound.html'), 404
