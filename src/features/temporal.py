import holidays
import pandas as pd

_FR_HOLIDAYS = holidays.France()


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des features temporelles à partir de la colonne 'fetched_at'.

    Colonnes ajoutées :
    - hour          : heure (0-23)
    - day_of_week   : jour de la semaine (0=lundi, 6=dimanche)
    - is_weekend    : True le samedi et dimanche
    - is_holiday    : True si jour férié en France
    - is_peak_hour  : True entre 7h-9h et 17h-19h (heure de pointe)
    - month         : mois (1-12)
    - week_of_year  : semaine ISO (1-52)
    """
    df = df.copy()
    dt = pd.to_datetime(df["fetched_at"])

    df["hour"] = dt.dt.hour
    df["day_of_week"] = dt.dt.dayofweek
    df["is_weekend"] = dt.dt.dayofweek >= 5
    df["is_holiday"] = dt.dt.date.apply(lambda d: d in _FR_HOLIDAYS)
    df["is_peak_hour"] = dt.dt.hour.apply(lambda h: (7 <= h < 9) or (17 <= h < 19))
    df["month"] = dt.dt.month
    df["week_of_year"] = dt.dt.isocalendar().week.astype(int)

    return df
