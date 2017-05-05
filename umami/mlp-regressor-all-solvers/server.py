"""Host a server to hold the local library and replay data in memory.

Reading the LocalLibrary and replay data dominates the runtime of the task so
this dramatically speeds up the hyperparameter optimization.

"""
from datetime import timedelta

import flask
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from slider import LocalLibrary
from slider.model import train_model, extract_from_replay_directory
from slider.model.model import MLPRegressor


features, accuracy = extract_from_replay_directory(
    '../../data/replays',
    LocalLibrary('../../data/maps'),
    age=timedelta(days=365 // 2),
)


app = flask.Flask(__name__)


@app.route('/mse')
def mse():
    train_features, test_features, train_acc, test_acc = train_test_split(
        features,
        accuracy,
    )

    model = MLPRegressor(
        alpha=float(flask.request.args['alpha']),
        hidden_layer_sizes=list(map(
            int,
            flask.request.args.getlist('hidden_layer_sizes'),
        )),
        solver=flask.request.args['solver'],
        activation=flask.request.args['activation'],
    )

    model = train_model(train_features, train_acc, model=model)
    return str(mean_squared_error(test_acc, model.predict(test_features)))