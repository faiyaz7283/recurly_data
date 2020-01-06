# Get the latest python3 alpine image
FROM python:3-alpine

# Install curl, git
RUN apk add curl git

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Add poetry to your PATH
ENV PATH="/root/.poetry/bin:$PATH"

# Install project
RUN git clone https://github.com/faiyaz7283/recurly_data.git

# Change working directory
WORKDIR /recurly_data

# Install package dependencies
RUN poetry install

# Run as an executable
ENTRYPOINT ["poetry", "run", "python", "-m", "recurly_data"] 
