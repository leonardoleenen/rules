
# LPU_EMI_OCA_CUADRO_COMPARATIVO

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
###########3333
import os
import sys
import base64
from reportlab.platypus import (Preformatted, Table, BaseDocTemplate, PageTemplate,
			NextPageTemplate, PageBreak, Frame, FrameBreak, Flowable, Paragraph, Image, Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from flask import Flask,current_app,jsonify,render_template,request, url_for,redirect,flash,session,make_response,abort
import uuid
###########3333
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import file_storage_bp 
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 
from utils import toolbox 





class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['data']) 
		tabla_cuadrocomp_cuadrocomp = []
		try:
			if 'gr_cuadrocomp' in message['data'] and 'tabla_cuadrocomp_cuadrocomp' in message['data']['gr_cuadrocomp'] and message['data']['gr_unicooferente']['ch_unicooferente_unicooferente'] == 'NO':
				tabla_cuadrocomp_cuadrocomp = message['data']['gr_cuadrocomp']['tabla_cuadrocomp_cuadrocomp']
				for linea in message['data']['gr_cuadrocomp']['tabla_cuadrocomp_cuadrocomp']:
					if linea['0'] != None and linea['0'] != '':

						if not toolbox.valida_cuit(str(linea['0'])):
							return False, 'Cuadro Comparativo: CUIT erroneo: ' + str(linea['0'])			

						if linea['7'] == None:
							return False, "Para la columna 'Tipo de Oferta' los unicos valores permitidos son 'BASE', 'ALTERNATIVA' y'VARIANTE'"
						elif  linea['7'] == '':
							return False, "Para la columna 'Tipo de Oferta' los unicos valores permitidos son 'BASE', 'ALTERNATIVA' y'VARIANTE'"
						elif linea['7'].strip().upper() == 'BASE':
							print "BASE"
						elif linea['7'].strip().upper() == 'ALTERNATIVA':
							print 'ALTERNATIVA'
						elif linea['7'].strip().upper() == 'VARIANTE':
							print 'VARIANTE'
						else:
							return False, "Para la columna 'Tipo de Oferta' los unicos valores permitidos son 'BASE', 'ALTERNATIVA' y'VARIANTE'"


			if 'gr_datosoferta' in message['data'] and 'tabla_datosoferta_datosoferta' in message['data']['gr_datosoferta'] and message['data']['gr_unicooferente']['ch_unicooferente_unicooferente'] == 'NO':
				for linea in message['data']['gr_datosoferta']['tabla_datosoferta_datosoferta']:
					if linea['0'] != None and linea['0'] != '':
						if not toolbox.valida_cuit(str(linea['0'])):
							return False, 'Cuadro Comparativo: CUIT erroneo: ' + str(linea['0'])			


		except Exception, e:
			return False, 'Error durante la validacion '+ str(e)		
		
		# Generacion de PDF 
		global styles
		styles = getSampleStyleSheet()
		styles.add(ParagraphStyle(name='stileheader', fontweight='bold', fontName='Helvetica', fontSize=15, leading=16, backColor=colors.white, textColor='#666666', alignment=TA_LEFT))
		styles.add(ParagraphStyle(name='stileheader2', fontweight='bold', fontName='HelveticaUltraLight', fontSize=12, leading=12, backColor=colors.white, textColor='#666666', alignment=TA_LEFT)) 
		styles.add(ParagraphStyle(name='stileLeyenda', fontweight='bold', fontName='Helvetica', fontSize=8, leading=9, backColor=colors.white, textColor='#000000', alignment=TA_LEFT)) 
		styles.add(ParagraphStyle(name='stileVal', fontweight='normal', fontName='Helvetica', fontSize=6, leading=8, backColor=colors.white, textColor='#666666', alignment=TA_LEFT)) 
		global separador
		# separador = Image(current_app.config["APP_PATH"] + '/src/etc/img/linea.png', width=560, height=0.7)
		global files
		extension = '.pdf'
		filename=str(uuid.uuid1())
		files = current_app.config["TMP_FOLDER"] + os.sep + filename + extension
		LineLengLebel = 132  # Total caracteres por linea 
		LineLengVal = 132  # Cantidad de Cacacteres por linea 

		try: # adjunto el pdf custom 
			if tabla_cuadrocomp_cuadrocomp != []:
				tabla = sorted(tabla_cuadrocomp_cuadrocomp, key=getKey)
				encoded_string = get_base64_pdf_content(tabla)
				# creo pdf custon y lo guardo dentro de bucket 
				id_bucket = file_storage_bp.add_raw_file(encoded_string, 'FILE_STORAGE_BUCKET_PATH')
				# Busco si ya hay pdf generados y los reemplazo por el nuevo 
				repo_client = repo.get_instance("workflow")
				instance = repo_client.get_by_id("instances", message['instance_id'])
				if len(instance['instance']['current_task']['docs']) != 0:
					newlist = filter(lambda x: x["name"] != "cuadro.pdf", instance['instance']['current_task']['docs'])
					instance['instance']['current_task']['docs'] = newlist
					repo_client.update("instances", message['instance_id'], instance)

				doc = {
					"key" : str(id_bucket),
					"type" : "application/pdf",
					"name" : "cuadro.pdf",
					"size" : "12"
					}
				repo_client.insert_doc(message['instance_id'], doc)
		except Exception, e:
			return False, "Error durante la generacion del PDF: " + str(e)

		return True, 'ok'

