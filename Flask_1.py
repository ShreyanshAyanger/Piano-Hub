from flask import Flask,render_template,request,session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math



with open('params.json','r') as c:
    params=json.load(c)["params"]

app=Flask(__name__)
app.secret_key= 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = params['DATABASE_URL']
# local_server=True
# if(local_server):
#     app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
# else:
#     pass



db = SQLAlchemy(app)

class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(20), nullable=False)
    Phone_number = db.Column(db.String(12), nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    Content = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts']) ]
    if(page==1):
        prev="#"
        next="/?page="+ str(page+1)
    elif(page==last):
        prev="/?page="+ str(page-1)
        next="#"
    else:
        prev="/?page="+ str(page-1)
        next="/?page="+ str(page+1)

    return render_template('index.html', params=params, posts=posts, previous=prev, next=next )



@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(Name=name, Email = email, Phone_number = phone, Message = message, Date= datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/post", methods=['GET','POST'])
def Dashboard():
    if('user' in session and session['user']==params['admin_user']):
        posts=Posts.query.all()
        return render_template('dashboard.html', params=params , posts=posts)

    if request.method=="POST":
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if (username==params['admin_user'] and userpass==params['admin_pass']):
            session['user']=username
            posts=Posts.query.all()
            return render_template('dashboard.html', params=params , posts=posts)

    else:
        return render_template('login.html',params=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if('user' in session and session['user']==params['admin_user']):
        if request.method=='POST':
            title= request.form.get('Title')
            slug= request.form.get('slug')
            content= request.form.get('Content')
            image= request.form.get('img_file')
            date=datetime.now()

            if sno=='0':
                post=Posts(Title=title, slug=slug,Content=content,img_file=image, Date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.Title=title
                post.slug=slug
                post.Content=content
                post.img_file=image
                post.Date=date
                db.session.commit()
                return redirect('/edit/'+ sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post ,sno=sno)

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if('user' in session and session['user']==params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/post')



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/post')


# app.run(debug=True)