from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date


app = Flask (__name__)

app.secret_key = 'biblioteca_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/sistema_biblioteca'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Livro(db.Model):
	__tablename__ = 'livros'

	id = db.Column(db.Integer, primary_key = True)
	titulo = db.Column(db.String(255), nullable = False)
	autor = db.Column(db.String(255), nullable = False)
	categoria = db.Column(db.String(100))
	ano = db.Column(db.Integer)

	disponivel = db.Column (db.Boolean, default = True)

	emprestimos = db.relationship(
		'Emprestimo',
		backref= 'livro',
		lazy = True
		)

class Usuario(db.Model):
	__tablename__ = 'usuarios'

	id = db.Column(db.Integer, primary_key = True)

	nome = db.Column(db.String(255), nullable = False)
	email = db.Column(db.String(255), nullable = False)
	telefone = db.Column(db.String(20))
	senha = db.Column(db.String(255), nullable = False)
	tipo = db.Column(db.String(20), default='leitor')

	emprestimos = db.relationship(
		'Emprestimo',
		backref= 'usuario',
		lazy = True
		)

class Emprestimo(db.Model):
	__tablename__ = 'emprestimos'

	id = db.Column(db.Integer, primary_key = True)
	status = db.Column(db.String(20), default='ativo')

	id_usuario = db.Column(
		db.Integer,
		db.ForeignKey('usuarios.id')
		)

	id_livro = db.Column(
		db.Integer,
		db.ForeignKey('livros.id')

		)

	data_emprestimo = db.Column(db.Date)
	data_devolucao = db.Column(db.Date)




#Rota de conexão para o html
@app.route('/')
def home():
	return render_template('login.html')

#Rota para tela de cadastro do usuario
@app.route('/cadastro')
def tela_cadastro():

	return render_template(
		'cadastrar_usuario.html'
		)



#Rota login
@app.route('/login', methods = ['POST'])
def login():

	email = request.form['email']
	senha = request.form['senha']

	usuario = Usuario.query.filter_by(
		email = email,
		senha = senha
		).first()

	if usuario:

		session['usuario_id'] = usuario.id
		session['usuario_nome'] = usuario.nome
		session['usuario_tipo'] = usuario.tipo
		
		if usuario.tipo == 'admin':
			return redirect('/dashboard_admin')

		else:
			return redirect('/dashboard_leitor')


	return 'Email ou senha inválidos'


#Rota dashboard admin
@app.route('/dashboard_admin')
def dashboard_admin():

	livros_cadastrados = Livro.query.count()

	emprestimos_ativos = Emprestimo.query.filter_by(
		data_devolucao = None
		).count()

	devolucoes_pendentes = Emprestimo.query.filter_by(
		data_devolucao = None
		).count()

	return render_template(

		'dashboard_admin.html',

		livros_cadastrados = livros_cadastrados,

		emprestimos_ativos = emprestimos_ativos,

		devolucoes_pendentes = devolucoes_pendentes

		)

#Rota tela de gerenciamento admin
@app.route('/admin')
def admin():

	lista_livros = Livro.query.all()

	return render_template(
		'admin.html',
		livros = lista_livros
		)

#Rota dashboard leitor
@app.route('/dashboard_leitor')
def dashboard_leitor():

	livros_disponiveis = Livro.query.filter_by(
		disponivel = True
		).count()

	meus_emprestimos = Emprestimo.query.filter_by(
		data_devolucao = None
		).count()

	historico = Emprestimo.query.count()


	return render_template(

	'dashboard_leitor.html',

	livros_disponiveis = livros_disponiveis,

	meus_emprestimos = meus_emprestimos,

	historico = historico

	)

#Rota tela recuperar senha
@app.route('/recuperar')
def recuperar():

	return render_template(
		'recuperar.html'
		)

#Rota alterar senha
@app.route('/alterar_senha', methods = ['POST'])
def alterar_senha():

	email = request.form['email']
	nova_senha = request.form['senha']

	usuario = Usuario.query.filter_by(
		email = email
		).first()

	if usuario:

		usuario.senha = nova_senha

		db.session.commit()

		return redirect('/')

	return 'Usuário não encontrado'

#Rota livros
@app.route('/livros')
def livros():


	lista_livros = Livro.query.all()

	return render_template(
		'livros.html',
		livros = lista_livros
		)

#Rota livros api
@app.route('/api/livros')
def api_livros():

	livros = Livro.query.all()

	lista = []

	for livro in livros: 

		status = 'disponivel'

		if livro.disponivel == False:
			status = 'alugado'

		lista.append({

			'id' : livro.id,
			'titulo': livro.titulo,
			'autor': livro.autor,
			'categoria': livro.categoria,
			'ano': livro.ano,
			'status': status

			})

	return jsonify(lista)


#Rota cadastro livro
@app.route ('/cadastrar_livro', methods = ['POST'])
def cadastrar_livro():

	titulo = request.form['titulo']
	autor = request.form['autor']
	categoria = request.form['categoria']
	ano = request.form['ano']


	novo_livro = Livro(
		titulo = titulo,
		autor = autor,
		categoria = categoria,
		ano = ano
		)

	db.session.add(novo_livro)
	db.session.commit()


	return redirect('/admin')

#Rota editar livro
@app.route('/editar_livro/<int:id>')
def editar_livro(id):

	livro = Livro.query.get_or_404(id)

	return render_template(
		'editar_livro.html',
		livro = livro
		)

