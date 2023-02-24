import multiprocessing

import app
from app import database
from app.worker import Worker

if __name__ == '__main__':
    app = app.create_app()
    database.init_database(app.config['TESTING'])

    worker = Worker()
    process = multiprocessing.Process(target=worker.start)
    process.start()

    app.run()
