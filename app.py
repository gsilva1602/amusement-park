from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


# Configurating falsk app and the SQLAlchemy
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Configurating data model
class ToyA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lines = db.relationship('LineA', backref='toy_a', lazy=True)

class LineA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    toy_a_id = db.Column(db.Integer, db.ForeignKey('toy_a.id'))

class ToyB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lines = db.relationship('LineB', backref='toy_b', lazy=True)

class LineB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    toy_b_id = db.Column(db.Integer, db.ForeignKey('toy_b.id'))

class ToyC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lines = db.relationship('LineC', backref='toy_c', lazy=True)

class LineC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    toy_c_id = db.Column(db.Integer, db.ForeignKey('toy_c.id'))


# Creating table data
with app.app_context():
    db.create_all()


# Checking if the cellphone number is in line 
def is_number_in_line(number):
    if LineA.query.filter_by(number=number).first():
        return True
    
    if LineB.query.filter_by(number=number).first():
        return True
    
    if LineC.query.filter_by(number=number).first():
        return True
    
    return False


# Changing the name "Toy" to "Brinquedo"
def map_toy_name(db_toy_name):
    if db_toy_name == "Toy A":
        return "Brinquedo A"
    elif db_toy_name == "Toy B":
        return "Brinquedo B"
    elif db_toy_name == "Toy C":
        return "Brinquedo C"
    return db_toy_name

# Define home page and render the form
@app.route('/')
def home():
    return render_template('home.html')


# Function to leave of the line if the user wants
@app.route('/leave_line/<toy>/<string:number>', methods=['POST'])
def leave_line(toy, number):
    if toy == 'A':
        line_model = LineA
    elif toy == 'B':
        line_model = LineB
    elif toy == 'C':
        line_model = LineC
    else:
        return 'Brinquedo não encontrado'

    line = line_model.query.filter_by(number=number).first()
    if line:
        db.session.delete(line)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return 'Registro não encontrado na fila'


# If the administrator wants delete an user
@app.route('/delete_user', methods=['POST'])
def delete_user():
    toy = request.form.get('toy')
    line_id = request.form.get('line_id')

    if toy == 'Brinquedo A':
        line_model = LineA
    elif toy == 'Brinquedo B':
        line_model = LineB
    elif toy == 'Brinquedo C':
        line_model = LineC
    else:
        return 'Brinquedo não encontrado.'

    line = line_model.query.get_or_404(line_id)
    db.session.delete(line)
    db.session.commit()

    return redirect(url_for('list_toy', toy_name=toy))


# List of registers
@app.route('/list')
def list():
    all_toys = ["Brinquedo A", "Brinquedo B", "Brinquedo C"]
    toy_lines = {toy: [] for toy in all_toys}
    
    return render_template('list.html', toy_lines=toy_lines, selected_toy=None, all_toys=all_toys)


# Place where the admin can see the people subscribed on the line
@app.route('/list/<toy_name>')
def list_toy(toy_name):
    if toy_name == 'Brinquedo A':
        toy = ToyA.query.filter_by(name='Toy A').first()
    elif toy_name == 'Brinquedo B':
        toy = ToyB.query.filter_by(name='Toy B').first()
    elif toy_name == 'Brinquedo C':
        toy = ToyC.query.filter_by(name='Toy C').first()
    else:
        return 'Brinquedo não encontrado.'
    
    if toy is None:
        return 'Brinquedo não encontrado no banco de dados.'
    
    lines = []
    if toy:
        for line in toy.lines:
            lines.append((line.name, line.number, line.id))

    toy_lines = {toy.name: lines}
    all_toys = ["Brinquedo A", "Brinquedo B", "Brinquedo C"]

    return render_template('list.html', toy_lines=toy_lines, selected_toy=toy_name, all_toys=all_toys)


# Home page where the user can choose the toy that they want
@app.route('/choose_toy', methods=['POST'])
def choose_toy():
    selected_toy = request.form.get('toy')
    if selected_toy == 'A':
        return redirect(url_for('register_toy_a', toy=selected_toy))
    elif selected_toy == 'B':
        return redirect(url_for('register_toy_b', toy=selected_toy))
    elif selected_toy == 'C':
        return redirect(url_for('register_toy_c', toy=selected_toy))


# Check the line position from Toy A
@app.route('/position_toy_a/<string:number>')
def position_toy_a(number):
    line = LineA.query.filter_by(number=number).first()
    if line:
        position = LineA.query.filter(LineA.id < line.id).count() + 1
        return render_template('position.html', name=line.name, number=line.number, position=position, toy='A')
    else:
        return render_template('home.html')
    

