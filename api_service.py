{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 0,
   "metadata": {
    "application/vnd.databricks.v1+cell": {
     "cellMetadata": {
      "byteLimit": 2048000,
      "rowLimit": 10000
     },
     "inputWidgets": {},
     "nuid": "23e400e1-e033-4b10-abf9-27b2a69566b8",
     "showTitle": false,
     "tableResultSettingsMap": {},
     "title": ""
    }
   },
   "outputs": [
    {
     "output_type": "stream",
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Error loading model: Method 'get_latest_versions' is unsupported for models in the Unity Catalog. Detected attempt to load latest model version in stages ['Production']. You may see this error because:\n1) You're attempting to load a model version by stage. Setting stages and loading model versions by stage is unsupported in Unity Catalog. Instead, use aliases for flexible model deployment. See https://mlflow.org/docs/latest/model-registry.html#deploy-and-organize-models-with-aliases-and-tags for details.\n2) You're attempting to load a model version by alias. Use syntax 'models:/your_model_name@your_alias_name'\n3) You're attempting load a model version by version number. Verify that the version number is a valid integer\n"
     ]
    }
   ],
   "source": [
    "# Save this file as 'api_service.py' in your Databricks environment\n",
    "\n",
    "import mlflow\n",
    "import uvicorn\n",
    "from fastapi import FastAPI\n",
    "from pydantic import BaseModel\n",
    "import pandas as pd\n",
    "\n",
    "# Define the Pydantic model for the request body\n",
    "class InputData(BaseModel):\n",
    "    gender: str\n",
    "    age: int\n",
    "    category: str\n",
    "    quantity: int\n",
    "    price: float\n",
    "\n",
    "# Initialize the FastAPI app\n",
    "app = FastAPI()\n",
    "\n",
    "# --- Load the model from MLflow Model Registry ---\n",
    "# Replace 'Customer_Segmentation_Model' with your registered model name\n",
    "# Replace 'Production' with the stage you want to use (e.g., 'Staging', 'Production')\n",
    "model_name = \"Customer_Segmentation_Model\"\n",
    "model_stage = \"Production\"\n",
    "logged_model = f\"models:/{model_name}/{model_stage}\"\n",
    "try:\n",
    "    model = mlflow.pyfunc.load_model(logged_model)\n",
    "    print(f\"Model {model_name} from stage {model_stage} loaded successfully.\")\n",
    "except Exception as e:\n",
    "    print(f\"Error loading model: {e}\")\n",
    "    model = None # Set to None to handle errors in the endpoint\n",
    "\n",
    "@app.post(\"/predict\")\n",
    "def predict(data: InputData):\n",
    "    \"\"\"\n",
    "    Predicts total revenue based on input features.\n",
    "    \"\"\"\n",
    "    if model is None:\n",
    "        return {\"error\": \"Model not loaded.\"}\n",
    "\n",
    "    # Convert the input data to a pandas DataFrame\n",
    "    input_df = pd.DataFrame([data.dict()])\n",
    "\n",
    "    # Get the model's prediction\n",
    "    prediction = model.predict(input_df)[0]\n",
    "\n",
    "    return {\"predicted_revenue\": prediction}\n",
    "\n",
    "# To run the API, you would execute this command in a terminal or a Databricks Job\n",
    "# uvicorn api_service:app --host 0.0.0.0 --port 8000"
   ]
  }
 ],
 "metadata": {
  "application/vnd.databricks.v1+notebook": {
   "computePreferences": null,
   "dashboards": [],
   "environmentMetadata": {
    "base_environment": "",
    "environment_version": "3"
   },
   "inputWidgetPreferences": null,
   "language": "python",
   "notebookMetadata": {
    "pythonIndentUnit": 4
   },
   "notebookName": "api_service",
   "widgets": {}
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}