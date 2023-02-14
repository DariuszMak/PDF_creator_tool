```bash
python3 -m pip install virtualenv
```

```bash
python3 -m virtualenv venv
```

Setup default local `venv` interpreter in Pycharm

```bash
python3 -m pip install -r requirements.txt
```

Run tests

```bash
pytest .
```


Docker

```bash
docker build -t python-training-excercise .
```

```bash
docker run -dp 5005:5000 -w /app -v "$(pwd):/app" python-training-excercise
```
