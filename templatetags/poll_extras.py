# -*- coding: utf-8 -*-
from django import template
import MySQLdb

import datetime

register = template.Library()
import re


@register.filter(name='inday')
def inday(value, arg):
    if arg in value:
        return value[arg]
    else:
        return None

