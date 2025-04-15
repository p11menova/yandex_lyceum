from flask import Flask, render_template, request, redirect
from data import db_session
from data.users import User
from data.jobs import Posts

db_session.global_init("db/usersposts_meow.db")
db_sess = db_session.create_session()
db_sess.query(Posts).filter(Posts.author >= 0).delete()
db_sess.query(User).filter(User.id >= 0).delete()
db_sess.commit()
