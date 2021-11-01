from datetime import datetime
import re
from flask import Flask , render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
import json
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import random




# Json file
with open("config.json") as fl:
    content = json.load(fl)["content"]



# APP SETTEING
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data2021.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = "CollegeProject"


# MAIL System
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = content['gmail-user'],
    MAIL_PASSWORD = content['gmail-password']
)
mail = Mail(app)



# Gym Fess 

fess = {
    "Only Gym" :{
            "3 months" : 2000,
            "6 months" : 3000,
            "1 year" : 4000
    },
    "Only Cardio" : {        
          "3 months" : 1500,
          "6 months" : 2000,
          "1 year" : 3000
    },
    "Gym & Cardio" : {
          "3 months" : 3000,
          "6 months" : 4000,
          "1 year" : 5500
    },
    "Personal Training" : {
          "3 months" : 4500,
          "6 months" : 5000,
          "1 year" : 6500
    }      
}



# Contact form database
class Contact_form(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), unique=False, nullable=False)
    Phone_number = db.Column(db.String(20), unique=False, nullable=False)
    Message = db.Column(db.String(500), unique=False, nullable=False)
    Date_time = db.Column(db.DateTime,nullable=False ,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.Sno}--{self.Name}"

class New_user(db.Model):
    Sr_no = db.Column(db.Integer, primary_key=True)
    F_name = db.Column(db.String(80), unique=False, nullable=False)
    L_name = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other', name='varchar'), nullable=False)
    Email_id = db.Column(db.String(120), unique=False, nullable=False) 
    Contact_number = db.Column(db.String(20), unique=False, nullable=False)
    Addharcard = db.Column(db.String(50), unique=False, nullable=False)
    Fitness_Plan = db.Column(db.String(50), unique=False)
    active = db.Column(db.Boolean(), default=False)
    membership = db.Column(db.Boolean(), default=False)
    Date_time = db.Column(db.DateTime,nullable=False ,default=datetime.utcnow)
    payment_method = db.Column(db.Enum('cash', 'online' , name='varchar'))
    unique_ID = db.Column(db.String(10), unique=False, nullable=False)


    def __repr__(self) -> str:
        return f"{self.Sr_no}  {self.F_name} {self.L_name}"


            
# Passing JSON file to Globaly using "content"
@app.context_processor
def context_processor():
    return dict(content=content, fess=fess)





@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/admin", methods=['POST', 'GET'])
def admin():   
    members = New_user.query.all()
    
    if('user' in session and session['user'] == content["Admin_username"]):
          return render_template('Admin_panel/dashboard.html' , members = members)

    if (request.method == "POST"):
        username = request.form.get('username')
        userpass = request.form.get('passwd')
        if(userpass == content["Admin_passwd"] and username == content["Admin_username"]):
            session['user'] = username
            return render_template('Admin_panel/dashboard.html', members= members)
        else:
            msg = "Username & password did'nt Match!"
            return render_template('Admin_panel/admin_login.html', msg=msg)
    return render_template('Admin_panel/admin_login.html')



@app.route('/buy/<plan_name>/<int:price>')
def buy_plans(plan_name, price):

    return render_template('pre_memberse.html')




@app.route('/Just_buy', methods=['POST', 'GET'])
def just_buy_plans():
    if (request.method == "POST"):
        email_id = request.form.get('email_id')
        unique_id = request.form.get('unique_id')
        plan = request.form.get('Plan_info')

        user = New_user.query.filter_by(Email_id = email_id).first()
        Checking_unique_id  =user.unique_ID == unique_id 
        check_fitness_plan = user.Fitness_Plan
        print(check_fitness_plan, user , Checking_unique_id)
        # print(user.posts)
        if user is not None and Checking_unique_id == True:
            if check_fitness_plan == None:
                user.Fitness_Plan = plan
                user.active = True
                db.session.commit()
                # user.add(Fitness_Plan = plan)

                return render_template('pre_memberse.html', message = { 'alert-primary' : "Your Plan is Activated !!!" })
            else:
                return render_template('pre_memberse.html', message = { 'alert-warning' : "Your Plan  is Already Activated" })
        else:
            return render_template('pre_memberse.html', message = {'alert-danger' : "Email-id and Unique code doesn't Mathch!"})    


    return render_template('pre_memberse.html')




