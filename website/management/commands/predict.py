from django.core.management.base import BaseCommand
from website.models import StopUpdate
import mysql.connector # Ideally this probably shouldn't be used but I'm not sure how to use Pandas with Django models
import pandas as pd
from sklearn.preprocessing import StandardScaler
import keras
import numpy as np

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('trip_id', type=str, help='Trip_id to lookup')

    def handle(self, *args, **kwargs):
        model = keras.models.load_model('website/ml_model/model.keras')
        #stop_updates = StopUpdate.objects.get(trip_id=kwargs['trip_id'])
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='8001',
            database='map_site',
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        trip_updates_query = f"SELECT * FROM website_tripupdate WHERE trip_id = '{kwargs['trip_id']}'"
        trip_updates = pd.read_sql(trip_updates_query, conn)
        stop_updates_query = f"SELECT * FROM website_stopupdate WHERE trip_id = '{kwargs['trip_id']}'"
        stop_updates = pd.read_sql(stop_updates_query, conn)
        conn.close()

        data = pd.merge(trip_updates, stop_updates, on='trip_id')
        data.fillna(method='ffill', inplace=True)
        #print(data.columns)

        features = ['start_time', 'departure_delay', 'direction_id', 'day', 'start_date', 'route_id', 'stop_sequence']
        #target = 'arrival_delay'
        scaler = StandardScaler()
        print(data[features].columns)
        data[features] = scaler.fit_transform(data[features])
        
        seq_length = 20  # Use the same sequence length as during training
        sequences = []
        for i in range(len(data) - seq_length + 1):
            seq = data[features].iloc[i:i + seq_length]
            sequences.append(seq)

        converted_sequences = np.array(sequences)
        predictions = model.predict(converted_sequences)
        print(f"The predictions are {predictions}.")
        print(type(predictions))
        return predictions