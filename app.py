from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

app = Flask(__name__)

DB_URL = 'sqlite:///posts.db'

engine = create_engine(DB_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    body = Column(String)

class Comments(Base):
    __tablename__ = 'comments'
    primaryid = Column(Integer, primary_key=True)
    foreignid = Column(Integer, ForeignKey('posts.id'))
    text = Column(String)
    post = relationship("Posts", back_populates = "comments")


Posts.comments = relationship("Comments", order_by = Comments.primaryid, back_populates = "post")
Base.metadata.create_all(engine)


@app.route('/')
def home():
    session = Session()
    post_entries = session.query(Posts).all()
    session.close()
    return render_template('home.html', post_entries=post_entries)

@app.route('/<post_title>', methods=['GET', 'POST'])
def post_page(post_title):
    session = Session()
    post_entry = session.query(Posts).filter_by(title=post_title).first()

    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text and post_entry:
            new_comment = Comments(text=comment_text, post=post_entry)
            session.add(new_comment)
            session.commit()

    comments = session.query(Comments).filter_by(foreignid=post_entry.id).all()
    session.close()
    return render_template('postpage.html', post_entry=post_entry, comments=comments)

@app.route('/createpost', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        session = Session()
        title = request.form.get('title')
        content = request.form.get('content')

        newpost = Posts(title=title, body=content)
        session.add(newpost)
        session.commit()

        print(f"Post Created: {title} - {content}")
        session.close()
        return redirect(url_for('post_page', post_title=title))
    return render_template('createpost.html')

@app.route('/delete/<post_title>')
def delete_page(post_title):
    session = Session()
    post_entry = session.query(Posts).filter(Posts.title.ilike(post_title)).first()
    session.delete(post_entry)
    session.commit()
    session.close()
    return redirect(url_for('home'))

@app.route('/edit/<post_title>', methods=['GET', 'POST'])
def edit_post(post_title):
    session = Session()
    post_entry = session.query(Posts).filter(Posts.title.ilike(post_title)).first()

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_body = request.form.get('content')

        post_entry.title = new_title
        post_entry.body = new_body

        session.commit()
        session.close()

        return redirect(url_for('post_page', post_title=new_title))

    session.close()
    return render_template('editpage.html', post_entry=post_entry)

if __name__ == '__main__':
    app.run(debug=True)
