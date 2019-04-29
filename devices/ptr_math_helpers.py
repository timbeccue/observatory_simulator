# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 20:13:35 2019

@author: wrosing

A gaggle of short routines to manipulate angles, sexagesimal strings and the like.
Known throughout the code as 'pmh'.  Many more to be added eventually.

"""

from math import *

#These functions do not work for **mechanical** coordinate ranges.

def reduce_ha(pHa):
    while pHa <= -12:
        pHa += 24.0
    while pHa > 12:
        pHa -= 24.0
    return pHa

def reduce_ra(pRa):
    while pRa < 0:
        pRa += 24.0
    while pRa >= 24:
        pRa -= 24.0
    return pRa

def average_sidereal_times(tick, tock):
    '''
    Produces a glitch-free average around the 23.999 to 0.001 transition.
    '''
    if abs(tick - tock) >= 12:
        return reduce_ra((tick - 24) + tock)
    else:
        return (tick + tock)/2.
        

def trim_dec( pDec):
    '''
    Trims illegal over-pole values to the respective pole.
    '''
    if pDec > 90.0:
        pDec = 90.0
    if pDec < -90.0:
        pDec = -90.0
    return pDec

def trim_alt(pAlt):
    '''
    Trims illegal over-pole values to the respective pole.
    '''
    if pAlt > 90.0:
        pAlt = 90.0
    if pAlt < -90.0:
        pAlt = -90.0
    return pAlt

def reduce_az(pAz):
    '''
    This range-reduction function used rotations where 0 is preferred to 360
    '''
    while pAz < 0.0:
        pAz += 360
    while pAz >= 360.0:
        pAz -= 360.0
    return pAz
#This fuction used for rotations where 360 may be preferred to O
def reduce_rot(pAz):
    '''
    This range-reduction function produces rotations where 360 is preferred to O
    '''
    while pAz <= 0.0:
        pAz += 360
    while pAz > 360.0:
        pAz -= 360.0
    return pAz