#Rota atualizar livro
@app.route('/atualizar_livro/<int:id>', methods = ['POST'])
def atualizar_livro(id):

	livro = Livro.query.get_or_404(id)

	livro.titulo = request.form['titulo']
	livro.autor = request.form['autor']
	livro.categoria = request.form['categoria']
	livro.ano = request.form ['ano']

	db.session.commit()

	return redirect('/admin')

#Rota deletar
@app.route('/deletar_livro/<int:id>')
def deletar_livro(id):

	livro = Livro.query.get_or_404(id)

	db.session.delete(livro)
	db.session.commit()


	return redirect('/admin')

#Rota devolução de livros
@app.route('/devolucoes')
def devolucoes():

	lista_emprestimos = Emprestimo.query.filter_by(
		data_devolucao = None
		).all()

	return render_template(
		'devolucoes.html',
		emprestimos = lista_emprestimos
		)


#rota lista usuarios
@app.route('/usuarios')
def usuarios():

	lista_usuarios = Usuario.query.all()

	return render_template(
		'usuarios.html',
		usuarios = lista_usuarios)

#Rota cadastrar usuário
@app.route('/cadastrar_usuario', methods = ['POST'])
def cadastrar_usuario():

	nome = request.form['nome']
	email = request.form['email']
	telefone = request.form['telefone']
	senha = request.form['senha']


	novo_usuario = Usuario(
		nome = nome,
		email = email,
		telefone = telefone,
		senha = senha
		)

	db.session.add(novo_usuario)
	db.session.commit()

	return redirect('/')

#Rota editar usuário 
@app.route('/editar_usuario/<int:id>')
def editar_usuario(id):

	usuario = Usuario.query.get(id)

	return render_template(
		'editar_usuario.html',
		usuario = usuario
		)

#Rota atualizar usuário
@app.route('/atualizar_usuario/<int:id>', methods = ['POST'])
def atualizar_usuario(id):

	usuario = Usuario.query.get(id)


	usuario.nome = request.form['nome']
	usuario.email = request.form['email']
	usuario.telefone = request.form['telefone']
	usuario.senha = request.form['senha']

	db.session.commit()

	return redirect('/usuarios')

#Rota deletar usuário
@app.route('/deletar_usuario/<int:id>')
def deletar_usuario(id):

	usuario = Usuario.query.get(id)

	db.session.delete(usuario)
	db.session.commit()

	return redirect('/usuarios')

#Rota Listar empréstimos
@app.route('/emprestimos')
def emprestimos():
	
	lista_emprestimos = Emprestimo.query.all()


	return render_template(
		'emprestimos.html',
		emprestimos = lista_emprestimos
		)

#Rota Realizar empréstimos
@app.route('/realizar_emprestimo', methods = ['POST'])
def realizar_emprestimo():

	id_usuario = session['usuario_id']
	id_livro = request.form['id_livro']

	livro = Livro.query.get(id_livro)


	if livro.disponivel == False:
		return 'Livro indisponível'


	novo_emprestimo = Emprestimo(

		id_usuario = id_usuario,
		id_livro = id_livro,

		data_emprestimo = date.today()
		)

	livro.disponivel = False

	db.session.add(novo_emprestimo)
	db.session.commit()

	return jsonify({
		'mensagem': 'Livro alugado com sucesso'
		})

#Rota devolver livros
@app.route('/devolver/<int:id>')
def devolver(id):

	emprestimo = Emprestimo.query.get(id)


	livro = Livro.query.get(
		emprestimo.id_livro
		)

	livro.disponivel = True

	emprestimo.data_devolucao = date.today()

	db.session.commit()

	return redirect('/emprestimos')

#Tela meus livros
@app.route('/meuslivros')
def tela_meus_livros():

	return render_template(
		'meuslivros.html'
		)


#Rota meus livros
@app.route('/meus_livros')
def meus_livros():

	lista_emprestimos = Emprestimo.query.all()

	lista = []

	for emprestimo in lista_emprestimos:

		livro = Livro.query.get(
			emprestimo.id_livro
		)

		lista.append({

			'id': emprestimo.id,

			'titulo': livro.titulo,

			'data_emprestimo': str(
				emprestimo.data_emprestimo
			),

			'data_devolucao': str(
				str(emprestimo.data_devolucao)
				if emprestimo.data_devolucao
				else 'Não devolvido'
			)

		})

	return jsonify(lista)

#Tela buscar livros
@app.route('/buscar_livros')
def buscar_livros():

	return render_template(
		'livros.html'

		)

#Rota Tela do histórico
@app.route('/historico_html')
def historico_html():

	lista_emprestimos = Emprestimo.query.all()

	return render_template(
		'historicol.html',
		emprestimos = lista_emprestimos
		)

#Rota Api do histórico
@app.route('/historico')
def historico():

	lista_emprestimos = Emprestimo.query.all()

	lista = []

	for emprestimo in lista_emprestimos:

		livro = Livro.query.get(
			emprestimo.id_livro
		)

		status = 'Pendente'

		if emprestimo.data_devolucao:
			status = 'Devolvido'

		lista.append({

			'titulo': livro.titulo,

			'data_emprestimo': str(
				emprestimo.data_emprestimo
			),

			'data_devolucao': str(
				emprestimo.data_devolucao
				) if emprestimo.data_devolucao
				else 'Não devolvido',

				'status': status
			})


	return jsonify(lista)


if __name__ == '__main__':
	app.run(debug = True)

