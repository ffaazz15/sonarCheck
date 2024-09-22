from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/weather_app'
db = SQLAlchemy(app)

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String, nullable=False)
    temperature = db.Column(db.Float)
    description = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

API_KEY = 'b92c88dc24af35f247bdf7fce96f915f'  # Replace with your OpenWeatherMap API key

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        weather_data = WeatherData.query.filter_by(city=city).first()
        
        if not weather_data:
            # Fetch weather data from OpenWeatherMap API
            response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric')
            data = response.json()
            
            if response.status_code == 200:
                temperature = data['main']['temp']
                description = data['weather'][0]['description']
                new_weather_data = WeatherData(city=city, temperature=temperature, description=description)
                db.session.add(new_weather_data)
                db.session.commit()
                weather_data = new_weather_data
            else:
                return render_template('index.html', error=data['message'])

        return render_template('index.html', weather_data=weather_data)

    # Default to Pune's weather
    default_city = 'Pune'
    default_weather_data = WeatherData.query.filter_by(city=default_city).first()
    
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
