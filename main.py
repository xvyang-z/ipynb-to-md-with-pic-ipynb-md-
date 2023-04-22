base_dir = 'C:/Users/zxy/Desktop/tmp'

ipynb_dir = base_dir + '/ipynb'
md_dir = base_dir + '/md'

import json
import base64
from nbconvert import MarkdownExporter
import nbformat
import os

"""
ipynb_file_path: ipynb文件绝对路径

返回ipynb文件转md的文本数据
"""


def ipynb_to_md(ipynb_file_path):
    with open(ipynb_file_path, encoding='utf-8') as f:
        data = f.read()
    jake_notebook = nbformat.reads(data, as_version=4)

    md_exporter = MarkdownExporter()
    (body, resources) = md_exporter.from_notebook_node(jake_notebook)

    return body


"""
ipynb_file_path: ipynb文件绝对路径

在ipynb文件所在目录下的 `./.assets/文件名.assets/` 下保存图片文件
"""


def ipynb_to_md_with_img(ipynb_file_path: str):
    if not ipynb_file_path.endswith('.ipynb'):
        return

    # 解析文件名和ipynb文件的父目录
    file_name = ipynb_file_path.split('/')[-1].split('.ipynb')[0]

    parent_dir = ipynb_file_path.split(file_name)[0]

    # ipynb 生成的 md文件的目录
    md_dir2 = parent_dir.replace(ipynb_dir, md_dir)
    if not os.path.exists(md_dir2):
        os.makedirs(md_dir2)

    # 等会生成图片的存放目录
    img_dir = md_dir2 + f'.assets/{file_name}.assets/'

    # 读取 ipynb 文件, 变成json对象以便进一步解析
    with open(ipynb_file_path, encoding='utf-8') as f:
        json_obj = json.load(f)

    # ipynb转md, 得到md的文本数据
    md_data = ipynb_to_md(ipynb_file_path)

    # 图片索引, typora以17位格式化时间字符串作图片名, 这里就不用时间了, 直接用17位数字作图片名 '{:0>17}'.format(index)
    img_index = 0

    # 遍历每一个单元格
    # cell_index 是单元格索引, ipynb转md时, 若代码生成了图片, 会命名为如下格式  ![png](output_3_1.png)  其中 3 是单元格索引, 1 是output索引 (均从0开始)
    for cell_index, cell in enumerate(json_obj.get('cells', {})):
        # 单元格分为markdown和code, markdown中可以粘贴图片, code可以输出图片, 这两个是不同的处理逻辑
        if cell['cell_type'] == 'markdown':
            # 遍历该markdown单元格中所有图片
            for img in cell.get('attachments', {}):
                img_name = img
                img_base64_data = cell['attachments'][img_name]['image/png']

                out = base64.b64decode(img_base64_data)

                new_img_name = 'image-{:0>17}.png'.format(img_index)
                img_index += 1

                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)
                # 图片写入指定位置
                with open(img_dir + new_img_name, 'wb') as f:
                    f.write(out)

                # 替换md_data中的图片路径
                md_data = md_data.replace(
                    f"![{img_name}](attachment:{img_name})",
                    f"![{new_img_name.replace('.png', '')}](./.assets/{file_name}.assets/{new_img_name})"
                )

        if cell['cell_type'] == 'code':
            # 遍历该code单元格中所有输出块
            for output_index, output in enumerate(cell.get('outputs', {})):

                # 有的 output 无 data 和 image/png 键
                try:
                    img_base64_data = output['data']['image/png']
                    out = base64.b64decode(img_base64_data)

                    new_img_name = 'image-{:0>17}.png'.format(img_index)
                    img_index += 1

                    if not os.path.exists(img_dir):
                        os.makedirs(img_dir)
                    # 图片写入指定位置
                    with open(img_dir + new_img_name, 'wb') as f:
                        f.write(out)

                    # 替换md_data中的图片路径
                    md_data = md_data.replace(
                        f"![png](output_{cell_index}_{output_index}.png)",
                        f"![{new_img_name.replace('.png', '')}](./.assets/{file_name}.assets/{new_img_name})"
                    )
                except KeyError:
                    ...

    # 将更改后的md_data写入文件
    with open(md_dir2 + f'{file_name}.md', 'w', encoding='utf-8') as f:
        f.write(md_data)


# 递归地遍历ipynb所在文件夹
def main(dir_or_file):
    for i in os.listdir(dir_or_file):
        if i == '.ipynb_checkpoints':
            continue

        i = dir_or_file + '/' + i

        if os.path.isdir(i):
            main(i)
        else:
            ipynb_to_md_with_img(i)


main(ipynb_dir)
