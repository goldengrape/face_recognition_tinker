
# coding: utf-8

# # 给所有函数修饰
# 
# Numba是一个python的加速器, 最简单的加速方式仅仅是在导入numba以后, 在函数定义之前增加@jit. 
# 
# 本程序是为了测试简单增加或者消除所有函数前@jit

# In[1]:


import os, sys
import glob
import re


# # 打开文件

# In[2]:


def get_file_content(input_filename):
    _,ext=os.path.splitext(input_filename)
    with open(input_filename,'rt') as f_input:
        f_content=f_input.read()
    return ext,f_content


# # 依照模式增加或移除
# 使用了正则表达式```'(\n)(\s*)(def)'```, 因为不能确定def之前的缩进有多少, 只知道肯定之前是由换行的. (当然也有可能什么也不导入, 直接就定义函数的py程序, 但那样也太罕见了了吧)
# 
# 正则表达式还不熟练, 不知道```r'(\n)(\s*)(def)'```找到以后如何用group来拆分. 所以干脆取巧, 反正中间的缩进部分是要重复两遍的, 不妨就先把整体重复两遍, 然后再替换掉其中一个
# 

# In[3]:


def add_pattern(text,prefix,target_word,add_string):
    target_pattern=re.compile(prefix+target_word)    
    def add_core(m):
        s=m.group()
        new=s+'\n'+s
        return (re.sub(target_word+'\n',add_string,new))
    return (target_pattern.sub(add_core,text))

def remove_pattern(text,prefix,target_word):
    target_pattern=re.compile(prefix+target_word)
    def remove_core(m):
        s=m.group()
        return ""
    return (target_pattern.sub(remove_core,text))



# # 增加/去除@jit
# 
# * add_jit: 在每一个def之前添加@git
# * remove_jit: 将每个单行的@jit去除

# In[4]:


def add_jit(text,ext):
    if ext=='.py':
        prefix='(\n)(\s*)'
        add_numba='from numba import jit'
        add_numba_jit='@jit'
    elif ext=='.ipynb':
        prefix='(\n)(\s*)(\")(\s*)'
        add_numba='from numba import jit", '
        add_numba_jit='@jit", '
        
    text = add_pattern(text,prefix,'import numpy as np',add_numba)
    text = add_pattern(text,prefix,'def',add_numba_jit)
    text = text.replace('jit"','jit\\n"') #此处用re.sub总是会把\n给翻译掉, 试过多种方式
    return text

def remove_jit(text,ext):
    if ext=='.py':
        prefix='(\n)(\s*)'
        add_numba='from numba import jit'
        add_numba_jit='@jit'
    elif ext=='.ipynb':
        prefix='(\s*)'
        add_numba='from numba import jit'
        add_numba_jit='@jit'

    text = remove_pattern(text,prefix,add_numba)
    text = remove_pattern(text,prefix,add_numba_jit)
    return text

# jit_added  =add_jit(f_content)
# jit_removed=remove_jit(f_content)


# # 写入文件

# In[5]:


def write_content(output_filename,f_content):
    with open(output_filename,'wt') as f_output:
        f_output.write(f_content)
    return True


# # 整合包装

# In[6]:


def decorate_with_jit(input_filename,output_filename,marker):
    ext,f_content=get_file_content(input_filename)
    if marker=='--a':
        f_content = add_jit(f_content, ext)
    elif marker=='--r':
        f_content = remove_jit(f_content,ext)   
    write_content(output_filename,f_content)
    print("{}\t->\t{}".format(input_filename, output_filename))


# # 参数调用

# In[7]:


if __name__=="__main__":
    argv1=sys.argv[1]
    argv2=sys.argv[2]
    argv3=sys.argv[3]
#     argv1='--a'
#     argv2="allipynb"
#     argv3="numba"

    marker=argv1
    input_filename=argv2
    
    parameters={"allpy":   "*.py",
                "allipynb":"*.ipynb"
               }
    if input_filename=="allpy" or input_filename=="allipynb":
        input_filelist=glob.glob(parameters[input_filename])
        output_path=argv3
        os.makedirs(output_path, exist_ok=True)

        output_filelist=[os.path.join(output_path,f) for f in input_filelist]
        for (i,o) in zip(input_filelist,output_filelist):
            decorate_with_jit(i,o,marker)
    else:
        output_filename=argv3
        decorate_with_jit(input_filename,output_filename,marker)

