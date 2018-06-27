#
 ### LPU_EMI_OCA_DICTAMEN_ECONOMICO

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
from bson.json_util import dumps

class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['data'])   		
		array_preseleccion = message['data']['gr_evaluacioneco']['tabla_preselecion_evaluacioneco']
		array_desierto = message['data']['gr_rendesiertos']['tabla_rendesiertos_rendesiertos']
		array_desestimadas = message['data']['gr_Ofertasdesestimadas']['sin_titulo15']
		array_fracasados = message['data']['gr_renfracasado']['tabla_renfracasado_renfracasado']


		array_preseleccion = filter(lambda x: len(filter(lambda y: y is None, x)) < 16 , array_preseleccion)
		array_desierto = filter(lambda x: len(filter(lambda y: y is None, x)) < 2 , array_desierto)
		array_desestimadas = filter(lambda x: len(filter(lambda y: y is None, x)) < 12 , array_desestimadas)
		array_fracasados = filter(lambda x: len(filter(lambda y: y is None, x)) < 2 , array_fracasados)

		# array_preseleccion = array_filtered

		unique_values= map(int,list(set(map(lambda x: x['0'], array_preseleccion))))
		unique_desierto= map(int,list(set(map(lambda x: x['0'], array_desierto))))
		unique_fracasados= map(int,list(set(map(lambda x: x['0'], array_fracasados))))
		unique_desestiamdas= map(int,list(set(map(lambda x: x['0'], array_desestimadas))))

		# unique_desierto = json.loads(dumps(unique_desierto))
		# unique_values = json.loads(dumps(unique_values))
		# unique_fracasados = json.loads(dumps(unique_fracasados))
		# unique_desestiamdas = json.loads(dumps(unique_desestiamdas))
		
		
		for unique_value in unique_values:
			array_de_ordenes_de_merito = map(lambda x: x[13],filter(lambda y: y['0'] == unique_value, array_preseleccion))
			if len(list(set(array_de_ordenes_de_merito))) != len(array_de_ordenes_de_merito):
				return False, "Numeracion de Orden de Merito erroneo"

		if len(set(unique_values) & set(unique_fracasados)) != 0:
			return False, 'Error grupo Fracasados: Renglon no puede estar en mas de 1 grupo 1'

		if len(set(unique_values) & set(unique_desierto)) != 0:
			return False, 'Error grupo Desiertos: Renglon no puede estar en mas de 1 grupo 2'
		
		if len(set(unique_values) & set(unique_desestiamdas)) != 0:
			return False, 'Error grupo Desestimadas: Renglon no puede estar en mas de 1 grupo 3' 

		if len(set(unique_fracasados) & set(unique_desierto)) != 0:
			return False, 'Error grupo Fracasados: Renglon no puede estar en mas de 1 grupo 4'

		if len(set(unique_fracasados) & set(unique_desestiamdas)) != 0:
				return False, 'Error grupo Desestimadas: Renglon no puede estar en mas de 1 grupo '

		if len(set(unique_desestiamdas) & set(unique_fracasados)) != 0:
			return False, 'Error grupo Desestimadas: Renglon no puede estar en mas de 1 grupo'


		try:

			# Generacion de PDF 
			global styles
			styles = getSampleStyleSheet()
			styles.add(ParagraphStyle(name='stileheader', fontweight='bold', fontName='Helvetica', fontSize=20, leading=16, backColor=colors.white, textColor='#666666', alignment=TA_LEFT))
			styles.add(ParagraphStyle(name='stileheader2', fontweight='bold', fontName='HelveticaUltraLight', fontSize=13, leading=12, backColor=colors.white, textColor='#666666', alignment=TA_LEFT)) 
			styles.add(ParagraphStyle(name='stileLeyenda', fontweight='bold', fontName='Helvetica', fontSize=8, leading=9, backColor=colors.white, textColor='#000000', alignment=TA_LEFT)) 
			styles.add(ParagraphStyle(name='stileVal', fontweight='normal', fontName='Helvetica', fontSize=8, leading=8, backColor=colors.white, textColor='#666666', alignment=TA_LEFT)) 
			global separador
			# separador = Image(current_app.config["APP_PATH"] + '/src/etc/img/linea.png', width=560, height=0.7)
			global files
			extension = '.pdf'
			filename=str(uuid.uuid1())
			files = current_app.config["TMP_FOLDER"] + os.sep + filename + extension
			LineLengLebel = 132  # Total caracteres por linea 
			LineLengVal = 132  # Cantidad de Cacacteres por linea 
			file_base64 = get_base64_pdf_content(array_preseleccion)
			id_bucket = file_storage_bp.add_raw_file(file_base64, 'FILE_STORAGE_BUCKET_PATH')
			
			# Busco si ya hay pdf generados y los reemplazo por el nuevo 
			repo_client = repo.get_instance("workflow")
			instance = repo_client.get_by_id("instances", message['instance_id'])
			
			if len(instance['instance']['current_task']['docs']) != 0:
				newlist = filter(lambda x: x["name"] != "Dictamen.pdf", instance['instance']['current_task']['docs'])
				instance['instance']['current_task']['docs'] = newlist
				repo_client.update("instances", message['instance_id'], instance)

			doc = {
				"key" : str(id_bucket),
				"type" : "application/pdf",
				"name" : "Dictamen.pdf",
				"size" : "12"
				}
			repo_client.insert_doc(message['instance_id'], doc)
		except Exception, e:
			return False, "Error durante la generacion del PDF" + str(e)



		# please, respect the SLA! 
		return True,'Este es el mensaje de retorno' 


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
	# story.append(separador)
	story.append(Spacer(1, 10))

	line = []
	for linea in renglones:
		if renglon != '' and renglon != str(linea['0']):
			renglon = str(linea['0']) 
			title = []
			line = []
			title.append(Preformatted('Renglon', styles['stileLeyenda'], maxLineLength=7))
			title.append(Preformatted('Cantidad', styles['stileLeyenda'], maxLineLength=8))
			title.append(Preformatted('Unidad de Medida', styles['stileLeyenda'], maxLineLength=16))
			title.append(Preformatted('Codigo SIByS', styles['stileLeyenda'], maxLineLength=20))
			title.append(Preformatted('Descripcion', styles['stileLeyenda']))
			line.append(title)
			title = []
			title.append(Preformatted(str(linea['0']), styles['stileVal'], maxLineLength=7))
			title.append(Preformatted(str(linea['1']), styles['stileVal'], maxLineLength=16))
			title.append(Preformatted(str(linea['2']), styles['stileVal'], maxLineLength=16))
			title.append(Preformatted(str(linea['3']), styles['stileVal'], maxLineLength=20))
			title.append(Preformatted(str(linea['4']), styles['stileVal'], maxLineLength=80))
			line.append(title)
			table = Table(line)    
			story.append(table)
			line = []

		row = []
		row.append(Preformatted('Orden de Merito', styles['stileLeyenda'], maxLineLength=15))
		row.append(Preformatted(str(linea['13']), styles['stileVal'], maxLineLength=4))
		line.append(row)
		row = []
		row.append(Preformatted('Razon Social', styles['stileLeyenda'], maxLineLength=15))        
		row.append(Preformatted(str(linea['6']), styles['stileVal'], maxLineLength=70))
		line.append(row)
		row = []
		row.append(Preformatted('CUIT', styles['stileLeyenda'], maxLineLength=6))
		row.append(Preformatted(str(linea['5']), styles['stileVal'], maxLineLength=14))
		line.append(row)
		row = []
		row.append(Preformatted('Tipo de Oferta', styles['stileLeyenda'], maxLineLength=14))
		row.append(Preformatted(str(linea['7']), styles['stileVal'], maxLineLength=14))
		line.append(row)
		row = []
		row.append(Preformatted('Cantidad Asignada', styles['stileLeyenda'], maxLineLength=18))
		row.append(Preformatted(str(linea['8']), styles['stileVal'], maxLineLength=16))
		line.append(row)
		row = []
		row.append(Preformatted('IVA', styles['stileLeyenda'], maxLineLength=4))
		row.append(Preformatted(str(linea['10']), styles['stileVal'], maxLineLength=16))
		line.append(row)
		row = []
		row.append(Preformatted('Precio Total', styles['stileLeyenda'], maxLineLength=15))
		row.append(Preformatted(str(linea['11']), styles['stileVal'], maxLineLength=16))
		line.append(row)
		row = []
		row.append(Preformatted('Descuentos', styles['stileLeyenda'], maxLineLength=50))
		row.append(Preformatted(str(linea['12']), styles['stileVal'], maxLineLength=16))
		line.append(row)
		row = []
		row.append(Preformatted('Fundamento', styles['stileLeyenda'], maxLineLength=50))
		row.append(Preformatted(str(linea['14']), styles['stileVal'], maxLineLength=60))
		line.append(row)
		row = []
		row.append(Preformatted('Observaciones', styles['stileLeyenda'], maxLineLength=50))
		row.append(Preformatted(str(linea['15']), styles['stileVal'], maxLineLength=60))
		line.append(row)
		row = []
		table = Table(line)
		table.rowheights = 1
		table.hAlign = TA_LEFT
		story.append(table)
		# aca agrego una linea vacia para separar !! 
		line = []
		row.append([])
		line.append(row)
		table = Table(line)
		line = []
		table.rowheights = 1
		table.hAlign = TA_LEFT
		story.append(table)
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