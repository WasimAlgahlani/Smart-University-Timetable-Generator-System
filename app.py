from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from ast import literal_eval
import json
from algorithm import evolutionary_algorithm

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Timetable.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# toastr = Toastr(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(250), unique=True, nullable=False)
    user_pass = db.Column(db.String(250), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)


class College(db.Model):
    coll_id = db.Column(db.Integer, primary_key=True)
    coll_name = db.Column(db.String(70), unique=True, nullable=False)
    departments = db.relationship("Department", backref="college")
    majors = db.relationship("Major", backref="college")
    teachers = db.relationship("Teacher", backref="college")


class Department(db.Model):
    dept_id = db.Column(db.Integer, primary_key=True)
    coll = db.Column(db.Integer, db.ForeignKey('college.coll_id'), nullable=False)
    dept_name = db.Column(db.String(50), unique=True, nullable=False)
    majors = db.relationship("Major", backref="department")


class Major(db.Model):
    major_id = db.Column(db.Integer, primary_key=True)
    coll = db.Column(db.Integer, db.ForeignKey('college.coll_id'), nullable=False)
    dept = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)
    maj_name = db.Column(db.String(50), unique=True, nullable=False)
    subjects = db.relationship("Subject", backref="major")


class Subject(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    maj = db.Column(db.Integer, db.ForeignKey('major.major_id'), nullable=False)
    sub_name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    term = db.Column(db.Integer, nullable=False)


class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(70), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(15), nullable=False)


class Teacher(db.Model):
    teach_id = db.Column(db.Integer, primary_key=True)
    coll = db.Column(db.Integer, db.ForeignKey('college.coll_id'), nullable=False)
    teach_name = db.Column(db.String(50), unique=True, nullable=False)
    contract = db.Column(db.String(15), nullable=False)


class TeacherSubjects(db.Model):
    te_sub_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.Integer, nullable=False)
    teacher = db.Column(db.Integer, nullable=False)
    sub_type = db.Column(db.String(15), nullable=False)
    sub_hours = db.Column(db.Integer, nullable=False)


class Availability(db.Model):
    time_id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.Integer, unique=True, nullable=False)
    ava = db.Column(db.String(500), nullable=False)


class Student(db.Model):
    stu_id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)


db.create_all()


# def login_required(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return f(*args, **kwargs)
#         else:
#             flash("You need to login first")
#             return redirect(url_for('main_screen'))
#
#     return wrap


# @app.route('/success', methods=['GET'])
# def success():
#     return render_template('success.html')
#
#
# @app.route('/error', methods=['GET'])
# def error():
#     return render_template('error.html')


@app.route('/fail', methods=['GET'])
def login_popup():
    return render_template('fail.html')


@app.route('/', methods=['GET', 'POST'])
def main_screen():  # first to run
    if request.method == "POST":
        user = request.form['user']
        passw = request.form['passw']
        us = User.query.filter_by(user_name=user).first()
        if us:
            us_pass = us.user_pass
            us_type = us.user_type
            if us_pass == passw:
                # session.
                if us_type == 'admin':
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('regular'))
            else:
                return redirect(url_for('login_popup'))
        else:
            return redirect(url_for('login_popup'))

    return render_template('index.html', status="success")


@app.route('/Admin')
def admin():
    return render_template('home2.html')


@app.route('/Users')
def regular():
    return render_template('home.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    all_users = db.session.query(User).all()
    if request.method == "POST":
        new_user = User(user_name=request.form["uName"], user_pass=request.form["uPass"],
                        user_type=request.form["uType"])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('add_user'))
    return render_template('addUser.html', all_users=all_users)


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    all_users = db.session.query(User).all()
    if request.method == "POST":
        u_name = request.form["uName"]
        user_to_update = User.query.filter_by(user_name=u_name).first()
        user_to_update.user_name = request.form["newName"]
        user_to_update.user_pass = request.form["uPass"]
        user_to_update.user_type = request.form["uType"]
        db.session.commit()
        return redirect(url_for('update_user'))
    return render_template('updateUser.html', all_users=all_users)


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    all_users = db.session.query(User).all()
    if request.method == "POST":
        u_name = request.form["uName"]
        user_to_delete = User.query.filter_by(user_name=u_name).first()
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('delete_user'))
    return render_template('deleteUser.html', all_users=all_users)


