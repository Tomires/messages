from __future__ import division
import json
import os
import datetime
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from time import mktime

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
ts_hourly = []
ts_weekday = []
unknown_ids = []
delay_total = []
delay_msgs = []

for t in range(len(threads)):
    if IGNORE_GROUP_CONVERSATIONS and len(threads[t]['participants']) > 2:
        continue

    for m in range(len(threads[t]['messages'])):
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

# friend ranking based on number of messages sent
total_messages = 0
rest_messages = 0
current_user = ''
owner_ratio = 0
user_threshold = 0
for sender in sorted_pop:
    total_messages += sender[1]
    if sender[1] > MIN_MESSAGES:
        print sender[0] + " " + str(sender[1])
        user_threshold += 1
    else:
        rest_messages += sender[1]
    if current_user == '':
        current_user = sender[0]
        owner_messages = sender[1]

print '--------------------------'
print 'TOTAL MESSAGES: ' + str(total_messages)
print 'TOTAL USERS: ' + str(len(sorted_pop))


# personal message statistics
print 'Considering ' + current_user + ' as your account name. Hope it\'s correct!'

print 'Judging by the stats above, your messages make up for ' + str(int(owner_messages * 100 / total_messages)) + '% of total count.'

for i in range(24):
    ts_hourly.append(0)
    delay_total.append(0)
    delay_msgs.append(0)

for i in range(7):
    ts_weekday.append(0)

awaiting_reply = False
last_timestamp = 0

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
            timestamp = datetime.datetime.strptime(threads[t]['messages'][m]['date'].split('+')[0], '%Y-%m-%dT%H:%M')
            ts_hourly[timestamp.hour] += 1
            ts_weekday[timestamp.weekday()] += 1
            if awaiting_reply:
                hour = datetime.datetime.fromtimestamp(last_timestamp).hour
                current_delay = (mktime(timestamp.timetuple()) - last_timestamp) / 60 # in minutes
                if current_delay < 1440: # it doesn't make sense for us to count past a day
                    delay_total[hour] += current_delay
                    delay_msgs[hour] += 1
                awaiting_reply = False
        else:
            awaiting_reply = True
            last_timestamp = mktime(datetime.datetime.strptime(threads[t]['messages'][m]['date'].split('+')[0], '%Y-%m-%dT%H:%M').timetuple())
    awaiting_reply = False # move onto next thread

combo = ' '.join(messages)
word_average = int(len(combo) / owner_messages)
print 'You have written ' + str(len(combo)) + ' words across ' + str(owner_messages) + ' messages. Your average message contains ' + str(word_average) + ' words.'

if DEBUG:
    print '> DEBUG MODE ON'
    print '> PLEASE SUPPLY NAMES FOR THE FOLLOWING IDS:'
    for id in unknown_ids:
        print '> ' + id

# message distribution over time of day
plt.bar(range(24), ts_hourly, align='center', color='k', alpha=0.75)
plt.xticks([0,6,12,18], ['12 AM','6 AM', '12 PM', '6 PM'], fontsize=9)
plt.xlabel('Hour', fontsize=12)
plt.ylabel('Messages', fontsize=12)
plt.savefig('output/ts_hourly.png')
plt.close()

# message distribution over days of week
plt.bar(range(7), ts_weekday, align='center', color='k', alpha=0.75)
plt.xticks([0,1,2,3,4,5,6], ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], fontsize=9)
plt.xlabel('Weekday', fontsize=12)
plt.ylabel('Messages', fontsize=12)
plt.savefig('output/ts_weekday.png')
plt.close()

# user popularity
fig, ax = plt.subplots()
sorted_pop_messages = [item[1] for item in sorted_pop[1:user_threshold]]
sorted_pop_messages.append(rest_messages)

sorted_pop_users = [item[0] for item in sorted_pop[1:user_threshold]]
sorted_pop_users.append('Other users')
for i in range(len(sorted_pop_users)):
    sorted_pop_users[i] = unicode(sorted_pop_users[i], "utf-8")

ax.pie(sorted_pop_messages, labels=sorted_pop_users, shadow=True, startangle=90)
ax.axis('equal')
plt.savefig('output/ts_users.png')
plt.close()

# average delay in replying to messages
average_delay = []
for hour in range(24):
    if delay_msgs[hour] == 0:
        average_delay.append(0)
    else:
        average_delay.append(delay_total[hour] / delay_msgs[hour])

plt.bar(range(24), average_delay, align='center', color='k', alpha=0.75)
plt.xticks([0,6,12,18], ['12 AM','6 AM', '12 PM', '6 PM'], fontsize=9)
plt.xlabel('Hour', fontsize=12)
plt.ylabel('Minutes', fontsize=12)
plt.savefig('output/avg_delay.png')
plt.close()
