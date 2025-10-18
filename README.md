# Real-Time Ride-Hailing Data Platform

This repository contains the source code for a complete, end-to-end data engineering project that builds a real-time ride-hailing data platform. The system ingests trip requests, calculates costs, and fans out the data to two destinations: an Elasticsearch cluster for live visualization and Google Cloud Platform for advanced analytics.

---

## 🏛️ Architecture

The platform uses a modern, streaming-first architecture orchestrated by Apache Airflow. Data flows through the system in a series of orchestrated steps managed by two distinct DAGs.



1.  **Ingestion:** A standalone Python producer (`producer.py`) simulates trip requests and sends them to a Kafka topic (`topic_source`).
2.  **Enrichment (DAG 1):** The `dag_1_trip_processing` DAG consumes raw trip data, calculates the distance and cost (`ComputCostTravel`), and publishes the enriched message to `topic_result`.
3.  **Loading (DAG 2):** The `dag_2_load_data` DAG consumes the enriched data and fans it out to two sinks:
    * **Real-Time Sink:** Data is transformed (`TransformJson`) and indexed into Elasticsearch for visualization.
    * **Analytics Sink:** Data is sent to Google Cloud Storage (GCS) to serve as a data lake for BigQuery.
4.  **Analytics & ML:** BigQuery uses an external table over the GCS data and a pre-trained K-Means model to run real-time analytical queries.

---

## 🛠️ Tech Stack

* **Orchestration:** Apache Airflow
* **Messaging System:** Apache Kafka
* **Real-Time Search & Visualization:** Elasticsearch & Kibana
* **Cloud & Analytics:** Google Cloud Platform (GCS, BigQuery, BigQuery ML)
* **Core Language:** Python
* **Containerization:** Docker & Docker Compose

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.9+
* Docker Desktop
* A Google Cloud Platform (GCP) project with a configured service account key (`gcp-credentials.json`).

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/adamfaik/ride-hailing-data-platform.git](https://github.com/adamfaik/ride-hailing-data-platform.git)
    cd ride-hailing-data-platform
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start Local Services (Kafka, Elasticsearch, Kibana):**
    ```bash
    docker-compose up -d
    ```

5.  **Set up Airflow:**
    * Initialize and start Airflow using the standalone command:
        ```bash
        airflow standalone
        ```
    * Update the `dags_folder` in your `~/airflow/airflow.cfg` to point to the `dags` folder in this project, then restart `airflow standalone`.

---

## ▶️ How to Run the Pipeline

1.  **Create Kafka Topics:** Run these commands in your terminal to create the necessary topics.
    ```bash
    docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic topic_source --partitions 1 --replication-factor 1
    docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic topic_result --partitions 1 --replication-factor 1
    ```

2.  **Start the Producer:** In a new terminal, start the Python script to begin sending data.
    ```bash
    python3 producer.py
    ```

3.  **Trigger the DAGs:** In the Airflow UI (`http://localhost:8080`) or via the CLI, trigger the DAGs in order:
    * First, trigger `dag_1_trip_processing`.
    * Wait for it to complete, then trigger `dag_2_load_data`.

4.  **Verify the Results:**
    * Check your **Kibana dashboard** (`http://localhost:5601`) to see the new data.
    * Check your **GCS bucket** to see the new JSON file.
    * Run your saved analytical query in **BigQuery** to see the updated revenue report.