@app.route('/add_coll', methods=['GET', 'POST'])
def add_coll():
    all_colls = db.session.query(College).all()
    if request.method == "POST":
        new_coll = College(coll_name=request.form["cName"])
        db.session.add(new_coll)
        db.session.commit()
        return redirect(url_for('add_coll'))
    return render_template('addColl.html', all_colls=all_colls)


@app.route('/update_coll', methods=['GET', 'POST'])
def update_coll():
    all_colls = db.session.query(College).all()
    if request.method == "POST":
        c_name = request.form["cName"]
        coll_to_update = College.query.filter_by(coll_name=c_name).first()
        coll_to_update.coll_name = request.form["newName"]
        db.session.commit()
    return render_template('updateColl.html', all_colls=all_colls)


@app.route('/delete_coll', methods=['GET', 'POST'])
def delete_coll():
    all_colls = db.session.query(College).all()
    if request.method == "POST":
        c_name = request.form["cName"]
        coll_to_delete = College.query.filter_by(coll_name=c_name).first()
        db.session.delete(coll_to_delete)
        db.session.commit()
        return redirect(url_for('delete_coll'))
    return render_template('deleteColl.html', all_colls=all_colls)


@app.route('/add_dept', methods=['GET', 'POST'])
def add_dept():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    if request.method == "POST":
        coll_n = request.form["cName"]
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        new_dept = Department(coll=coll_i, dept_name=request.form["dName"])
        db.session.add(new_dept)
        db.session.commit()
        return redirect(url_for('add_dept'))
    return render_template('addDept.html', all_colls=all_colls, all_depts=all_depts)


@app.route('/update_dept', methods=['GET', 'POST'])
def update_dept():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    if request.method == "POST":
        n_dept = request.form["dName"]
        dept_to_update = Department.query.filter_by(dept_name=n_dept).first()
        coll_n = request.form["cName"]
        dept_n = request.form["newName"]
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        dept_to_update.dept_name = dept_n
        dept_to_update.coll = coll_i
        db.session.commit()
        return redirect(url_for('update_dept'))
    return render_template('updateDept.html', all_colls=all_colls, all_depts=all_depts)


@app.route('/delete_dept', methods=['GET', 'POST'])
def delete_dept():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    if request.method == "POST":
        d_name = request.form['dName']
        dept_to_delete = Department.query.filter_by(dept_name=d_name).first()
        db.session.delete(dept_to_delete)
        db.session.commit()
        return redirect(url_for('delete_dept'))
    return render_template('deleteDept.html', all_colls=all_colls, all_depts=all_depts)


@app.route('/add_major', methods=['GET', 'POST'])
def add_major():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    all_majors = db.session.query(Major).all()
    if request.method == "POST":
        coll_n = request.form["cName"]
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        dept_n = request.form["dName"]
        dept_n2 = Department.query.filter_by(dept_name=dept_n).first()
        dept_i = dept_n2.dept_id
        new_major = Major(coll=coll_i, dept=dept_i, maj_name=request.form["mName"])
        db.session.add(new_major)
        db.session.commit()
        return redirect(url_for('add_major'))
    return render_template('addMajor.html', all_colls=all_colls, all_depts=all_depts, all_majors=all_majors)


@app.route('/update_major', methods=['GET', 'POST'])
def update_major():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    all_majors = db.session.query(Major).all()
    if request.method == "POST":
        maj_n = request.form['mName']
        dept_n = request.form['dName']
        coll_n = request.form['cName']
        n_maj = request.form['newName']
        major_to_update = Major.query.filter_by(maj_name=maj_n).first()
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        dept_n2 = Department.query.filter_by(dept_name=dept_n).first()
        dept_i = dept_n2.dept_id
        major_to_update.maj_name = n_maj
        major_to_update.coll = coll_i
        major_to_update.dept = dept_i
        db.session.add(major_to_update)
        db.session.commit()
        return redirect(url_for('update_major'))
    return render_template('updateMajor.html', all_colls=all_colls, all_depts=all_depts, all_majors=all_majors)


@app.route('/delete_major', methods=['GET', 'POST'])
def delete_major():
    all_colls = db.session.query(College).all()
    all_depts = db.session.query(Department).all()
    all_majors = db.session.query(Major).all()
    if request.method == "POST":
        m_name = request.form['mName']
        major_to_delete = Major.query.filter_by(maj_name=m_name).first()
        db.session.delete(major_to_delete)
        db.session.commit()
        return redirect(url_for('delete_major'))
    return render_template('deleteMajor.html', all_colls=all_colls, all_depts=all_depts, all_majors=all_majors)


