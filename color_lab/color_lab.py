from flask import Flask
from flask import request
import redis
import xlrd
import random
import time
import json



class my_color:
  def __init__(self, color_desc, color_class, l, a, b, R, G, B):
    self.color_desc = color_desc
    self.color_class = color_class
    self.color_l = l
    self.color_a = a
    self.color_b = b
    self.color_R = R
    self.color_G = G
    self.color_B = B
    self.lab = ((l<<16) | (a << 8) | b)
    self.rgb = ((R<<16) | (G << 8) | B)

  def __repr__(self) -> str:
      return ("color_item:  color_desc: {}, color_class: {}, color_l: {}, color_a: {}, color_b: {}, color_R: {}, color_G: {}, color_B: {}, lab: {}, rgb: {}".format(
        self.color_desc, 
        self.color_class, 
        self.color_l, 
        self.color_a, 
        self.color_b, 
        self.color_R, 
        self.color_G, 
        self.color_B, 
        self.lab, 
        self.rgb, 
      ))


# flask
app = Flask(__name__)

# redis connect
redis_conn = redis.Redis(host='0.0.0.0', port=6379)

# all_color_config table
all_color_config = {}
background_config = {}
all_color_list = []
all_color_list_back = []
background_list = []

# 接口1; 返回给客户端唯一标识
@app.route('/init', methods=['GET'])
def router1():
    # redis incry max:uniq:id 返回作为唯一id
    # 生成唯一id
    uid = 0
    key = "max:uniq:id"
    uid = redis_conn.incr(key, "1")
    
    # 初始化都进入模式0
    mode = 0
    key = "user:mode:" + uid
    expire = 60 * 60 * 2  # 2h 后过期
    redis_conn.setnx(key, mode, expire)

    # 当前毫秒时间
    t = time.time()
    time_ms = round(t * 1000)

    # 记录用户初始化操作
    key = "user:operator:" + uid
    filed = "init"
    value = {}
    value["time_ms"] = time_ms
    redis_conn.hset(key, filed, json.dumps(value))
    redis_conn.expire(key, expire)

    # 背景颜色
    background_color = background_list[mode].rgb

    # 回包
    proto_rs = {}
    proto_rs["code"] = 0

    rs = {}
    rs["uid"] = uid
    rs["background_color"] = background_color
    proto_rs["data"] = [rs]

    return proto_rs
    

# 已经准备
@app.route('/ready', methods=['GET'])
def ready():
  # 取用户id
  uid = request.args.get("uid")

  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 背景颜色
  background_color = background_list[mode].rgb
  
  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:" + uid
  filed = "ready_" + mode
  value = {}
  value["time_ms"] = time_ms
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 回包
  proto_rs = {}
  proto_rs["code"] = 0

  rs = {}
  rs["uid"] = uid
  rs["background_color"] = background_color
  proto_rs["data"] = [rs]
  return proto_rs


# 出现目标颜色
@app.route('/show_target_color', methods=['GET'])
def show_target_color():
  # 取用户id
  uid = request.args.get("uid")

  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 根据规则取该给用户显示的颜色
  rule_target_color = 0
  rule_target_color_class = 0
  # 根据模式取当前的完成数
  fini_num = 0
  key = "fini:num:" + fini_num
  fini_num = redis_conn.get(key)
  fini_num = int(fini_num)
  color_list_len = len(all_color_list_back)
  rand_index = int(fini_num) % color_list_len
  rule_target_color = all_color_list_back[rand_index].rgb
  rule_target_color_class = all_color_list_back[rand_index].color_class
  background_color = background_list[mode].rgb


  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:"+uid
  filed = "show_target_color_" + mode
  value = {}
  value["time_ms"] = time_ms
  value["rgb"] = rule_target_color
  value["class"] = rule_target_color_class
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 回包
  proto_rs = {}
  proto_rs["code"] = 0
  #
  rs = {}
  rs["uid"] = uid
  rs["background_color"] = background_color
  rs["color"] = rule_target_color
  proto_rs["data"] = [rs]
  return proto_rs


# 客户端请求返回的随机颜色集合
@app.route('/rand_color_set', methods=['GET'])
def rand_color_set():
  # 取用户id
  uid = request.args.get("uid")

  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 背景颜色
  background_color = background_list[mode].rgb

  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:"+uid
  filed = "show_rand_color_set_" + mode
  value = {}
  value["time_ms"] = time_ms
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 读取配表中的所有颜色返回
  color_item = {}
  color_list = []
  random.shuffle(all_color_list) # 先洗牌
  for item in all_color_list:
    color_item = {}
    color_item["RGB"] = item.rgb
    color_list.append(color_item)


  # 回包
  proto_rs = {}
  proto_rs["code"] = 0
  rs = {}
  rs["uid"] = uid
  rs["background_color"] = background_color
  rs["color_list"] = color_list
  proto_rs["data"] = [rs]
  return proto_rs



