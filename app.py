import sqlite3
from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, socket

app = Flask(__name__)
app.secret_key = os.urandom( 24 )

@app.before_request
def before_request():
        g.user = session['user'] if 'user' in session else None
        g.rol = session['rol'] if 'rol' in session else None
        g.home_page = session['homepage'] if 'homepage' in session else None

@app.route('/', methods=['GET'])
def index():
    if g.user:
        return redirect(session['homepage'])
    return render_template("index.html")

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    #Evita el retorno a login en caso de que el usuario ya haya ingresardo y quiera volver a login.
    if g.user:
        return redirect(session['homepage'])
    if request.method=='POST':
        username = request.form['user']
        password = request.form['password']

        con = sqlite3.connect('db_empleados.db')
        cursor = con.cursor()

        user = cursor.execute("SELECT * FROM empleado WHERE nombre_usuario = ? ", (username, )).fetchone()
        con.close() 
        if user is None:
            mensaje="No se encontró el usuario"
            
            return render_template('index.html', mensaje=mensaje)
      
        else:

            okPass=check_password_hash(user[4], password)

            if okPass:
                session['sessaddr'] = request.remote_addr
                session['user']= user[1]
                session['name_user']=user[11]
                if user[10] == 2: 
                    session['rol']="Administrador"
                    session['homepage'] = url_for('loginAdmin')
                    return redirect(url_for('loginAdmin'))
                elif user[10] ==3:
                    session['rol']="Empleado"
                    session['homepage'] = url_for('loginEmployee')
                    return loginEmployee()
                elif user[10] == 1:
                    session['rol']="SuperAdmin"
                    session['homepage'] = url_for('loginSuperadmin') 
                    return loginSuperadmin()
            else:
                mensaje="Contraseña incorrecta"
            return render_template('index.html', mensaje=mensaje)

       
    else: 

        return render_template('index.html')

@app.route('/login/superadmin', methods=('GET', 'POST'))
def loginSuperadmin():
    return redirect(url_for('dashboard'))

@app.route('/login/employee', methods=('GET', 'POST'))
def loginEmployee():

    print(request.method)
    print(session['user'])

    if request.method == 'POST' and  'user' in session:

        username = request.form['user']

        con = sqlite3.connect('db_empleados.db')
        cursor = con.cursor()
        
        cursor.execute("SELECT * FROM empleado WHERE nombre_usuario = ?", (username, ))
        row=cursor.fetchone()

        cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row[8],))
        rw = cursor.fetchone()
   
        cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row[9],))
        rw2 = cursor.fetchone()

        cursor.execute("SELECT mes FROM retroalimentacion WHERE empleado_id = ?", (row[0],))
        meses=cursor.fetchall()

        mesesarray=[]
        
        for mes in meses:
            stri=''.join(mes)
            mesesarray.append(stri)
      
        return render_template('user_employee.html', nombre=row[1], id=row[0], direccion=row[5], telefono=row[6], inicio=rw[1], contrato=row[8], fin=rw[2], dependencia=rw2[1], salario=rw[3], meses=mesesarray)
    
    
    elif request.method == 'GET' and  'user' in session:

        username = session['name_user']

        con = sqlite3.connect('db_empleados.db')
        cursor = con.cursor()
        
        cursor.execute("SELECT * FROM empleado WHERE nombre_usuario = ?", (username, ))
        row=cursor.fetchone()

        cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row[8],))
        rw = cursor.fetchone()
   
        cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row[9],))
        rw2 = cursor.fetchone()

        cursor.execute("SELECT mes FROM retroalimentacion WHERE empleado_id = ?", (row[0],))
        meses=cursor.fetchall()

        mesesarray=[]
        
        for mes in meses:
            stri=''.join(mes)
            mesesarray.append(stri)

        return render_template('user_employee.html', nombre=row[1], id=row[0], direccion=row[5], telefono=row[6], inicio=rw[1], contrato=row[8], fin=rw[2], dependencia=rw2[1], salario=rw[3], meses=mesesarray)

    else:
        return render_template('user_employee.html')


