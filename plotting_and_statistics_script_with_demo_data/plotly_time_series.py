#!/usr/bin/env python3
# pylint: disable=trailing-whitespace
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=import-error
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=consider-using-f-string
# pylint: disable=import-outside-toplevel
# pylint: disable=unspecified-encoding

r'''  

Plotly time series data with ISO date format, e. g. HBO lamp Lux data or temperatures

This code can be used as a generic template for plotly time series plots.

Lines with wrongly formatted ISO dates are optionally removed by parser

Header coded time zone for fixed-time zone RTC, such as clk_UTC, clk_CET, clk_CEST
are optionally presented in legally valid local time.

Data may contain comments. Multiple header lines are not allowed.

https://plot.ly/python/time-series/

20250509 canonic sensor names my be appended with "_ppendix", e.g. ADT1_Goslar_Innenraum

20251217 ISO8601 UTC and timezone offsets implemented

accepted ISO8601 formtats versions are:
--------------------------------------
2025-12-02T15:25:00
2025-12-02T15:25:00+01:00
2025-12-02T15:25:00Z

non-iso accepted formats are:
------------------------------
2025-12-02 15:25:00
2025-12-02 15:25:00+01:00
2025-12-02 15:25:00Z

'''

import re
import os
import sys
import datetime 
from dateutil import tz
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------- user settings --------------------------

# -------- task control and mode selector --------------------

convert_RTC_to_legal_local_time = True # True is not robust, fails on datetime formatting errors
PARSE_FOR_bad_date_lines = True # my Circuit-python logger generated a few bad dates before midnight. This search takes time!
USE_DOTS = False
PRODUCE_for_localhost = True
PRODUCE_HTML = True
APPEND_statistics_to_logfile = True

FILTER_rolling_average = False
FILTER_NIGHT_time = False
FILTER_DAY_time = False
DAYTIME_start = "08:00"
DAYTIME_end = "20:00"

ROLLING_AVERAGE_SAMPLES_n = 144  # 144 * 300 s = 12 h

# ----------------- content definitions ------------------------

#CHAR_CODING = "ansi"  # für Excel mit Sonderzeichen wie z.B. °C in den Tabellenköpfen
CHAR_CODING = "utf8"

SENSOR_Comment_sep_char_list =["@", "#", " "] # you can use "_" in sensor names, but not in annotation separation

STATS_file_separator = "\t"


                            # interactive plot legend comes in this order:
allsensor_options_default = ['TMP1','TMP2','TMP3','TMP4',
                             'ADT1','ADT2','ADT3','ADT4',       
                             'MLX','Mlx_temp', 'Mlx_ir_temp', 'BME_temp', 'DS3231_temp',
                             'BME_humidity',
                             'CO2',
                             'BME_pressure',
                             'Dum1',
                             'Lux', 
                             'BME_air',
                             'FrbW','delta_1hr', 'deltaT',                           # Freiburg Uni Wetter web scraper
                             'SZX12_R', 'ImagerZ1', 'M165FC', 'Lumar', 'Axioplan2', 'SZX12_L', # 1wire chain  lab optical room  
                             'Freiburg', 'Goslar', 'Holzminden', 'Goettingen', 
                             'Systolische', 'Diastolische', 'Puls­frequenz', # Umlaute in Plotly Namen nicht hinbekommen
                             'Systolic Pressure', 'Diastolic Pressure', 'Mean Arterial Pressure', 'Pulse Rate', 'Pulse Pressure',
                             "Heizung(kWh)", "Warmwasser(kWh)",  "Außentemperatur(°C)",  "Raumtemperatur(°C)", 
                             ] + ["DS"+str(x) for x in range(0,256)]                 # add 256 options for fingerprinted DS18B20 Sensors
                             
do_not_use = ['BME_temp']                             
                             
#separate_y_scale_sensors =  ['BME_pressure', 'BME_humidity'] 
separate_y_scale_sensors =  ['BME_pressure','CO2', "Außentemperatur(°C)",  "Raumtemperatur(°C)", ] 

