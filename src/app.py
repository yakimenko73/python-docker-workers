import multiprocessing

from src import db, init_app
from src.worker import WorkersManager

if __name__ == '__main__':
    app = init_app()
    db.init(app.config['TESTING'])

    worker = WorkersManager()
    process = multiprocessing.Process(target=worker.start)
    process.start()

    app.run()
