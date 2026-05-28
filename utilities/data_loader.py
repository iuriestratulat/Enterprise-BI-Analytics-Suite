import streamlit as st
import polars as pl
from google.oauth2 import service_account
from google.cloud import storage
import io
import json

def get_gcs_client():
    """Autentifică securizat aplicația folosind string-ul JSON din Streamlit Secrets."""
    # Citim string-ul JSON stocat sub json_key
    json_string = st.secrets["gcs_credentials"]["json_key"]
    
    # Îl convertim într-un dicționar Python nativ
    creds_dict = json.loads(json_string)
    
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    return storage.Client(credentials=credentials, project=creds_dict.get("project_id"))

def load_parquet_from_gcs(file_name: str) -> pl.DataFrame:
    """Descarcă un fișier Parquet direct din bucket-ul privat GCS în memoria Polars."""
    bucket_name = "stratulat-bi-data-storage"
    
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Descarcă fișierul direct în bytes (în memorie) pentru viteză maximă
        data_bytes = blob.download_as_bytes()
        
        # Polars citește uluitor de rapid direct din buffer-ul de memorie
        return pl.read_parquet(io.BytesIO(data_bytes))
    except Exception as e:
        st.error(f"Eroare la încărcarea fișierului {file_name} din Cloud Storage: {e}")
        raise e