@app.route('/addmission', methods=['POST','GET'])
def Addmission():
    if (request.method == "POST"):
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        Addhar_num = request.form.get('AddharNumber')
        Gender = request.form.get('Gender')

        already_Addhar_exist = New_user.query.filter_by(Addharcard=Addhar_num).first()
        already_Email_exist = New_user.query.filter_by(Email_id=email).first()
        print(already_Addhar_exist, already_Email_exist)
        if ((already_Addhar_exist is None) and (already_Email_exist is None)) :
            
            unique_num = random.randint(1000,9999)
            testing_unique_id = New_user.query.filter_by(unique_ID=unique_num).first()
            while testing_unique_id is not None:
                unique_num = random.randint(1000,9999)
                testing_unique_id = New_user.query.filter_by(unique_ID=unique_num).first()
            entry_to_db = New_user(F_name = f_name, L_name = l_name, gender = Gender, Email_id=email, Contact_number = contact_number, Addharcard = Addhar_num,  Date_time= datetime.now(), unique_ID = unique_num)
            db.session.add(entry_to_db)
            db.session.commit()
            mail.send_message('Unique ID From Tauras',
                            sender = f"From Taurus | Testing",
                            recipients =  [email],
                            body =  f'This is for testing purpose \n {unique_num} <- this is your Unique ID , when you buy our any plan, please Login with this code.'
                            )
                
        elif (already_Email_exist is not None):
            return render_template('New_user.html', message = "Email_id Already Used")
        elif (already_Addhar_exist is not None):
            return render_template('New_user.html', message = "This Addhar Card Number Already Used ")

    return render_template('New_user.html')




@app.route('/add_member', methods=['POST','GET'])
def Add_member():
    if('user' in session and session['user'] == content["Admin_username"]):
    
        if (request.method == "POST"):
            f_name = request.form.get('f_name')
            l_name = request.form.get('l_name')
            email = request.form.get('email')
            contact_number = request.form.get('contact_number')
            Addhar_num = request.form.get('AddharNumber')
            Gender = request.form.get('Gender')

            already_Addhar_exist = New_user.query.filter_by(Addharcard=Addhar_num).first()
            already_Email_exist = New_user.query.filter_by(Email_id=email).first()
            print(already_Addhar_exist, already_Email_exist)
            if ((already_Addhar_exist is None) and (already_Email_exist is None)) :

                unique_num = random.randint(1000,9999)
                testing_unique_id = New_user.query.filter_by(unique_ID=unique_num).first()
                while testing_unique_id is not None:
                    unique_num = random.randint(1000,9999)
                    testing_unique_id = New_user.query.filter_by(unique_ID=unique_num).first()

                entry_to_db = New_user(F_name = f_name, L_name = l_name, gender = Gender, Email_id=email, Contact_number = contact_number, Addharcard = Addhar_num,  Date_time= datetime.now(),unique_ID = unique_num)
                db.session.add(entry_to_db)
                db.session.commit()
                mail.send_message('Unique ID From Tauras',
                            sender = f"From Taurus | Testing",
                            recipients =  [email],
                            body =  f'This is for testing purpose \n {unique_num} <- this is your Unique ID , when you buy our any plan, please Login with this code.'
                            )
                # print(f_name, l_name, email, contact_number, Addhar_num, Gender) 

            elif (already_Email_exist is not None):
                return render_template('Admin_panel/Add_member.html', message = "Email_id Already Used")
            elif (already_Addhar_exist is not None):
                return render_template('Admin_panel/Add_member.html', message = "This Addhar Card Number Already Used ")


        return render_template('Admin_panel/Add_member.html')
    else:
        return redirect('/admin')



@app.route("/team")
def team():
    return render_template("team.html")




@app.route("/contact",  methods=['POST', 'GET'])
def contact():
    
    if (request.method == "POST"):

        name = request.form.get('name')
        ph_number = request.form.get('num')
        user_message = request.form.get('message')
        entry = Contact_form(Name=name,Phone_number= ph_number, Message=user_message, Date_time= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                        sender = f"From Taurus | {name}",
                        recipients = [content["gmail-user"]],
                        body =  f'Name : {name} \nmessage : {user_message} \nPhone number : {ph_number}'
                        )
        # print(name, ph_number, user_message)

        message= "Your Message was sent, Thankyou!!"
        return render_template("contact.html", message= message)
    return render_template("contact.html")







@app.route("/admin/contact_database")
def contact_database():
    if('user' in session and session['user'] == content["Admin_username"]):
        contacts_data = Contact_form.query.all()
        return render_template("Admin_panel/contact_db.html", contacts_data = contacts_data)
    else:
        return redirect('/admin')




@app.route('/delete/<int:sr_no>')
def delete(sr_no):
    if('user' in session and session['user'] == content["Admin_username"]):
        contact_data = Contact_form.query.get(sr_no)
        db.session.delete(contact_data)
        db.session.commit()
        return redirect('/admin/contact_database')
    else:
        redirect('/admin')




@app.route('/Details_edit/<int:Sr_no>', methods=['POST','GET'])
def details_edits(Sr_no):
    if('user' in session and session['user'] == content["Admin_username"]):
        member = New_user.query.get(Sr_no)
        if (request.method == "POST"):

            F_name = request.form.get('F_name')
            L_name = request.form.get('L_name')
            Email_id = request.form.get('Email_id')
            contact_num = request.form.get('contact') 
            
            member.F_name = F_name
            member.L_name = L_name
            member.Email_id = Email_id
            member.Contact_number = contact_num
           
            db.session.commit() 
            return render_template('Admin_panel/Edit_detail.html', member=member)
        else:
            return render_template('Admin_panel/Edit_detail.html', member=member)
    else:
        redirect('/admin')



@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/admin')
                 




if __name__ == "__main__":
     app.run(debug=True)    