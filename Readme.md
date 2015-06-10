sudo -E add-apt-repository ppa:ubuntugis/ubuntugis-unstable

sudo apt-get update

sudo apt-get install qgis

* QGIS > 2.8 nécessaire

#### Installation
* installer pyQT4 (PyQT4-dev sous linux)
* installer le module pymouse (utile pour le test d'intégration)
    * **Windows:**
        * télécharger get-pip.py (https://bootstrap.pypa.io/get-pip.py)
        * ajouter au path {python_dir}/Scripts/pip.exe
        * l'exécuter (set HTTPS_PROXY si besoin)
        * cmd 'pip install PyUserInput'
* cmd 'make deploy' dans le répertoire OutilNomade

#### Environnement de dev
* Plugin eclipse 'pydev' : http://pydev.org/updates

#### Gestion des mises à jour dans le repository
Lorsqu'une release est prête:

* Modifier la version dans metadata.txt
* Générer MappingTools.zip dans le répertoire de dépôt avec la commande 'make zip'
* Remplacer MappingTools.zip dans le repository par celui généré précédamment
* Modifier la version dans le fichier MappingTools.xml du repository publie la mise à jour. Renseigner dans ce même fichier les infos de mise à jour.