from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final_p_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Username(db.Model):
    __tablename__ = "username"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String, nullable=False, unique=True)

class Tracker(db.Model):
    __tablename__ = 'trackers'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    Name = db.Column(db.String, nullable=False)
    Description = db.Column(db.String, nullable=False)
    Type = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable = False)

class Details(db.Model):
    __tablename__ = 'details'
    no = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, nullable=False)
    trackername = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)
    timestamp = db.Column(db.String, nullable = False)
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    user = request.form['name']
    verify = Username.query.filter(Username.username == user).first()
    if verify:
        return redirect(f"dashboard/{user}")
    return render_template('usernotexist.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = request.form['name']
    verify = Username.query.filter(Username.username == user).first()
    if verify:
        return render_template('userexist.html')
    new = Username(username = user)
    db.session.add(new)
    db.session.commit()
    return redirect('/login')

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dash(username):
    user = Username.query.filter(Username.username == username).first()
    trackers = Tracker.query.all()
    det = Details.query.all()
    return render_template('dashboard.html', trackers = trackers, name = user, det=det)

@app.route('/thanks', methods=['GET', 'POST'])
def thanks():
    return render_template('thanks.html')

@app.route('/trackers/add/<username>', methods=['GET', 'POST'])
def addtracker(username):
    if request.method == 'GET':
        user = Username.query.filter(Username.username==username).first()
        return render_template('addtracker.html', user=user)
    user = Username.query.filter(Username.username==username).first()
    name = user.username
    t_name = request.form['name']
    t_desc = request.form['desc']
    t_type = request.form['type']
    new_track = Tracker(Name = t_name, Description = t_desc, Type = t_type, username = name)
    db.session.add(new_track)
    db.session.commit()   
    return redirect(f"/dashboard/{name}")

@app.route('/log/<username>/<tracker>', methods=['GET', 'POST'])
def log(username, tracker):
    if request.method == 'GET':
        user = Username.query.filter(Username.username==username).first()
        trackers = Tracker.query.filter(Tracker.Name == tracker).first()
        det = Details.query.all()
        print(det)
        return render_template('Logentry.html', det = det, username = user, trackers = trackers)
    user = Username.query.filter(Username.username==username).first()
    trackers = Tracker.query.filter(Tracker.Name == tracker).first()
    t_name = trackers.Name
    u_name = user.username
    u_value = request.form['value']
    u_note = request.form['note']
    time = request.form['date']
    new = Details(username=u_name, trackername=t_name, value=u_value, note=u_note, timestamp = time)
    db.session.add(new)
    db.session.commit()
    return redirect(f'/logdetails/{u_name}/{t_name}')


@app.route('/trackers/<username>/delete/<int:tid>', methods=['GET', 'POST'])
def trackerdelete(tid, username):
    tracker = Tracker.query.filter(Tracker.id == tid).first()
    user = Username.query.filter(Username.username==username).first()
    name = user.username
    db.session.delete(tracker)
    db.session.commit()
    return redirect(f'/dashboard/{name}')

@app.route('/trackers/<username>/update/<int:tid>', methods=['GET', 'POST'])
def trackerupdate(tid, username):
    if request.method == 'GET':
        tracker = Tracker.query.filter(Tracker.id == tid).first()
        user = Username.query.filter(Username.username==username).first()
        return render_template('updatetracker.html', tracker = tracker, user = user)

    new = Tracker.query.filter(Tracker.id == tid).first()
    user = Username.query.filter(Username.username==username).first()
    name = user.username
    new.Name = request.form['name']
    new.Description = request.form['desc']
    new.Type = request.form['type']

    db.session.commit()
    return redirect(f'/dashboard/{name}')

@app.route('/log/<username>/<tracker>/delete/<int:lid>', methods=['GET', 'POST'])
def logdelete(username, tracker, lid):
    user = Username.query.filter(Username.username==username).first()
    name = user.username
    tracker = Tracker.query.filter(Tracker.Name == tracker).first()
    tracker_name = tracker.Name
    log = Details.query.filter(Details.no == lid).first()
    db.session.delete(log)
    db.session.commit()
    return redirect(f'/logdetails/{name}/{tracker_name}')

@app.route('/log/<username>/<tracker>/update/<int:lid>', methods=['GET', 'POST'])
def logupdate(username, tracker, lid):
    if request.method == 'GET':
        user = Username.query.filter(Username.username==username).first()
        trackers = Tracker.query.filter(Tracker.Name == tracker).first()
        log = Details.query.filter(Details.no == lid).first()

        return render_template('updatelog.html', username = user, trackers = trackers, data = log)
    user = Username.query.filter(Username.username==username).first()
    name = user.username
    tracker = Tracker.query.filter(Tracker.Name == tracker).first()
    tracker_name = tracker.Name
    new = Details.query.filter(Details.no == lid).first()
    new.value = request.form['value']
    new.note = request.form['note']
    db.session.commit()
    return redirect(f'/logdetails/{name}/{tracker_name}')

@app.route('/logdetails/<username>/<tracker>')
def logdetails(username, tracker):
    user = Username.query.filter(Username.username==username).first()
    trackers = Tracker.query.filter(Tracker.Name == tracker).first()
    det = Details.query.all()
    l = []
    values = []
    time = []
    for data in det:
        if data.username == user.username and data.trackername == trackers.Name:
            l.append(data)
            if trackers.Type == 'Numerical':
                t = data.timestamp
                ntt = t[4:10] + ' ' + t[16:24]
                v = data.value
                values.append(float(v))
                time.append(ntt)
            if trackers.Type == "Boolean":
                t = data.timestamp
                ntt = t[4:10] + ' ' + t[16:24]
                v = data.value
                values.append(v)
                time.append(ntt)
    plt.clf()
    fig = plt.plot(time, values)
    plt.xlabel('values')
    plt.ylabel('TimePeriod')
    plt.xticks(rotation=25, fontsize = 7)
    plt.savefig("static/trendline.png")



    return render_template('logdetails.html', name = user, tracker = trackers, det = det, l=l)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8000)

