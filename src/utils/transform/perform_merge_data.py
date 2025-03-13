import pandas as pd
import logging
import tqdm
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def _perform_delete_nan(df_events: str) -> list:
    train_events = pd.read_csv(df_events)

    series_has_NaN = train_events.groupby('series_id')['step'].apply(lambda x: x.isnull().any())

    log.info(f"Number of series containing NaN values:\n{series_has_NaN.value_counts()}")

    no_NaN_series = series_has_NaN[~series_has_NaN].index.tolist()

    for remove_id in ['31011ade7c0a', 'a596ad0b82aa']:
        if remove_id in no_NaN_series:
            no_NaN_series.remove(remove_id)

    return no_NaN_series

def get_train_series(df_series: str, df_events: str, series_id: str):
    train_series = pd.read_parquet(df_series, filters=[('series_id', '=', series_id)])
    train_events = pd.read_csv(df_events).query('series_id == @series_id')

    train_events = train_events.dropna()
    train_events["step"] = train_events["step"].astype(int)
    train_events["event"] = train_events["event"].replace({"onset": 1, "wakeup": 0})

    train = pd.merge(train_series, train_events[['step', 'event']], on='step', how='left')

    train["event"] = train["event"].bfill(axis='rows')

    train["event"] = train["event"].fillna(1).astype(int)

    return train

def perform_merge_data(df_series: str, df_events: str, series_list, output_dir:str) -> None:
    final_data = []
    for series_id in tqdm.tqdm(series_list, desc="Merging data"):
        df = get_train_series(df_series, df_events, series_id)
        final_data.append(df)
    train_data = pd.concat(final_data).reset_index(drop=True)
    train_data.to_parquet(output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process sleep state detection data.")
    parser.add_argument("--df_series", type=str, help="Path to Train Series parquet data")
    parser.add_argument("--df_events", type=str, help="Path to Train Events CSV data")
    parser.add_argument("--output_dir", type=str, help="Path to Train Events CSV data")

    args = parser.parse_args()

    no_NaN_series = _perform_delete_nan(args.df_events)

    log.info("Performing Data Merging")
    merged_data = perform_merge_data(args.df_series, args.df_events, no_NaN_series, args.output_dir)
    log.info(f"New data saved: {args.output_dir}")