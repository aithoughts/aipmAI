import threading
import time
from typing import Union

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from crewai.utilities.logger import Logger


class RPMController(BaseModel):
    """
    控制每分钟请求数 (RPM) 的类。
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    max_rpm: Union[int, None] = Field(default=None)  # 每分钟最大请求数
    logger: Logger = Field(default=None)  # 日志记录器
    _current_rpm: int = PrivateAttr(default=0)  # 当前分钟内的请求数
    _timer: threading.Timer | None = PrivateAttr(default=None)  # 定时器
    _lock: threading.Lock = PrivateAttr(default=None)  # 线程锁
    _shutdown_flag = False  # 关闭标志

    @model_validator(mode="after")
    def reset_counter(self):
        """
        模型验证后重置请求计数器。
        """
        if self.max_rpm:
            if not self._shutdown_flag:
                self._lock = threading.Lock()
                self._reset_request_count()
        return self

    def check_or_wait(self):
        """
        检查是否允许发送请求，如果达到最大 RPM 则等待。

        :return: 如果允许发送请求则返回 True，否则等待并返回 True。
        """
        if not self.max_rpm:  # 如果未设置最大 RPM，则直接允许
            return True

        with self._lock:
            if self._current_rpm < self.max_rpm:  # 如果当前 RPM 小于最大值
                self._current_rpm += 1  # 增加请求计数
                return True
            else:  # 否则达到最大 RPM
                self.logger.log(
                    "info", "已达到最大 RPM，等待下一分钟开始。"
                )  # 记录日志
                self._wait_for_next_minute()  # 等待下一分钟
                self._current_rpm = 1  # 重置请求计数
                return True

    def stop_rpm_counter(self):
        """
        停止 RPM 计数器。
        """
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _wait_for_next_minute(self):
        """
        等待下一分钟开始。
        """
        time.sleep(60)
        self._current_rpm = 0

    def _reset_request_count(self):
        """
        重置请求计数器。
        """
        with self._lock:
            self._current_rpm = 0
        if self._timer:
            self._shutdown_flag = True
            self._timer.cancel()
        self._timer = threading.Timer(60.0, self._reset_request_count)
        self._timer.start()
