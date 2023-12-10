install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

# Local training of the model
localtrain:
    python3 modeling/local_classification_model_exp.py