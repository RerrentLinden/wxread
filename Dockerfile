FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置时区为中国时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PATH="/usr/local/bin:${PATH}"

# 复制项目文件
COPY main.py push.py config.py log_utils.py scheduler.py ./

# 安装 Python 依赖
RUN python -m pip install --no-cache-dir \
    'requests>=2.32.3' \
    'urllib3>=2.2.3' \
    'apscheduler>=3.10.4'

# 不写 cron：python:3.10-slim 既没有 /etc/cron.d 也没有 cron 守护进程，
# 这三行会让构建直接失败（cannot create /etc/cron.d/...: Directory nonexistent）。
# 定时由 scheduler.py 用 APScheduler 自己完成，读 CRON_SCHEDULE 环境变量。
# 日志走 stdout/stderr，用 docker logs 查看。

# 启动命令
CMD ["python", "-u", "scheduler.py"]
