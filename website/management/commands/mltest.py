import tensorflow as tf
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import GRU, Dense, Dropout
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from website import views
from django.core.management.base import BaseCommand
from website.models import SiteSettings, ArchiveStopUpdate, ArchiveTripUpdate
from keras._tf_keras.keras.preprocessing.sequence import pad_sequences

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            maintence_settings = SiteSettings.objects.get()
        except SiteSettings.DoesNotExist:
            maintence_settings = SiteSettings.objects.create()
        maintence_settings.maintenance_mode = True
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='8001',
            database='map_site',
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        trip_updates_query = "SELECT * FROM website_archivetripupdate"
        trip_updates = pd.read_sql(trip_updates_query, conn)
        print(f"The trip_updates are {trip_updates}")
        stop_updates_query = "SELECT * FROM website_archivestopupdate"
        stop_updates = pd.read_sql(stop_updates_query, conn)
        print(f"The stop_updates are {stop_updates}")
        conn.close()

        data = pd.merge(trip_updates, stop_updates, on='trip_id')
        data.fillna(method='ffill', inplace=True)
        print(f"The merged data is {data}")

        features = ['start_time', 'departure_delay', 'direction_id', 'day', 'start_date', 'route_id', 'stop_sequence']
        target = 'arrival_delay'

        scaler = StandardScaler()
        data[features] = scaler.fit_transform(data[features])
        print(f"The features columns are {data[features]}")

        '''def create_sequences(data, seq_length):
            sequences = []
            targets = []
            for trip_id in data['trip_id'].unique():
                trip_data = data[data['trip_id'] == trip_id]
                for i in range(len(trip_data) - seq_length):
                    seq = trip_data[features].iloc[i:i + seq_length]
                    sequences.append(seq)
                    targets.append(trip_data[target].iloc[i + seq_length])
            return np.array(sequences), np.array(targets)'''
        def create_sequences(data, seq_length):
            sequences = []
            targets = []
            for trip_id in data['trip_id'].unique():
                trip_data = data[data['trip_id'] == trip_id]
                for i in range(len(trip_data) - seq_length + 1):
                    seq = trip_data[features].iloc[i:i + seq_length].values
                    sequences.append(seq)
                    targets.append(trip_data[target].iloc[i + seq_length - 1])
            '''for trip_id in data['trip_id'].unique():
                trip_data = data[data['trip_id'] == trip_id]
                if len(trip_data) >= seq_length:
                    for i in range(len(trip_data) - seq_length + 1):
                        seq = trip_data[features].iloc[i:i + seq_length].values
                        sequences.append(seq)
                        targets.append(trip_data[target].iloc[i + seq_length - 1])
                else:
                    # Pad sequences that are shorter than seq_length
                    seq = trip_data[features].values
                    padded_seq = pad_sequences([seq], maxlen=seq_length, dtype='float32')[0]
                    sequences.append(padded_seq)
                    targets.append(trip_data[target].iloc[-1])  # Use the last available target'''
            return np.array(sequences), np.array(targets)

        seq_length = 20
        #seq_length = 50
        sequences, targets = create_sequences(data, seq_length)
        print(f"Sequences is {sequences}, targets is {targets}")
        X = sequences
        y = targets
        split = int(0.8 * len(X))
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]

        print(f"The shape of X is {X.shape}, the data is {X}")
        model = Sequential([
            GRU(50, activation='relu', input_shape=(seq_length, X.shape[2])),
            Dropout(0.1),
            Dense(128, activation='relu'),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32)
        loss = model.evaluate(X_val, y_val)
        print(f'Validation Loss: {loss}')
        predictions = model.predict(X_val)
        model.save('website/ml_model/model.keras')
        #ArchiveTripUpdate.objects.all().delete()
        #ArchiveStopUpdate.objects.all().delete()
        #views.reload_model_view(None)

        '''for i in range(20):
            print(f"Predicted: {predictions[i]}, Actual: {y_val[i]}")

        plt.figure(figsize=(10, 6))
        plt.plot(y_val, label='Actual')
        plt.plot(predictions, label='Predicted')
        plt.xlabel('Sample Index')
        plt.ylabel('Arrival Delay')
        plt.title('Predicted vs Actual Arrival Delay')
        plt.legend()
        plt.show()'''

        maintence_settings.maintenance_mode = False