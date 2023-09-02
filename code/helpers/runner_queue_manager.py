from __future__ import annotations
import json
from time import sleep
from typing import Any

from redis import Redis

from helpers.exceptions import ServerError
from helpers.unwrapper import unwrap
from services.runner.runner import Runner

CHANNEL='manager-channel'

class RunnerQueueManager:
    __shared: RunnerQueueManager | None = None

    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host, port, decode_responses=True)
        self.subscriber = self.redis.pubsub()
        self.subscriber.subscribe(CHANNEL)

    @staticmethod
    def __redis() -> Redis[str]:
        return unwrap(RunnerQueueManager.__shared).redis

    @staticmethod
    def __dict_for(runner: Runner) -> dict[str, Any]:
        current_dict = RunnerQueueManager.__redis().get(runner.language_name)
        if current_dict is None:
            new_dict = {
                'count': 0,
                'current_run': -1
            }
            RunnerQueueManager.__set_value(runner.language_name, new_dict)
            return new_dict
        _json = json.loads(str(current_dict))
        return dict[str, int](_json)

    @staticmethod
    def __set_value(key: str, new_value: dict[str, int]) -> None:
        value = json.dumps(new_value)
        if not RunnerQueueManager.__redis().set(key, value):
            raise ServerError()

    @staticmethod
    def check_container_available(runner: Runner) -> bool:
        current_run = int(RunnerQueueManager.__dict_for(runner)['current_run'])
        return current_run == -1

    @staticmethod
    def set_using_container(runner: Runner) -> None:
        RunnerQueueManager.__set_dict(runner, True)

    @staticmethod
    def __set_dict(runner: Runner, using: bool) -> dict[str, int]:
        value = RunnerQueueManager.__dict_for(runner)
        current_run = -1
        if using:
            value['count'] += 1
            current_run = value['count']
        value['current_run'] = current_run
        RunnerQueueManager.__set_value(runner.language_name, value)
        return value

    @staticmethod
    def __message(runner: Runner, count: int) -> str:
        return f'{runner.language_name}-{count}'

    @staticmethod
    def release_container(runner: Runner) -> None:
        new_dict = RunnerQueueManager.__set_dict(runner, False)
        RunnerQueueManager.__redis().publish(CHANNEL, RunnerQueueManager.__message(runner, new_dict['count']))

    @staticmethod
    def continue_when_available(runner: Runner) -> None:
        while True:
            message = unwrap(RunnerQueueManager.__shared).subscriber.get_message()
            if message is not None and message['data'] == RunnerQueueManager.__message(runner, RunnerQueueManager.__dict_for(runner)['count']):
                break
            sleep(0.01)

    @staticmethod
    def initialize(address: str) -> None:
        if RunnerQueueManager.__shared is not None:
            return
        host, port = address.split(':')
        RunnerQueueManager.__shared = RunnerQueueManager(host, int(port))
