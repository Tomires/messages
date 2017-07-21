from __future__ import division
import json
import os
import datetime
import csv
#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
from collections import Counter

# config
MIN_MESSAGES = 100
IGNORE_GROUP_CONVERSATIONS = True
DEBUG = False

names = {}
with open('data/names.csv', 'rb') as names_csv:
    names_file = csv.reader(names_csv, delimiter=',', quotechar='|')
    for row in names_file:
        names[row[0].replace('@facebook.com','')] = row[1]

json_data = open('data/messages.json')

threads = json.load(json_data)['threads']
sender_pop = {}
messages = []
unknown_ids = []

for t in range(len(threads)):
    #print threads[t]['participants']
    if IGNORE_GROUP_CONVERSATIONS and len(threads[t]['participants']) > 2:
        continue

    for m in range(len(threads[t]['messages'])):
        #print threads[t]['messages'][m]['sender'].encode('utf-8') + " ! " + threads[t]['messages'][m]['date'] + " ! " + threads[t]['messages'][m]['message'].encode('utf-8')
        sender = threads[t]['messages'][m]['sender'].encode('utf-8')
        if '@' in sender:
            try:
                sender = names[sender.replace('@facebook.com','')]
            except KeyError:
                if sender not in unknown_ids:
                    unknown_ids.append(sender)

        if sender in sender_pop:
            sender_pop[sender] += 1
        else:
            sender_pop[sender] = 1

sorted_pop = sorted(sender_pop.iteritems(), key=lambda x:-x[1])[:len(sender_pop)]

total_messages = 0
current_user = ''
owner_ratio = 0
for sender in sorted_pop:
    total_messages += sender[1]
    if sender[1] > MIN_MESSAGES:
        print sender[0] + " " + str(sender[1])
    if current_user == '':
        current_user = sender[0]
        owner_messages = sender[1]

print '--------------------------'
print 'TOTAL MESSAGES: ' + str(total_messages)
print 'TOTAL USERS: ' + str(len(sorted_pop))

print 'Considering ' + current_user + ' as your account name. Hope it\'s correct!'

print 'Judging by the stats above, your messages make up for ' + str(int(owner_messages * 100 / total_messages)) + '% of total count.'

for t in range(len(threads)):
    for m in range(len(threads[t]['messages'])):
        sender = threads[t]['messages'][m]['sender'].encode('utf-8')
        if '@' in sender:
            try:
                sender = names[sender.replace('@facebook.com','')]
            except KeyError:
                pass
        if sender == current_user:
            messages.append(threads[t]['messages'][m]['message'].encode('utf-8'))

combo = ' '.join(messages)
word_average = int(len(combo) / owner_messages)
print 'You have written ' + str(len(combo)) + ' words across ' + str(owner_messages) + ' messages. Your average message contains ' + str(word_average) + ' words.'

if DEBUG:
    print '> DEBUG MODE ON'
    print '> PLEASE SUPPLY NAMES FOR THE FOLLOWING IDS:'
    for id in unknown_ids:
        print '> ' + id
