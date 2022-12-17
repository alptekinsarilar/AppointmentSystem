from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import column_property
from datetime import datetime
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.fields import SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5746@localhost/PROJE_DENEME6'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class Appointment(db.Model):
    _tablename_ = 'appointment'
    doc_id = db.Column(db.String(9), primary_key=True)
    pat_ssn = db.Column(db.String(9), primary_key=True)
    app_date = db.Column(db.Date, nullable=False)
    app_time = db.Column(db.Time, nullable=False)
    app_desc = db.Column(db.String(240))

class Patient(db.Model):
    _tablename_ = 'patient'
    ssn = db.Column(db.String(9), primary_key=True)
    bdate = db.Column(db.Date, nullable=False)
    blood_type = db.Column(db.String(3))
    sex = db.Column(db.String(1))
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)

class Hospital(db.Model):
    _tablename_ = 'hospital'
    hnumber = db.Column(db.String(9), primary_key=True)
    hname = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(300))

class Clinic(db.Model):
    _tablename_ = 'clinic'
    clinic_number = db.Column(db.String(9), primary_key=True)
    clinic_name = db.Column(db.String(35), nullable=False)

class HospitalClinic(db.Model):
    _tablename_ = 'hospital_clinic'
    hnumber = db.Column(db.String(9), primary_key=True)
    clinic_number = db.Column(db.String(9), nullable=False)

class Doctor(db.Model):
    _tablename_ ='doctor'
    doctor_id = db.Column(db.String(9), primary_key = True)
    clinic_number = db.Column(db.String(9), nullable = False)
    hnumber = db.Column(db.String(9), nullable = False)
    bdate = db.Column(db.DateTime)
    fname = db.Column(db.String(20), nullable = False)
    lname = db.Column(db.String(20), nullable = False)
    phone_number = db.Column(db.String(11))
    full_name = column_property(fname + " " + lname)

    def _init_(self, doctor_id, clinic_number, hnumber,fname,lname,phone_number):
        self.doctor_id = doctor_id
        self.clinic_number = clinic_number
        self.hnumber = hnumber
        self.fname = fname
        self.lname = lname
        self.phone_number = phone_number


def the_hospital_factory():
    return Hospital.query

def the_clinic_factory():
     return [Clinic.query.get(item) for item in session['clinics']]

def the_doctor_factory():
     return [Doctor.query.get(item) for item in session['doctors']]


class selectHospitalForm(FlaskForm):
    all_hospitals =  QuerySelectField(query_factory=the_hospital_factory, get_label='hname')# render_kw={"onclick": "clinicFunction();"}
    submit = SubmitField()

class SelectClinicForm(FlaskForm):
    clinics = QuerySelectField(query_factory=the_clinic_factory, get_label='clinic_name')
    submit = SubmitField()

class SelectDoctorForm(FlaskForm):
    doctors = QuerySelectField(query_factory=the_doctor_factory, get_label='clinic_name')
    submit = SubmitField()

@app.route('/', methods = ['POST','GET'])
def index():
    return render_template('show.html', hospital_form=selectHospitalForm())
    # hnumber = ''
    # clinic_num = ''
    # doc_num= ''

    # if request.method == "POST": 
    #     print("HI")

    # try:
    #     Hospitals = Hospital.query.order_by(Hospital.hname).all()
    #     hnames = []
    #     for h in Hospitals:
    #         hnames.append(h.hname)
    #     return render_template('index.html',hnames = hnames)
    # except Exception as e:
    #     # e holds description of the error
    #     error_text = "<p>The error:<br>" + str(e) + "</p>"
    #     hed = '<h1>Something is broken.</h1>'
    #     return hed + error_text


@app.route('/appointment',methods=['POST','GET'])
def appointment():
    session['doctors'] = []
    session['clinics'] = []
    hospital_form = selectHospitalForm()
    clinic_form = SelectClinicForm()
    doctor_form = SelectDoctorForm()



    return render_template('appointment.html',hospital_form =hospital_form, clinic_form = clinic_form, doctor_form = doctor_form)

@app.route("/appointment/<hospital>")
def get_hospital(hospital):
    joined_table = db.session.query(Clinic, Hospital, HospitalClinic
        ).filter(Hospital.hnumber==hospital
        ).join(HospitalClinic,HospitalClinic.hnumber==Hospital.hnumber 
        ).join(Clinic, Clinic.clinic_number==HospitalClinic.clinic_number
        ).all()    
    print(joined_table)
    clinic_array = []

    for all in joined_table:
        clinic = all[0]
        cliObj = {}
        cliObj["clinic_number"]  = clinic.clinic_number
        cliObj["clinic_name"]  = clinic.clinic_name
        clinic_array.append(cliObj)

    return jsonify({'clinics':clinic_array})   

@app.route("/appointment/<hospital>/<clinic>")
def get_doctors(hospital,clinic):
    doctors = Doctor.query.filter_by(hnumber = hospital,clinic_number = clinic)
    doctor_array = []

    for doctor in doctors:
        docObj = {}
        docObj["doctor_id"]  = doctor.doctor_id
        docObj["full_name"]  = doctor.full_name
        doctor_array.append(docObj)

    return jsonify({'doctors':doctor_array})      

  

@app.route('/hospital',methods=['POST','GET'])
def hospital():
    hospital = selectHospitalForm()
    clinic_form = SelectClinicForm()


    return render_template('show.html', hospital_form=hospital ,clinic_form = clinic_form)

@app.route('/get-clinics', methods=['GET', 'POST'])
def get_clinics():
    print("HI!")
    selected_hospital= request.get_json(silent=False)
    selected_clinics = Clinic.query.all()
    session['clinics'] = [item.clinic_number for item in selected_clinics]
    session['selected_hospital'] = selected_hospital
    return render_template('show.html', hospital_form = selectHospitalForm() , clinic_form =SelectClinicForm() )


@app.route("/doctors")
def doctors():
    try:
        doctors = Doctor.query.order_by(Doctor.fname).all()
        doc_text = '<ul>'
        for doctor in doctors:
            sock_text += '<li>' + sock.fname + ', ' + sock.lname +',' + '</li>'
            print(doctor.fname)
        sock_text += '</ul>'
        return sock_text
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text



@app.route("/addperson")
def addperson():
    return render_template("add_doctor.html")   

@app.route("/deneme")
def deneme():
    return render_template("deneme.html")   

@app.route('/create_file', methods=['POST'])
def create_file():
    if request.method == 'POST':
        print("Request handled")
        return render_template('add_doctor.html')


@app.route("/personadd", methods=['POST'])
def personadd():
    doctor_id = request.form["doctor_id"]
    clinic_number = request.form["clinic_number"]
    hnumber = request.form["hnumber"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    phone_number = request.form["phone_number"]
    entry = Doctor( doctor_id, clinic_number, hnumber,fname,lname,phone_number)
    db.session.add(entry)
    db.session.commit()

    return render_template("add_doctor.html")


if(__name__== "__main__"):
    # db.create_all()
    csrf.init_app(app)
    app.run(debug=True)    
    