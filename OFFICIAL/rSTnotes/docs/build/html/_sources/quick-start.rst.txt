.. _header-n3:

快速指南
--------

.. _header-n4:

概念
~~~~

-  标记元素分两种：指令（Directives）和角色（Role），指令是块级元素，像段落一样使用。角色是行内元素，可以写在普通文本之中

-  指令和它要包含的内容之间需要一个空行

-  几组特殊符号：反斜杠 ``\``\ 、反引号、点号 ``.``\ 、冒号 ``:`` 和空格

-  空行、空格和缩进都是有意义的，与 Python 相同，reStructuredText
   讲究对齐缩进

-  每级缩进推荐用 4 个空格

-  块级元素可以用缩进来嵌套，除了标题（标题是一种特殊的块级元素，不能放在缩进的文本中）

-  行内元素虽然有些可以嵌套，但极不推荐

.. _header-n20:

标题
~~~~

-  一级标题在标题文本的第二行使用 ``#`` 标记

-  二级以后标题分别用 ``* + = : -``\ ，通常不需要那么多级

-  标题递进必须按顺序，即一级标题的下一级只能是二级标题

-  原则上标题的标记长度至少与标题等长（指字符长度），也可以超过

.. code:: rst

   一级标题
   #######

   二级标题
   *******

   三级标题
   +++++++

.. _header-n31:

段落
~~~~

-  段落必须使用一个空行加以区分，否则会被折叠到上一行

-  直接换行在渲染之后是不会真正换行的，只会自动增加一个空格

-  在行尾添加反斜杠 ``\`` 可以避免自动添加空格

-  段内换行使用竖线 ``|`` +空格开头（注意竖线后要有空格）

.. code:: rst

   第一个段落。

   第二个段落。

   第三个段落。
   直接换行。\
   添加反斜杠。

   | 第四个段落。
   | 段内换行。
   | 不常用，这种情况使用列表更合适。

.. _header-n42:

列表
~~~~

-  使用星号 ``*`` +空格表明本行是无序列表项，会被渲染为一个圆点

-  同级列表项之间可以空行，不会打断

-  换一个列表符号，列表就会被打断

-  无序列表符号除了星号 ``*`` 外，可以是加号 ``+``\ 、减号 ``-``

-  井号 ``#`` + 点号 ``.`` +
   空格表明本行是有序列表项，会被渲染为数字，且自动递增

-  嵌套列表，第一个子项要与父项相邻，不要空行

-  列表项中可以写段落，只需要缩进对齐，语法是“递归”的

-  最后一个子项或列表段落最后一行要与后面的父项通过空行隔开

-  列表项间插入其他元素会打断列表

-  有序列表除了使用井号 ``#``
   外，也可以使用数字或字母（“手动”序号），记得加上点号 ``.`` 和空格

.. code:: rst

   * 无序第一项
   * 无序第二项

   * 无序第三项
   	* 无序第三项，第一子项

   + 新无序第一项（换列表符号，打断）

   #. 有序第一项
   	#. 有序第一项，第一子项

   #. 有序第二项。
   	列表项写入段落。
   	
   	对齐缩进即可。

   其他元素

   #. 新有序第一项（插其他元素，打断）

   1. 手动序号 1
   2. 手动序号 2

.. _header-n65:

超链接
~~~~~~

-  直接粘贴网址，两端用空格隔开。示例：\ ``https://atomicoo.com``

-  可以用反斜杠 ``\`` 取消两端空格的显示

-  锚文本显示链接需要使用反引号、尖括号 ``<>`` 和下划线
   ``_``\ 。示例：\ :literal:`\`atomicoo.com <https://atomicoo.com>`\_`

-  尖括号包裹网址，反引号包裹转换内容，下划线标志转换为链接，reStructuredText
   中有很多种链接都是以下划线结尾

-  每一级标题都是一个锚，因此可以创建跳转链接，即页内锚文本

-  页内锚文本显示链接需要使用下划线
   ``_``\ 、反引号。示例：\ :literal:`\`这是页内的某个标题`\_`\ ，若标题本身没有空格则反引号可以省略（不建议）

-  因此，超链接最佳实践：\ :literal:`\\ `about link`_\\`

.. code:: rst

   网址超链接：\ https://atomicoo.com\ 

   锚文本超链接：\ `atomicoo.com <https://atomicoo.com>`_\ 

   页内锚文本超链接：\ `快速指南`_\ 

