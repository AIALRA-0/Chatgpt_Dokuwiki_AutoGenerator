版本：v0.1  
bot 模型：official v3  
 
 使用说明: 

1. 编译文件安装缺失依赖  
 
2. 编辑config  
	v3 : 填入你的api 以及 dokuwiki账号  
	v1 : 填入openai账号 或者 session token 以及 dokuwiki账号  
	
 3. 将dokuwiki 默认文件夹 复制到 DokuWikiStick文件夹 (里面应该有俩文件夹，一个server，一个dokuwiki  
 
 4. 打开格式文件夹，输入格式，里面放了格式的参考模板和案例 如果需要默认加载格式请将文件名加入 格式列表.txt  
 
 5. 双击run.bat运行/run_with_cmd为有命令行的运行，用于调试  
 
 6. 其他文件不需要更改  
 
 7. 如果想要调整bot版本请编辑GPT.py, 默认模型在third_party中  
 
 8. 基于项目：https://github.com/acheong08/ChatGPT  
 
 9. 目前v3 仅可用gpt3.5模型，其余端点目前需要修复  
 
 10. 本人代码水平极差，格式混乱，但是目前没空调整，所以请见谅  

 11. 强烈推荐人工二次审核输出页面（而且你自己做的词条不看做了有啥用），某些输出可能需要迭代才能自洽，否则将会严重不收敛
