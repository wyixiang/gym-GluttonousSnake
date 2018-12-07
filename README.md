#gym-GluttonousSnake
本项目基于daishengdong的[Games游戏包](https://github.com/daishengdong/Games)中的GluttonousSnake

我们使用gym环境对贪吃蛇游戏进行了封装和重新开发，目前已经开发完成三个项目：
 - Glu-v0 传统贪吃蛇
 - Glu-v1 贪吃蛇大作战（四向移动版）
 - Glu-v2 贪吃蛇大作战（360°移动版）

## Requirements

 - python3
 - keras
 - gym
 - pygame


## Install
```bash
cd ~/gym-GluttonousSnake
pip3 install -e .
```

## Run

```bash
cd ~/gym-GluttonousSnake/example
```
传统贪吃蛇
```bash
python3 rand.py
```
贪吃蛇大作战简版
```bash
python3 multi_rand.py
```
贪吃蛇大作战完全版
```bash
python3 multi2_rand.py
```


## 更新日志

### 20181207
1.增加了新的环境——贪吃蛇大作战完全版(Glu-v2)  
2.优化了Glu-v1的代码架构，提升代码的稳定性  
3.新环境中蛇头更加拟真化，蛇节改为圆形    
4.按惯例推出了Glu-v2的原始代码和测试文件multi2_rand.py

### 20181205 
1.增加了新的环境——贪吃蛇大作战  
2.修复原环境中图片帧慢一个回合的bug  
3.移除之前环境中的get_step()方法，采用环境自动计数  
4.添加针对两种环境的随机（手动）策略，以便于测试环境，默认为手动操作  
5.添加未封装的原始游戏文件（在game文件夹）  
6.移除原环境中的img属性