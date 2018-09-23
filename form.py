from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(1,64)])
    remember_me = BooleanField("Keep me logged in")
    submit1 = SubmitField('Log in')
    
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(1,64)])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirmation = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit2 = SubmitField('Register')

class NewItemForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField("Category", choices=[('snowboarding','Snowboarding'), ('soccer','Soccer'), ('basketball', 'Basketball'), ('baseball','Baseball'), ('frisbee','Frisbee'), ('rock_climbing','Rock Climbing'), ('foosball','Foosball'), ('hockey','Hockey')])
    submit3 = SubmitField('Add new item')

class DeleteForm(FlaskForm):
    submit4 = SubmitField("Delete")

