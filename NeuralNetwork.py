import numpy as np
import pickle


class BugNN:
    architecture = [
        {"inputs": 6, "outputs": 6, "activation": "relu"},
        {"inputs": 6, "outputs": 5, "activation": "sigmoid"}
    ]
    action_dict = {
        0: "left",
        1: "straight",
        2: "right",
        3: "eat"
    }
    @staticmethod
    def relu(x):
        return np.where(x < 0, 0, x)

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1 + np.exp(-x))

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)

    def __init__(self, action_dict=None, architecture=None, seed=22):
        self.action_dict = action_dict if action_dict is not None else BugNN.action_dict
        self.architecture = architecture if architecture is not None else BugNN.architecture
        np.random.seed(seed)
        self.layers = [self.weights_from_layer(layer) for layer in self.architecture]

    def weights_from_layer(self, layer):
        num_in, num_out = layer["inputs"], layer["outputs"]
        activation = BugNN.relu if layer["activation"] == "relu" else BugNN.sigmoid
        weight_matrix = np.random.random((num_out, num_in)) - 0.5
        bias_matrix = np.random.random(num_out)
        return weight_matrix, bias_matrix, activation

    def forward(self, inputs):
        curr_vector = inputs
        for layer in self.layers:
            w, b, activation = layer
            curr_vector = activation(w @ curr_vector + b)
        return curr_vector

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)
