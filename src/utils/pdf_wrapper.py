#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# -*- coding: utf-8 -*-         
#!/usr/bin/python
# -*- coding: ascii -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding: latin-1 -*-
#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
from profile import Stats
import os
import sys
import json
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
from utils import toolbox 

def init():
    global pdfmetrics
    global styles
    global LineLengVal
    global separador
    global LineLengLebel
    global files
    pdfmetrics.registerFont(TTFont('HelveticaNeue', current_app.config["APP_PATH"] + '/src/etc/fonts/HelveticaNeue.ttf'))
    pdfmetrics.registerFont(TTFont('HelveticaNeueBold',  current_app.config["APP_PATH"] + '/src/etc/fonts/HelveticaNeueBold.ttf'))
    pdfmetrics.registerFont(TTFont('HelveticaNeueUltraLight',  current_app.config["APP_PATH"] + '/src/etc/fonts/HelveticaNeueUltraLight.ttf'))
    pdfmetrics.registerFont(TTFont('HelveticaNeueCondensedBlack',  current_app.config["APP_PATH"] + '/src/etc/fonts/HelveticaNeueCondensedBlack.ttf'))
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle( name='stileheader',  fontweight= 'bold',   fontName ='HelveticaNeue',           fontSize=20, leading=16, backColor = colors.white, textColor='#666666', alignment=TA_LEFT))
    styles.add(ParagraphStyle( name='stileheader2', fontweight= 'bold',   fontName ='HelveticaNeueUltraLight', fontSize=13, leading=12, backColor = colors.white, textColor='#666666', alignment=TA_LEFT)) 
    styles.add(ParagraphStyle( name='stileLeyenda', fontweight= 'bold',   fontName ='HelveticaNeueBold',       fontSize=8,  leading=5,  backColor = colors.white, textColor='#666666', alignment=TA_LEFT)) 
    styles.add(ParagraphStyle( name='stileVal',     fontweight= 'normal', fontName ='HelveticaNeue',           fontSize=8,  leading=9,  backColor = colors.white, textColor='#666666', alignment=TA_LEFT)) 
    styles.add(ParagraphStyle( name='stileValGrid', fontweight= 'normal', fontName ='HelveticaNeue',           fontSize=8,  leading=7,  backColor = colors.white, textColor='#666666', alignment=TA_LEFT)) 
    
    LineLengLebel = 132     # Total caracteres por linea 
    LineLengVal = 132       # Cantidad de Cacacteres por linea 
    #separador = Image( current_app.config["APP_PATH"] + '/src/etc/img/linea.png', width = 560, height=0.7 )

    extension = '.pdf'
    filename=str(uuid.uuid1())
    files = current_app.config["TMP_FOLDER"] + os.sep + filename + extension

#CREAMOS LOS CANVAS
#==================
def Header(canvas,doc):
    canvas.saveState()
    #canvas.drawImage( current_app.config["APP_PATH"] + '/src/etc/img/logo1.png', 10, 800 , mask='auto')
    #canvas.drawImage( current_app.config["APP_PATH"] + '/src/etc/img/logo2.png', 430, 800, width=140, height=25, mask='auto')

    canvas.setStrokeColor('#ABAAAB')
    canvas.line(A4[0]-700, A4[1]-53, A4[0]-0, A4[1]-53)
    canvas.setFillColor('#666666')
    canvas.setFont('HelveticaNeueBold', 20) 
    canvas.drawString(10, A4[1] - 77, form['header']['name'])
    canvas.line(A4[0]-700, A4[1]-90, A4[0]-0, A4[1]-90)
    canvas.restoreState()
     
def Footer(canvas,doc):
    canvas.saveState()
    canvas.setFillColor('#666666')
    canvas.setFont('HelveticaNeue',8)
    canvas.setStrokeColor('#ABAAAB')
    canvas.line(A4[0] - 800, A4[1] - 818, A4[0] - 0, A4[1] - 818)
    canvas.drawString(275,  A4[1]-835, "Pág. %d" % doc.page)
    canvas.drawString( 20,  A4[1]-835, 'Codigo: '+form['header']['code'])
    canvas.restoreState()

def formatDate(date):
    day, month, year = date[8:10], date[5:7], date[:4]
    return day+'/'+month+'/'+year

