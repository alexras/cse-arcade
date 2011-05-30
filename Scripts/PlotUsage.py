#!/usr/bin/env python

import os,sys,sqlite3

from boomslang import Line, Plot, Bar, PlotLayout, Utils
from optparse import OptionParser
import datetime

def executeQuery(query, dbFile):

    rowIterator = db.execute(query)

    return rowIterator

def hourNumToString(hourNum):
    if hourNum == 0:
        return "12 AM"
    elif hourNum < 12:
        return "%d AM" % (hourNum)
    elif hourNum == 12:
        return "12 PM"
    else:
        return "%d PM" % (hourNum - 12)

def getBinBars(rows, binKey, quantityKey, xLabelFormattingFunction,
                     xLabel, yLabel, xLabelRotation = 0):
    bins = []
    countsPerBin = []

    for row in rows:
        bins.append(int(row[binKey]))
        countsPerBin.append(int(row[quantityKey]))

    bar = Bar()
    bar.xValues = bins
    bar.yValues = countsPerBin

    if xLabelFormattingFunction is not None:
        bar.xTickLabelPoints = range(len(bins))
        bar.xTickLabels = map(xLabelFormattingFunction,
                              bar.xTickLabelPoints)

    if xLabelRotation > 0:
        bar.setXTickLabelProperties(rotation=str(xLabelRotation))

    barPlot = Plot()
    barPlot.add(bar)
    barPlot.setXLabel(xLabel)
    barPlot.setYLabel(yLabel)
#    barPlot.setXLimits(0, None)
    return barPlot

def binByHourOfDay(db):
    rows = db.execute("""
SELECT strftime('%H', datetime(start, 'unixepoch', 'localtime')) AS hour, SUM(end - start) / 3600.0 as sum
from Plays GROUP BY hour
""")

    plot = getBinBars(rows, 'hour', 'sum', hourNumToString,
                            "Hour", "Total Play Time (Hours)", 90)
    plot.setPlotParameters(bottom=0.18)
    plot.save("played_hours.png")

def binByDayOfWeek(db):
    dayOfWeekStrings = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    rows = db.execute("""
SELECT strftime('%w', datetime(start, 'unixepoch', 'localtime')) AS weekday,
SUM(end - start) / 3600.0 AS sum FROM Plays GROUP BY weekday
""")

    plot = getBinBars(rows, 'weekday', 'sum',
                      lambda x: dayOfWeekStrings[x],
                      "Day of Week", "Total Play Time (Hours)")
    plot.save("played_days.png")

def binByGameDuration(db):
    rows = db.execute("""
SELECT ((P.end - P.start) / 60) as minutes_played, count(*) as count
FROM Games G, Plays P
WHERE G.id = P.game
AND minutes_played >= 0
GROUP BY minutes_played
""")

    plot = getBinBars(rows, 'minutes_played', 'count',
                      None, "Minutes Played", "# Games")
    plot.save("minutes_played.png")

def PlotUsage(dbFile):
    db = sqlite3.connect(dbFile)
    db.row_factory = sqlite3.Row

    binByHourOfDay(db)
    binByDayOfWeek(db)
    binByGameDuration(db)

if __name__ == "__main__":
    optionParser = OptionParser(usage="usage: %prog [options] <db file>")

    (options, args) = optionParser.parse_args()

    if len(args) != 1:
        optionParser.error("Incorrect argument count")

    (dbFile,) = args

    if not os.path.exists(dbFile):
        print >>sys.stderr, "Can't find DB file '%s'" % (dbFile)
        sys.exit(1)

    PlotUsage(dbFile)