@app.route('/add_sub', methods=['GET', 'POST'])
def add_sub():
    all_majors = db.session.query(Major).all()
    all_subs = db.session.query(Subject).all()
    if request.method == "POST":
        maj_n = request.form["mName"]
        maj_n2 = Major.query.filter_by(maj_name=maj_n).first()
        maj_i = maj_n2.major_id
        new_sub = Subject(maj=maj_i, sub_name=request.form["sName"], term=int(request.form["tName"]),
                          level=int(request.form["lName"]))
        db.session.add(new_sub)
        db.session.commit()
        return redirect(url_for('add_sub'))
    return render_template('addSubject.html', all_majors=all_majors, all_subs=all_subs)


@app.route('/update_sub', methods=['GET', 'POST'])
def update_sub():
    all_majors = db.session.query(Major).all()
    all_subs = db.session.query(Subject).all()
    if request.method == "POST":
        maj_n = request.form['mName']
        n_maj = Major.query.filter_by(maj_name=maj_n).first()
        n_maj2 = n_maj.major_id
        sub_n = request.form['sName']
        lev_n = request.form['lName']
        term_n = request.form['tName']
        n_sub = request.form['newName']
        subject_to_update = Subject.query.filter_by(sub_name=sub_n, maj=n_maj2).first()
        maj_na = request.form['newMaj']
        na_maj = Major.query.filter_by(maj_name=maj_na).first()
        na_maj2 = na_maj.major_id
        subject_to_update.maj = na_maj2
        subject_to_update.sub_name = n_sub
        subject_to_update.level = lev_n
        subject_to_update.term = term_n
        db.session.add(subject_to_update)
        db.session.commit()
        return redirect(url_for('update_sub'))
    return render_template('updateSubject.html', all_majors=all_majors, all_subs=all_subs)


@app.route('/delete_sub', methods=['GET', 'POST'])
def delete_sub():
    all_majors = db.session.query(Major).all()
    all_subs = db.session.query(Subject).all()
    if request.method == "POST":
        s_name = request.form['sName']
        m_name = request.form['mName']
        m_name2 = Major.query.filter_by(maj_name=m_name).first()
        m_name3 = m_name2.major_id
        sub_to_delete = Subject.query.filter_by(sub_name=s_name, maj=m_name3).first()
        db.session.delete(sub_to_delete)
        db.session.commit()
        return redirect(url_for('delete_sub'))
    return render_template('deleteSubject.html', all_majors=all_majors, all_subs=all_subs)


@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    all_rooms = db.session.query(Room).all()
    if request.method == "POST":
        new_room = Room(room_name=request.form["rName"], capacity=int(request.form["cap"]),
                        room_type=request.form["rType"])
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('add_room'))
    return render_template('addRoom.html', all_rooms=all_rooms)


@app.route('/update_room', methods=['GET', 'POST'])
def update_room():
    all_rooms = db.session.query(Room).all()
    if request.method == "POST":
        r_name = request.form["rName"]
        room_to_update = Room.query.filter_by(room_name=r_name).first()
        room_to_update.room_name = request.form["newName"]
        room_to_update.capacity = int(request.form["cap"])
        room_to_update.room_type = request.form["rType"]
        db.session.commit()
        return redirect(url_for('update_room'))
    return render_template('updateRoom.html', all_rooms=all_rooms)


@app.route('/delete_room', methods=['GET', 'POST'])
def delete_room():
    all_rooms = db.session.query(Room).all()
    if request.method == "POST":
        r_name = request.form["rName"]
        room_to_delete = Room.query.filter_by(room_name=r_name).first()
        db.session.delete(room_to_delete)
        db.session.commit()
        return redirect(url_for('delete_room'))
    return render_template('deleteRoom.html', all_rooms=all_rooms)


@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    all_colls = db.session.query(College).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        coll_n = request.form["cName"]
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        new_teacher = Teacher(coll=coll_i, teach_name=request.form["tName"], contract=request.form["con"])
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('add_teacher'))
    return render_template('addTeacher.html', all_colls=all_colls, all_teachers=all_teachers)


@app.route('/update_teacher', methods=['GET', 'POST'])
def update_teacher():
    all_colls = db.session.query(College).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        n_teach = request.form["tName"]
        teach_to_update = Teacher.query.filter_by(teach_name=n_teach).first()
        teach_n = request.form["newName"]
        coll_n = request.form["cName"]
        coll_n2 = College.query.filter_by(coll_name=coll_n).first()
        coll_i = coll_n2.coll_id
        con_n = request.form["con"]
        teach_to_update.teach_name = teach_n
        teach_to_update.coll = coll_i
        teach_to_update.contract = con_n
        db.session.commit()
        return redirect(url_for('update_teacher'))
    return render_template('updateTeacher.html', all_colls=all_colls, all_teachers=all_teachers)


