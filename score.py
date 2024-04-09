def calculate_score(input_text, loaded_model, threshold=0.5):
    pred_proba = loaded_model.predict_proba([input_text])[0, 1]

    assert type(input_text) == str
    assert ((type(threshold) == float) or type(threshold) == int) and (0 <= threshold <= 1)

    if pred_proba >= threshold:
        prediction = 1
    else:
        prediction = 0

    return prediction, pred_proba