BAT_voltage_field_names = ['Vbatt', 'ubat',] # first is default name
                             
Date_time_field_names = ["Date_time", "date_time", "Time Stamp", "Zeitstempel", "unix-time"] # first is default name

Logger_id_field_names = [ "Logger-id", "logger-id",] # first is default name

default_separator = "\t" 

default_title = "TSV log data"

default_time_zone = None
#default_time_zone = "CET"  # Central European Time, this is UTC + 1 hour; Central European Summer Time, is UTC + 2 hours
                           # if set to None or to "" the time is reported without change to legal local time


clock_mode_prefix = "clk_"  # used to optionally read clock time zone UTC, CET, CEST from a speceal header

# -----------------end of  content definitions ------------------------

if PRODUCE_HTML:
    import plotly.offline


class Field_dynamic_names():
    """used to store the currently valid field name for a category, one out of a candidate list"""    
    def __init__(self):
        self.datetime = ""
        self.Vbat = ""
        self.logger_id = ""
    
    def identify_names(self, header):
        '''load data from header string'''
        for logger_id_name in Logger_id_field_names:
            if logger_id_name in header:
                self.logger_id = logger_id_name
                break    

        for date_name in Date_time_field_names:
            if date_name in header:
                self.datetime = date_name
                break

        for bat_name in BAT_voltage_field_names:
            if bat_name in header:
                self.Vbat = bat_name
                break
        


field_names = Field_dynamic_names()  # here to have this global


def is_high_quality_temperature(sens_name):
    return (
        sens_name.startswith("DS")
        or sens_name.startswith("ADT")
        or sens_name.startswith("TMP")
        or sens_name.startswith("MLX")
        or sens_name.startswith("FrbW")        
    )


def has_statistics(linesl):
    '''tests if statitics was already appenden to log file'''
    has_st = False
    for ll in linesl:
        if ll.startswith('#') and 'Mean' in ll:
            has_st = True
    return has_st


def accept_sensors_with_comments(dfl, all_sensor_optionsl):
    sensorsl = []
    for column_name in dfl.columns:
        for sep_char in SENSOR_Comment_sep_char_list:
            if column_name.split(sep_char)[0] in all_sensor_optionsl:
                sensorsl.append(column_name)
                break
    return sensorsl


def append_temperature_statistics_to_log_file(dfl, logger_tsv_filel, accepted_sensorsl, skip_frames=0):
    '''prepare and append statistics message to log file, if not present yet'''
    n_txt = "{number:.2f}"
    stat_header_line = ("Sensor" + STATS_file_separator
                + "Mean " + STATS_file_separator
                + "Min " + STATS_file_separator
                + "Max " + STATS_file_separator
                + "Stdev " + STATS_file_separator
                + "duration" + STATS_file_separator
                #  + "2 hrs equilibration omitted"

                + "\n"
            )
            
    #starttime = datetime.datetime.strptime(dfl[field_names.datetime].iloc[0], "%Y-%m-%d %H:%M:%S")
    #endtime = datetime.datetime.strptime(dfl[field_names.datetime].iloc[-1], "%Y-%m-%d %H:%M:%S")

    starttime = dfl[field_names.datetime].iloc[0]
    endtime = dfl[field_names.datetime].iloc[-1]

    timeDelta = endtime - starttime
    
    stat_data_lines = []
    for sensor in accepted_sensorsl:  # find and plot first track
        try:
            #if sensor in dfl.columns and is_high_quality_temperature(sensor):
            if sensor in dfl.columns:
                stat_line =(
                    sensor                                                 + STATS_file_separator
                    + n_txt.format(number=dfl[sensor][skip_frames:].mean()) + STATS_file_separator
                    + n_txt.format(number=dfl[sensor][skip_frames:].min())  + STATS_file_separator
                    + n_txt.format(number=dfl[sensor][skip_frames:].max())  + STATS_file_separator
                    + n_txt.format(number=dfl[sensor][skip_frames:].std())  + STATS_file_separator
                    #+ str(datetime.timedelta(seconds = int(timeDelta))) + STATS_file_separator                                        
                    + str(timeDelta) + STATS_file_separator                                  
                )
                # if skip_frames >0:
                    # stat_line += 'yes'
                # else:
                    # stat_line += 'no'
                stat_data_lines.append(stat_line+'\n')
        except:
            print('...statistics for sensor ' + sensor + ' failed')
    if stat_data_lines:
        try:
            with open(logger_tsv_filel, "a") as log_file:
                log_file.write('#\n# '+stat_header_line+'# '+'# '.join(stat_data_lines)+'#\n')
        except PermissionError:
            print('Failed to append statistics.\nClose other application (e.g. Excel) blocking ' + logger_tsv_filel + '\n')
            input('Press Enter to quit.')
            sys.exit()



