from flask import Flask, render_template,request,flash,redirect,url_for,session
from newsapi import NewsApiClient
import ibm_db
import requests
import smtplib 

def sendMaile(email,text):
    fromaddr = 'rishabhkmishra2209@gmail.com'
    toaddrs  = email
    msg = text
    username = 'rishabhkmishra2209@gmail.com'   
    password = 'ewqsrgvkordkwvtj'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()






app = Flask(__name__)
app.app_context().push()


app.config['DEBUG'] = True






app.secret_key='a'

connection = ibm_db.connect("DATABASE=bludb ; HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT= 32733; SECURITY=SSL; SSLServerertificate=/Users/pradeep/PycharmProjects/Flask SQLite/certificate.crt; UID=trk06303; PWD=YLyf6RxcgUb1iCcI;",'','' )


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
 if request.method == 'POST':
     try:
      username = request.form['username']
      mail = request.form['mail']
      contact = request.form['contact']
      password = request.form['password']
      print(username,mail,contact,password)
    #   query = "INSERT INTO users (username,password,mail,contact) VALUES(?,?,?,?)"
    #   stmt = ibm_db.prepare(connection, query)
    #   ibm_db.bind_param(stmt, 1, username)
    #   ibm_db.bind_param(stmt, 2, password)
    #   ibm_db.bind_param(stmt, 3, mail)
    #   ibm_db.bind_param(stmt, 4, contact)
    #   ibm_db.execute(stmt)
      query = "INSERT INTO users (username,password,mail,contact) VALUES('"+username+"','"+password+"','"+mail+"','"+contact+"');"
      stmt = ibm_db.prepare(connection,query)
      ibm_db.execute(stmt)
      flash("Registered  Successfully","success")
     except Exception as e:
         print(e)
         flash("Error in Insert Operation", "danger")
     finally:
         sendMaile(mail,"You hav sucessfully registered News tracker application")
         return redirect(url_for("index"))
         con.close()
 return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
 global userid
 if request.method == "POST":
    username = request.form['username']
    password = request.form['password']
    query = "SELECT * FROM USERS where username=? and password=?"
    stmt = ibm_db.prepare(connection, query)
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.bind_param(stmt, 2, password)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
        session['Loggedin'] = True
        session['id'] = account['USERNAME']
        session['username'] = account['USERNAME']
        return redirect("/news")
    else:
        flash("Oops Username and Password Mismatch", "danger")
        return redirect(url_for("index"))


@app.route("/news")
def home():
    api_key = 'b62e986d019b416fbc1f506b4167852b'

    newsapi = NewsApiClient(api_key=api_key)

    top_headlines = newsapi.get_top_headlines(sources="bbc-news")
    all_articles = newsapi.get_everything(sources="bbc-news")

    t_articles = top_headlines['articles']
    a_articles = all_articles['articles']

    news = []
    desc = []
    img = []
    p_date = []
    url = []

    for i in range(len(t_articles)):
        main_article = t_articles[i]

        news.append(main_article['title'])
        desc.append(main_article['description'])
        img.append(main_article['urlToImage'])
        p_date.append(main_article['publishedAt'])
        url.append(main_article['url'])

        contents = zip(news, desc, img, p_date, url)

    news_all = []
    desc_all = []
    img_all = []
    p_date_all = []
    url_all = []

    for j in range(len(a_articles)):
        main_all_articles = a_articles[j]

        news_all.append(main_all_articles['title'])
        desc_all.append(main_all_articles['description'])
        img_all.append(main_all_articles['urlToImage'])
        p_date_all.append(main_all_articles['publishedAt'])
        url_all.append(main_article['url'])

        all = zip(news_all, desc_all, img_all, p_date_all, url_all)

    return render_template('home.html', contents=contents, all=all)


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            query = "INSERT INTO weather (city) VALUES('"+new_city+"');"
            stmt = ibm_db.prepare(connection,query)
            ibm_db.execute(stmt)

    query = "SELECT city FROM weather;"
    stmt = ibm_db.prepare(connection,query)
    ibm_db.execute(stmt)
    cities = ibm_db.fetch_assoc(stmt)
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=2a78921b9bffcab5e471564c6a553385'
    print(cities)
    weather_data = []
    
    for city in cities['city']:
        r = requests.get(url.format(city)).json()

        weather = {
            'city': city,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(weather)
    print(weather_data)
    return render_template('weather.html', weather_data=weather_data)



@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5000",debug=True)