def getKey(item):
    return item['2']


#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------

#############################################################################
#############################################################################
#############################################################################
#############################################################################
def get_base64_pdf_content(renglones):
	reload(sys)
	sys.setdefaultencoding("utf-8")
	story = []
	line = []
	row = []
	renglon = []

	story.append(Spacer(1, 5))
	#story.append(separador)
	story.append(Spacer(1, 10))
	line = []
	for linea in renglones:
	  if len(linea) !=0:
	  	print linea  	
		if renglon != '' and renglon != str(linea['2']):
			if line != []:
				table = Table(line)    
				table.rowheights = 1
				table.hAlign = TA_LEFT
				story.append(table)
				line = []

			renglon = str(linea['2']) 
			title = []
			line.append([])
			title.append(Preformatted('Renglon', styles['stileLeyenda'], maxLineLength=7))
			title.append(Preformatted('Cantidad', styles['stileLeyenda'], maxLineLength=8))
			title.append(Preformatted('Unidad de Medida', styles['stileLeyenda'], maxLineLength=16))
			title.append(Preformatted('Codigo SIByS', styles['stileLeyenda'], maxLineLength=20))
			title.append(Preformatted('Descripcion', styles['stileLeyenda']))
			line.append(title)
			title = []
			title.append(Preformatted(str(linea['2']), styles['stileVal'], maxLineLength=7))
			title.append(Preformatted(str(linea['3']), styles['stileVal'], maxLineLength=16))
			title.append(Preformatted(str(linea['4']), styles['stileVal'], maxLineLength=16))
			title.append(Preformatted(str(linea['5']), styles['stileVal'], maxLineLength=20))
			title.append(Preformatted(str(linea['6']), styles['stileVal'], maxLineLength=30))  
			line.append(title)
			title = []
			row = []
			row.append(Preformatted('Razon Social', styles['stileLeyenda'], maxLineLength=15))        
			row.append(Preformatted('CUIT', styles['stileLeyenda'], maxLineLength=11))
			row.append(Preformatted('Tipo de Oferta', styles['stileLeyenda'], maxLineLength=14))
			row.append(Preformatted('Cantidad Ofertada', styles['stileLeyenda'], maxLineLength=17))
			row.append(Preformatted('Importe Unitario', styles['stileLeyenda'], maxLineLength=18))
			row.append(Preformatted('IVA', styles['stileLeyenda'], maxLineLength=4))
			row.append(Preformatted('Importe Total', styles['stileLeyenda'], maxLineLength=13))
			row.append(Preformatted('Descuentos', styles['stileLeyenda'], maxLineLength=10))
			line.append(row)
		row = []
		row.append(Preformatted(str(linea['1']), styles['stileVal'], maxLineLength=25))
		row.append(Preformatted(str(linea['0']), styles['stileVal'], maxLineLength=12))
		row.append(Preformatted(str(linea['7']), styles['stileVal'], maxLineLength=14))
		row.append(Preformatted(str(linea['8']), styles['stileVal'], maxLineLength=16))
		row.append(Preformatted(str(linea['9']), styles['stileVal'], maxLineLength=16))
		row.append(Preformatted(str(linea['10']), styles['stileVal'], maxLineLength=16))
		row.append(Preformatted(str(linea['11']), styles['stileVal'], maxLineLength=16))
		row.append(Preformatted(str(linea['12']), styles['stileVal'], maxLineLength=16))
		line.append(row)
		row = []


	table = Table(line)
	table.rowheights = 1
	table.hAlign = TA_LEFT
	story.append(table)

	# CONSTRUIMOS EL PDF
	#==================
	doc = docTemplate()  # Nombre del archivo ... 
	doc.build(story)
	with open(files, "rb") as image_file:  # Transforma PDF en binario base64
	   encoded_string = base64.b64encode(image_file.read())
	os.remove(files)  # Elimina PDF fisico.
	return encoded_string

