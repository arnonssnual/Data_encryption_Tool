import hashlib
from flask import Flask, render_template, redirect, url_for, flash,session,request,jsonify
import neo4j_app as neo4j
import encryption as encryption
import gcs_app as gcs

#Neo4j connection
neo4j_uri = "neo4j+s://97aba373.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_password = "-----------------------------------"
neo4j = neo4j.App(neo4j_uri, neo4j_user, neo4j_password)


#Encryption service
encryption = encryption.encryption_app()


#Flask app declaration
app = Flask(__name__)
app.secret_key = 'super secret key'


#GCS
gcs = gcs.GCS()

@app.route('/')
def index():
    if('username' in session):
        return redirect('/profile')
    else:
        return redirect(url_for('login'))


#--------------------------------------------------------------
#User authentication functions
#--------------------------------------------------------------
#Login function
@app.route('/login', methods=['GET', 'POST'])
def login():

    if('username' in session):
        return redirect('/profile')
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_exits,database_password = (neo4j.check_user(username))
            neo4j.close()
            if(user_exits):
                password = encryption.hashing(password)
                if(password == database_password):
                    session['username'] = username
                    return render_template('profile.html', username=session['username'])
                else:
                    flash('Wrong password!')
                    return render_template('login.html')
            else:
                flash('Incorrect username or password!')
                return render_template('login.html')
            
        else:
            return render_template('login.html')
    

#Log out function
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if('username' in session):
        return render_template('profile.html', username=session['username'])
    else:
        return redirect(url_for('login'))

#Register function
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password']
        password2 = request.form['confirm-password']
        email = request.form['email']
        user_exits,_ = neo4j.check_user(username)
        if(not user_exits):
            if(password1 == password2):
                email_check = neo4j.check_user_email(email)
                neo4j.close()
                if(email_check):
                    flash('Email already Taken!')
                    return render_template('register.html')
                else:
                    password = encryption.hashing(password1)
                    neo4j.enroll_user(username,password,email)
                    neo4j.close()
                    flash('User created!')
                    return redirect(url_for('login'))
            else:
                flash('Passwords do not match!')
                return render_template('register.html')
        else:
            flash('Username already Taken!')
            return render_template('register.html')
    else:
        return render_template('register.html')
#--------------------------------------------------------------
#User RSA key management functions
#--------------------------------------------------------------
@app.route('/gen_rsa')
def gen_rsa():
    if('username' in session):
        username = session.get('username')
        return render_template('gen_rsa.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/rsapbkeysubmit', methods=['POST'])
def rsapbkeysubmit():
    data = request.get_json()
    username = data['username']
    keySize = data['keySize']
    key_value = data['k_value']
    
    if(neo4j.multiple_key_check(username) >= 1):
        neo4j.update_pb_key(username,keySize,key_value)
        return render_template('profile.html')
    else:
        neo4j.submit_pb_rsa(username,keySize,key_value)
        return render_template('profile.html') #Return With Error Notice


@app.route("/request_pb_key", methods=["GET"])
def request_public_key():
    server_pvkey = gcs.get_server_private_key() 
    server_pbkey = neo4j.request_server_masterKey()['m']
    response = server_pbkey['value']
    response_json = {"pbkey": response, "pvkey": server_pvkey}
    return jsonify(response_json)



#--------------------------------------------------------------
#File management functions
#--------------------------------------------------------------
@app.route('/file_access_premission', methods=['POST'])
def file_access_premission_form():
    username = session.get('username')
    owned_list = (neo4j.file_owner(username))
    can_access = neo4j.file_permission_access(username)
    file_shared_to = neo4j.file_shared_to(username)
    return jsonify(owned_list,can_access,file_shared_to)


@app.route("/file_access_premission_cancel", methods=["POST"])
def file_access_premission_cancel():
    username = session.get('username')
    file_name = request.json['filename']
    datauser = request.json['datauser']

    neo4j.delete_access(datauser,file_name)
    return 'Form submitted successfully!'

@app.route("/deletefile_in_GCS", methods=["POST"])
def delete_file():
    username = session.get('username')
    file_name = request.json['filename']
    neo4j.delete_file_inGCS(username,file_name)
    delete = gcs.delete_file(encryption.hashing(username),file_name)
    if(delete):
        return 'success'
    else:
        return 'fail'
    


@app.route("/getfile_in_GCS", methods=["POST"])
def showfile_inGCS():
    #get username from session
    username = session.get('username')
    #hash username for folder name
    #get file list from GCS
    filename = request.json['filename']
    owner = request.json['owner']
    where = request.json['where']
    if(owner == 'Owner'):
        username_hash = encryption.hashing(username)
        file_url = (gcs.get_public_url((username_hash+"/"+filename)))
    #jsonify(file_list)
    else:
        username_hash = encryption.hashing(owner)
        file_url = gcs.get_public_url((username_hash+"/"+filename))
    return (file_url)