@app.route('/delete_teacher', methods=['GET', 'POST'])
def delete_teacher():
    all_colls = db.session.query(College).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        t_name = request.form['tName']
        teacher_to_delete = Teacher.query.filter_by(teach_name=t_name).first()
        db.session.delete(teacher_to_delete)
        db.session.commit()
        return redirect(url_for('delete_teacher'))
    return render_template('deleteTeacher.html', all_colls=all_colls, all_teachers=all_teachers)


@app.route('/add_time', methods=['GET', 'POST'])
def add_time():
    all_times = db.session.query(Availability).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        d = {}
        if request.form["sat"]:
            d["السبت"] = [request.form["sat"]]
        if request.form["sun"]:
            d["الأحد"] = [request.form["sun"]]
        if request.form["mon"]:
            d["الإثنين"] = [request.form["mon"]]
        if request.form["tue"]:
            d["الثلاثاء"] = [request.form["tue"]]
        if request.form["wen"]:
            d["الأربعاء"] = [request.form["wen"]]
        if request.form["thu"]:
            d["الخميس"] = [request.form["thu"]]
        if len(d) > 0:
            d2 = str(d)
        else:
            d2 = "غير محدد بعد"
        new_time = Availability(teacher=teach_i, ava=d2)
        db.session.add(new_time)
        db.session.commit()
        return redirect(url_for('add_time'))
    return render_template('addTime.html', all_times=all_times, all_teachers=all_teachers)


@app.route('/update_time', methods=['GET', 'POST'])
def update_time():
    all_times = db.session.query(Availability).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        d = {}
        if request.form["sat"]:
            d["السبت"] = [request.form["sat"]]
        if request.form["sun"]:
            d["الأحد"] = [request.form["sun"]]
        if request.form["mon"]:
            d["الإثنين"] = [request.form["mon"]]
        if request.form["tue"]:
            d["الثلاثاء"] = [request.form["tue"]]
        if request.form["wen"]:
            d["الأربعاء"] = [request.form["wen"]]
        if request.form["thu"]:
            d["الخميس"] = [request.form["thu"]]
        if len(d) > 0:
            d2 = str(d)
        else:
            d2 = "غير محدد بعد"
        time_to_update = Availability.query.filter_by(teacher=teach_i).first()
        time_to_update.teacher = teach_i
        time_to_update.ava = d2
        db.session.commit()
        return redirect(url_for('update_time'))
    return render_template('updateTime.html', all_times=all_times, all_teachers=all_teachers)


@app.route('/delete_time', methods=['GET', 'POST'])
def delete_time():
    all_times = db.session.query(Availability).all()
    all_teachers = db.session.query(Teacher).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        time_to_delete = Availability.query.filter_by(teacher=teach_i).first()
        db.session.delete(time_to_delete)
        db.session.commit()
        return redirect(url_for('delete_time'))
    return render_template('deleteTime.html', all_times=all_times, all_teachers=all_teachers)


@app.route('/add_teacher_subject', methods=['GET', 'POST'])
def add_teacher_subject():
    all_subs = [r.sub_name for r in db.session.query(Subject.sub_name).distinct()]
    all_subs2 = db.session.query(Subject).all()
    all_teachers = db.session.query(Teacher).all()
    all_tea_subs = db.session.query(TeacherSubjects).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        sub_n = request.form["sName"]
        sub_n2 = Subject.query.filter_by(sub_name=sub_n).first()
        sub_i = sub_n2.sub_id
        ty = request.form["rType"]
        ho = request.form["hName"]
        rec = TeacherSubjects(subject=sub_i, teacher=teach_i, sub_type=ty, sub_hours=ho)
        db.session.add(rec)
        db.session.commit()
        return redirect(url_for('add_teacher_subject'))
    return render_template('addTeacherSubject.html', all_teachers=all_teachers, all_subs=all_subs,
                           all_tea_subs=all_tea_subs, all_subs2=all_subs2)


