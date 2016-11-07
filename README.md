Automate
==================
Automate是一个数据处理的自动化框架，旨在提供一套快速、灵活、便捷、幂等式的数据处理方案。它不仅提供了常用的数据处理类和函数，也提供了一套命令行式的接口以处理和维护版本内单一、重复、繁琐的任务。

## Introduction
Automate将传统的任务按照如下结构组织起来：

* **bin** 框架提供的命令文件；
* **conf** 每期任务对应的特定参数的配置文件，相当于传统脚本运行时的参数列表；
* **data** 默认数据存储区域，脚本运行时读取及生成的数据默认存放在与之对应的文件夹下；
* **logs** 脚本运行产生的对应的日志文件；
* **tools** 运行时需要的相关工具，通常为二进制或其他语言编写的可执行文件；
* **src** 代码目录：
	* **src/apps** 每一类任务即一个app，也可理解成实现了特定接口的一个（组）脚本；
	* **src/settings.py** 通用配置文件，包含框架运行的核心参数配置，不应修改；
	* **src/settings_local.py** 本地配置文件，包含本地自定义的参数配置，可覆盖通用配置中的配置项；
	* **src/*** 数据处理库和模块。
## Commands
Automate提供了一系列的命令以方便用户对任务进行快速配置和管理：

* **list** 列出所有命令及使用方法；
* **gen_config** 生成配置文件模板，默认调用app对应的*gen_template.py*，如果不存在则拷贝对应的*template.cnf*，如果不存在则拷贝*src/conf/common.cnf*;
* **run** 运行相应app；
* **clean** 清除对应app内或为空或为冗余的配置文件和输出文件；
* **crontab** 设定定时任务（TODO）；
* **utility** 常用工具的命令行式调用（TODO）；
* **branch** app版本管理，便于对不稳定的需求变更进行版本管理（TODO）。

## Libraries
除了方便的命令接口，Automate也提供了对通用功能的抽象和封装：

* **core**
	* **handlers**
		* *decrypt* 加密解密功能；
		* *download* http或ftp方式获取数据；
	* **storage**
		* *database* 提供对sqlserver和MongoDB数据库访问；
		* *smb_proxy* 提供对ftp的访问；
	* **common**
		* *mail* 邮件系统，提供任务完成通知；
		* 
* **utils**
	* *parse* 配置文件解析；
	* *stocking* 出库相关的数据库查询操作；
	* *traverse* 文件遍历；
	* *crop* 图片剪切；
	* *match* 关键字匹配。