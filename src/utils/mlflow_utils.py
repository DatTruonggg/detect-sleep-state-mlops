import mlflow
from mlflow.tracking.fluent import ActiveRun
from datetime import datetime

from logs import log

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
)
from contextlib import contextmanager

@contextmanager  # type: ignore
def activate_mlflow(
    experiment_name: Optional[str] = None,
    run_id: Optional[str] = None,
    run_name: Optional[str] = None,
    tag: Optional[Dict[str, Any]] = None,
) -> Iterable[mlflow.ActiveRun]:
    set_experiment(experiment_name, tag)

    run: ActiveRun
    with mlflow.start_run(run_name=run_name, run_id=run_id) as run:
        yield run
        
def set_experiment(
    experiment_name: Optional[str] = None, tag: Optional[Dict[str, Any]] = None
) -> None:
    if experiment_name is None:
        experiment_name = "Default"

    try:
        mlflow.create_experiment(name=experiment_name, tags=tag)
    except mlflow.exceptions.RestException:
        pass

    mlflow.set_experiment(experiment_name)
    
def get_client(MLFLOW_TRACKING_URI: str) -> mlflow.MlflowClient:
    return mlflow.MlflowClient(MLFLOW_TRACKING_URI)

def log_model(model_path, model_name):

    mlflow.sklearn.log_model(model_path, model_name)
    log.info(f"🚀 Model '{model_name}' saved in MLflow!")

def generate_run_name_by_date_time() -> str:
    now = datetime.now()

    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")

    run_name = f"{date_str}_{time_str}"
    return run_name