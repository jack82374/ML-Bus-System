from django.core.management.base import BaseCommand
from website.models import NextDelay
import mysql.connector # Ideally this probably shouldn't be used but I'm not sure how to use Pandas with Django models
import pandas as pd
from sklearn.preprocessing import StandardScaler
import keras
import numpy as np
from keras._tf_keras.keras.preprocessing.sequence import pad_sequences

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('trip_id', type=str, help='Trip_id to lookup')

    def handle(self, *args, **kwargs):
        #model = keras.models.load_model('website/ml_model/model.keras')
        model = keras.models.load_model('website/ml_model/model2.keras')
        #stop_updates = StopUpdate.objects.get(trip_id=kwargs['trip_id'])
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='8001',
            database='map_site',
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        trip_updates_query = f"SELECT * FROM website_tripupdate WHERE trip_id = '{kwargs['trip_id']}'" #
        trip_updates = pd.read_sql(trip_updates_query, conn)
        stop_updates_query = f"SELECT * FROM website_stopupdate WHERE trip_id = '{kwargs['trip_id']}'" #
        stop_updates = pd.read_sql(stop_updates_query, conn)
        conn.close()

        data = pd.merge(trip_updates, stop_updates, on='trip_id')
        data.fillna(method='ffill', inplace=True)
        #print(data.columns)

        features = ['start_time', 'departure_delay', 'direction_id', 'day', 'start_date', 'route_id', 'stop_sequence']
        #target = 'arrival_delay'
        scaler = StandardScaler()
        #print(f"The data feature columns are: {data[features].columns}")
        #print(f"The data features values are: {data[features]}")
        try:
            data[features] = scaler.fit_transform(data[features])
        
            #seq_length = 20  # Use the same sequence length as during training
            seq_length = 50
            '''sequences = []
            for i in range(len(data) - seq_length + 1):
                seq = data[features].iloc[i:i + seq_length]
                sequences.append(seq)
                # padding here'''
            sequences = []
            for trip_id in data['trip_id'].unique():
                trip_data = data[data['trip_id'] == trip_id]
                if len(trip_data) >= seq_length:
                    for i in range(len(trip_data) - seq_length + 1):
                        seq = trip_data[features].iloc[i:i + seq_length].values
                        sequences.append(seq)
                else:
                    # Pad sequences that are shorter than seq_length
                    seq = trip_data[features].values
                    padded_seq = pad_sequences([seq], maxlen=seq_length, dtype='float32')[0]
                    sequences.append(padded_seq)

            converted_sequences = np.array(sequences)
            predictions = round(float(model.predict(converted_sequences)))
            print(f"The delay for {trip_id} is {predictions}.")
            #print(type(predictions))
            NextDelay.objects.update_or_create(trip_id = trip_id,
                                                        defaults={
                                                            'delay': predictions
                                                        }
                                                        )
        except ValueError as notEnoughData:
            print(f"Error {notEnoughData} caused by not having saved enough updates yet, skipping for now")
        #return predictions