def types_grid(title,data):
    line = []
    header = []
    title_par = ''
    LineLeng = 20
    print title
    for i in title:
        if i != '|':
            title_par += i
        else:
            header.append(Preformatted(title_par,styles['stileLeyenda'],maxLineLength=LineLeng))
            title_par = ''
    header.append(Preformatted(title_par,styles['stileLeyenda'],maxLineLength=LineLeng))
    line.append(header)
    for linea in data:
        new_line = []
        for cell in sorted(linea):
            # if cell != None:
            new_line.append(Preformatted(str(linea[cell]),styles['stileVal'],maxLineLength=LineLeng)) # Valores 
            # else:
                # new_line.append(Preformatted(str(''),styles['stileVal'],maxLineLength=LineLeng)) # Valores 
        line.append(new_line)
    return line


def Group(group,grupo):
    leyenda = []
    line = []
    dato = []
    if 'columns' in group[group.keys()[0]]['properties']:
        columns = group[group.keys()[0]]['properties']['columns']   # Cantidad de columnas de cada grupo 
    else:
        columns = '1'
    LineLeng  = LineLengLebel // int(columns)                        # cantidad de caracteres por fila Titulos         
    LineLeng2 = LineLengVal  // int(columns)                         # cantidad de caracteres por fila Valores
    for component in group[group.keys()[0]]['components']:           # Recorro Componentes 
        types = component[component.keys()[0]]['type']
        if 'label' in component[component.keys()[0]]['properties']:
            if types == 'grid':
                leyenda = component[component.keys()[0]]['properties']['header']
            else:
                leyenda.append(Preformatted(component[component.keys()[0]]['properties']['label'],styles['stileLeyenda'],maxLineLength=LineLeng))     # Etiquetas de las columnas 
        else: 
            leyenda.append(Preformatted('',styles['stileLeyenda'],maxLineLength=LineLeng))     # Etiquetas de las columnas 
        try:
            if types == 'combo':
                if 'multiselect' in component[component.keys()[0]]['properties']:
                    if component[component.keys()[0]]['properties']['multiselect']:
                        texto = toolbox.multiSelection_to_text(valor[grupo][component[component.keys()[0]]['properties']['name']])
                    else:
                        texto = str(valor[grupo][component[component.keys()[0]]['properties']['name']]['text'])
                else:
                    texto = str(valor[grupo][component[component.keys()[0]]['properties']['name']]['text'])
            elif types == 'date':
                texto = str(formatDate(valor[grupo][component[component.keys()[0]]['properties']['name']]))
            elif types == 'label':
                texto = str('')       
            # elif  types == 'password':
                # texto = '**********' 
            elif types == 'grid':
                return types_grid(leyenda,valor[grupo][component[component.keys()[0]]['properties']['name']])
            else:
                texto = str(valor[grupo][component[component.keys()[0]]['properties']['name']])
        except Exception, e:
            texto =  '____________________'
        dato.append(Preformatted(texto,styles['stileVal'],maxLineLength=LineLeng2)) # Valores 
        if columns == str(len(leyenda)):    # Carga las Lineas. 
            line.append(leyenda)
            leyenda = []
            line.append(dato)
            dato = [] 
    if len(leyenda) > 0:                    # Ultima Linea
        line.append(leyenda)
        line.append(dato)

    return line 

def Grid(group,grupo):
    leyenda = []
    name = []
    line = []
    dato = []
    obj = []
    columns = len(group[group.keys()[0]]['components'])
    LebelLeng = LineLengLebel // int(columns)
    for component in group[group.keys()[0]]['components']:          
        if 'showdatagrid' in component[component.keys()[0]]['properties']:
            if component[component.keys()[0]]['properties']['showdatagrid'] == True:
                leyenda.append(Preformatted(component[component.keys()[0]]['properties']['label'],styles['stileLeyenda'],maxLineLength=LebelLeng))  # Etiquetas de las columnas 
                obj.append((component[component.keys()[0]]['properties']['name'],component[component.keys()[0]]['type']))
    if len(obj) != 0:
        line.append(leyenda)
        if grupo in valor: # Load columns Val 
            for i in range(0,len(valor[grupo])):
                for x in obj:
                    if x[0] in valor[grupo][i]:
                        if x[1] == 'date':
                            dato.append(Preformatted(str(formatDate(valor[grupo][i][x[0]])),styles['stileValGrid'],maxLineLength=LebelLeng))
                        elif x[1] == 'combo':
                            dato.append(Preformatted(str(valor[grupo][i][x[0]]['text']),styles['stileValGrid'],maxLineLength=LebelLeng))
                        elif x[1] == 'numeric':
                            if valor[grupo][i][x[0]] is None:
                                dato.append(Preformatted(str(''),styles['stileValGrid'],maxLineLength=LebelLeng))
                            else: 
                                dato.append(Preformatted(str(valor[grupo][i][x[0]]),styles['stileValGrid'],maxLineLength=LebelLeng))
                        else:
                            dato.append(Preformatted(str(valor[grupo][i][x[0]]),styles['stileValGrid'],maxLineLength=LebelLeng))                    
                    else : 
                        dato.append('')
                line.append(dato)
                dato=[]                            
    return line 

