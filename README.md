# Udatacity_DataEng_P1
Udacity Data Engineer course:  Project 1, Data Modeling with Postgres.
https://www.udacity.com/course/data-engineer-nanodegree--nd027 

## Requirements

- install psycopg2

- Have the scripts all in the same folder, along with both logs folders in a folder "data".

## Overview

In this project the goal is to design & create the appropriate database with its tables for a music streaming app (sparkify).
Once done the task is to set up an ETL pipeline to ingest and store in this newly DB 2 datasets in JSON, logs and songs data (See Dataset section).
The database is a relational DB with the DBMA PostgreSQL.

### Architecure

The project makes use of different tools to ensure different layers of tasks are sequenced:

![image](https://user-images.githubusercontent.com/32632731/141261265-be91badd-8aca-4c2d-b448-895ef4b9f2d4.png)


#### The Data
Made of many log files & song files structured in different hierarchy of folderss (see Dataset section).

#### The "SQL" files
Both the create_tables.py & the sql_queries.py are the main files containing the SQL queries used on the Database for the pipeline.
- create_tables is focused on creating the tables (and dropping any existing previously).
- sql_queries main role is a placeholder for SQL queries. It has no direct interface with the DB. Both the create & drop queries used for the create_tables.py script are defined in this file. Also it is greatly used for both the etl python & jupyter notebook files, in order to insert data in the DB.

#### The Test / Dev files

- etl.ipynb is the development file for the etl pipeline. In here we test small fractions of the dataset and make sure that we can transform and insert the data properly in the database.
- test.ipynb is the testing notebook, allowing us to query the different tables & see how the data has been inserted.

#### The ingestion pipeline

etl.py is in a way the final result, picking up most of what has been developped & tested in the 2 notebooks, this script execute inserts of all the dataset available in the sparkify DB.

### Dataset

Composed of 2 parts, songs & logs.

#### Song Data
- The song dataset is coming from the Million Song Dataset (https://labrosa.ee.columbia.edu/millionsong/). Each file contains metadat about 1 song and is in json format.
Folder structure goes as follow: song_data/[A-Z]/[A-Z]/[A-Z]/name.json
Here is an example of the file structure:

```json

{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}

```

#### Log Data
- The second dataset is generated from an event simulator (https://github.com/Interana/eventsim) based on songs in the previous dataset. Also in json it containes the logs of activity of the music streaming app.
Folder structure goes as follow : log_data/[year]/[month]/[year]-[month]-[day]-events.json
The file structure itself is similar to this:

![image](https://user-images.githubusercontent.com/32632731/141263859-72aa801e-bad3-4a23-86e4-7898c3cca585.png)



## Tables Creation & DB queries

The sparkify DB and tables is created as showed in this diagramm, following Star Schema, were the songplays table is the fact table and the other 4 (users, songs, artists, time) are the dimension tables:

![image](https://user-images.githubusercontent.com/32632731/141192328-6a415d71-9bb5-4c78-95c7-ee628d0c8041.png)

## ETL (Extract Tranform Load)

### Song Data & Artist Data
After fetching each file we pick up the data in a Dataframe and then select only the values to insert (song ID, title, artist ID, year, and duration)
Once done we insert using the prepared query.
Same goes for the the artist data with  ID, name, location, latitude, and longitude.

```python

def process_song_file(cur, filepath):
    # open song file
    df = pd.read_json(filepath,typ='series')

    # insert song record
    song_data = [df.values[6],df.values[7] ,df.values[1], df.values[9],df.values[8]]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = [df.values[1],df.values[5],df.values[4],df.values[2],df.values[3]]
    cur.execute(artist_table_insert, artist_data)


```



### Time & Users Data

We first fetch all the files in the logs_data folder and for each entry / file we push it to a DataFrame, filter the records with page = "NextSong", use the timestamp to retrieve other data formats and finally insert it into the time table once the data has the relevant parameters ("timestamp", "hour", "day","week", "month", "year", "weekday")
For the Users data, out of the first Dataset after filter, we pick user ID, first name, last name, gender and level and insert into users table.

```python

def process_log_file(cur, filepath):
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

```
### Songplays data

In here we need not only the logs_data as source but also previously inserted data from songs & artists table.
We retrieve from the logs_data previously created DataFrame the values timestamp, user ID, level, session ID, location, and user agent.
From the same Dataframe we use the song name, artist and length to query the DB for a match using a JOIN as follow:
```SQL

SELECT song_id , artists.artist_id \
                FROM (songs JOIN artists ON songs.artist_id = artists.artist_id) \
                WHERE songs.title = (%s) AND  artists.name= (%s) AND songs.duration = (%s)

```

And then we finally can order all the data and insert into the songplays table:

```python
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

```




## Improvement suggestions / Additional work
