from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class InputForm(FlaskForm):
    src_long = StringField("Longitude Co-ordinates", validators=[DataRequired()])
    src_lat = StringField("Latitude Co-ordinates", validators=[DataRequired()])
    dest_long = StringField("Longitude Co-ordinates", validators=[DataRequired()])
    dest_lat = StringField("Latitude Co-ordinates", validators=[DataRequired()])
    offset = StringField("Distance Offset (meters)", validators=[DataRequired()])
    submit = SubmitField("Submit")

