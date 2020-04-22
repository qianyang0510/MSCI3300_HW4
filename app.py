from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qianyang:@localhost/pokemon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

@app.before_first_request
def create_db():
    # Recreate database each time for demo
    db.create_all()

def serialize_list(model_list):
    return [m.as_dict() for m in model_list]

class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100))
    attack = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class NewPokemonForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    attack = IntegerField("Attack", validators=[DataRequired()])

class UpdatePokemonForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    attack = IntegerField("Attack", validators=[DataRequired()])

class SearchPokemonForm(FlaskForm):
    name = StringField("Pokemon Name:")

class DeletePokemonForm(FlaskForm):
    id = IntegerField()

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_form = SearchPokemonForm()
        if search_form.validate_on_submit():
            results = Pokemon.query.filter(Pokemon.name.like('%{}%'.format(search_form.name.data))).all()
            return render_template('search.html',results=results)
    return render_template('search.html')   

@app.route("/")
def index(form=None):
    if form is None:
        form = NewPokemonForm()
    pokemons = list(Pokemon.query.order_by(Pokemon.id))
    return render_template("master.html", pokemons=pokemons, form=form)


@app.route("/detail/<int:id>", methods=['GET','POST'])
def detail(id,form=None):
    pokemon = Pokemon.query.filter_by(id=id).one()
    if form is None:
        form = UpdatePokemonForm()
    return render_template('detail.html',pokemon=pokemon,form=form)


@app.route("/add/", methods=["POST"])
def add_pokemon():
    form = NewPokemonForm()
    if form.validate_on_submit():
        db.session.add(Pokemon(name=form.name.data, type=form.type.data, attack=form.attack.data))
        db.session.commit()
        return redirect(url_for("index"))
    return index(form)


@app.route("/update/<int:id>", methods=["POST"])
def update_pokemon(id):
    pokemon = Pokemon.query.filter_by(id=id).one()
    form = UpdatePokemonForm()
    if form.validate_on_submit():
        pokemon.name = form.name.data
        pokemon.type = form.type.data
        pokemon.attack = form.attack.data
        db.session.commit()
    return detail(id)


@app.route("/delete", methods=("POST",))
def delete_pokemon():
    form = DeletePokemonForm()
    if form.validate_on_submit():
        pokemon = db.session.query(Pokemon).filter_by(id=form.id.data).one()
        db.session.delete(pokemon)
        db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
