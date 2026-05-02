# HR Chatbot

This is an HR FAQ chatbot built with RASA, Streamlit, and MySQL.

## Setup

1. Install dependencies: `pip install rasa rasa-sdk streamlit mysql-connector-python PyPDF2`

2. Extract handbook text: Run `python extract_pdf.py` (already done)

3. Train model: `rasa train`

## Running

1. Start actions server: `rasa run actions`

2. Start RASA server: `rasa run --enable-api`

3. Start UI: `streamlit run streamlit_app.py`

## Features

- Handbook-driven section selection UI
- No free-form user query input required
- Shows a short, simple 5-line summary for each section
- After the summary, a small ERP issue form appears for top attendance, salary, and leave cases
- Covers common issues like missed punch out, salary not credited, and missed leave application
- Collects feedback after every section view

## Knowledge Base

Extracted from "Orchids Handbook- Regular 10062023 (1).pdf"