def docTemplate():   
	# CREAMOS EL DOCTEMPLATE
	#===========================
	doc = BaseDocTemplate(files, topMargin=95, bottomMargin=25,
	                              leftMargin=5, rightMargin=10)  #  pagesize=A4) #landscape(A4) para Horizontal #,showBoundary=1 recuadro de las paginas  
	# CREAMOS LOS FRAMES
	#========================
	frame = Frame(doc.leftMargin, doc.bottomMargin,
	                doc.width, doc.height, id='col1')
	# CREAMOS LOS PAGETEMPLATE
	#======================== 
	doc.addPageTemplates([
	                     PageTemplate(id='contenido', frames=frame,
	                        onPage=encabezado, onPageEnd=piePagina),
	                    ])
	return doc 

def encabezado(canvas, doc):
	canvas.saveState()
	#canvas.drawImage(app_home + 'logo1.png', 15, 800, width=140, height=29, mask='auto')
	# canvas.drawImage(current_app.config["APP_PATH"] + '/src/etc/img/' + 'logo2.png', 430, 800, width=140, height=25, mask='auto')
	canvas.setStrokeColor('#ABAAAB')
	canvas.line(A4[0] - 700, A4[1] - 53, A4[0] - 0, A4[1] - 53)
	canvas.setFillColor('#666666')
	canvas.setFont('Helvetica', 20) 
	# canvas.drawString(10, A4[1] - 77, form['data']['header']['name'])
	canvas.line(A4[0] - 700, A4[1] - 90, A4[0] - 0, A4[1] - 90)
	canvas.restoreState()
 
def piePagina(canvas, doc):
	canvas.saveState()
	canvas.setFillColor('#666666')
	canvas.setFont('Helvetica', 8)
	canvas.setStrokeColor('#ABAAAB')
	canvas.line(A4[0] - 800, A4[1] - 818, A4[0] - 0, A4[1] - 818)
	canvas.drawString(275, A4[1] - 835, "Pag. %d" % doc.page)
	# canvas.drawString( 20,  A4[1]-835, 'Codigo: '+form['data']['header']['code'])
	canvas.restoreState()

def docTemplate():   
	# CREAMOS EL DOCTEMPLATE
	#============================
	doc = BaseDocTemplate(files, topMargin=95, bottomMargin=25,
	                              leftMargin=5, rightMargin=10)  #  pagesize=A4) #landscape(A4) para Horizontal #,showBoundary=1 recuadro de las paginas  
	# CREAMOS LOS FRAMES
	#========================
	frame = Frame(doc.leftMargin, doc.bottomMargin,
	                doc.width, doc.height, id='col1')
	# CREAMOS LOS PAGETEMPLATE
	#======================== 
	doc.addPageTemplates([
	                     PageTemplate(id='contenido', frames=frame,
	                        onPage=encabezado, onPageEnd=piePagina),
	                    ])
	return doc 	