def bad_date_and_repeated_header_masker(linesl):
    '''masks badlyformatted iso dates. Runs on lines of text, not on df. Used for my circuit-python logger'''
    date_pattern_c1 = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d')
    date_pattern_c2 = re.compile(r'\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d')
    skiplinesl =[]
    toplines=True
            
    for ln,l in enumerate(linesl):
        if l.startswith('#'):  # comment found, redundant with pandas df load comment =
            skiplinesl.append(ln)
        elif field_names.logger_id in l: 
            if toplines:
                if ln>0: 
                    skiplinesl.append(ln-1) # leave last of multiple top header lines. This is required for re-starts in case the restart was done due to an observed sensor count failure (LED blinks)
            else:
                skiplinesl.append(ln)
        else:
            toplines = False # first values found
            if bool(field_names.datetime) and field_names.datetime != "unix-time" and PARSE_FOR_bad_date_lines:
                if not re.search(date_pattern_c1, l) and not re.search(date_pattern_c2, l):
                    skiplinesl.append(ln)      
    return skiplinesl





def convert_fixed_clock_tz_to_legal_local_clock(dfl):
    
    ''' code For datetime objects, we get the legal local time at the day of the recording,
        with correct consideration of daylight savings time
    '''

    def get_loggers_fixed_time_zone_from_header(dfl):
        if default_time_zone:
            logger_clock_time_zone = default_time_zone
        else:
            logger_clock_time_zone = ""
        for label in dfl.columns:  # search time zone information in header
            if label.startswith(clock_mode_prefix):
                logger_clock_time_zone = label.split("_")[1]
        return logger_clock_time_zone

    def get_UTC_offset_of_logger_clock(logger_clock_time_zonel):
        ''' determines UTC offset_hours of logger clock from time zone '''
        if logger_clock_time_zonel == "UTC":
            offset_hours = 0
        elif  logger_clock_time_zonel == "CET":
            offset_hours = 1
        elif  logger_clock_time_zonel == "CEST":
            offset_hours = 2
        elif  logger_clock_time_zonel == "": # no fixed time zone indicated, do not touch data
            offset_hours = 0
        else:
            print("Time zone correction for "+logger_clock_time_zonel+" not implemented yet.")
            sys.exit(1)
        return offset_hours    
    
    
    logger_clock_time_zone = get_loggers_fixed_time_zone_from_header(dfl)
   
    if logger_clock_time_zone: # time zone hint in header. Convert first to UTC, then to local legal time

        offset_hours = get_UTC_offset_of_logger_clock(logger_clock_time_zone)

        dfl[field_names.datetime] = dfl[field_names.datetime] - pd.Timedelta(hours=offset_hours, minutes=0, seconds=0) # gives utc

        # next line fails on already time zone aware datetimes!
        dfl[field_names.datetime] = dfl[field_names.datetime].dt.tz_localize('utc').dt.tz_convert("Europe/Berlin")
        
    elif dfl[field_names.datetime].dt.tz is not None: # log file is time zone aware, convert this to local legal time
        dfl[field_names.datetime] = dfl[field_names.datetime].dt.tz_convert("Europe/Berlin")
    # if log is time-zone agnostic, make no change


