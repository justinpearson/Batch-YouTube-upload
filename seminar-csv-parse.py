import csv
from pprint import pprint
import textwrap
import datetime

filename = 'CCDC Seminars - Seminars.csv'
f = open(filename,'rU')


# Video categories: https://gist.github.com/dgp/1b24bf2961521bd75d6c
# 28 - Science & Technology  <-- this one seems good.
# 27 - Education


cols = [
        'Talk Video',
        'Talk Title',
        'Speaker Name',
        'Speaker Organization',
        'Date start',
        'Speaker Bio',
        'Talk Abstract',
        'Seminar Series'
        ]



for nline,line in enumerate(csv.reader(f)):
    if nline == 0:
        inds = {k:line.index(k) for k in cols}
        continue

    # For now, only upload CCDC Seminars. No ECE236 lectures.
    seminar_type = line[inds['Seminar Series']].strip()
    if len(seminar_type) == 0 or seminar_type != 'CCDC Seminar': continue

    file = line[inds['Talk Video']].strip()
    title = line[inds['Talk Title']].strip()
    name = line[inds['Speaker Name']].strip()
    date = line[inds['Date start']].strip()

    if len(file) <= 0 or len(title) <= 0 or len(name) <= 0 or len(date) <= 0 or ' ' not in name: continue

    date = datetime.datetime.strptime(date,'%m/%d/%Y %H:%M:%S').strftime('%b %d, %Y')


    abstract = line[inds['Talk Abstract']].strip()
    bio = line[inds['Speaker Bio']].strip()
    org = line[inds['Speaker Organization']].strip()



    description = '''Research Seminar at the Center for Controls, Dynamical Systems, and Computation

Seminar speaker: {speaker} {org}
Title: {title}
Date: {date}
Host: University of California, Santa Barbara
                    '''.format(
                       speaker=name,
                       date=date,
                       title=title,
                       org = '({})'.format(org) if len(org)>0 else ''
                       )

    description = textwrap.dedent(description)

    if len(abstract) > 0 and abstract != 'seminar flyer (pdf)': description += '\nAbstract: {}\n'.format(abstract)
    if len(bio) > 0 : description += '\nSpeaker Bio: {}\n'.format(bio)

    description += '\nCopyright 2017 University of California. All rights reserved.'
    
    keywords = 'UCSB,CCDC,Engineering'
    category = '28' # Science & Technology
    priv = 'private'


    d = {}
    d['file']           = file
    d['title']          = title
    d['description']    = description
    d['keywords']       = keywords
    d['category']       = category
    d['privacyStatus']  = priv

    print('=======================================')

    print(description)

    pprint(d)

f.close()