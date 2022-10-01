import numpy as np
import pickle
from dataclasses import dataclass
from typing import Callable


@dataclass
class Layer:
    """One layer of BugNN"""
    num_inputs: int
    num_outputs: int
    activation: Callable
    weights: np.ndarray
    biases: np.ndarray


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

    @staticmethod
    def random_weights_from_layer_desc(layer_desc):
        num_in, num_out = layer_desc["inputs"], layer_desc["outputs"]
        activation = BugNN.relu if layer_desc["activation"] == "relu" else BugNN.sigmoid
        weight_matrix = 2 * np.random.random((num_out, num_in)) - 1
        bias_matrix = np.random.random(num_out)
        layer = Layer(num_in, num_out, activation,
                      weight_matrix.astype(dtype=np.float32),
                      bias_matrix.astype(dtype=np.float32))
        return layer

    @staticmethod
    def construct_layer(layer, weights, biases):
        pass

    def __init__(self, action_dict=None, architecture=None, seed=22):
        self.action_dict = action_dict if action_dict is not None else BugNN.action_dict
        self.architecture = architecture if architecture is not None else BugNN.architecture
        np.random.seed(seed)
        self.layers = [BugNN.random_weights_from_layer_desc(layer_desc)
                       for layer_desc in self.architecture]

    def forward(self, inputs):
        curr_vector = inputs
        for layer in self.layers:
            w, b, activation = layer.weights, layer.biases, layer.activation
            curr_vector = activation(w @ curr_vector + b)
        return curr_vector

    def get_brain_genome(self):
        """Construct brain genome from weights and biases"""
        weight_list, bias_list = [], []
        for layer in self.layers:
            w, b = layer.weights, layer.biases
            weight_list.extend(list(w.flatten()))
            bias_list.extend(list(b.flatten()))
        return [weight_list, bias_list]

    def set_brain_connections(self, brain_genome):
        """Set weights and biases of brain from brain_genome"""
        curr_index = 0
        for layer in self.layers:
            # get weights from weight_list and put it back in layer
            weight_shape = layer.weights.shape
            num_weights = weight_shape[0] * weight_shape[1]
            weights = brain_genome[curr_index:curr_index+num_weights]
            curr_index += num_weights
            layer.weights = np.asarray(weights).reshape(weight_shape)

        for layer in self.layers:
            # get biases from bias_list and put it back in layer
            bias_shape = layer.biases.shape
            num_biases = bias_shape[0]
            biases = brain_genome[curr_index:curr_index+num_biases]
            curr_index += num_biases
            layer.biases = np.asarray(biases)

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)
