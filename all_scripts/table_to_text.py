# -*- coding: UTF-8 -*-
"""
:Script:   table_to_text.py
:Author:   Dan.Patterson@carleton.ca
:Modified: 2017-04-02
:Purpose:
:    To produce a formatted list/array format for ndarray, structured
:    arrays, recarrays
:References:
:  http://pyopengl.sourceforge.net/pydoc/numpy.lib.recfunctions.html
:  http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-data-access/
:        featureclasstonumpyarray.htm
:
"""
import sys
import numpy as np
import arcpy
from textwrap import dedent

formatter = {'float': '{:0.3f}'.format,
             'float64': '{:0.3f}'.format}
np.set_printoptions(edgeitems=3, linewidth=80, precision=2, suppress=True,
                    threshold=200, formatter=formatter)
script = sys.argv[0]


def tbl_arr(in_tbl, in_flds=None):
    """Convert a table to text
    :Requires
    :--------
    :  in_tbl - a table from within arcmap
    :  in_flds - either None, a list/tuple of field names.  If None or an
    :            empty list or tuple, then all fields are returned.
    """
    if not isinstance(in_flds, (list, tuple, type(None), "")):
        return "Input is not correct"
    if in_flds is None:
        in_flds = "*"
    elif isinstance(in_flds, (list, tuple)):
        if len(in_flds) == 0:
            in_flds = "*"
    a = arcpy.da.TableToNumPyArray(in_tbl, in_flds)
    return a


def tweet(msg):
    """Produce a message for both arcpy and python
    : msg - a text message
    """
    m = "\n{}\n".format(msg)
    arcpy.AddMessage(m)
    print(m)
    print(arcpy.GetMessages())


# ----------------------------------------------------------------------
# (6) frmt_struct .... code section --- from frmts.py in arraytools
#
def _col_format(a, nme="fld", deci=0):
    """Determine column format given a desired number of decimal places.
    :  Used by frmt_struct.
    :  a - a column in an array
    :  nme - column name
    :  deci - desired number of decimal points if the data are numeric
    :Notes:
    :-----
    :  The field is examined to determin whether it is a simple integer, a
    :  float type or a list, array or string.  The maximum width is determined
    :  based on this type.
    """
    a_kind = a.dtype.kind
    a_nm = nme
    if a_kind in ('i', 'u'):                 # integer type
        w_, m_ = [':> {}.0f', '{:> 0.0f}']
        col_wdth = len(m_.format(a.max())) + 1
        col_wdth = max(len(a_nm), col_wdth) + 1  # + deci
        c_fmt = w_.format(col_wdth, 0)
        # print("name {} c_fmt {}, wdth {}".format(a_nm, c_fmt, col_wdth))
    elif a_kind == 'f' and np.isscalar(a[0]):   # float type with rounding
        w_, m_ = [':> {}.{}f', '{:> 0.{}f}']
        a_max, a_min = np.round(np.sort(a[[0, -1]]), deci)
        col_wdth = max(len(m_.format(a_max, deci)),
                       len(m_.format(a_min, deci))) + 1
        col_wdth = max(len(a_nm), col_wdth) + 1
        c_fmt = w_.format(col_wdth, deci)
    else:                                   # lists, arrays, strings
        col_wdth = max([len(str(i)) for i in a])
        col_wdth = max(len(a_nm), col_wdth) + 1  # + deci
        c_fmt = "!s:>" + "{}".format(col_wdth)
    return c_fmt, col_wdth


def frmt_struct(a, deci=2, f_names=True, prn=False):
    """Format a structured array with a mixed dtype.
    :Requires
    :-------
    : a - a structured/recarray
    : deci - to facilitate printing, this value is the number of decimal
    :        points to use for all floating point fields.
    : _col_format - does the actual work of obtaining a representation of
    :  the column format.
    :Notes
    :-----
    :  It is not really possible to deconstruct the exact number of decimals
    :  to use for float values, so a decision had to be made to simplify.
    """
    nms = a.dtype.names
    N = len(nms)
    title = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:N], nms][f_names]
    # ---- get the column formats from ... _col_format ----
    dts = []
    wdths = []
    for i in nms:
        c_fmt, col_wdth = _col_format(a[i], nme=i, deci=deci)
        dts.append(c_fmt)
        wdths.append(max(col_wdth, len(i)))
        # print("name {} c_frmt {}, wdth {}".format(i, c_fmt, col_wdth))
    rf = " ".join([('{' + i + '}') for i in dts])
    hdr = ["!s:>" + "{}".format(wdths[i]) for i in range(N)]
    hdr2 = " ".join(["{" + hdr[i] + "}" for i in range(N)])
    header = hdr2.format(*title)
    txt = [header]
    for i in range(a.shape[0]):
        row = rf.format(*a[i])
        txt.append(row)
    if prn:
        for i in txt:
            print(i)
    msg = "\n".join([i for i in txt])
    return msg


# ---- main section ----

script = sys.argv[0]
in_tbl = sys.argv[1]
in_flds = sys.argv[2]
out_txt = str(sys.argv[3]).replace("\\", "/")

in_flds = in_flds.split(";")

frmt = """\n
:---------------------------------------------------------------------:
Running.... {}
Input table ....... {}
With fields... {}
Output text file... {}\n
:---------------------------------------------------------------------:
"""
args = [script, in_tbl, in_flds, out_txt]
msg = dedent(frmt).format(*args)
tweet("Input parameters {}".format(msg))
a = tbl_arr(in_tbl, in_flds)  # call tble_arr to get array
# msg = frmt_rec(a, deci=2, f_names=True, max_rows=-1)  # send a message
msg = frmt_struct(a, deci=2, f_names=True, prn=False)

f = open(out_txt, 'w')
print(msg, file=f)
f.close()


if __name__ == "__main__":
    """run sample"""
#    in_tbl = r"C:\GIS\Tools_scripts\Table_tools\Table_tools.gdb\poly_pnts"
#    in_flds = ['OBJECTID', 'Shape', 'Id', 'Area', 'file_part', 'X_c']
#    in_flds = None
#    out_txt = r"c:\temp\x.txt"