.. _header-n82:

代码
~~~~

-  行内代码使用两对反引号包裹，两端用空格隔开。示例：\ :literal:`\``source code`\``

-  行内标记的嵌套容易造成混乱，建议使用原始文本块（任何标记都不会被转换，随便写）

-  原始文本块使用两个连续的英文 ``::``
   来标记，之后跟空行，内容要缩进，再以空行结束

-  块级代码使用 ``.. code:: language`` 来标记，当不标记程序语言名
   ``language`` 时，\ ``.. code::`` 与原始文本块 ``::`` 是基本一样的

-  语言支持列表：\ `Pygments Supported
   Languages <http://www.bary.com/goto/t/aHR0cDovL3B5Z21lbnRzLm9yZy9sYW5ndWFnZXMv/?title=Pygments+Supported+Languages>`__

-  更多详细用法：\ `Pygments
   Lexers <http://www.bary.com/goto/t/aHR0cDovL3B5Z21lbnRzLm9yZy9kb2NzL2xleGVycy8=/?title=Pygments+Lexers>`__

.. code:: rst

   行内代码：``source code``

   原始文本块：

   ::

   	原始文本块内的任何标记都不会被转换：\ `快速指南`_\ 

   块级代码：

   .. code:: python

       def func():
           print("Hello, World!")

.. _header-n97:

斜体与粗体
~~~~~~~~~~

-  斜体使用一对星号 ``*`` 包裹

-  粗体使用两对星号 ``*`` 包裹

.. code:: rst

   这是*斜体*
   这是**粗体**

.. _header-n104:

引用
~~~~

-  引用纯文本，直接使用原始文本块 ``::`` 即可

-  想在引用里使用 reStructuredText 语法，删除 ``::`` 保留缩进

.. code:: rst

       使用\ **语法**\ 的引用

.. _header-n111:

图片
~~~~

-  图片是块级元素，不能嵌入行内，需要自成段落

-  图片使用 ``.. image::`` 标记，与块级代码语法类似

-  行内图片，譬如表情，需要一些高阶技巧

.. code:: rst

   本地图片：

   .. image:: /path/to/example.jpg

   网络图片：

   .. image:: https://domain.com/path/to/example.jpg

.. _header-n120:

表格
~~~~

-  reStructuredText 提供多种列表实现方法

-  列表表格，通过创建一组嵌套的列表来渲染成表格

-  父项是行，子项是列，每行列数必须一致，不支持合并单元格

-  可以使用 ``:header-rows:`` 为列表表格添加标题行

.. code:: rst

   .. list-table::
   	:header-rows: 1

   	* - h00
   	  - h01
   	  - h02
   	* - a10
   	  - a11
   	  - a12
   	* - 
   	  - a21
   	  - 

.. _header-n131:

彩蛋
~~~~

-  在文档开头或结尾添加以下语句，可以定义一个短字符 ``res`` 用于替换
   ``reStructuredText``\ ，使用时只需 ``|res|`` 即可

.. code:: rst

   .. |rst| replace:: reStructuredText

.. _header-n136:

其他资源
~~~~~~~~

-  `RestructuredText
   primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__

-  `RestructuredText 初级读本 -
   中英文对照 <https://blog.csdn.net/virhuiai/article/details/105833480>`__

-  `reStructuredText on
   SourceForge <http://www.bary.com/goto/t/aHR0cDovL2RvY3V0aWxzLnNvdXJjZWZvcmdlLm5ldC9kb2NzL3JlZi9yc3QvcmVzdHJ1Y3R1cmVkdGV4dC5odG1s/?title=reStructuredText+on+SourceForge>`__

.. _header-n144:
