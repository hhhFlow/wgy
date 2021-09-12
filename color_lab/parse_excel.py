import xlrd

color_lab_config_path = "./lab_color_config.xls"

ef = xlrd.open_workbook(color_lab_config_path)

all_color_sheet = ef.sheet_by_name("all_color")
backgroud_sheet = ef.sheet_by_name("background")

# print(all_color_sheet.nrows)
# all_color_sheet.row_values()

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
    self.lab = (l<<16 | a << 8 | b)
    self.rgb = (R<<16 | G << 8 | B)

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


# print (all_color_sheet.row_values(2))

# parse_color_table(all_color_sheet)
# print (parse_color_table(backgroud_sheet))

import redis
import json

redis_conn = redis.Redis(host='0.0.0.0', port=6379)
value = {}
value["time"] = 11111

redis_conn.set("hhh", json.dumps(value))

value_json = '{}'
value_json = redis_conn.get("hhh")
z_value = json.loads(value_json)

print(value_json)
print(z_value)