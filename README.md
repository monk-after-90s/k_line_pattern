# 形态匹配记录

每当K线更新，计算一遍各symbol各K线Interval的形态匹配，以供项目alpha_rabbit_server查询使用。

程序启动后，对历史K线的形态匹配计算、存储和实时的形态匹配计算、存储同时进行。只要傻瓜化地启动项目，就能维护好历史和实时形态匹配记录。

[config.py](config.py)记录了数据库配置和匹配的周期，具体symbol的配置
在quant库里的dbbaroverview里。