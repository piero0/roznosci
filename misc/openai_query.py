#!/bin/env python3

from openai import OpenAI
import peewee
import datetime
import pathlib
import argparse
import json


class Config:
    def __init__(self):
        pass

    @staticmethod
    def load(filepath):
        configObject = Config()
        with open(filepath, 'r') as file:
            config = json.load(file)
            for key, value in config.items():
                setattr(configObject, key, value)
        return configObject


database = peewee.SqliteDatabase(None)


class ChatCompletion(peewee.Model):
    query = peewee.TextField()
    content = peewee.TextField()
    prompt_tokens = peewee.IntegerField()
    comletion_tokens = peewee.IntegerField()
    model = peewee.TextField()
    creation_date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database


class Client:
    def __init__(self, db_name='chat.db'):
        basePath = pathlib.Path(__file__).parent
        self.config = Config.load(basePath / 'config.json')
        self.client = OpenAI(
            api_key=self.config.api_key,
        )
        database.init(basePath / db_name)
        database.connect()
        if not database.table_exists('chatcompletion'):
            database.create_tables([ChatCompletion])

    def _convert_model(self, model):
        if isinstance(model, int):
            if model == 40:
                return 'gpt-4o'
            elif model == 3:
                return 'gpt-3.5-turbo'
            else:
                return 'gpt-4o-mini'
        return model

    def __del__(self):
        database.close()

    def get_models(self):
        return self.client.models.list()

    def _chat(self, messages, model):
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
        )

    def chat(self, message, model=3):
        model = self._convert_model(model)
        response = self._chat(self._make_message(message), model=model)
        self.save(response, message)
        return response

    def _make_message(self, message):
        return [{'role': 'user', 'content': message}]

    def save(self, response, message):
        completion = ChatCompletion(query=message,
                                    content=response.choices[0].message.content,
                                    prompt_tokens=response.usage.prompt_tokens,
                                    comletion_tokens=response.usage.completion_tokens,
                                    model=response.model)
        completion.save()

    def show_db(self):
        for chat in ChatCompletion.select():
            print(chat.query, chat.content, chat.model, chat.prompt_tokens,
                  chat.comletion_tokens, chat.creation_date)


class CLI:
    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('query', help='query to send to chatGPT')
        parser.add_argument('--model', '-m', type=int, default=4,
                            help='model to use (3,4 or 40). Default: 4')
        parser.add_argument('--tts', '-t', action='store_true')
        args = parser.parse_args()

        start = datetime.datetime.now()
        c = Client('cli.db')
        resp = c.chat(args.query, model=args.model)
        elapsed = datetime.datetime.now() - start

        if len(resp.choices) == 0:
            print('No response')
            return

        if not args.tts:
            print(f'Q: {args.query}')
            print(f'GPT-{args.model} ({elapsed.total_seconds()}s):')
        print(resp.choices[0].message.content)


if __name__ == '__main__':
    args = CLI().run()
