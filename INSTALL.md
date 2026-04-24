# Installation Guide

Follow these steps to set up the AI-Based Intelligent Database Query Optimization System on your local machine.

## Prerequisites
* Python 3.8 or higher installed on your system.
* Git installed on your system.

## Step 1: Clone the Repository
Open your terminal or command prompt and run:
`git clone https://github.com/[YourUsername]/intelligent-db-optimizer.git`
`cd intelligent-db-optimizer`

## Step 2: Create a Virtual Environment (Recommended)
It is best practice to run this in an isolated environment.

**On Windows:**
`python -m venv venv`
`venv\Scripts\activate`

**On macOS/Linux:**
`python3 -m venv venv`
`source venv/bin/activate`

## Step 3: Install Dependencies
The project relies on scikit-learn for the machine learning model and numpy/pandas for data handling.
`pip install scikit-learn numpy pandas`

## Step 4: Train the Initial Model
Before running predictions, you must train the model using the provided query logs to generate the model.pkl file.
`python train_model.py`

## Step 5: Verify Installation
Run the interactive CLI to ensure everything is working correctly:
`python main.py`