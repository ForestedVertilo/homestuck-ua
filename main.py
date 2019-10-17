import datetime
from google.cloud import datastore
import os
from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, IntegerField,StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    page = IntegerField('Page')
    title = StringField('Title')
    media =  MultipleFileField('File(s) Upload')
    text = TextAreaField('Text')
    isFlash = BooleanField('Is Flash?')

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
datastore_client = datastore.Client()
def store_time(page, title, media, text, isFlash):
    entity = datastore.Entity(key=datastore_client.key('page'))
    entity.update({
        "page": page,
        'media': media,
        'text': text,
        'isFlash': isFlash,
        'title': title
    })

    datastore_client.put(entity)

def fetch_times(page):
    query = datastore_client.query(kind='page')
    query.add_filter('page', '=', page)
    page = list(query.fetch())
    return page[0]

@app.route('/')
@app.route('/<int:num_page>')
def pages(num_page = 1):
    page = fetch_times(num_page)
    action= ''
    try:
       action = fetch_times(num_page+1)
    except IndexError:
        action = ''
    else:
        action = action["title"]
    print(action)
    return render_template(
        'index.html', page=page, action=action)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = MyForm()
    if form.validate_on_submit():
        file_filenames = []
        print(list(form.media.data))
        for files in form.media.data:
            file_filenames.append(files.filename)
            files.save('static/pages_img/' + files.filename)
        store_time(form.page.data, form.title.data, file_filenames, form.text.data, form.isFlash.data)
        return render_template('admin.html', form=form)
    return render_template(
        'admin.html', form=form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
