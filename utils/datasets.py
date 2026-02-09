# Predefined Datasets Configuration
# In a real production system, 'files' would point to S3 URLs or local paths.
# Since we are running a bot, we can use public URLs that the bot will fetch and forward.

DATASETS = {
    "MLParest": {
        "description": "MLParest: A comprehensive dataset for Multi-Layer Perceptron research...",
        "files": [
            {"name": "train.csv", "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv", "type": "document"}, # Placeholder URL
            {"name": "test.csv", "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv", "type": "document"}, # Placeholder URL
            {"name": "README.md", "url": "https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/README.rst", "type": "document"} # Placeholder URL
        ]
    },
    "Titanic": {
        "description": "Titanic: Machine Learning from Disaster",
        "files": [
            {"name": "train.csv", "url": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv", "type": "document"}
        ]
    }
}
