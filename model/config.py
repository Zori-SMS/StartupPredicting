class Config:
    def __init__(self, batch_size=1024, input_size=31, max_length=4, hidden_size=100, static_size = 5):
        self.batch_size = batch_size
        self.input_size = input_size
        self.max_length = max_length
        self.hidden_size = hidden_size
        self.static_size = static_size