from shlex import shlex
from time import strftime
from time import strftime
from werkzeug.utils import secure_filename
import snapshot as snapshot
from flask import Flask,flash, g, redirect, request, jsonify, render_template, session, url_for
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

users = []
users.append(User(id=1, username='march', password='310090'))
users.append(User(id=2, username='', password=''))
users.append(User(id=3, username='', password=''))




@app.route('/')
def home():
    import os
    #print(os.path.realpath)
    import pathlib
    print(pathlib.Path(__file__).parent.resolve())
    print(pathlib.Path().resolve())

    if os.path.isfile(app.static_folder + "/shop_bar.png"):
        print('in if')
        os.remove(app.static_folder + "/shop_bar.png")
    else:
        print('in else')

    if os.path.isfile(app.static_folder + "/shop_pie.png"):
        print('in if')
        os.remove(app.static_folder + "/shop_pie.png")
    else:
        print('in else')

    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
        })

    import datetime
    today = datetime.datetime.now()
    today = strftime("%Y%m%d")
    print("today", today)

    ref = db.reference('Product')
    # print(' '+stateSearch)

    #snapshot = ref.order_by_child("time").equal_to(today).get()
    snapshot = ref.order_by_child("expireDate").limit_to_last(20).get()
    today_array = []
    for user, val in snapshot.items():
        today_list = ""
        pk = val.get("pk")
        fileName = val.get("fileName")
        fileName1 = val.get("fileName")
        country = val.get("country")
        brand = val.get("brand")
        productName = val.get("productName")
        textArea = val.get("textArea")
        textArea = textArea.replace(",", "   ")
        fileName = val.get("fileName")
        quantity = val.get("quantity")
        quantity = str(quantity)
        price = val.get("price")
        price = str(price)
        expireDate = val.get("expireDate")


        time = val.get("time")


        # print(phone)
        # print(state)
        # print(city)
        # print(position)
        # print(jobtype)
        # print(wage)
        # print(time)
        print(type(pathlib.Path().resolve()))
        if str(pathlib.Path().resolve()) == '/app':
            print('    ////// app' )
            image = "https://oilybeauty.herokuapp.com/static/uploads/"+fileName
            image1 = "https://oilybeauty.herokuapp.com/static/uploads/"+fileName1
        else:
            print('    ////// not app')
            image = "/static/uploads/"+fileName
            image1 = "/static/uploads/"+fileName1
        #imagepath = "{{ url_for('display_image', filename= "+ "ob0001.png" +") }}"

        today_list = today_list + image+ ","+ image+ ", "+ pk +" ," + country + "," + brand + "," + productName +" , " +textArea +  "," + quantity + " , " + price + "," + expireDate + ","+time
        today_array.append(today_list)

    return render_template('index.html',today=today_array)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    import os

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('product_register.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
@app.route('/service', methods=['GET'])
def service():
    return render_template('index.html')

@app.route('/contactUs', methods=['GET'])
def contactUs():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('product'))

        return redirect(url_for('login'))

    return render_template('login.html')


# @app.route('/edit/<string:pkid>' ,methods = ['GET','POST'])
# def edit(pkid: str):
#     # if not g.user:
#     #     return redirect(url_for('login'))
#     print(pkid)
#
#     return render_template('index.html')


@app.route('/sell', methods=['GET'])
def sell():
    # if request.method == 'POST':
    #     # do stuff when the form is submitted
    #
    #     # redirect to end the POST handling
    #     # the redirect can be to the same route or somewhere else
    #     return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('sell.html')


@app.route('/product', methods=['GET', 'POST'])
def product():

    if not g.user:
        return redirect(url_for('login'))
    # show the form, it wasn't submitted
    import datetime, timedelta
    today = datetime.date.today()
    expireDate = today + datetime.timedelta(days=365)
    expireDate = expireDate.strftime("%Y%m%d")

    return render_template('product_register.html',expireDate = expireDate,user= g.user.username)