@app.route('/login/employee/feed', methods=('GET', 'POST'))
def feed():

    if request.method == 'POST':

        try:
            mes = request.form['Mes']
            username = request.form['id']

            print(username)

            con = sqlite3.connect('db_empleados.db')
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM empleado WHERE empleado_id = ?", (username, ))
            row1 = cursor.fetchone()
            
            cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row1[8],))
            rw1 = cursor.fetchone()

            cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row1[9],))
            rw21 = cursor.fetchone()

            cursor.execute("SELECT * FROM retroalimentacion WHERE mes = ?", (mes,))
            rw31 = cursor.fetchone()

            cursor.execute("SELECT mes FROM retroalimentacion WHERE empleado_id = ?", (username,))
            meses=cursor.fetchall()

            mesesarray=[]
        
            for mes in meses:
                stri=''.join(mes)
                mesesarray.append(stri)
        
            return render_template('user_employee.html', nombre=row1[1], id=row1[0], direccion=row1[5], telefono=row1[6], inicio=rw1[1], contrato=row1[8], fin=rw1[2], dependencia=rw21[1], salario=rw1[3], feed=rw31[3], meses=mesesarray)
        
        except TypeError:
            return render_template('user_employee.html', msn="fail")

    else:
        return render_template('user_employee.html')

@app.route('/login/admin', methods=('GET', 'POST'))
def loginAdmin():
    if session['rol'] != "Administrador":
        mensaje="No esta autroizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('view_admin.html')
    
           

@app.route('/admin/addemployee/', methods=('GET', 'POST'))
def adminAdd():
    if 'SuperAdmin' != g.rol !="Administrador":
        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('add_employee.html')

@app.route('/admin/addemployee/new', methods=('GET', 'POST'))
def adminAddnew():

    if request.method=='POST' and 'SuperAdmin' == g.rol or g.rol == "Administrador":

        name = request.form['name']
        cedula = request.form['cedula']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        genero = request.form['genero']
        contrasena = request.form['contrasena']
        usuario = request.form['usuario']
        correo = request.form['correo']
        admision = request.form['admision']
        contract = request.form['contract']
        contract_end = request.form['contract_end']
        dependencia = request.form['dependencia']
        salary = request.form['salary']
        rol = request.form['rol']
      

        con = sqlite3.connect('db_empleados.db')
        cursor = con.cursor()

        cursor.execute("INSERT INTO contrato values (?, ?, ?, ?)", (contract, admision, contract_end, salary))
        cursor.execute("INSERT INTO empleado (nombre, cedula, genero, password, direccion, telefono, correo, contrato_id, dependencia_id, rol_id, nombre_usuario) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, cedula, genero, generate_password_hash(contrasena), direccion, telefono, correo, contract, dependencia, rol, usuario))

        con.commit()
        con.close()
        return render_template('add_employee.html', name=name)

    else:
        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)



@app.route('/admin/findemployee')
def adminFind():
    if 'SuperAdmin' != g.rol !="Administrador":
        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('find_employee.html')

@app.route('/admin/findemployee/find', methods = ['GET', 'POST'])
def find():

    if request.method=='POST' and session['rol']=="Administrador":
        try:
            cedula = request.form['findbyname']
            
            con = sqlite3.connect('db_empleados.db')
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM empleado WHERE cedula = ?", (cedula,))

            row = cursor.fetchone()
            
            cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row[8],))

            rw = cursor.fetchone()

            cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row[9],))

            rw2 = cursor.fetchone()
        
            return render_template('find_employee.html', nombre=row[1], id=row[0], direccion=row[5], telefono=row[6], inicio=rw[1], contrato=row[8], fin=rw[2], dependencia=rw2[1], salario=rw[3])
        
        except TypeError:

            return render_template('find_employee.html', msn="fail")

        
    else: 

        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)

@app.route('/admin/Editemploye/')
def adminEdit():
    if 'SuperAdmin' != g.rol !="Administrador":
        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('edit_employee.html', id="")

