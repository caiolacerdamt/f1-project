from flask import Flask, render_template, request
import fastf1 as ff1
import pandas as pd
import numpy as np
import pytz
from PIL import Image, ImageDraw
import tensorflow as tf

app = Flask(__name__)

cache = {}

def get_circuits(year):
    if year in cache:
        return cache[year]
    schedule = ff1.get_event_schedule(year)["EventName"].unique()
    cache[year] = list(schedule)
    return cache[year]

@app.route('/', methods=['GET', 'POST'])
def index():
    anos = list(range(2018, 2025))

    return render_template('index.html', anos=anos)

if __name__ == '__main__':
    app.run(debug=True)