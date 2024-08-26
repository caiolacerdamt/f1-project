# 🧪 Formula 1 Data Science Project

## Description

This project aims to analyze and visualize Formula 1 data using Python. The goal is to provide telemetry data for drivers in specific races of the current year, details about upcoming races, and driver standings tables. Additionally, the project was created to enhance my data science skills by developing a neural network that predicts the probability of a driver winning the next race based on their performance in recent races.

## Features

- **Telemetry Visualization**: Graphs and analyses of car telemetry, including lap times and sectors.
- **Race Predictions**: Use of neural network models to predict the probability of drivers winning future races.
- **Upcoming Race Information**: Details about upcoming races, including schedules and locations.

## Technologies Used

- **Python**: Main language for data analysis and visualization.
- **pandas** and **numpy**: Data manipulation and analysis.
- **matplotlib**: Data visualization.
- **scikit-learn** and **TensorFlow**: Neural network models.
- **Streamlit**: Web interface development.
- **FastF1**: Library for accessing Formula 1 data.
- **BeautifulSoup** and **Selenium**: Web scraping to collect additional data.

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/caiolacerdamt/f1-project.git
    cd f1-project
    ```

2. **Create a virtual environment** (optional, but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Add the dataset provided at the link:
   [Datasets](https://drive.google.com/drive/folders/1_Zo0denAUHlFhfR09L-rp5VyRm7wUgpH?usp=sharing)
   into a folder named `data` within the project.

2. **Run the web application**:

    ```bash
    streamlit run app.py
    ```

## Project Structure

- `app.py`: Main file for the Streamlit application.
- `model/`: Folder containing the neural network model and the script to retrain the model.
- `data/`: Folder containing CSV files and other data.
- `notebooks/`: Jupyter notebooks for exploration and preliminary analysis.
- `Pages/`: Files containing the functions used in each tab of the application.
- `requirements.txt`: List of project dependencies.

## Usage Examples

https://github.com/user-attachments/assets/e82e6fda-0c4a-46df-a9bd-005f2f64d8b8

## Contributions

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1. **Fork the repository**.
2. **Create a new branch** for your changes.
3. **Commit and send a pull request**.
4. **Open an issue** if you find a bug or have suggestions for improvements.

## License

This project is licensed under the ([LICENSE](https://github.com/caiolacerdamt/f1-project/blob/main/LICENSE.md)). See the `LICENSE` file for more details.

## Contact

Open to feedback and suggestions. If you want to reach out to me, here are the contact channels:

<div align="center">
  <a href="https://www.linkedin.com/in/caiolacerdamt">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="https://instagram.com/caiolmt" target="_blank">
    <img src="https://img.shields.io/badge/-Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram">
  </a>
  <a href="mailto:caiolacerdamt@gmail.com">
    <img src="https://img.shields.io/badge/E-mail-red?style=for-the-badge&logo=mail.ru&logoColor=white" alt="E-mail">
  </a>
</div>
