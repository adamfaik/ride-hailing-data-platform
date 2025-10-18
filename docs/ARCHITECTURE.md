# Kafka Architecture Proposal

This document outlines the proposed architecture for a production-ready Kafka cluster to support the real-time ride-hailing data platform.

---

## 1. Number of Brokers

* **Proposal:** **3 Brokers**
* **Justification:** A 3-broker cluster is the industry-standard minimum for achieving high availability and fault tolerance. This setup allows us to use a replication factor of 3 for critical topics, meaning the cluster can withstand the complete failure of one broker without data loss or service interruption.
    * **Single Broker:** A single point of failure.
    * **Two Brokers:** Prone to "split-brain" issues during leader election.
    * **Three Brokers:** Provides a robust and resilient foundation.

---

## 2. Disk Space per Broker

* **Proposal:** **50 GB of fast SSD storage per broker**.
* **Justification:** The required disk space can be estimated using the following formula:

    `(Avg. Message Size) x (Messages per Day) x (Retention Period) x (Replication Factor)`

    #### Assumptions:
    * **Avg. Message Size:** 2 KB (our JSON messages are lightweight).
    * **Messages per Day:** 1,000,000 (simulating a moderately busy service).
    * **Retention Period:** 7 days (a standard default for real-time data).
    * **Replication Factor:** 3 (to align with our 3-broker setup).

    #### Calculation:
    ```
    2 KB * 1,000,000 * 7 * 3 = 42,000,000 KB
    42,000,000 KB ≈ 42 GB
    ```
    The total required storage is approximately **42 GB**. Allocating **50 GB per broker** provides sufficient headroom for OS overhead, Kafka's own logs, and future data growth.

---

## 3. Number of Partitions per Topic

* **Proposal:**
    * `topic_source`: **3 partitions**
    * `topic_result`: **6 partitions**
* **Justification:** Partitions are the primary unit of parallelism in Kafka. The number should be determined by the expected consumer throughput.
    * **`topic_source` (3 partitions):** This allows our initial processing DAG (`dag_1_trip_processing`) to scale up to 3 parallel consumer tasks if ingestion volume increases.
    * **`topic_result` (6 partitions):** This is a critical "fan-out" topic. A higher partition count (greater than the number of brokers) provides greater flexibility for future consumers. It allows multiple downstream applications (our `dag_2_load_data` and potentially others) to consume data in parallel without creating bottlenecks.

---

## 4. Monitoring Tools

* **Proposal:** A monitoring stack composed of **Prometheus, Grafana, and Alertmanager**.
* **Justification:** This is the most widely adopted and powerful open-source solution for monitoring systems like Kafka.
    * **Prometheus:** A time-series database that will scrape and store key operational metrics from the Kafka brokers via a **Kafka Exporter**. Key metrics include message throughput, consumer lag, and broker health.
    * **Grafana:** A visualization tool that will connect to Prometheus to create real-time dashboards. These dashboards will give us an at-a-glance view of the cluster's health and performance.
    * **Alertmanager:** A component of the Prometheus ecosystem that will be configured to send automated alerts (e.g., via Slack or email) if critical thresholds are breached, such as a broker going offline or consumer lag exceeding a predefined limit.