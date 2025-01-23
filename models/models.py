from keras import models
import mediapipe as mp


def tiny_model():
    return models.load_model('models/tiny_model.h5')


def amazing_model():
    return models.load_model('models/amazing_model.h5')


def localizer_model():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    return hands