import os
from urllib.request import urlopen as uReq
import urllib.error
from bs4 import BeautifulSoup as soup
import pandas as pd
import json

versions = {

}

# Connecting the sqlite3 database
import sqlite3
from sqlite3 import Error

con = sqlite3.connect('nodejs.db')
print('connected....')
cursorObj = con.cursor()


url_downloads = "https://nodejs.org/en/download/releases/";
major_downloads = "https://endoflife.software/programming-languages/server-side-scripting/nodejs"

try:
    uClient = uReq(url_downloads)
    downloads_html = uClient.read()
    uClient = uReq(major_downloads)
    major_html = uClient.read()
    uClient.close()

    download_page_soup = soup(downloads_html, "html.parser")
    major_page_soup = soup(major_html, "html.parser")

    all_version_table = download_page_soup.find_all("table")
    major_version_table = major_page_soup.find_all(class_ = "tablesorter")

    # Truncating the table
    sql = ''' DELETE FROM all_versions '''
    cursorObj.execute(sql)
    con.commit()

    print("Nodejs minor versions table truncated....\n")
    df_all_versions = pd.read_html(str(all_version_table))
    versions['all_versions'] = []
    for i in range(int(len(df_all_versions[0]["Version"]))):
        version = df_all_versions[0]["Version"][i]
        lts = df_all_versions[0]["LTS"][i]
        date = df_all_versions[0]["Date"][i]
        v8 = df_all_versions[0]["V8"][i]
        npm = df_all_versions[0]["npm"][i]

        version_details = [version, lts, date, v8, npm]
        print(version_details)

        versions['all_versions'].append({
            "id": str(i),
            "version": str(version),
            "lts": str(lts),
            "date": str(date),
            "v8": str(v8),
            "npm": str(npm)
        })

        sql = ''' INSERT INTO all_versions(id, version, lts, date, v8, npm) VALUES(?,?,?,?,?,?) '''
        cursorObj.execute(sql, (
            i + 1, version, lts, date, v8, npm))
    print('\nChanges committed in nodejs minor versions table.....\n')

    sql = ''' DELETE FROM major_versions '''
    cursorObj.execute(sql)
    con.commit()

    print("Nodejs major versions table truncated....\n")
    df_major_version = pd.read_html(str(major_version_table))
    versions['major_versions'] = []
    for i in range(int(len(df_major_version[0]["Release"]))):
        release = df_major_version[0]["Release"][i]
        codename = df_major_version[0]["Codename"][i]
        release_date = df_major_version[0]["Release date"][i]
        active_lts_start = df_major_version[0]["Active LTS Start"][i]
        maintenance_start = df_major_version[0]["Maintenance Start"][i]
        end_of_life = df_major_version[0]["End of life"][i]

        version_details = [release, codename, release_date, active_lts_start, maintenance_start, end_of_life]
        print(version_details)


        versions['major_versions'].append({
            "id": str(i),
            "release": str(release),
            "codename": str(codename),
            "release_date": str(release_date),
            "active_lts_start": str(active_lts_start),
            "maintenance_start": str(maintenance_start),
            "end_of_life": str(end_of_life)
        })

        sql = ''' INSERT INTO major_versions(id, release, codename, release_date, active_lts_start, maintenance_start, end_of_life) VALUES(?,?,?,?,?,?,?) '''
        cursorObj.execute(sql, (
            i + 1, release, codename, release_date, active_lts_start, maintenance_start, end_of_life))
    print('\nChanges committed in nodejs major versions table.....\n')

except urllib.error.URLError as e:
    print("Error in page request!")

with open('nodejs_versions_json.json','w') as outfile:
    json.dump(versions, outfile, indent=4, separators=(',', ': '))

con.commit()
con.close()

print("Json file and Database updated!....")