@app.route("/upload_AESencrypted_file", methods=["POST"])
def uploadAES_file():
    if "file" not in request.files:
        return "No file provided", 400
    #get username from session
    username = session.get('username')
    #get file from request
    file = request.files["file"]
    filename = file.filename
    for_chek = filename.startswith(filename)
    print(for_chek)
    #hash username for folder name
    username_hash = encryption.hashing(username)
    #upload File to GCS
    file_name_duplicated = (neo4j.check_duplicate_file(username,filename))
    if(file_name_duplicated != None):
        if(len(file_name_duplicated) >= 1):
            filename = filename + "_"+str(len(file_name_duplicated))

    condtion = gcs.upload_cs_file(username_hash,file,filename)

    #hash file content for integrity check
    hash_object = hashlib.sha256()
    while True:
        chunk = file.read(4096)
        if not chunk:
            break
        hash_object.update(chunk)
    hash_file = hash_object.hexdigest()

    metadata = gcs.get_metadata(username_hash,filename)

    iv = request.form['iv']
    key = request.form['key']
    neo4j.data_node(metadata,username,hash_file)
    #key and iv encrypted by server public key
    
    neo4j.session_key_node_for_owner(username,iv,key,filename)

    return "File uploaded successfully", 200


#--------------------------------------------------------------
#Encryption functions
#--------------------------------------------------------------
@app.route("/encrypt")
def encrypt():
    #get username from session
    if('username' in session):
        username = session.get('username')
        return render_template('encryption.html', username=username)
        

@app.route("/decrypt")
def decrypt():
    #get username from session
    if('username' in session):
        username = session.get('username')
        return render_template('decryption.html', username=username)


def RSA_reencrypt(username,filename):
    hash_username = encryption.hashing(username)
    #filename = hash_username+"/"+filename

    session_key_node = neo4j.request_session_key(username,filename)['s']
    session_iv = session_key_node['iv']
    session_key = session_key_node['value']


    private_key_server = gcs.get_server_private_key()
    public_key_user = (neo4j.request_public_key(username)['pb'])
    public_key_user = public_key_user['value']

    decrypted_session_key = (encryption.decrypt_RSA(session_key,private_key_server)).decode("utf-8")
    encrypted_session_key_user = encryption.encrypt_RSA(bytes(decrypted_session_key, 'utf-8'), public_key_user).decode('utf-8')
    
    decrypted_session_iv = (encryption.decrypt_RSA(session_iv,private_key_server)).decode("utf-8")
    encrypted_session_iv_user = encryption.encrypt_RSA(bytes(decrypted_session_iv, 'utf-8'), public_key_user).decode('utf-8')

    return encrypted_session_iv_user,encrypted_session_key_user

@app.route("/request_sessionkey", methods=["POST"])
def respone_sessionkey():
    
    username = session.get('username')
    #get file from request
    filename = request.json['filename']


    encrypted_session_iv_user,encrypted_session_key_user = RSA_reencrypt(username,filename)
    response = {"iv": encrypted_session_iv_user, "key": encrypted_session_key_user}
    return jsonify(response)


@app.route("/share_file")
def share_file():
    #get username from session
    if('username' in session):
        username = session.get('username')
        return render_template('share_file.html', username=username)


@app.route('/distribute_key', methods=['POST'])
def distribute_key_form():
    owner = session.get('username')
    
    user_shared = []
    text_inputs = request.form.getlist('text')

    for i, text_input in enumerate(text_inputs):
        user_shared.append(text_input)
    file = request.files["file"]
    file_name = file.filename
    file_name_meta_node  = encryption.hashing(owner)+"/"+file_name
    iv = request.form['iv']
    key = request.form['key']
    
    
    hash_object = hashlib.sha256()
    while True:
        chunk = file.read(4096)
        if not chunk:
            break
        hash_object.update(chunk)

    hash_file = hash_object.hexdigest()
    
    hash_username = encryption.hashing(owner)
    gcs.upload_cs_file(hash_username,file,file_name)
    metadata = gcs.get_metadata(hash_username,file_name)
    neo4j.data_node(metadata,owner,hash_file) # data node have only 1 node
    neo4j.session_key_node_for_owner(owner,iv,key,file_name) 
    for i in user_shared:
        print(i)
        check_user,_ = neo4j.check_user(i)
        print(check_user)
        if(check_user):
            neo4j.session_key_node(owner,iv,key,i,file_name)# session key node have = to number of user shared
            
        else:
            return 'User not found', 404
    return redirect(url_for('profile'))



@app.route("/pb_key_exits", methods=["POST"])
def pb_key_exits():
    username = session.get('username')
    key_num = neo4j.multiple_key_check(username)
    if(key_num == 1):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

if(__name__ == '__main__'):
    app.run(debug=True)
