# Project Guide: Real-Time Ride-Hailing Platform

This document provides a clear, step-by-step guide to completing this data streaming project.

---

## 🎯 Project Objective

Develop a real-time data platform that ingests trip data, calculates costs, and loads the results into a live dashboard (Kibana) and an analytics data warehouse (BigQuery) for machine learning.

---

## 🛠️ Tech Stack

* **Orchestration:** Apache Airflow
* **Messaging:** Apache Kafka
* **Real-Time Dashboard:** Elasticsearch & Kibana
* **Analytics Warehouse:** Google Cloud Platform (GCS & BigQuery)
* **Core Logic:** Python
* **Local Environment:** Docker

---

## 📋 Main Steps

### **Step 1: Data Ingestion (Producer -> Kafka)**

* **Goal:** Simulate trip requests by sending JSON messages to Kafka.
* **Action:** Run the `producer.py` script.
* **Input Data Model:** The script reads from `data_projet.json`, which has the required nested structure.
* **Source Topic:** `topic_source`

### **Step 2: Data Enrichment (Airflow DAG 1)**

* **Goal:** Consume raw data, calculate trip distance and cost, and publish the result.
* **Architecture:** `ConsumKafka` -> `ComputCostTravel` -> `PublishKafka`.
* **Action:** Trigger the `dag_1_trip_processing` DAG in Airflow.
* **`ComputCostTravel` Logic:**
    1.  Calculate the distance in kilometers between client and driver coordinates.
    2.  Calculate `prix_travel` = `distance` * `prix_base_per_km`.
    3.  Add `distance` and `prix_travel` fields to the message.
* **Output Data Model:** The enriched JSON message as shown in the project slide.
* **Destination Topic:** `topic_result`

### **Step 3: Data Loading (Airflow DAG 2)**

* **Goal:** Consume enriched data and load it into Elasticsearch and Google Cloud Storage (GCS).
* **Architecture:** `ConsumKafka` -> `TransformJson` -> (`PutElasticSearch`, `PutGCP`).
* **Action:** Trigger the `dag_2_load_data` DAG in Airflow.
* **`TransformJson` Logic:**
    1.  Flatten the nested JSON structure.
    2.  Add an `agent_timestamp` field with the current UTC time.
* **Output Data Model:** A flat JSON object.
* **Destinations:**
    * **Elasticsearch:** The flattened JSON is indexed.
    * **GCS:** The flattened JSON is saved as a file in your bucket.

### **Step 4: Real-Time Visualization (Kibana)**

* **Goal:** Create a dashboard to visualize the live trip data from Elasticsearch.
* **Action:** In Kibana, build a dashboard containing:
    1.  A horizontal bar chart showing the sum of `prix_travel` for each `confort` type.
    2.  A map visualization plotting the `locationClient` of the trips.
* **Requirement:** The dashboard must match the project slide.

### **Step 5: Advanced Analytics (BigQuery ML)**

* **Goal:** Analyze the GCS data and apply a machine learning model.
* **Requirement Checklist:**
    1.  **Create an External Table:** In BigQuery, create a table that points to the JSON files in your GCS bucket.
    2.  **Train a Model:** Use the provided `uber-split2.csv` file to train a K-Means model with 8 clusters based on latitude and longitude.
    3.  **Run Analytical Query:** Write and execute a SQL query that joins the live data from the external table with the ML model's predictions to calculate the total `chiffre d'affaire` (revenue) for each cluster and each comfort type.

### **Step 6: Architecture Proposal (Documentation)**

* **Goal:** Propose a production-ready architecture for the Kafka cluster.
* **Action:** Create a document that specifies and justifies:
    1.  Number of Brokers (e.g., 3 for high availability).
    2.  Disk space per Broker (based on estimated data volume).
    3.  Number of partitions for each topic (based on parallelism needs).
    4.  Monitoring tools (e.g., Prometheus/Grafana).
* **Requirement:** Address all four points from the project slide.