@ECHO OFF

REM save the path:
if not exist tmp.txt echo %PATH%> tmp.txt

call c:\OSGeo4W\bin\o4w_env.bat

set PYTHONPATH=C:\OSGeo4W\apps\qgis\python;%PYTHONPATH%
set PATH=C:\OSGeo4W\bin;%PATH%
set PATH=C:\OSGeo4W\apps\qgis\bin;%PATH%
set PYTHONPATH=C:\OSGeo4W\apps\qgis\python\plugins;%PYTHONPATH%
set PYTHONPATH=%USERPROFILE%\.qgis2\python\plugins;%PYTHONPATH%
set PYTHONPATH=./;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set QGISDIR=%UserProfile%\.qgis2\python\plugins

set PLUGINNAME=MappingTools

set PY_FILES= ^
	mapping_tools.py ^
	import_feature.py ^
	fusion.py ^
	common.py ^
	__init__.py

set UI_FILES=

set EXTRAS=metadata.txt

set COMPILED_RESOURCE_FILES=resources_rc.py

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
	echo.
)

if "%1" == "compile" (
	:compile
	echo.
	echo.------------------------------------------
	echo.Compiling resources.
	echo.------------------------------------------
	rem pyuic4 -o outil_nomade_dialog.py  outil_nomade_dialog_base.ui
	pyrcc4 -o resources_rc.py resources.qrc
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
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q
	)
	for %%i in (%UI_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q
	)
	for %%i in (%COMPILED_RESOURCE_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q
	)
	for %%i in (%EXTRAS%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q 
	)
	goto end
)

if "%1" == "test" (
	:test
	echo.
	echo.-----------------------------------
	echo.Launching tests.
	echo.-----------------------------------
	python test\src\testFusion.py
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
	echo.
	echo.-----------------------------
	echo.Removing rcc generated files.
	echo.-----------------------------
	if exist %COMPILED_RESOURCE_FILES% del %COMPILED_RESOURCE_FILES%
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

:end
REM if exist tmp.txt for /f "delims=" %%i in (tmp.txt) do set PATH=%%i
REM if exist tmp.txt del tmp.txt