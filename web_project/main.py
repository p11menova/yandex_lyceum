from flask import Flask, render_template, request, redirect
from data import db_session
from data.users import User
from data.jobs import Posts
from PIL import Image
from data.users_here import User_in
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

USER_IN = User_in()


@app.route('/', methods=['POST', 'GET'])
def start():
    if request.method == 'GET':
        return render_template("news.html", posts=posts_for_news(), USER=USER_IN.get_value())
    elif request.method == 'POST':
        if request.form.get("login") != None:
            if not USER_IN.get_value():
                return redirect('/registration')
            else:
                return redirect(f'user/{USER_IN.get_user_id()}/page')
        elif request.form.get('news_w_theme') != None:
            return render_template("news.html", posts=posts_for_news(request.form['theme'], request), USER=USER_IN.get_value())
        elif request.form.get('exit') != None:
            USER_IN.change_value = False
            return render_template('news.html', posts=posts_for_news(), USER=False)


def posts_for_news(theme='', request=''):
    db_session.global_init("db/usersposts_meow.db")
    db_sess = db_session.create_session()
    posts, posts1 = [], []
    if USER_IN.get_value() and request != '':
        if request.form.get('my_themes')!= None:
            themes = db_sess.query(User).filter(User.id == USER_IN.get_user_id()).first().preferences
            print(themes)
            for i in themes:
                i = i.rstrip(", ") if ", " in i else i
                posts1 += db_sess.query(Posts).filter(Posts.preferences.like(f'%{i}%')).all()

            for i in posts1:
                if i not in posts and i != []:
                    posts.append(i)
            print(posts)
            print(posts1)
    else:
        posts = db_sess.query(Posts).filter(Posts.preferences.like(f'%{theme}%')).all()

    if not posts:
        return False
    else:
        all_posts = []

        for post in posts:
            author = db_sess.query(User).filter(User.id == post.author).first()
            pd = {"author": f'{author.surname}  {author.name}',
            "profile_pic": author.profile_pic,
            "post": post}
            all_posts.append(pd)
        all_posts.reverse()
        return all_posts


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('selection.html')
    elif request.method == 'POST':
        return make_new_user(request)


def make_new_user(request):
    db_session.global_init("db/usersposts_meow.db")
    db_sess = db_session.create_session()


    user = User()
    user.surname = request.form['surname']
    user.name = request.form['name']
    user.age = int(request.form['age'])
    user.sex = request.form['sex']
    if request.form['photo']:
        user.profile_pic = request.form['photo']
    elif not request.form['photo']:
        user.profile_pic = "nophoto.png"

    user.email = request.form['email']
    user.hashed_password = request.form['password']



    #!!!!!!!!!!!!!!
    db_sess.query(User).filter(User.id >= 0).delete()


    db_sess.add(user)
    db_sess.commit()

    USER_IN.change_value(True)
    USER_IN.change_user_id(user.id)

    return redirect(f'/user/{user.id}/page')


def make_new_post(request, id):
    db_session.global_init("db/usersposts_meow.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    post = Posts()
    post.author = user.id
    post.text = request.form['post_text']

    post.image = request.form['image'] if request.form['image'] else ' '
    if request.form['image']:
        image_size = Image.open(f'static/image/{post.image}').size
        w, h = image_size
        post.width_or_height = "height" if h >= w else "width"
    post.preferences = request.form['preference'] if request.form['preference'] != 'ни с одной из перечисленных тем' else ''

    # !!!!!!!!!!!!!!
    #db_sess.query(Posts).filter(Posts.author >= 0).delete()


    db_sess.add(post)
    db_sess.commit()
    return redirect(f'/user/{user.id}/page')


@app.route('/user/<id>/page', methods=['POST', 'GET'])
def userspage(id):
    db_session.global_init("db/usersposts_meow.db")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if request.method == 'GET':
        return render_template("user_page.html", user=user)
    elif request.method == 'POST':

        if request.form.get('preferences_test') != None:
            return redirect(f'/preferences_test/{id}')
        elif request.form.get('new_post') != None:
            return make_new_post(request, id)
        elif request.form.get('news') != None:
            return redirect('/')



@app.route('/preferences_test/<id>', methods=['POST', 'GET'])
def preferences_test(id):
    if request.method == 'GET':
        return render_template('preferences_test.html')
    elif request.method == 'POST':

        db_session.global_init("db/usersposts_meow.db")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()

        preferences_dict = {"reading": "Чтение книг", "sport": "Спорт", "psychology": "Психология",
                            "art": "Чтение", "fashion": "Мода", "space": "Космос", "Путешествия": "travelling"}

        for i in 'reading, sport, psychology, art, fashion, space, travelling'.split(', '):
            try:
                if request.form[i]:
                    user.preferences += preferences_dict[i] + ', ' if preferences_dict[i] not in user.preferences else ''
            except BaseException:
                continue

        db_sess.commit()
    return redirect(f'/user/{id}/page')


if __name__ == '__main__':

    app.run(port=8088, host='127.0.0.1')