def main():

    print("initializing...")

    allsensor_options = [x for x in allsensor_options_default if x not in do_not_use]

    #-------------------- file picker ------------------------
    if (len(sys.argv) < 2  or  len(sys.argv) > 2): # 2 is for one parameter , 1 means no argument given, 2 means one argument given
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename
        Tk().withdraw()                      # we don't want a full GUI, so keep the root window from appearing
        logger_tsv_file  = askopenfilename(initialdir=os.getcwd(), title = "Select temperature logger .tsv file. Use -h for help in console mode.",filetypes = (("tsv files","*.tsv"),("csv files","*.csv"),("all files","*.*"))) # show an "Open" dialog box and return the path to the selected file
        if logger_tsv_file  == "":
            sys.exit() # Abort has been pressed
    else:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print(__doc__)
            sys.exit()
        else:
            logger_tsv_file = sys.argv[1]

    #-------------------- read data first as text to filter, than as pandas df ----------------------------
    #  ----------------- find bad line numbers, such as repeated headers from logger re-starts
    print("loading...")
    skiplines = []

    with open(logger_tsv_file, encoding='utf-8-sig', errors="ignore") as f:
        lines = f.readlines()

    field_names.identify_names(lines[0])  # fin out, which of the aliases is used
    
    if field_names.logger_id:  # one of my data loggers
        skiplines = bad_date_and_repeated_header_masker(lines)
    
    try:
        df = pd.read_csv(logger_tsv_file, encoding=CHAR_CODING, sep=None, comment='#', engine='python', skiprows=skiplines,  on_bad_lines="skip" )
    except UnicodeDecodeError:
        df = pd.read_csv(logger_tsv_file, encoding="ansi", sep=None, comment='#', engine='python', skiprows=skiplines,  on_bad_lines="skip" )
    
    # simpler alternative for good old python 3.5 on 2027 RaspberryPi3+ installation, used 202508
    # df = pd.read_csv(logger_tsv_file, encoding='utf-8', sep="\t", comment='#', skiprows=skiplines)  
    
    # -------------- convert datetime ----------------------
    if not field_names.datetime:
        print('Datetime stamp is missing in tsv-data')
        print(df)
        sys.exit()
    
    if field_names.datetime == "unix-time":
        df[Date_time_field_names[0]] = pd.to_datetime(df["unix-time"], unit='s')
        field_names.datetime = Date_time_field_names[0]
    else:
        df[field_names.datetime] = pd.to_datetime(df[field_names.datetime])

    if convert_RTC_to_legal_local_time:
        convert_fixed_clock_tz_to_legal_local_clock(df)

    # ------------ data we later need--------------------
    my_title = df[field_names.logger_id][1] if field_names.logger_id else default_title        

    accepted_sensors = accept_sensors_with_comments(df, allsensor_options)

    # -------- go to work ------------------------
    if APPEND_statistics_to_logfile and not has_statistics(lines[-13:]):
        print("appending statistics...")
        append_temperature_statistics_to_log_file(df, logger_tsv_file, accepted_sensors)       

    # ---------------------- plot battery voltage -----------------------------------------
    
    if field_names.Vbat: 

        print("plotting  Vbatt...")
        
        fig = go.Figure(go.Scatter(x = df[field_names.datetime], y = df[field_names.Vbat],name=field_names.Vbat))                        

        fig.update_layout(title=my_title+": Battery Voltage [mV]    (full: 4200, empty: 3600)",plot_bgcolor='rgb(230, 230,230)', showlegend=True)
        if PRODUCE_for_localhost:
            fig.show()

  # ---- selecting daily time intervals if requested

    nstr = ""    
    if FILTER_NIGHT_time or FILTER_DAY_time:

        df.index = df[field_names.datetime]
        # Converting the index as date
        #df.index = pd.to_datetime(df.index)
    
        if FILTER_NIGHT_time:
            subset = df.between_time(DAYTIME_end, DAYTIME_start) # at daylight time
            nstr = 'at night'
        elif FILTER_DAY_time:
            subset = df.between_time(DAYTIME_start, DAYTIME_end) # at night time
            nstr = 'at daytime'
        # print(subset.head(3))
        # print('...')
        # print(subset.tail(3))    
        df = subset


    # -----------plot temperature data violin plot. 

    try:   # just in case something happens, we would still get the timeline plot
        print("plotting violin plot...")

        n = 0
        for sensor in accepted_sensors: 
            if sensor in df.columns:
                n += 1
        fig = make_subplots(rows=1, cols=n)
               
        c = 0
        for sensor in accepted_sensors: 

            if sensor in df.columns:
                c += 1
                fig.append_trace(
                    go.Violin(
                        y=df[sensor],
                        name=sensor+nstr,
                        box_visible=True,
                        #line_color="black",
                        meanline_visible=True,
                    ), row=1, col=c
                )  # plot second to last trace

        #fig.update_layout(title='temperature logged',plot_bgcolor='rgb(230, 230,230)', showlegend=True)
        #fig.update_layout(title=df[field_names.logger_id][1],plot_bgcolor='rgb(230, 230,230)', showlegend=True)
        if PRODUCE_for_localhost:
            fig.show()
    except:
        print('Violin plot failed')
        raise

    # ------------------- make moving average, if requested ----------------------------

    if FILTER_rolling_average:
        ROLLING_filter_appendix = " rolling average"
        nstr += ROLLING_filter_appendix
        for head_name in df.columns:
            if is_high_quality_temperature(head_name):
                df[head_name] = df[head_name].rolling(ROLLING_AVERAGE_SAMPLES_n).mean()
                #df[head_name+ROLLING_filter_appendix] = df[head_name].rolling(ROLLING_AVERAGE_SAMPLES_n).mean()
                #accepted_sensors.remove(head_name)
                #accepted_sensors.append(head_name+ROLLING_filter_appendix)


    #-------------------- plot temperature data timeline plot ----------------------------

    print("plotting timeline...")
    # Create figure with secondary y-axis

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for sensor in accepted_sensors:
        # find and plot first track
        if sensor in df.columns and not sensor in separate_y_scale_sensors and not sensor in do_not_use: 
            #fig.add_trace(go.Scatter(x = df[field_names.datetime], y = df[sensor], name=sensor, hovertemplate="%{x|%d %b %Y, %H:%M:%S} %{y}"), secondary_y=False)
            fig.add_trace(go.Scatter(x = df[field_names.datetime], y = df[sensor], name=sensor, hovertemplate="%{x|%d %b %Y, %H:%M} %{y}"), secondary_y=False)
        elif sensor in df.columns and sensor in separate_y_scale_sensors: 
            #fig.add_trace(go.Scatter(x = df[field_names.datetime], y = df[sensor], name=sensor, hovertemplate="%{x|%d %b %Y, %H:%M:%S} %{y}"), secondary_y=True)
            fig.add_trace(go.Scatter(x = df[field_names.datetime], y = df[sensor], name=sensor, hovertemplate="%{x|%d %b %Y, %H:%M} %{y}"), secondary_y=True)

    fig.update_layout(title=my_title+nstr,plot_bgcolor='rgb(230, 230,230)', showlegend=True)
    
    if USE_DOTS:
        fig.update_traces(marker_size=10, mode="markers")    

    if PRODUCE_for_localhost:
        fig.show()

    if PRODUCE_HTML:
        # the following line ensures that the output file goes besides the script, for simple RasPi Scripting
        plotly.offline.plot(fig, filename = os.path.dirname(sys.argv[0])+os.sep+'plotly_generated.html', auto_open=False)


if __name__ == '__main__':
    main()
