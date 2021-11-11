import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    
    """
    Description: This function is responsible for reading the json file, passing it in a Dataframe
                 filtering the relavant fields and inserting them in songs & artists tables.

    Arguments:
        cur: the cursor object.
        filepath: song data file path.

    Returns:
        None
    """
    
    
    # open song file
    df = pd.read_json(filepath,typ='series')

    # insert song record
    song_data = [df.values[6],df.values[7] ,df.values[1], df.values[9],df.values[8]]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = [df.values[1],df.values[5],df.values[4],df.values[2],df.values[3]]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    
    """
    Description: This function is responsible for reading the json file, passing it in a Dataframe
                 filtering the relavant fields and inserting them in time & users tables.
                    - filter on page = "NextSong"
                    - convert timestamp to datetime
                    
                 For each row of the file, the function calls a SELECT function to match a song, artist, length
                  with a record in songs & artists so to retrieve user_id & artist_id. Then calls a fucntion to
                  insert values into songplays.
    Arguments:
        cur: the cursor object.
        filepath: log data file path.

    Returns:
        None
    """
    
    
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'],unit="ms")
    
    # insert time data records
    time_data = [df['ts'],t.dt.hour,t.dt.day,t.dt.week,t.dt.month,t.dt.year,t.dt.weekday]
    column_labels = ["timestamp", "hour", "day","week", "month", "year", "weekday"]
    time_dict = dict(zip(column_labels,time_data))
    time_df = pd.DataFrame.from_dict(time_dict)


    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId","firstName","lastName","gender","level"]]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts,row.userId,row.level,songid,artistid,row.sessionId,row.location,row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
        Description: This function is responsible for listing the files in a directory,
        and then executing the ingest process for each file according to the function
        that performs the transformation to save it to the database.

        Arguments:
            cur: the cursor object.
            conn: connection to the database.
            filepath: log data or song data file path.
            func: function that transforms the data and inserts it into the database.

        Returns:
            None
        
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Description: This function is the main function of this file.
                 It creates the connection to the DB and its cursor.
                 Then calls the respective process_data functions to
                 execute the complete etl pipeline.

    Arguments:
        None

    Returns:
        None
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
