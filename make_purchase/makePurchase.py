from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pika
import uuid
from datetime import datetime
import sys
from os import environ
import json

app = Flask(__name__)
CORS(app)

customeURL = environ.get('customerURL')
recommendationURL = environ.get("recommendationURL")
partURL = environ.get("partURL")

