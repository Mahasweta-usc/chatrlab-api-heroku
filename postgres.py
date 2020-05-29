import os, sys
import urllib, requests,random
import psycopg2
from google.cloud import storage
from flask import Flask, request, session, render_template, redirect, url_for
import urllib.parse, urllib.request, json, pickle 
import pandas as pd
from psycopg2 import sql
#psycopg2.connect("dbname=tukai user=postgres")

def initiate():
	DATABASE_URL = os.environ['DATABASE_URL']
	connection = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = connection.cursor()
	try:
		postgres_insert_query = """ SELECT * FROM instagram """
		cur.execute(postgres_insert_query)
		return
	except:
		pass

	try:
		cur.close()
		connection = psycopg2.connect(DATABASE_URL, sslmode='require')
		cursor = connection.cursor()
		create_table_query = '''CREATE TABLE instagram
		      (ID TEXT PRIMARY KEY,
		      CAPTION TEXT,
		      IMAGE_TEXT TEXT);'''
		cursor.execute(create_table_query)
		connection.commit()
	except:
		pass

	try:
		cursor.close()
		connection = psycopg2.connect(DATABASE_URL, sslmode='require')	
		cursor = connection.cursor()
		data = pd.read_csv('samples.csv')
		for ind in data.index:
			file, caption, image_text = data['filename'][ind],data['caption'][ind], data["image_text"][ind]
			postgres_insert_query = """ INSERT INTO instagram (ID, CAPTION, IMAGE_TEXT) VALUES (%s,%s,%s)"""
			record_to_insert = (file, caption, image_text) #.replace("_","-").strip("-UTC.json")
			# print(record_to_insert)
			cursor.execute(postgres_insert_query, record_to_insert)
			connection.commit()
		cursor.close()
	except:
		pass

def start(username):
	DATABASE_URL = os.environ['DATABASE_URL']
	connection = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = connection.cursor()
	#find username index
	postgres_insert_query = """SELECT * FROM instagram limit 0"""
	cur.execute(postgres_insert_query)          
	colnames = [desc[0] for desc in cur.description]
	index = colnames.index(username)
	

	postgres_insert_query = """SELECT * FROM instagram"""  #ORDER BY ID
	cur.execute(postgres_insert_query)          
	ver = cur.fetchall()
	cur.close()
	empty = [elem for elem in ver if not elem[index]] #yet to be completed

	# print(len(empty),index,colnames)
	try:
		count = len(ver) -  len(empty)
		return (count, random.choice(empty))
	except:
		return (None,None)


def add_column(username):
	DATABASE_URL = os.environ['DATABASE_URL']
	try:
		connection = psycopg2.connect(DATABASE_URL, sslmode='require')
		curs = connection.cursor()
		curs.execute('ALTER TABLE %s ADD COLUMN %s text' % ('instagram', username))
		connection.commit()
		curs.close()
	except:
		pass

#return details of a post
def retrieve(file):
	DATABASE_URL = os.environ['DATABASE_URL']
	connection = psycopg2.connect(DATABASE_URL, sslmode='require')
	cursor = connection.cursor()
	query = "SELECT * FROM instagram WHERE ID = CAST(%s AS TEXT)"
	cursor.execute(query, (file,))
	mobile_records = cursor.fetchall()
	# print(mobile_records)
	cursor.close()
	return mobile_records

#save response
def save(file,username,action):
	DATABASE_URL = os.environ['DATABASE_URL']
	connection = psycopg2.connect(DATABASE_URL, sslmode='require')
	cursor = connection.cursor()
	query = sql.SQL("UPDATE instagram SET {} = CAST(%s AS TEXT) WHERE ID = CAST(%s AS TEXT)")
	query = query.format(sql.Identifier(username))
	# print(query)
	cursor.execute(query, (action,file))
	connection.commit()
	cursor.close()

def remove(file):
	DATABASE_URL = os.environ['DATABASE_URL']
	connection = psycopg2.connect(DATABASE_URL, sslmode='require')
	cursor = connection.cursor()
	sql_delete_query = """DELETE FROM instagram WHERE ID = CAST(%s AS TEXT)"""
	cursor.execute(sql_delete_query, (file, ))
	connection.commit()
	cursor.close()
