
## 🛠️ How We Built It
Pipeline with Gemini 2.0 flash large language model API leveraged within Google cloud functions triggered through Google Cloud Storage (GCS).
BigQuery used for indexing emails to quickly identify duplicates and learn.
Additional feature - Looker deployed on BigQuery could help analyze requests created and gain valuable insight.

## 🚧 Challenges We Faced
Generating a sizeable dataset with a wide variety of emails and formats.

## 🏃 How to Run
1. Place file into GCS bucket
2. Call function to obtain results for specific email

## 🏗️ Tech Stack
- 🔹 Frontend: NA
- 🔹 Backend: Google Cloud Functions, Google Cloud Storage
- 🔹 Database: BigQuery
- 🔹 Other: Gemini 2.0 Flash Large Language Model

## 👥 Team
- **Pavan Kulkarni**
- **Niraj Singh**
- **Kunal Kishore**
- **Prashant Kumar**
- **Rakesh Kalra**