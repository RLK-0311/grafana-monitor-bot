from src.config_loader import ConfigLoader

loader = ConfigLoader()

config = loader.load_all()

print(config)
