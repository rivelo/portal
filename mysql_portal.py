# -*- coding: utf-8 -*-

import sys
import MySQLdb
from settings import *


def get_conn():
    conn = MySQLdb.connect (host = DATABASE_HOST,
                            user = "root",
                            passwd = "mysql",
                            db = "phpbb",
                            use_unicode=True,
                            charset="utf8")
    return conn


def get_month_event(year, month):
    html = ""
    try:
        conn = get_conn()
        cursor = conn.cursor ()
        cursor.execute (u"""SELECT topic_id, ride_meeting_place, ride_meeting_time, ride_map, ride_details FROM phpbb_rides 
                        WHERE MONTH(ride_meeting_time) = MONTH('%s-%s-01');""" % (year, month) )

        result = cursor.fetchall()

    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    conn.close()
    return result


def get_month_events(year, month):
    events = {}
    try:
        conn = get_conn()
        cursor = conn.cursor ()
        cursor.execute ("""SELECT * FROM phpbb_rides WHERE MONTH(ride_meeting_time) = MONTH('%s-%s-01');""" % (year, month))
        
        while (1):
            row = cursor.fetchone ()
            if row == None:
                break
            events[row[3].day] = row

    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    conn.close()
    return events


def get_day_events(year, month, day):
    events = {}
    try:
        conn = get_conn()
        cursor = conn.cursor ()
        cursor.execute ("""SELECT * FROM phpbb_rides WHERE MONTH(ride_meeting_time) = MONTH('%s-%s-%s') and DAY(ride_meeting_time) = DAY('%s-%s-%s');""" % (year, month, day, year, month, day))
        
        while (1):
            row = cursor.fetchone ()
            if row == None:
                break
            events[row[3].day] = row

    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    conn.close()
    return events

