from app import app
from config import config

if __name__ == '__main__':
	app.run(host=config.HOST, port=config.PORT)
