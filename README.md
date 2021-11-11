# Udatacity_DataEng_P1
Udacity Data Engineer course:  Project 1, Data Modeling with Postgres.
https://www.udacity.com/course/data-engineer-nanodegree--nd027 

## Requirements
install psycopg2

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

#### Song Data

#### Log Data

## Tables Creation & DB queries

![image](https://user-images.githubusercontent.com/32632731/141192328-6a415d71-9bb5-4c78-95c7-ee628d0c8041.png)

## ETL (Extract Tranform Load)

## Improvement suggestions / Additional work
