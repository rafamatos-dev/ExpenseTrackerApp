from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure MongoDB

if 