# 用户选择颜色
@app.route('/select_color', methods=['GET'])
def select_color():
  # 取用户id 请求信息
  uid = request.args.get("uid")
  color_rgb = request.args.get("rgb")
  color_class = request.args.get("class")

  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 背景颜色
  background_color = background_list[mode].rgb

  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:"+uid
  filed = "select_color_" + mode
  value = {}
  value["time_ms"] = time_ms
  value["rgb"] = color_rgb
  value["class"] = color_class
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 回包
  proto_rs = {}
  proto_rs["code"] = 0
  rs = {}
  rs["uid"] = uid
  rs["background_color"] = background_color
  proto_rs["data"] = [rs]
  return proto_rs


# 显示随机颜色
@app.route('/show_rand_color', methods=['GET'])
def show_rand_color():
  # 取用户id 请求信息
  uid = request.args.get("uid")

  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 检查之前选择的颜色
  last_show_color = 0
  last_show_color_class = 0
  key = "user:operator:"+uid
  filed = "show_target_color_" + mode
  value_json = '{}'
  value_json = redis_conn.hget(key, filed)
  z_value = json.loads(value_json)
  last_show_color = z_value["rgb"]
  last_show_color_class = z_value["class"]

  # 从色系中选择一个颜色
  rand_class_color = 0
  class_color_list = all_color_config[last_show_color_class]
  class_color_list_len = len(class_color_list)
  rand_index = random.randint(0, class_color_list_len)
  rand_class_color = class_color_list[rand_index].rgb

  # 背景颜色
  background_color = background_list[mode].rgb

  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:"+uid
  filed = "show_rand_color_" + mode
  value = {}
  value["time_ms"] = time_ms
  value["rgb"] = rand_class_color
  value["class"] = last_show_color_class
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 回包
  proto_rs = {}
  proto_rs["code"] = 0
  rs = {}
  rs["uid"] = uid
  rs["rgb"] = rand_class_color
  rs["background_color"] = background_color
  proto_rs["data"] = [rs]
  return proto_rs

@app.route('/confirm_color', methods=['GET'])
def confirm_color():
  # 取用户id 请求信息
  uid = request.args.get("uid")
  confirm_color = request.args.get("confirm_color")
  
  # 检查当前所处的模式
  mode = 0
  key = "user:mode:" + uid
  mode = redis_conn.get(key)
  mode = int(mode)

  # 背景颜色
  background_color = background_list[mode].rgb

  # 当前毫秒时间
  t = time.time()
  time_ms = round(t * 1000)

  # 记录用户操作
  key = "user:operator:"+uid
  filed = "confirm_color_" + mode
  value = {}
  value["time_ms"] = time_ms
  value["rgb"] = confirm_color
  expire = 60 * 60 * 2  # 2h 后过期
  redis_conn.hset(key, filed, json.dumps(value))
  redis_conn.expire(key, expire)

  # 记录完成次数
  key = "fini:num:" + mode
  redis_conn.incr(key)

  # 回包
  proto_rs = {}
  proto_rs["code"] = 0
  rs = {}
  rs["uid"] = uid
  rs["background_color"] = background_color
  proto_rs["data"] = [rs]
  return proto_rs



# 模式变更
@app.route('/mode_change', methods=['GET'])
def mode_change():
    # 取用户id
    uid = request.args.get("uniq_id")

    # 模式变更为1
    key = "user:mode:" + uid
    redis_conn.set(key, 1)

    # 回包
    proto_rs = {}
    proto_rs["code"] = 0
    #
    rs = {}
    rs["uid"] = uid
    proto_rs["data"] = [rs]
    return proto_rs




# 解析所有颜色 分类存
def parse_color_table(excel_all_color_sheet):
  all_class_color = {}
  nrow = excel_all_color_sheet.nrows
  for i in range(nrow):
    if i < 2:
      continue
    color_desc = excel_all_color_sheet.cell_value(i, 0)
    color_class = int(excel_all_color_sheet.cell_value(i, 1))
    color_l = int(excel_all_color_sheet.cell_value(i, 2))
    color_a = int(excel_all_color_sheet.cell_value(i, 3))
    color_b = int(excel_all_color_sheet.cell_value(i, 4))
    color_R = int(excel_all_color_sheet.cell_value(i, 6))
    color_G = int(excel_all_color_sheet.cell_value(i, 7))
    color_B = int(excel_all_color_sheet.cell_value(i, 8))
      
    color_item = my_color(color_desc, color_class, color_l, color_a, color_b, 
      color_R, color_G, color_B)

    if color_class in all_class_color.keys():
      all_class_color[color_class].append(color_item)
    else:
      all_class_color[color_class] = [color_item]
  # for k,v in all_class_color.items():
  #   print(len(v))
  return all_class_color


def parse_color_config_table():
  color_lab_config_path = "./lab_color_config.xls"
  ef = xlrd.open_workbook(color_lab_config_path)
  all_color_sheet = ef.sheet_by_name("all_color")
  backgroud_sheet = ef.sheet_by_name("background")
  all_color_config = parse_color_table(all_color_sheet)
  background_config = parse_color_table(backgroud_sheet)
  for k,v in all_color_config.items():
    list_len = len(v)
    for item in v:
      all_color_list.append(item)
      all_color_list_back.append(item)
  for k,v in background_config.items():
    list_len = len(v)
    for item in v:
      background_list.append(item)


# 解析颜色配置表
parse_color_config_table()
# 启动服务
app.run(host="0.0.0.0", port=int("80"))

