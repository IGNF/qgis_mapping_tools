@ECHO OFF

REM save the path:
if not exist tmp.txt echo %PATH%> tmp.txt

set ROOT="C:\Program Files\QGIS WIEN"

call %ROOT%\bin\o4w_env.bat

set PYTHONPATH=%ROOT%\apps\qgis\python;%PYTHONPATH%
set PATH=%ROOT%\bin;%PATH%
set PATH=%ROOT%\apps\qgis\bin;%PATH%
set PYTHONPATH=%ROOT%\apps\qgis\python\plugins;%PYTHONPATH%
set PYTHONPATH=%USERPROFILE%\.qgis2\python\plugins;%PYTHONPATH%
set PYTHONPATH=./;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set QGISDIR=%UserProfile%\.qgis2\python\plugins

set PLUGINNAME=MappingTools

set PY_FILES= ^
	src\mapping_tools.py ^
	src\import_feature.py ^
	src\fusion.py ^
	src\custom_maptool.py ^
	src\__init__.py ^
	src\custom_action.py

set UI_FILES=ui\sourcelayerselector.ui

set EXTRAS=metadata.txt

set COMPILED_RESOURCE_FILES=resources\resources_rc.py

set PLUGIN_UPLOAD=%cd%/plugin_upload.py

if "%1" == "" goto help

if "%1" == "help" (
	:help
	echo.
	echo.Please use `make ^<target^>` where ^<target^> is one of
	echo.
	echo.  compile       to compile resources.
	echo.  deploy        to compile and deploy plugin into qgis plugins directory.
	echo.  test          to lauch tests.
	echo.  dclean        to remove compiled python files of qgis plugins directory.
	echo.  derase        to remove deployed plugin.
	echo.  clean         to remove rcc generated file.
	echo.  zip           to create plugin zip bundle.
	echo.  upload        to upload plugin to Plugin repo ^(TODO !!!^).
	echo.  doc           to auto-generate html doc with sphinx.
	echo.
)

if "%1" == "compile" (
	:compile
	echo.
	echo.------------------------------------------
	echo.Compiling resources.
	echo.------------------------------------------
	rem for %%i in (%UI_FILES%) DO (
	rem pyuic4 -o %%i.py %%i.ui
	rem )
	pyrcc4 -o resources\resources_rc.py resources\resources.qrc
	goto end
)

if "%1" == "deploy" (
	:deploy
	call make compile
	echo.
	echo.------------------------------------------
	echo.Deploying plugin to your .qgis2 directory.
	echo.------------------------------------------
	if not exist %QGISDIR%\%PLUGINNAME% mkdir %QGISDIR%\%PLUGINNAME%
	for %%i in (%PY_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%UI_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%COMPILED_RESOURCE_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%EXTRAS%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	goto end
)

if "%1" == "test" (
	:test
	echo.
	echo.-----------------------------------
	echo.Launching tests.
	echo.-----------------------------------
	rem python test\src\UnitTestsMappingTools.py
	call %ROOT%\bin\qgis-ltr.bat --defaultui --code test\src\testMappingTools.py
	goto end
)

if "%1" == "dclean" (
	:dclean
	echo.
	echo.-----------------------------------
	echo.Removing any compiled python files.
	echo.-----------------------------------
	if exist %QGISDIR%\%PLUGINNAME%\*.pyc del %QGISDIR%\%PLUGINNAME%\*.pyc
	goto end
)

if "%1" == "derase" (
	:derase
	echo.
	echo.-------------------------
	echo.Removing deployed plugin.
	echo.-------------------------
	if exist %QGISDIR%\%PLUGINNAME% rmdir %QGISDIR%\%PLUGINNAME% /s /q
	goto end
)

if "%1" == "clean" (
	:clean
	echo.
	echo.-----------------------------
	echo.Removing rcc generated files.
	echo.-----------------------------
	if exist %COMPILED_RESOURCE_FILES% del %COMPILED_RESOURCE_FILES%
	if exist %UI_FILES%.py del %UI_FILES%.py
	del *.pyc
	goto end
)

if "%1" == "zip" (
	:zip
	call make deploy
	call make dclean
	echo.
	echo.---------------------------
	echo.Creating plugin zip bundle.
	echo.---------------------------
	REM The zip target deploys the plugin and creates a zip file with the deployed
	REM content. You can then upload the zip file on http://plugins.qgis.org
	if exist %PLUGINNAME%.zip del %PLUGINNAME%.zip > nul
	%QGISDIR:~0,2%
	cd %QGISDIR%
	zip -9r %cd%/%PLUGINNAME%.zip %PLUGINNAME% > nul
	%cd:~0,2%
	cd %cd%
	goto end
)

REM TODO: doesn't work, see at plugin_upload.py
if "%1" == "upload" (
	:upload
	call make zip
	echo.
	echo.--------------------------------
	echo.Uploading plugin to Plugin repo.
	echo.--------------------------------
	%PLUGIN_UPLOAD% %PLUGINNAME%.zip
	goto end
)

if "%1" == "doc" (
	:doc
	echo.
	echo.--------------------------------
	echo.Auto-generating html doc.
	echo.--------------------------------
	cd help
	call make html
	cd ..
	goto end
)

:end
if exist tmp.txt for /f "delims=" %%i in (tmp.txt) do set PATH=%%i
if exist tmp.txt del tmp.txt