@app.route('/update_teacher_subject', methods=['GET', 'POST'])
def update_teacher_subject():
    all_subs = [r.sub_name for r in db.session.query(Subject.sub_name).distinct()]
    all_subs2 = db.session.query(Subject).all()
    all_teachers = db.session.query(Teacher).all()
    all_tea_subs = db.session.query(TeacherSubjects).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        sub_n = request.form["sName"]
        sub_n2 = Subject.query.filter_by(sub_name=sub_n).first()
        sub_i = sub_n2.sub_id
        ty_n = request.form["rType"]

        sub_nn = request.form["newName"]
        sub_nn2 = Subject.query.filter_by(sub_name=sub_nn).first()
        sub_ii = sub_nn2.sub_id
        tea_nn = request.form["teName"]
        tea_nn2 = Teacher.query.filter_by(teach_name=tea_nn).first()
        tea_nn_i = tea_nn2.teach_id
        tea_sub_to_update = TeacherSubjects.query.filter_by(teacher=teach_i, subject=sub_i, sub_type=ty_n).first()
        tea_sub_to_update.teacher = tea_nn_i
        tea_sub_to_update.subject = sub_ii
        tea_sub_to_update.sub_type = request.form["rType2"]
        tea_sub_to_update.sub_hours = request.form["hName"]
        db.session.commit()
        return redirect(url_for('update_teacher_subject'))
    return render_template('updateTeacherSubject.html', all_teachers=all_teachers, all_subs=all_subs,
                           all_tea_subs=all_tea_subs, all_subs2=all_subs2)


@app.route('/delete_teacher_subject', methods=['GET', 'POST'])
def delete_teacher_subject():
    all_subs = [r.sub_name for r in db.session.query(Subject.sub_name).distinct()]
    all_subs2 = db.session.query(Subject).all()
    all_teachers = db.session.query(Teacher).all()
    all_tea_subs = db.session.query(TeacherSubjects).all()
    if request.method == "POST":
        teach_n = request.form["tName"]
        teach_n2 = Teacher.query.filter_by(teach_name=teach_n).first()
        teach_i = teach_n2.teach_id
        sub_n = request.form["sName"]
        sub_n2 = Subject.query.filter_by(sub_name=sub_n).first()
        sub_i = sub_n2.sub_id
        ty_n = request.form["rType"]
        tea_sub_to_delete = TeacherSubjects.query.filter_by(teacher=teach_i, subject=sub_i, sub_type=ty_n).first()
        db.session.delete(tea_sub_to_delete)
        db.session.commit()
        return redirect(url_for('delete_teacher_subject'))
    return render_template('deleteTeacherSubject.html', all_teachers=all_teachers, all_subs=all_subs,
                           all_tea_subs=all_tea_subs, all_subs2=all_subs2)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    all_majs = db.session.query(Major).all()
    all_stus = db.session.query(Student).all()
    if request.method == "POST":
        maj_n = request.form["mName"]
        maj_n2 = Major.query.filter_by(maj_name=maj_n).first()
        maj_i = maj_n2.major_id
        new_stu = Student(major=maj_i, level=request.form["lName"], number=request.form["num"])
        db.session.add(new_stu)
        db.session.commit()
        return redirect(url_for('add_student'))
    return render_template('addStudent.html', all_majs=all_majs, all_stus=all_stus)


@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    all_majs = db.session.query(Major).all()
    all_stus = db.session.query(Student).all()
    if request.method == "POST":
        maj_n = request.form["mName"]
        maj_n2 = Major.query.filter_by(maj_name=maj_n).first()
        maj_i = maj_n2.major_id
        stu_to_update = Student.query.filter_by(major=maj_i, level=request.form["lName"]).first()
        stu_to_update.number = request.form["num"]
        db.session.commit()
        return redirect(url_for('update_student'))
    return render_template('updateStudent.html', all_majs=all_majs, all_stus=all_stus)


@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    all_majs = db.session.query(Major).all()
    all_stus = db.session.query(Student).all()
    if request.method == "POST":
        maj_n = request.form["mName"]
        maj_n2 = Major.query.filter_by(maj_name=maj_n).first()
        maj_i = maj_n2.major_id
        stu_to_delete = Student.query.filter_by(major=maj_i, level=request.form["lName"]).first()
        db.session.delete(stu_to_delete)
        db.session.commit()
        return redirect(url_for('delete_student'))
    return render_template('deleteStudent.html', all_majs=all_majs, all_stus=all_stus)


