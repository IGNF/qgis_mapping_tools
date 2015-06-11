@echo off
if "%1" == "" goto usage
if "%2" == "" goto usage
if "%3" == "" goto usage

setlocal enabledelayedexpansion

REM Boucle 
set counter=0
for %%x in (%*) do (
	set /A counter+=1
	
	REM Skip le premier parametre 
	if !counter! gtr 1 (
		
		if !counter! gtr 2 (			
			
			REM Recupere le nom du fichier
			echo source file : !LAST_PARAM!
			for %%y in (!LAST_PARAM!) do (
				SET LAST_FILENAME=%%~ny
			)
			
			fme fme\MiseEnCoherenceSegmentation.fmw  --chemin_child "%1\!LAST_FILENAME!.shp" --chemin_father %%x --chemin_sortie %1
			
		) else (
		
			REM copie du premer fil dans le rep resultat 
			mkdir %1
			copy "%%~dpnx.*" %1
		)		
		set LAST_PARAM=%%x
	)	
)



goto fin

:usage
echo Ce script prend au moins 3 parametres :
echo Le repertoire en sortie
echo Ensuite, les shapefiles en entree, du plus segmente au moins segmente, il en faut au moins 2..
echo
echo fmeScript.bat out "test\data\etat-major-1820\segment-16.shp" "test\data\etat-major-1820\segment-20.shp" "test\data\etat-major-1820\segment-30.shp" "test\data\etat-major-1820\segment-40.shp"
echo
goto fin2

:fin
echo "FINI"
REM  echo 

:fin2

REM fme fme\MiseEnCoherenceSegmentation.fmw   --chemin_father "test\data\etat-major-1820\segment-40.shp" --chemin_child "test\data\etat-major-1820\segment-30.shp" --chemin_sortie out