def docTemplate(docname):   
    doc = BaseDocTemplate(files,topMargin = 95, bottomMargin = 25, leftMargin = 5, rightMargin = 10 ) #  pagesize=A4) #landscape(A4) para Horizontal #,showBoundary=1 recuadro de las paginas  
    #CREAMOS LOS FRAMES
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='col1')
    #CREAMOS LOS PAGETEMPLATE
    doc.addPageTemplates([PageTemplate(id='contenido', frames=frame, onPage = Header, onPageEnd=Footer)])
    return doc 

def build(spec,data):   
    reload(sys)
    sys.setdefaultencoding("utf-8")    
    init()
    global form
    form = spec
    global valor 
    valor = data 
    story=[]
    head = []
    header = form['header']['name']                             # Title Form
    for group in  form['payload']:                              # Load Group
        # si el grupo tiene propiedad showby y no tiene 'data' no se imprime el mismo. 
        if 'showby' in group[group.keys()[0]]['properties']:        
            showby = group[group.keys()[0]]['properties']['showby']
            if showby == None:
                group_showby = True
            elif showby == 'true':
                group_showby = True    
            elif showby == '':
                group_showby = True
            elif showby == False:
                group_showby = False
            elif showby == True:
                group_showby = True    
            elif len(showby) != 0:
                if group.keys()[0] in valor:    # si el grupo tiene datos 
                    if len(valor[group.keys()[0]]) == 0:
                        group_showby = False
                    else:    
                        group_showby = True
                else:
                    group_showby = False
            else:
                group_showby = True
        else:
            group_showby = True

        # check 'notshowgroupinpdf'
        if 'notshowgroupinpdf' in group[group.keys()[0]]['properties']:
            if group[group.keys()[0]]['properties']['notshowgroupinpdf'] == True:
                group_showby = False

        if group_showby:
            head = []
            if 'label' in group[group.keys()[0]]['properties']:
                head.append([Preformatted(group[group.keys()[0]]['properties']['label'],styles['stileheader2'], maxLineLength=500)])     # Titulo del Grupo / meto el titulo dentro de la tabla para obtener la misma tabulacion de los detalles
            else:
                head.append([Preformatted('',styles['stileheader2'], maxLineLength=150)])     # Titulo del Grupo / meto el titulo dentro de la tabla para obtener la misma tabulacion de los detalles
            table = Table(head,colWidths = '100%')
            table.hAlign = TA_LEFT
            story.append(table)
            story.append(Spacer(1, 3))
            #story.append(separador)
            story.append(Spacer(1, 5))
            table = Table([''])

            grupo = group[group.keys()[0]]['properties']['name']            # nombre del Grupo
            if 'usedatagrid' in group[group.keys()[0]]['properties']:       
                datagrid = group[group.keys()[0]]['properties']['usedatagrid'] 
            else:
                datagrid = False

            if 'components' in group[group.keys()[0]] and datagrid == True:
                data_Grid = Grid(group,grupo)
                if len(data_Grid) != 0:
                    table = Table(data_Grid, colWidths = '100%')
            elif 'components' in group[group.keys()[0]] and datagrid == False:
                table = Table(Group(group,grupo), colWidths = '100%')
            else:
                table = Table([''])            

            table.hAlign = TA_LEFT
            story.append(table)
            story.append(Spacer(1, 15))

    doc = docTemplate(files) 
    doc.build(story)    # save pdf

    with open(files, "rb") as image_file:       # Transforma PDF en binario base64
        encoded_string = base64.b64encode(image_file.read())
    os.remove(files)            # remove  file 

    return encoded_string
      







