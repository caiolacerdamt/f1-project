import pandas as pd
import numpy as np
import fastf1 as ff1
from datetime import datetime as dt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import BatchNormalization, LeakyReLU
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def get_dataframe_schedule(year):
    df = ff1.get_event_schedule(year)
    return (
        df
        .drop(columns=["Location", "OfficialEventName", "Session1Date", "Session1DateUtc", "Session2Date", "Session2DateUtc", "Session3Date", "Session3DateUtc",
                       "Session4Date", "Session4DateUtc", "Session5Date", "Session5DateUtc", "F1ApiSupport"])
        .loc[~df['EventName'].str.contains('Pre-Season', na=False)]
        .reset_index(drop=True)
    )

def get_race(year, gp):
    race = ff1.get_session(year, gp, "R")
    race.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
    race_results_df = race.results
    race_results_df = race_results_df.drop(columns=["BroadcastName", "Abbreviation", "DriverId", "TeamColor", "TeamId", "FirstName", "LastName", "HeadshotUrl", "CountryCode", "Q1", "Q2", "Q3", "Time"])
    df_event = get_dataframe_schedule(year)
    event_name = df_event.at[gp-1, "EventName"]
    race_results_df["EventName"] = event_name
    return race_results_df

def get_laps_data(year, gp):
    race = ff1.get_session(year, gp, "R")
    race.load(telemetry=False, weather=False, messages=False, livedata=False)
    df_laps = race.laps
    df_laps = df_laps.drop(columns=["Time", "PitOutTime", "PitInTime", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "SpeedFL", "SpeedST",
                           "IsPersonalBest", "LapStartTime", "LapStartDate", "TrackStatus", "DeletedReason", "FastF1Generated", "IsAccurate"])
    return df_laps

def fill_na_mean(df, cols):
    for col in cols:
        mean_values = df.groupby(["EventName", "FullName"])[col].transform(lambda x: x.dropna().mean())
        df[col].fillna(mean_values, inplace=True)
    return df

def get_dataframe():
    df = pd.read_csv("data/current_df_to_train.csv")

    season = dt.now().year
    events = ff1.get_event_schedule(season)
    today = pd.Timestamp.now()
    past_events = events[events["EventDate"] <= today]
    last_event = past_events.iloc[-1]
    race = last_event.RoundNumber

    if race in df["EventName"].values:
        return df
    else:
        df_race = get_race(2024, race)
        laps = get_laps_data(2024, race)

        if pd.isna(df_race["Position"].iloc[0]):
            max_lap_number = laps['LapNumber'].max()
            last_lap = laps[laps["LapNumber"] == max_lap_number]
            last_positions = last_lap.set_index('DriverNumber')['Position']
            df_race["Position"] = df_race["DriverNumber"].map(last_positions).fillna(0).astype(int)
            df_race['IsZero'] = df_race['Position'] == 0
            df_race = df_race.sort_values(by=['IsZero', 'Position']).reset_index(drop=True)
            df_race = df_race.drop(columns=['IsZero'])

        df_last_race = pd.merge(df_race, laps, on="DriverNumber")
        df_last_race["Sector1Time"] = pd.to_timedelta(df_last_race["Sector1Time"])
        df_last_race["Sector2Time"] = pd.to_timedelta(df_last_race["Sector2Time"])
        df_last_race["Sector3Time"] = pd.to_timedelta(df_last_race["Sector3Time"])
        df_last_race["LapTime"] = pd.to_timedelta(df_last_race["LapTime"])

        columns_to_fill = ['SpeedI1', 'SpeedI2', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'LapTime']   
        df_last_race = fill_na_mean(df_last_race, columns_to_fill)
        df_last_race['Sector1Time'] = df_last_race['Sector1Time'].dt.total_seconds()
        df_last_race['Sector2Time'] = df_last_race['Sector2Time'].dt.total_seconds()
        df_last_race['Sector3Time'] = df_last_race['Sector3Time'].dt.total_seconds()
        df_last_race['LapTime'] = df_last_race['LapTime'].dt.total_seconds()

        df_last_race['Status'] = np.where(df_last_race['Status'] == 'Finished', 1, 0)

        values_to_replace = ["R", "D", "E", "W", "F", "N"]
        df_last_race["ClassifiedPosition"] = np.where(df_last_race["ClassifiedPosition"].isin(values_to_replace), 0, df_last_race["ClassifiedPosition"])

        df_last_race["FreshTyre"] = df_last_race["FreshTyre"].astype(int)

        label_encoder = LabelEncoder()

        df_last_race['EventName'] = race
        df_last_race['Compound'] = label_encoder.fit_transform(df_last_race['Compound'])
        df_last_race["NameEncoder"] = label_encoder.fit_transform(df_last_race["FullName"])

        df_last_race = df_last_race.drop(columns=["DriverNumber", "TeamName", "FullName",
                                    "ClassifiedPosition", "Points",
                                    "Driver", "LapNumber", "Team",
                                    "Position_y", "Deleted"])

        df_last_race = df_last_race.dropna()
        event_name = df_last_race.pop('EventName')
        df_last_race.insert(0, 'EventName', event_name)
        df_concat_to_model = pd.concat([df, df_last_race], ignore_index=True)
        df_concat_to_model.to_csv("data/current_df_to_train.csv", index=False)
        return df_concat_to_model
    
def mean_features(df):
    scaler = StandardScaler()

    mean_df = df.groupby('NameEncoder').agg({
        "GridPosition": 'mean',
        "Status": 'mean',
        "LapTime": 'mean',
        "Stint": 'mean',
        "Sector1Time": 'mean',
        "Sector2Time": 'mean',
        "Sector3Time": 'mean',
        "SpeedI1": 'mean',
        "SpeedI2": 'mean',
        "Compound": 'mean',
        "TyreLife": 'mean',
        "FreshTyre": 'mean',
    }).reset_index()
    mean_df[['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'TyreLife']] = scaler.fit_transform(
        mean_df[['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'TyreLife']]
)
    
    name_encoder = mean_df.pop('NameEncoder')
    mean_df['NameEncoder'] = name_encoder
    
    return mean_df

def scaler_dataframe(df):
    scaler = StandardScaler()
    df_scaler = df.copy()
    df_scaler[['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'TyreLife']] = scaler.fit_transform(
        df_scaler[['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'TyreLife']]
    )
    df_scaler["Position_x"] = np.where(df_scaler["Position_x"] == 1.0, 1, 0)
    return df_scaler

def train_neural_network():
    df = get_dataframe()

    df_scaler = scaler_dataframe(df)
    X = df_scaler.drop(columns=["Position_x", "EventName"])
    y = df_scaler["Position_x"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = Sequential()
    model.add(Dense(248, input_dim=X_train.shape[1], kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(alpha=0.1))
    model.add(Dropout(0.5))

    model.add(Dense(124, kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(alpha=0.1))
    model.add(Dropout(0.3))

    model.add(Dense(64, kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(alpha=0.1))
    model.add(Dropout(0.5))

    model.add(Dense(32, kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(alpha=0.1))

    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, min_lr=1e-6)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    

    model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test), callbacks=[reduce_lr, early_stopping])

    model.save("model/model.keras")

    df_to_predict = df.copy()
    df_to_predict = mean_features(df_to_predict)
    df_to_predict.to_csv("data/current_df_to_predict.csv", index=False)

if __name__ == "__main__":
    train_neural_network()
