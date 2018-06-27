# -*- coding: utf-8; -*-
from flask import Blueprint, Flask, current_app, jsonify, render_template, request, url_for, redirect, flash, session
from pymongo import MongoClient
from flask import current_app
import httplib2 as http
import json
import ldap
import ldap.modlist as modlist


class BException(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)


http_client = http.Http(disable_ssl_certificate_validation=True)


def change_status(uid, status):
    '''
        Activates an user on LDAP by modifying inetUserStatus attr.
    '''
    try:
        l = get_ldap_client()
        l.modify_s(build_user_dn(str(uid)), [(ldap.MOD_REPLACE, "title", str(status))])
        return True, "Ok"
    except Exception, ex:
        current_app.logger.exception(ex)
        return False, "Error. " + str(ex)


def change_password(uid, new):
    try:
        l = get_ldap_client()
        l.modify_s(build_user_dn(uid), [(ldap.MOD_REPLACE, "userPassword", new)])
        return True, "Ok"
    except Exception, ex:
        current_app.logger.exception(ex)
        return False, "No se pudo conectar a repositorio para conectar el usuario. " + str(ex)


def change_data(uid, label, new_data):
    try:
        l = get_ldap_client()
        l.modify_s(build_user_dn(uid), [(ldap.MOD_REPLACE, label, new_data)])
        return True, "Ok"
    except Exception, ex:
        current_app.logger.exception(ex)
        return False, "No se pudo conectar a repositorio para conectar el usuario. " + str(ex)


def delete_user(uid):
    '''
        @author: skomlev
    '''
    try:
        l = get_ldap_client()
        l.delete_s(build_user_dn(uid))
        return True, "Ok"
    except Exception, ex:
        current_app.logger.exception(ex)
        return False, "No se pudo conectar a repositorio para conectar el usuario. " + str(ex)


def create_new_person_on_ldap(user_form):
    l = get_ldap_client()

    attrs = {}
    attrs['objectclass'] = current_app.config["LDAP_PERSON_OBJECT_CLASSES"]
    attrs['uid'] = str(user_form["user"]["username"])
    attrs['userPassword'] = str(user_form["security"]["password"])
    #attrs['cuit'] = str(user_form["user"]["cuit"])
    attrs['mail'] = str(user_form["user"]["email"])
    attrs['cn'] = str(user_form["user"]["cn"])
    attrs['sn']= str(user_form["user"]["sn"])
    attrs['title']= str("ACTIVE")
    #attrs['documentType']= str(user_form["user"]["comboBoxdocumentType"]["text"])
    #attrs['documentNumber']= str(user_form["user"]["documentNumber"])
    #attrs['telephoneNumber']= str(user_form["user"]["telephoneNumber"])
    #attrs['inetuserstatus']= str(current_app.config["LDAP_PERSON_STATUS_DEFAULT"])
    #attrs['mobileNumber']= str(user_form["user"]["mobileNumber"])
    try:
        l.add_s(build_user_dn(user_form["user"]["username"]), modlist.addModlist(attrs))
        return True, "Ok"
    except Exception, ex:
        current_app.logger.exception(ex)
        if str(ex[0]['desc']) == 'Already exists':
            return False, "El uid:" + str(user_form["user"]["username"]) + " ya esta siendo utilizado."
        else:
            return False, "Error al generar el usuario: " + ex[0]['desc']


def build_user_dn(uid):
    '''
        Build LDAP person DN for the given UID
        @author: Eric X. Engstfeld
    '''
    return "uid=" + str(uid) + "," + current_app.config['LDAP_PEOPLE_OU'] + "," + current_app.config['LDAP_BASE']


def get_ldap_client():
    '''
        Returns ldap client ready to use
        @author: Eric X. Engstfeld
    '''
    ldap_client = ldap.initialize(current_app.config['LDAP_SERVER'])
    ldap_client.simple_bind_s(current_app.config['LDAP_WHO'], current_app.config['LDAP_CRED'])
    return ldap_client


def get_uid_by_session_token(token):
    '''
    Returns the user uid corresponding to the given session token. Calls to OpenAM validation service
    @author: Eric X. Engstfeld
    '''
    current_app.logger.debug("Validating token with openam...")
    openam_response, openam_content = http_client.request(current_app.config['OPENAM_URL'] + '/json/users?_action=idFromSession', 'POST', '{}', {current_app.config['OPENAM_SESSION_COOKIE']: token, 'Content-Type': 'application/json; charset=UTF-8'})
    if openam_response["status"] != '200':
        raise Exception("Problem with OpenAM communication. Maybe an invalid token was given")
    return json.loads(openam_content).get("id")


def get_user_data(uid):
    '''
    Gets person attrs in ldap raw format. Should be used for internal LDAP operations
    @author: Eric X. Engstfeld
    Ex: uid = "20280377695"
    '''
    retrieve_attrs = ["uid", "cn", "mail"]
    l = get_ldap_client()
    base = current_app.config['LDAP_BASE']
    people_ou = current_app.config['LDAP_PEOPLE_OU']
    filter = "uid=" + uid
    dn, attrs = l.search_st(people_ou + "," + base, ldap.SCOPE_SUBTREE, filter, retrieve_attrs, 0, current_app.config['LDAP_TIMEOUT'])[0]
    attrs_normalized = {}
    for key, value in attrs.items():
        attrs_normalized[key] = value[0]
    return attrs_normalized


def get_status(uid):
    '''
    Gets person attrs in ldap raw format. Should be used for internal LDAP operations
    @author: Eric X. Engstfeld
    Ex: uid = "20280377695"
    '''
    retrieve_attrs = ["title"]
    l = get_ldap_client()
    base = current_app.config['LDAP_BASE']
    people_ou = current_app.config['LDAP_PEOPLE_OU']
    filter = "uid=" + uid

    try:
        dn, attrs = l.search_st(people_ou + "," + base, ldap.SCOPE_SUBTREE, filter, retrieve_attrs, 0, current_app.config['LDAP_TIMEOUT'])[0]
        return attrs['title'][0]
    except Exception, ex:
        current_app.logger.exception(ex)
        return "ACTIVE"


def check_existence_by_field(field, value):
    retrieve_attrs = ["uid"]
    l = get_ldap_client()
    base = current_app.config['LDAP_BASE']
    people_ou = current_app.config['LDAP_PEOPLE_OU']
    filter = str(field) + "=" + str(value)
    try:
        dn, attrs = l.search_st(people_ou + "," + base, ldap.SCOPE_SUBTREE, filter, retrieve_attrs, 0, 1000)[0]
        return True
    except Exception, ex:
        current_app.logger.exception(ex)
        return False


def checkPassword(username, password):

    try:
        ldap_client = ldap.initialize(current_app.config['LDAP_SERVER'])
        ldap_client.simple_bind_s("uid={0},{1},{2}".format(username, current_app.config['LDAP_PEOPLE_OU'], current_app.config['LDAP_BASE']), password)

        return True
    except Exception, ex:
         return False