# Check the line position from Toy B
@app.route('/position_toy_b/<string:number>')
def position_toy_b(number):
    line = LineB.query.filter_by(number=number).first()
    if line:
        position = LineB.query.filter(LineB.id < line.id).count() + 1
        return render_template('position.html', name=line.name, number=line.number, position=position, toy='B')
    else:
        return render_template('home.html')
    

# Check the line position from Toy C
@app.route('/position_toy_c/<string:number>')
def position_toy_c(number):
    line = LineC.query.filter_by(number=number).first()
    if line:
        position = LineC.query.filter(LineC.id < line.id).count() + 1
        return render_template('position.html', name=line.name, number=line.number, position=position, toy='C')
    else:
        return render_template('home.html')
        

# Where an user can subscribe to enter in the Toy A line
@app.route('/register_toy_a', methods=['GET', 'POST'])
def register_toy_a():
    if ToyA.query.count() == 0:
        toy_a = ToyA(name='Toy A')
        db.session.add(toy_a)
        db.session.commit()
        pass
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        toy_a = ToyA.query.filter_by(name='Toy A').first()

        if not toy_a:
            warning = 'Brinquedo A não encontrado.'
            return render_template('form.html', toy='A', warning=warning)
        
        existing_number = LineA.query.filter_by(toy_a_id=toy_a.id, number=number).first()
        if existing_number:
           warning = 'Este número de telefone já se encontra nesta fila.'
           return render_template('form.html', toy='A', warning=warning)
        
        if is_number_in_line(number):
            warning = 'Este número de telefone já se encontra na fila de outro brinquedo.'
            return render_template('form.html', toy='A', warning=warning)
        
        lines = LineA.query.filter_by(toy_a_id=toy_a.id).all()
        line_position = len(lines) + 1
        new_line = LineA(name=name, number=number, toy_a_id=toy_a.id)
        db.session.add(new_line)
        db.session.commit()

        return redirect(url_for('position_toy_a', toy=toy_a, name=new_line.name, number=new_line.number, position=line_position))
    return render_template('form.html', toy='A')


# Where an user can subscribe to enter in the Toy B line
@app.route('/register_toy_b', methods=['GET', 'POST'])
def register_toy_b():
    if ToyB.query.count() == 0:
        toy_b = ToyB(name='Toy B')
        db.session.add(toy_b)
        db.session.commit()

    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        toy_b = ToyB.query.filter_by(name='Toy B').first()

        if not toy_b:
            warning = 'Brinquedo B não encontrado.'
            return render_template('form.html', toy='B', warning=warning)
        
        existing_number = LineB.query.filter_by(toy_b_id=toy_b.id, number=number).first()
        if existing_number:
           warning = 'Este número de telefone já se encontra nesta fila.'
           return render_template('form.html', toy='B', warning=warning)
        
        if is_number_in_line(number):
            warning = 'Este número de telefone já se encontra na fila de outro brinquedo.'
            return render_template('form.html', toy='B', warning=warning)
        
        lines = LineB.query.filter_by(toy_b_id=toy_b.id).all()
        line_position = len(lines) + 1
        new_line = LineB(name=name, number=number, toy_b_id=toy_b.id)
        db.session.add(new_line)
        db.session.commit()

        return redirect(url_for('position_toy_b', toy=toy_b, name=new_line.name, number=new_line.number, position=line_position))
    return render_template('form.html', toy='B')


# Where an user can subscribe to enter in the Toy C line
@app.route('/register_toy_c', methods=['GET', 'POST'])
def register_toy_c():
    if ToyC.query.count() == 0:
        toy_c = ToyC(name='Toy C')
        db.session.add(toy_c)
        db.session.commit()

    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        toy_c = ToyC.query.filter_by(name='Toy C').first()

        if not toy_c:
            warning = 'Brinquedo C não encontrado.'
            return render_template('form.html', toy='C', warning=warning)
        
        existing_number = LineC.query.filter_by(toy_c_id=toy_c.id, number=number).first()
        if existing_number:
           warning = 'Este número de telefone já se encontra nesta fila.'
           return render_template('form.html', toy='C', warning=warning)
        
        if is_number_in_line(number):
            warning = 'Este número de telefone já se encontra na fila de outro brinquedo.'
            return render_template('form.html', toy='C', warning=warning)
        
        lines = LineC.query.filter_by(toy_c_id=toy_c.id).all()
        line_position = len(lines) + 1
        new_line = LineC(name=name, number=number, toy_c_id=toy_c.id)
        db.session.add(new_line)
        db.session.commit()

        return redirect(url_for('position_toy_c', toy=toy_c, name=new_line.name, number=new_line.number, position=line_position))
    return render_template('form.html', toy='C')


# Run time
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)