@app.route('/create_table', methods=['GET', 'POST'])
def create_table():
    all_colls = db.session.query(College).all()
    all_rooms = db.session.query(Room).all()
    all_majors = db.session.query(Major).all()
    all_teachers = db.session.query(Teacher).all()
    all_times = db.session.query(Availability).all()
    all_te_subs = db.session.query(TeacherSubjects).all()
    if request.method == "POST":
        coll_na = request.form['cName']
        coll_1 = db.session.query(College).filter_by(coll_name=coll_na).first()
        coll_i = coll_1.coll_id
        maj_1 = db.session.query(Major).filter_by(coll=coll_i).all()

        MajorsNum = {}
        for m in maj_1:
            st = db.session.query(Student).filter_by(major=m.major_id).all()
            for s in st:
                MajorsNum[f'{m.maj_name}{s.level}'] = s.number

        Rooms = {}
        RoomsCap = {}
        ro = []
        for r in all_rooms:
            RoomsCap[r.room_name] = r.capacity
            if r.room_type == "نظري":
                ro.append(str(r.room_name))
        Rooms['h'] = ro

        tea_times = []
        TeachersTime = []
        tt = {}
        for t in all_teachers:
            for ti in all_times:
                if ti.teacher == t.teach_id:
                    var = {t.teach_name: ti.ava}
                    tea_times.append(var)

        ti_ids = [i.teacher for i in all_times]
        for t in all_teachers:
            if t.teach_id not in ti_ids:
                var = {t.teach_name: "AllTime"}
                tea_times.append(var)

        for t_t in tea_times:
            for key, value in t_t.items():
                if value != "AllTime":
                    stri = value.replace("\'", "\"")
                    v = literal_eval(stri)
                else:
                    v = value
                tt[key] = v

        TeachersTime.append(tt)

        ter = request.form['tName']
        all_subs2 = db.session.query(Subject).all()
        all_subs = []
        for s2 in all_subs2:
            if s2.term == int(ter):
                all_subs.append(s2)

        class_room = ""
        classes = []
        maj_ids = [i.major_id for i in all_majors]
        tea_ids = [j.teach_id for j in all_teachers]
        for s in all_subs:
            if s.maj in maj_ids:
                maj = db.session.query(Major).filter_by(major_id=s.maj).first()
                groups = f"{maj.maj_name}{s.level}"
                for st in all_te_subs:
                    sub = db.session.query(Subject).filter_by(sub_id=st.subject).first()
                    sub_n = sub.sub_name
                    if sub_n == s.sub_name:
                        typ = st.sub_type
                        subject = sub_n
                        length = st.sub_hours
                        if typ == "نظري":
                            class_room = "h"
                            typ = "L"
                        for t_i in tea_ids:
                            if st.teacher == t_i:
                                for t in all_teachers:
                                    if t.teach_id == t_i:
                                        teacher = t.teach_name
                                        var = {"Subject": subject, "Type": typ, "Teacher": teacher, "Groups": [groups],
                                               "ClassRoom": class_room,
                                               "Length": length}
                                        classes.append(var)
                                        break

        ro = [v for k, v in RoomsCap.items()]
        for c in classes:
            holder = ""
            for c2 in classes:
                if c["Groups"][0] != c2["Groups"][0] and c2["Groups"][0] != holder:
                    if c["Subject"] == c2["Subject"]:
                        if c["Type"] == c2["Type"]:
                            if c["Teacher"] == c2["Teacher"]:
                                if c["Length"] == c2["Length"]:
                                    if (MajorsNum[c["Groups"][0]] + MajorsNum[c2["Groups"][0]]) in ro:
                                        c["Groups"].append(c2["Groups"][0])
                                        holder = c2["Groups"][0]
                                        classes.remove(c2)

        var2 = {"Rooms": Rooms, "RoomsCap": RoomsCap, "MajorsNum": MajorsNum,
                "TeachersTime": TeachersTime, "Classes": classes}

        with open("classes/input1.json", "w", encoding='utf-8') as fi:
            json.dump(var2, fi, ensure_ascii=False, indent=4)

        timetable = evolutionary_algorithm("classes/input1.json")

        levels = []
        for t in timetable:
            l = t["Groups"][0][-1]
            if f"المستوى {l}" not in levels:
                levels.append(f"المستوى {l}")

        timetable2 = []
        for l in levels:
            levels2 = []
            for t in timetable:
                if l[-1] == t["Groups"][0][-1]:
                    levels2.append(t)

            timetable2.append(levels2)

        return render_template('createTable2.html', table=timetable2, college=coll_na)
    return render_template('createTable.html', all_colls=all_colls)


# @app.route('/create_table2', methods=['GET'])
# def create_table2():
#     return render_template('createTable2.html')


if __name__ == '__main__':
    app.run(debug=True)