@app.route('/detail/<string:id>', methods=['GET', 'POST'])
def detail(id):
    if request.method == 'POST':
        print(' update ')

    id = id.strip();
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred,
                                      {'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
                                       })

    ref = db.reference('Product')

    #snapshot = ref.order_by_key().get()
    if request.method == 'POST':
        #ref = db.reference('Product')
        # pk_ref = ref.child("pk").equal_to("00000033333")
        # pk_ref.update({
        #     'price': '6'
        # })
        ref = db.reference("Product")
        best_sellers = ref.get()

        quantity = request.form.get("quantity")

        sellQuantity = request.form.get("sellQuantity")
        remain = int(quantity) - int(sellQuantity)
        priceWeb = request.form.get("price")
        print(best_sellers)
        for key, val in best_sellers.items():
            if (val["pk"] == id):

                ref.child(key).update({"quantity": str(remain)})

                country = val.get("country")
                brand = val.get("brand")
                productName = val.get("productName")
                textArea = val.get("textArea")
                textArea = textArea.replace(",", "   ")
                img = val.get("fileName")
                img1 = val.get("fileName1")
                img2 = val.get("fileName2")
                img3 = val.get("fileName3")
                img4 = val.get("fileName4")
                quantiity = val.get("quantity")
                quantity = str(quantity)

                price = val.get("price")
                if priceWeb!= price :
                    ref.child(key).update({"price": str(priceWeb)})
                price = str(price)
                expireDate = val.get("expireDate")
                print('update')

        return redirect(url_for('home'))
    else :
        snapshot = ref.order_by_child("pk").equal_to(id).get()
        for user, val in snapshot.items():
            country = val.get("country")
            brand = val.get("brand")
            productName = val.get("productName")
            textArea = val.get("textArea")
            textArea = textArea.replace(",", "   ")
            img = val.get("fileName")
            img1 = val.get("fileName1")
            img2 = val.get("fileName2")
            img3 = val.get("fileName3")
            img4 = val.get("fileName4")
            quantity = val.get("quantity")

            price = val.get("price")

            quantity = str(quantity)
            price = str(price)

            expireDate = val.get("expireDate")
            time = val.get("time")

        # print(phone)
        # print(state)
        # print(city)
        # print(position)
        # print(jobtype)
        # print(wage)
        # print(time)

        return render_template('product_detail.html',id = id,user = g.user.username , country=country,brand = brand,productName = productName,img = img,img1= img1, quantity = quantity,price = price, expireDate = expireDate)

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):

    # if not g.user:
    #     return redirect(url_for('login'))
    # show the form, it wasn't submitted
    print(id)
    return render_template('product_register.html')

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/product_register', methods=['POST'])
def product_register():
    # int_features = [int(x) for x in request.form.values()]
    import os

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if 'file1' not in request.files:
        flash('No file1 part')
        return redirect(request.url)

    file = request.files['file']
    file1 = request.files['file1']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file1.filename == '':
        flash('No image1 selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
    #    return render_template('product_register.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

    if file1 and allowed_file(file1.filename):
        filename1 = secure_filename(file1.filename)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
    #    return render_template('product_register.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

    country = request.form.get("country")
    brand = request.form.get("brand")
    productName = request.form.get("productName")

    quantity = request.form.get("quantity")
    price = request.form.get("price")
    expireDate = request.form.get("expireDate")
    shipOut= request.form.get("shipOut")
    textArea = request.form.get("textArea")

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]

    print(user.username)

    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
        })
    import datetime
    nowtime = datetime.datetime.now()

    nowtime = strftime("%Y-%m-%d")
    print("time", nowtime)

    ref = db.reference('Product')
    ref.push(
        {
            'pk' : brand+productName,
            'country': country,
            'brand': brand,
            'productName': productName,
            'fileName': filename,
            'fileName1': filename1,
            'quantity': quantity,
            'price': price,
            'expireDate': expireDate,
            'shipOut': shipOut,
            'textArea': textArea,
            'time': nowtime
        }
    )

    return render_template('product_register.html', result='Register done')


