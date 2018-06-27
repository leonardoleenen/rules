from flask import Flask, current_app, jsonify, render_template, request, url_for, redirect, flash, session, make_response, abort
from flask_cors import cross_origin
from functools import wraps
import os
import uuid
from pymongo import MongoClient


def secure_service(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token=request.headers.get("Authorization")
        if request.headers.get("Authorization") is None:
            current_app.logger.error("Acceso denegado. No provee token")
            return jsonify(success=False,msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"),403

        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        result=r.get(token)

        if result is None:
            app.logger.error("Acceso denegado. Intentando acceder a un recurso con un token no valido. Token provisto: " + token)
            return jsonify(success=False,msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"),403


        return func(*args, **kwargs)

    return decorated_function
