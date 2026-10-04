@echo off
cd /d "D:\Pycharm Projects\OrangeHRM_with_Selenium_Python"
call venv\Scripts\activate
pytest -s -v -m "regression" --html=Reports/automation_report.html --self-contained-html --browser="chrome"
pause

rem pytest -s -v --html=Reports/automation_report.html --self-contained-html --browser="chrome"