#!/usr/bin/python
import sys
import time
import datetime
import MySQLdb
import threading
import plotly.plotly as py
from plotly.graph_objs import Scatter, Bar, Layout, Figure, Data, Stream, YAxis



def readDB():
	global date
	global pH
	global LampTemp
	global SoilTemp
	global BedLevel
	global TankTemp
	global EV
	global TDS
	global Salt
	global SG
        conn = MySQLdb.connect(host="localhost", user="pi", passwd="a-51d41e", db="Farm")
        cursor = conn.cursor()
        cursor.execute('select date, LampTemp, SoilTemp,Level from farmdata order by date desc limit 1');
        data = cursor.fetchall()
        for row in data :
                date = row[0]
                LampTemp = row[1]
                SoilTemp = row[2]
		BedLevel = row[3]
        cursor.close ()
        cursor = conn.cursor()
        cursor.execute('select date, Temp, pH, EV, TDS, Salt, SG from H2O order by date desc limit 1');
        data = cursor.fetchall()
        for row in data :
                date = row[0] 
		TankTemp = row[1]
		pH = row[2]
		EV = row[3]
		TDS = row[4]
		Salt = row[5]
		SG = row[6]
        cursor.close ()
        conn.close ()


#######################
#                     #
# PLOTTLY setup       #
#                     #
#######################
def setupPlotly():
	global stream
	global stream1
	global stream2
	global stream3
	global stream4
	global stream5
	global stream6
        global stream7
        global stream8
        username = 'eric.soulliage'
        api_key = 'bdTewCudMX1yX1pkwnby'
        stream_token = 'itbrfoxov0'
        stream_token1 = '8fhj7e1lcz'
        stream_token2 = 'wn1s29to9p'
        stream_token3 = 's2dgh9mik3'
        stream_token4 = 'o68awkd2c9'
        stream_token5 = 'j1o6oz2goz'
        stream_token6 = '6eho02sw40'
	stream_token7 = 'dl6a3hu3sy'
        try:
                py.sign_in(username, api_key)
        except:
                print "Error cant login to plottly"
        pass
        Temp0 = Scatter(
                x=[],
                y=[0, 130],
                name='Temp Lamp',
                mode='lines',
                line=dict(
                        width=2,
                        color='rgb(204, 0, 0)'
                        ),
                stream=dict(
                        token=stream_token,
                        maxpoints=60000
                        )
                )

        Temp1 = Scatter(
                x=[],
                y=[0, 130],
                mode='lines',
                name='Temp midroom',
                line=dict(
                        width=2,
                        color='rgb(255, 51, 51)'
                ),
                stream=dict(
                        token=stream_token1,
                        maxpoints=60000
                        )
                )
        Temp2 = Scatter(
                x=[],
                y=[0, 130],
                mode='lines',
                name='Tank Temp',
                line=dict(
                        width=2,
                        color='rgb(255, 102, 255)'
                ),
                stream=dict(
                        token=stream_token2,
                        maxpoints=60000
                        )
                )
        pH = Scatter(
                x=[],
                y=[0, 10],
                mode='lines',
                name='pH',
                yaxis='y2',
                line=dict(
                        width=2,
                        color='rgb(76, 153 ,0)'
                ),
                stream=dict(
                        token=stream_token3,
                        maxpoints=60000
                )
        )

        EV = Scatter(
                x=[],
                y=[0, 10],
                mode='lines',
                name='EV',
                yaxis='y2',
                line=dict(
                        width=2,
                        color='rgb(0, 255, 0)'
                ),
                stream=dict( 
                        token=stream_token4,
                        maxpoints=60000
                )
        )

        TDS = Scatter(
                x=[],
                y=[0, 10],
                mode='lines',
                name='TDS',
                yaxis='y2',
                line=dict(
                        width=2,
                        color='rgb(0, 255, 255)'
                ),
                stream=dict(
                        token=stream_token5,
                        maxpoints=60000
                )
        )

        Salt = Scatter(
                x=[],
                y=[0, 10],
                mode='lines',
                name='Salinity',
                yaxis='y2',
                line=dict(
                        width=2,
                        color='rgb(51, 255, 255)'
                ),
                stream=dict(
                        token=stream_token6,
                        maxpoints=60000
                )
        )

	BedLevel = Scatter(
                x=[],
                y=[0, 130],
                mode='lines',
                name='BedLevel',
		fill='tozeroy',
                line=dict(
                        width=2,
                        color='rgb(22, 131, 226)',
                ),
                stream=dict(
                        token=stream_token7,
                        maxpoints=60000
                        )
                )


	layout = Layout(
        	title='GrowBot3',
        	yaxis=dict(
            		title='Temps & % ',
            		range=[0, 130],
            		autorange=False,
            		zeroline=True,
        		),
        	yaxis2=dict(
            		title='pH',
			side='right',
            		range=[0, 10],
            		autorange=False,
            		zeroline=True,
           		titlefont=dict(
                	color='rgb(148, 103, 189)'
            		),
            	tickfont=dict(
                	color='rgb(148, 103, 189)'
           		),
            	overlaying='y',
        	)
    	)


	fig = Figure(data=[Temp0, Temp1,Temp2, pH,EV,TDS,Salt, BedLevel], layout=layout)
        try:
                print py.plot(fig, filename='GrowBot6')
        except:
                print "error print to plottly"
        pass
    ###################################
    #                                 #
    # open ploty streams for writting #
    #                                 #
    ###################################

        stream = py.Stream(stream_token)
        stream.open()
        stream1 = py.Stream(stream_token1)
        stream1.open()
        stream2 = py.Stream(stream_token2)
        stream2.open()
        stream3 = py.Stream(stream_token3)
        stream3.open()
        stream4 = py.Stream(stream_token4)
        stream4.open()
        stream5 = py.Stream(stream_token5)
        stream5.open()
        stream6 = py.Stream(stream_token6)
        stream6.open()
        stream7 = py.Stream(stream_token7)
        stream7.open()
def plotit():
	readDB()
        print date, LampTemp, SoilTemp, pH, BedLevel, TankTemp, pH, EV, TDS, Salt, SG	
	###############
        #              #
        # plot graphic #
        #              #
        ################
	try:
	        stream.write({'x': date, 'y': LampTemp,})
	except:
		print "error print LampTemp to plottly"
	pass
	try:
	       	stream1.write({'x': date, 'y': SoilTemp})
        except:
                print "error print RoomTemp to plottly"
        pass
	try:
                stream2.write({'x': date, 'y': TankTemp})
        except:
                print "error print TankTemp to plottly"
        pass
        try:
		stream3.write({'x': date, 'y': pH})
        except:
                print "error print pH to plottly"
        pass
        try:
                stream4.write({'x': date, 'y': EV})
        except:
                print "error print EV to plottly"
        pass
        try:
                stream5.write({'x': date, 'y': TDS})  
        except:
                print "error print TDS to plottly"
        pass
        try:
                stream6.write({'x': date, 'y': Salt})
        except:
                print "error print Salinity to plottly"
        pass
        try:
		stream7.write({'x': date, 'y': BedLevel})
        except:
                print "error print BedLevel to plottly"
        pass
      
    
setupPlotly()
while True:
	
	plotit()
	time.sleep(2)