@app.route('/job_search', methods=['POST'])
def job_search():
    # int_features = [int(x) for x in request.form.values()]
    # final_features = [np.array(int_features)]
    # prediction = model.predict(final_features)
    # print(int_features[0])

    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred, { 'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
        })

    stateSearch = request.form.get("stateSearch")
    ref = db.reference('Job')
    # print(' '+stateSearch)

    if stateSearch == "ALL":
        snapshot = ref.order_by_key().limit_to_last(20).get()
    else:
        snapshot = ref.order_by_child("state").equal_to(stateSearch).limit_to_last(4).get()
    # snapshot = ref.order_by_child('time').start_at('20210919').get()

    statel = []

    share = []
    state_array = []
    price_array = []
    job_array = []
    shop_list = ""

    inttemp = 0

    for user, val in snapshot.items():

        state_list = ""
        shop_list = ""

        email = val.get("email")
        email = email.strip()
        #        print(type(email))

        if email is None:
            email = "-"

        if email == "":
            email = "-"

        phone = val.get("phone")
        contactPerson = val.get("contactPerson")
        state = val.get("state")
        city = val.get("city")
        position = val.get("position")
        jobtype = val.get("jobtype")
        wage = val.get("wage")
        extra = val.get("extra")
        textArea = val.get("textArea")
        # textArea = textArea.replace("\r\n","   ")
        textArea = textArea.replace(",", "   ")

        time = val.get("time")
        # print(phone)
        # print(state)
        # print(city)
        # print(position)
        # print(jobtype)
        # print(wage)
        # print(time)

        if stateSearch == "ALL":
            state_array.append(str(state))
            price_array.append(int(wage))
            shop_list = shop_list + email + "," + phone + "," + contactPerson + " ," + state + "," + city + " , " + position + "," + jobtype + "," + wage + " confirm again, " + textArea + "," + time
            job_array.append(shop_list)

            if statel.__contains__(state) == False:
                inttemp = 0
                pricesnapshot = ref.order_by_child('state').equal_to(state).get()
                for user1, val1 in pricesnapshot.items():
                    inttemp = inttemp + int(val1.get('wage'))
                # print(' '+str(inttemp))
                share.append(inttemp / 100)
                statel.append(state)
            else:
                inttemp = 0
                # share.append(inttemp)
            result = "Found record"
        else:
            if stateSearch == state:
                state_array.append(str(state))
                price_array.append(int(wage))
                shop_list = shop_list + email + "," + phone + "," + contactPerson + " ," + state + "," + city + "  , " + position + " , " + jobtype + "," + wage + " confirm again, " + textArea + "," + time
                job_array.append(shop_list)
                result = "Found record"
            else:
                result = "No record found"

    # print(len(share))
    # print(statel)
    # print(state_array)
    # print(price_array)
    # print(job_array)

    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(len(state_array))
    # y1 = [3400, 5600, 1200]
    y1 = price_array
    width = 0.20

    # plot data in grouped manner of bar type
    plt.bar(x - 0.2, y1, width)
    # plt.bar(x+0.2, y2, width)

    # state = state_array
    # state = ['MA', 'WA', 'AR' ,'MA','WA','WA']

    # print(x)
    # print(state_array)
    plt.xticks(x, state_array)
    plt.xlabel("State")
    plt.ylabel("Amount")
    plt.legend(["Job"])

    import matplotlib.pyplot as plt

    plt.savefig('static/job_bar' + '.png')
    plt.close()

    # The slice names of a population distribution pie chart
    # pieLabels = 'Asia', 'Africa', 'Europe', 'North America', 'South America', 'Australia'
    pieLabels = statel
    # Population data
    # populationShare = [11,48.69, 16, 9.94, 7.79, 1,4.68]

    # print(share)
    populationShare = share
    figureObject, axesObject = plt.subplots()

    # Draw the pie chart
    axesObject.pie(populationShare,
                   labels=pieLabels,
                   autopct='%1.2f',
                   startangle=90)

    # Aspect ratio - equal means pie is a circle
    axesObject.axis('equal')

    plt.savefig('static/job_pie' + '.png')
    plt.close()

    return render_template('index.html', search_result=result, job_array=job_array)


@app.route('/stock', methods=['POST'])
def stock():
    # int_features = [int(x) for x in request.form.values()]

    email = request.form.get("email")
    phone = request.form.get("phone")
    contactPerson = request.form.get("contactPerson")
    state = request.form.get("statePost")
    city = request.form.get("city")
    area = request.form.get("area")
    price = request.form.get("price")
    textArea = request.form.get("textArea")

    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
        })
    import datetime
    nowtime = datetime.datetime.now()

    nowtime = strftime("%Y%m%d")
    print("time", nowtime)

    ref = db.reference('Shop')
    ref.push(
        {
            'email': email,
            'phone': phone,
            'contactPerson': contactPerson,
            'state': state,
            'city': city,
            'area': area,
            'price': price,
            'textArea': textArea,
            'time': nowtime
        }
    )

    return render_template('shop.html', result=' Shop post done')


