# HCI-Final-Project
 
## Usage


~~~bash

# Remember to add your Openai API KEY to the .env_example file and rename it to .env
cd .\chatgpt
python -m pip install -r requirements.txt
python manage.py makemigrations chatapp
python manage.py migrate
python manage.py runserver 

If you encounter error: 指定的裝置未開啟,或無法由 mci 所辨認
This can help: https://blog.csdn.net/weixin_50836014/article/details/122135430
~~~
