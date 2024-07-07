class AppContext:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppContext, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, bot, dynamo_table, dynamo_client, dynamo_storage, dispatcher_tg):
        if not self._initialized:
            self.bot = bot
            self.dynamo_table = dynamo_table
            self.dynamo_client = dynamo_client
            self.dynamo_storage = dynamo_storage
            self.dispatcher_tg = dispatcher_tg
            self._initialized = True

    def get_bot(self):
        return self.bot

    def get_dynamo_table(self):
        return self.dynamo_table

    def get_dynamo_client(self):
        return self.dynamo_client

    def get_dynamo_storage(self):
        return self.dynamo_storage

    def get_dispatcher_tg(self):
        return self.dispatcher_tg
