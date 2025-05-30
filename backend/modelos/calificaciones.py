from flask import Flask, render_template_string, request
import csv
import os

app = Flask(__name__)

DATA_CSV = './data/datos.csv'
RATINGS_CSV = './data/calificaciones.csv'

def load_data():
    data = []
    if os.path.exists(DATA_CSV):
        with open(DATA_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    return data

def load_ratings():
    ratings_list = []
    if os.path.exists(RATINGS_CSV):
        with open(RATINGS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ratings_list.append({
                    'dest_idx': row.get('dest_idx'),
                    'rating': float(row.get('rating',0)),
                    'comment': row.get('comment','')
                })
    return ratings_list

def aggregate_ratings(ratings_list):
    agg = {}
    for r in ratings_list:
        idx = r['dest_idx']
        if idx not in agg:
            agg[idx] = {
                'ratings': [],
                'comments': []
            }
        agg[idx]['ratings'].append(r['rating'])
        agg[idx]['comments'].append(r['comment'])
    # compute average ratings and count
    result = {}
    for idx, vals in agg.items():
        avg = sum(vals['ratings'])/len(vals['ratings']) if vals['ratings'] else None
        result[idx] = {
            'average': round(avg,2) if avg is not None else None,
            'count': len(vals['ratings']),
            'comments': vals['comments']
        }
    return result

def save_ratings(ratings):
    with open(RATINGS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['selected_row', 'rating', 'comment']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for selected_row, entries in ratings.items():
            for entry in entries:
                writer.writerow({
                    'selected_row': selected_row,
                    'rating': entry['rating'],
                    'comment': entry['comment']
                })

def calculate_average(rating_list):
    if not rating_list:
        return None
    total = 0
    for entry in rating_list:
        try:
            total += float(entry['rating'])
        except (ValueError, KeyError):
            pass
    avg = total / len(rating_list)
    return round(avg, 2)

