@ECHO OFF

set QGISDIR=%UserProfile%\.qgis2\python\plugins

set PLUGINNAME=MappingTools

set PY_FILES=__init__.py mapping_tools.py

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
	echo.  test          to checkout test dataset ^(git cmd required^) and launch QGIS.
	echo.  dclean        to remove compiled python files of qgis plugins directory.
	echo.  derase        to remove deployed plugin.
	echo.  clean         to remove rcc generated file.
	echo.  doc           to build sphinx doc.
	echo.  zip           to create plugin zip bundle.
	echo.  upload        to upload plugin to Plugin repo ^(TODO !!!^).
	echo.  db            to launch db creation.
	echo.  deployDb      to deploy db plugin.
	echo.  eraseDb       to erase deployed db plugin.
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
	if "%2" == "clean" (
		goto testclean
	) else if "%2" == "dirty" (
		goto testdirty
	) else if "%2" == "big" (
		goto testbig
	) else if "%2" == "fb" (
		goto testfb
	) else if "%2" == "topo" (
		goto testtopo
	) else if "%2" == "sqlite" (
		goto testsqlite
	) else (
		echo.
		echo.Please use `make test ^<target^>` where ^<target^> is one of
		echo.
		echo.  clean       to test with coherent datasets.
		echo.  dirty       to test with incoherent datasets.
		echo.  big         to test on a big dataset.
		echo.  fb          to test with "fond blanc".
		echo.  topo        to test topology on a very simple dataset.
		echo.  sqlite      to test with sqlite format layers.
		goto end
	)
	:testclean
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-4-orthos-clean-toporules.qgs
	goto end
	:testdirty
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-4-orthos-toporules.qgs
	goto end
	:testbig
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-medium-clean.qgs
	goto end
	:testfb
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-cher.qgs
	goto end
	:testtopo
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-topo.qgs
	goto end
	:testsqlite
	tasklist /fi "imagename eq qgis-bin.exe" |find ":" > nul
	if errorlevel 1 taskkill /f /im qgis-bin.exe >nul
	git checkout ..\test-data
	call make deploy
	echo.
	echo.------------------------------------------
	echo.Launching QGIS plugin.
	echo.------------------------------------------
	..\test-data\test-std-echg\sqlite.qgs
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
	goto end
)

if "%1" == "doc" (
	:doc
	echo.
	echo.------------------------------------
	echo.Building documentation using sphinx.
	echo.------------------------------------
	cd help
	call make html
	cd..
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

if "%1" == "deployDb" (
	:deployDb
	echo.
	echo.---------------------------
	echo.Deploy db generate plugin.
	echo.---------------------------
	if not exist %QGISDIR%\%PLUGIN_DB_NAME% mkdir %QGISDIR%\%PLUGIN_DB_NAME%
	for %%i in (%PLUGIN_DB_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGIN_DB_NAME% /Y /I /Q
	)
	goto end
)

if "%1" == "db" (
	:db
	call make deployDb
	echo.
	echo.---------------------------
	echo.Generate db.
	echo.---------------------------
	Db\empty.qgs
	ping -n 10 127.0.0.1 >nul
	call make eraseDb
	goto end
)

if "%1" == "eraseDb" (
	:eraseDb
	echo.
	echo.-------------------------
	echo.Removing deployed db plugin.
	echo.-------------------------
	if exist %QGISDIR%\%PLUGIN_DB_NAME% rmdir %QGISDIR%\%PLUGIN_DB_NAME% /s /q
	goto end
)

:end