@app.route('/sell_search', methods=['POST'])
def sell_search():
    # int_features = [int(x) for x in request.form.values()]
    # final_features = [np.array(int_features)]
    # prediction = model.predict(final_features)
    # print(int_features[0])
    import os
    file_name = './pic.png'

    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-sdk.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://microbittempreader-16e2d-default-rtdb.firebaseio.com/'
        })

    ref = db.reference('Shop')
    stateSearch = request.form.get("stateSearch")

    if stateSearch == "ALL":
        snapshot = ref.order_by_key().limit_to_last(11).get()
    else:
        snapshot = ref.order_by_child('state').equal_to(stateSearch).limit_to_last(4).get()

    # snapshot = ref.order_by_child('time').start_at('20210919').get()
    statel = []

    share = []
    state_array = []
    price_array = []
    shop_array = []
    shop_list = ""

    inttemp = 0

    for user, val in snapshot.items():

        state_list = ""
        shop_list = ""

        email = val.get("email")
        email = email.strip()

        if email is None:
            email = "-"

        if email == "":
            email = "-"

        phone = val.get("phone")
        contactPerson = val.get("contactPerson")
        state = val.get("state")
        city = val.get("city")
        area = val.get("area")
        price = val.get("price")
        textArea = val.get("textArea")
        textArea = textArea.replace(",", " ")
        time = val.get("time")
        # print(phone)
        # print(state)
        # print(area)
        # print(price)
        # print(time)

        if stateSearch == "ALL":
            state_array.append(str(state))
            price_array.append(int(price))
            shop_list = shop_list + email + "," + phone + "," + contactPerson + " ," + state + "," + city + "," + area + " m2 , " + price + " dollars, " + textArea + "," + time
            shop_array.append(shop_list)

            if statel.__contains__(state) == False:
                inttemp = 0
                pricesnapshot = ref.order_by_child('state').equal_to(state).get()
                for user1, val1 in pricesnapshot.items():
                    inttemp = inttemp + int(val1.get('price'))
                # print('  '+str(inttemp))
                share.append(inttemp / 100)
                statel.append(state)
            else:
                inttemp = 0
                # share.append(inttemp)
            result = "Found record"
        else:
            if stateSearch == state:
                state_array.append(str(state))
                price_array.append(int(price))
                shop_list = shop_list + email + "," + phone + "," + contactPerson + " ," + state + "," + city + "," + area + " m2 , " + price + " dollars, " + textArea + "," + time
                shop_array.append(shop_list)
                result = "Found record"
            else:
                result = "No record found"

    # print(len(share))
    # print(statel)
    # print(state_array)
    # print(price_array)
    # print(shop_array)

    import matplotlib.pyplot as plt
    import numpy as np

    # create data

    x = np.arange(len(state_array))
    # y1 = [3400, 5600, 1200]
    y1 = price_array
    y2 = [12, 56, 78, 45, 90]
    width = 0.40

    # plot data in grouped manner of bar type
    plt.bar(x - 0.2, y1, width)
    # plt.bar(x+0.2, y2, width)
    state = ['A', 'B', ' C', 'D', 'E']

    # state = state_array
    # state = ['MA', 'WA', 'AR' ,'MA','WA','WA']

    # print(x)
    # print(state_array)
    plt.xticks(x, state_array)
    plt.xlabel("State")
    plt.ylabel("Amount")
    plt.legend(["Shop"])

    import matplotlib.pyplot as plt

    plt.savefig('static/shop_bar' + '.png')
    plt.close()

    # The slice names of a population distribution pie chart
    # pieLabels = 'Asia', 'Africa', 'Europe', 'North America', 'South America', 'Australia'
    pieLabels = statel
    # Population data
    # populationShare = [11,48.69, 16, 9.94, 7.79, 1,4.68]

    # print(share)
    populationShare = share
    figureObject, axesObject = plt.subplots()

    # Draw the pie chart
    axesObject.pie(populationShare,
                   labels=pieLabels,
                   autopct='%1.2f',
                   startangle=90)

    # Aspect ratio - equal means pie is a circle
    axesObject.axis('equal')

    plt.savefig('static/shop_pie' + '.png')
    plt.close()

    return render_template('sell.html', search_result=result, shop_array=shop_array)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response


if __name__ == "__main__":
    # import os
    #
    # HOST = os.environ.get('SERVER_HOST', 'localhost')
    # try:
    #     PORT = int(os.environ.get('SERVER_PORT', '5557'))
    # except ValueError:
    #     PORT = 5557
    # app.run(HOST, PORT)
     app.run(debug=True)