@app.route('/admin/Editemploye/findedit', methods=('GET', 'POST'))
def findEdit():
    
    if request.method=='POST' and session['rol']=="Administrador":

        try:
            cedula = request.form['findbyname']
            
            con = sqlite3.connect('db_empleados.db')
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM empleado WHERE cedula = ?", (cedula,))
            row = cursor.fetchone()
                    
            cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row[8],))
            rw = cursor.fetchone()
    
            cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row[9],))

            rw2 = cursor.fetchone()
            
            return render_template('edit_employee.html', nombre=row[1], id=row[0], direccion=row[5], telefono=row[6], inicio=rw[1], contrato=row[8], fin=rw[2], dependencia=rw2[1], salario=rw[3])
        except TypeError:
            return render_template('edit_employee.html', error = "error")
    else:

        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
@app.route('/admin/Editemploye/edit', methods=('GET', 'POST'))
def Edit():

    if request.method=='POST' and session['rol']=="Administrador":
        nombre = request.form['name']
        identificador=request.form['cedula']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        inicio = request.form['inicio']
        contrato = request.form['contract']
        fin = request.form['fin']
        salario = request.form['salario']
        mes=request.form['Mes']
        feedback=request.form['txtarea']

        con = sqlite3.connect('db_empleados.db')
        cursor = con.cursor()

        cursor.execute("UPDATE empleado SET nombre = ?, direccion = ?, telefono = ?  WHERE empleado_id = ?", (nombre, direccion, telefono, identificador))
        cursor.execute("UPDATE contrato SET fecha_inicio = ?, fecha_fin = ?, salario = ?  WHERE contrato_id = ?", (inicio, fin, salario, contrato))
        cursor.execute("INSERT INTO retroalimentacion (empleado_id, mes, feedback) values(?, ?, ?)", (identificador, mes, feedback))

        con.commit()
        con.close()

        return render_template('edit_employee.html', identificador=identificador)
    else:

        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)

@app.route('/admin/deleteEmployee/')
def adminDelete():
    if 'SuperAdmin' != g.rol !="Administrador":
        mensaje="No esta autorizado para ingresar a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('delete_employee.html')

@app.route('/admin/deleteEmployee/findel', methods=['POST'])
def findelete():
    if request.method=='POST' and g.rol == 'Administrador' or g.rol == 'SuperAdmin':  
        try:
            cedula = request.form['findbyname']
            
            con = sqlite3.connect('db_empleados.db')
            cursor = con.cursor()
            
            cursor.execute("SELECT * FROM empleado WHERE cedula = ?", (cedula,))
            row = cursor.fetchone()
            
            cursor.execute("SELECT * FROM contrato WHERE contrato_id = ?", (row[8],))
            rw = cursor.fetchone()

            cursor.execute("SELECT * FROM dependencia WHERE dependencia_id = ?", (row[9],))
            rw2 = cursor.fetchone()
        
            return render_template('delete_employee.html', nombre=row[1], id=row[0], direccion=row[5], telefono=row[6], inicio=rw[1], contrato=row[8], fin=rw[2], dependencia=rw2[1], salario=rw[3])
        except TypeError: 

            return render_template('delete_employee.html', msn="fail")

    else:

        return redirect(url_for('loginAdmin'))


@app.route('/admin/deleteEmployee/del/<id>')
def delete(id=None):
    if 'Administrador' != g.rol != 'SuperAdmin':
        mensaje="No esta autorizado para acceder a este recurso"
        return render_template('index.html', mensaje=mensaje)
    if id == None or id == 1:
        return render_template('delete_employee.html')

    con = sqlite3.connect('db_empleados.db')
    cursor=con.cursor()

    cursor.execute("DELETE FROM empleado WHERE empleado_id= ?", (id, ))

    con.commit()
    con.close()

    return redirect(url_for('adminDelete', msn="OK")) 
@app.route('/superadmin/dashboard/')
def dashboard():
    if g.rol == None:
        return redirect(url_for('index'))
    if g.rol != "SuperAdmin":
        mensaje="No esta autorizado para acceder a este recurso"
        return render_template('index.html', mensaje=mensaje)
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def error404(e):
    if 'rol' in session:
        return redirect(g.home_page)
    return redirect(url_for('index'))
app.run(debug=True, host=f'{socket.gethostbyname(socket.gethostname())}')
