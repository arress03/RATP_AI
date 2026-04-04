import holidays
import polars as pl

_FR_HOLIDAYS = holidays.France()

# Pre-calcul des jours feries sur une plage large (2020-2030) pour eviter map_elements
_HOLIDAY_DATES = sorted(
    holidays.France(years=range(2020, 2031)).keys()
)


def add_temporal_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute des features temporelles a partir de la colonne 'fetched_at'.

    Colonnes ajoutees :
    - hour          : heure (0-23)
    - day_of_week   : jour de la semaine (0=lundi, 6=dimanche)
    - is_weekend    : True le samedi et dimanche
    - is_holiday    : True si jour ferie en France
    - is_peak_hour  : True entre 7h-9h et 17h-19h (heure de pointe)
    - month         : mois (1-12)
    - week_of_year  : semaine ISO (1-52)
    """
    return df.with_columns(
        [
            pl.col("fetched_at").dt.hour().alias("hour"),
            pl.col("fetched_at").dt.weekday().alias("day_of_week"),
            (pl.col("fetched_at").dt.weekday() >= 5).alias("is_weekend"),
            pl.col("fetched_at").dt.date().is_in(_HOLIDAY_DATES).alias("is_holiday"),
            (
                ((pl.col("fetched_at").dt.hour() >= 7) & (pl.col("fetched_at").dt.hour() < 9))
                | ((pl.col("fetched_at").dt.hour() >= 17) & (pl.col("fetched_at").dt.hour() < 19))
            ).alias("is_peak_hour"),
            pl.col("fetched_at").dt.month().alias("month"),
            pl.col("fetched_at").dt.week().alias("week_of_year"),
        ]
    )
